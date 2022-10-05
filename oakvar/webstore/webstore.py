import os
import json
from multiprocessing import Process, Manager
import time
import traceback
import asyncio
from aiohttp import web

from .. import consts
from ..util import admin_util as au
import shutil
import concurrent.futures
from ..system import get_system_conf
from ..module import InstallProgressHandler
from importlib import import_module
from importlib.util import find_spec
from typing import Optional

system_conf = get_system_conf()
install_manager = None
install_queue = None
install_state = {
        "stage": "",
        "message": "",
        "module_name": "",
        "module_version": "",
        "cur_chunk": 0,
        "total_chunks": 0,
        "cur_size": 0,
        "total_size": 0,
        "update_time": time.time()
}
install_worker = None
local_modules_changed = None
server_ready = False
servermode = None
logger = None
if find_spec("cravat_multiuser"):
    cravat_multiuser = import_module("cravat_multiuser")
else:
    cravat_multiuser = None

class InstallProgressMpDict(InstallProgressHandler):
    def __init__(self, module_name, module_version, install_state, quiet=True):
        super().__init__(module_name, module_version)
        self.module_name = module_name
        self.module_version = module_version
        self.install_state = install_state
        self.quiet = quiet

    def _reset_progress(self, update_time=False):
        self.install_state["cur_chunk"] = 0
        self.install_state["total_chunks"] = 0
        self.install_state["cur_size"] = 0
        self.install_state["total_size"] = 0
        if update_time:
            self.install_state["update_time"] = time.time()

    def stage_start(self, stage):
        from ..util.util import quiet_print

        global install_worker
        global last_update_time
        if self.install_state is None or len(self.install_state.keys()) == 0:
            self.install_state["stage"] = ""
            self.install_state["message"] = ""
            self.install_state["module_name"] = ""
            self.install_state["module_version"] = ""
            self.install_state["cur_chunk"] = 0
            self.install_state["total_chunks"] = 0
            self.install_state["cur_size"] = 0
            self.install_state["total_size"] = 0
            self.install_state["update_time"] = time.time()
            #last_update_time = self.install_state["update_time"]
        self.cur_stage = stage
        self.install_state["module_name"] = self.module_name
        self.install_state["module_version"] = self.module_version
        self.install_state["stage"] = self.cur_stage
        self.install_state["message"] = self._stage_msg(self.cur_stage)
        self.install_state["kill_signal"] = False
        self._reset_progress(update_time=True)
        #self.install_state["update_time"] = time.time()
        quiet_print(self.install_state["message"], {"quiet": self.quiet})

    def stage_progress(self, cur_chunk, total_chunks, cur_size, total_size):
        self.install_state["cur_chunk"] = cur_chunk
        self.install_state["total_chunks"] = total_chunks
        self.install_state["cur_size"] = cur_size
        self.install_state["total_size"] = total_size
        self.install_state["update_time"] = time.time()


def fetch_install_queue(install_queue, install_state, local_modules_changed):
    from ..module import install_module

    while True:
        try:
            data = install_queue.get()
            module_name = data["module"]
            module_version = data["version"]
            install_state["kill_signal"] = False
            stage_handler = InstallProgressMpDict(
                module_name, module_version, install_state, quiet=False
            )
            install_module(
                module_name,
                version=module_version,
                stage_handler=stage_handler,
            )
            local_modules_changed.set()
            time.sleep(1)
        except Exception as _:
            traceback.print_exc()
            local_modules_changed.set()


def get_remote_manifest_cache_path():
    from ..system import get_conf_dir
    from os.path import join
    return join(get_conf_dir(), "remote_manifest.json")

def save_remote_manifest_cache(content: dict):
    from json import dump
    cache_path = get_remote_manifest_cache_path()
    with open(cache_path, "w") as wf:
        dump(content, wf)

def get_remote_manifest_cache() -> Optional[dict]:
    from os.path import exists
    from json import load
    cache_path = get_remote_manifest_cache_path()
    if exists(cache_path):
        with open(cache_path) as f:
            content = load(f)
            return content
    return None

async def get_remote_manifest(_):
    from ..module.remote import make_remote_manifest
    global install_queue
    content = get_remote_manifest_cache()
    if content:
        return web.json_response(content)
    content = make_remote_manifest(install_queue)
    save_remote_manifest_cache(content)
    return web.json_response(content)


async def get_remote_module_output_columns(request):
    from ..module.remote import get_conf

    queries = request.rel_url.query
    module = queries["module"]
    conf = get_conf(module_name=module) or {}
    output_columns = conf.get("output_columns") or []
    return web.json_response(output_columns)


async def get_local_manifest(_):
    from ..module.cache import get_module_cache

    handle_modules_changed()
    content = {}
    for k, v in get_module_cache().local.items():
        content[k] = v.serialize()
    return web.json_response(content)


async def get_storeurl(request):
    from ..system import get_system_conf

    conf = get_system_conf()
    store_url = conf["store_url"]
    if request.scheme == "https":
        store_url = store_url.replace("http://", "https://")
    return web.Response(text=store_url)


async def get_module_readme(request):
    from oakvar.module import get_readme

    module_name = request.match_info["module"]
    version = request.match_info["version"]
    if version == "latest":
        version = None
    readme_md = get_readme(module_name)
    return web.Response(body=readme_md)


async def install_widgets_for_module(request):
    queries = request.rel_url.query
    module_name = queries["name"]
    au.install_widgets_for_module(module_name)
    content = "success"
    return web.json_response(content)


async def uninstall_module(request):
    from oakvar.module import uninstall_module
    from ..module.cache import get_module_cache

    global servermode
    if servermode and server_ready and cravat_multiuser:
        r = await cravat_multiuser.is_admin_loggedin(request)
        if r == False:
            response = "failure"
            return web.json_response(response)
    queries = request.rel_url.query
    module_name = queries["name"]
    uninstall_module(module_name)
    get_module_cache().update_local()
    response = "uninstalled " + module_name
    return web.json_response(response)


def start_worker():
    from time import time
    global install_worker
    global install_queue
    global install_state
    global install_manager
    global local_modules_changed
    install_manager = Manager()
    install_queue = install_manager.Queue()
    install_state = install_manager.dict()
    install_state["stage"] = ""
    install_state["message"] = ""
    install_state["module_name"] = ""
    install_state["module_version"] = ""
    install_state["cur_chunk"] = ""
    install_state["total_chunk"] = ""
    install_state["cur_size"] = ""
    install_state["total_size"] = ""
    install_state["update_time"] = time()
    local_modules_changed = install_manager.Event()
    if install_worker == None:
        install_worker = Process(
            target=fetch_install_queue,
            args=(install_queue, install_state, local_modules_changed),
        )
        install_worker.start()


async def send_socket_msg(install_ws=None):
    global install_state
    if install_state is not None:
        data = {}
        data["module"] = install_state["module_name"]
        data["msg"] = install_state["message"]
        #if "Downloading " in data["msg"]:
        #    data["msg"] = data["msg"]  # + " " + str(install_state["cur_chunk"]) + "%"
        if install_ws is not None:
            await install_ws.send_str(json.dumps(data))
        last_update_time = install_state["update_time"]
        return last_update_time
    else:
        return None


async def connect_websocket(request):
    global install_state
    last_update_time = None
    if not install_state:
        install_state = {}
        install_state["stage"] = ""
        install_state["message"] = ""
        install_state["module_name"] = ""
        install_state["module_version"] = ""
        install_state["cur_chunk"] = 0
        install_state["total_chunks"] = 0
        install_state["cur_size"] = 0
        install_state["total_size"] = 0
        install_state["update_time"] = time.time()
        install_state["kill_signal"] = False
        last_update_time = install_state["update_time"]
    install_ws = web.WebSocketResponse(timeout=60 * 60 * 24 * 365)
    await install_ws.prepare(request)
    while True:
        try:
            await asyncio.sleep(1)
        except concurrent.futures._base.CancelledError:
            return install_ws
        if not last_update_time or last_update_time < install_state["update_time"]:
            last_update_time = await send_socket_msg(install_ws=install_ws)
    # return install_ws


async def queue_install(request):
    global install_queue
    global servermode
    if servermode and server_ready and cravat_multiuser:
        r = await cravat_multiuser.is_admin_loggedin(request)
        if r == False:
            response = "notadmin"
            return web.json_response(response)
    queries = request.rel_url.query
    if "version" in queries:
        module_version = queries["version"]
    else:
        module_version = None
    module_name = queries["module"]
    data = {"module": module_name, "version": module_version}
    if install_queue is not None:
        install_queue.put(data)
    # deps, deps_pypi = get_install_deps(module_name, module_version)
    # if deps:
    #    for dep_name, dep_version in deps.items():
    #        if install_queue is not None:
    #            install_queue.put({"module": dep_name, "version": dep_version})
    return web.Response(text="queued " + queries["module"])


async def get_base_modules(_):
    global system_conf
    base_modules = system_conf["base_modules"]
    return web.json_response(base_modules)


async def install_base_modules(request):
    global servermode
    if servermode and server_ready and cravat_multiuser:
        r = await cravat_multiuser.is_admin_loggedin(request)
        if r == False:
            response = "failed"
            return web.json_response(response)
    from ..system.consts import base_modules_key

    base_modules = system_conf.get(base_modules_key, [])
    for module in base_modules:
        if install_queue is not None:
            install_queue.put({"module": module, "version": None})
    response = "queued"
    return web.json_response(response)


async def get_md(_):
    from ..system import get_modules_dir

    modules_dir = get_modules_dir()
    return web.Response(text=modules_dir)


async def get_module_updates(request):
    handle_modules_changed()
    queries = request.rel_url.query
    smodules = queries.get("modules", "")
    if smodules:
        modules = smodules.split(",")
    else:
        modules = []
    ret = await au.get_updatable_async(modules=modules)
    [updates, _, conflicts] = ret
    sconflicts = {}
    for mname, reqd in conflicts.items():
        sconflicts[mname] = {}
        for req_name, req in reqd.items():
            sconflicts[mname][req_name] = str(req)
    updatesd = {
        mname: {"version": info.version, "size": info.size}
        for mname, info in updates.items()
    }
    out = {"updates": updatesd, "conflicts": sconflicts}
    return web.json_response(out)


async def get_free_modules_space(_):
    from ..system import get_modules_dir

    modules_dir = get_modules_dir()
    free_space = shutil.disk_usage(modules_dir).free
    return web.json_response(free_space)


def unqueue(module):
    global install_queue
    tmp_queue_data = []
    if module is not None:
        while True:
            if install_queue is not None:
                if install_queue.empty():
                    break
                data = install_queue.get()
                if data["module"] != module:
                    tmp_queue_data.append([data["module"], data.get("version", "")])
    for data in tmp_queue_data:
        if install_queue is not None:
            install_queue.put({"module": data[0], "version": data[1]})


async def kill_install(request):
    global install_queue
    global install_state
    queries = request.rel_url.query
    module = queries.get("module", None)
    if install_state is not None:
        if "module_name" in install_state and install_state["module_name"] == module:
            install_state["kill_signal"] = True
    return web.json_response("done")


async def unqueue_install(request):
    global install_state
    queries = request.rel_url.query
    module = queries.get("module", None)
    unqueue(module)
    if install_state is not None:
        module_name_bak = install_state["module_name"]
        msg_bak = install_state["message"]
        install_state["module_name"] = module
        install_state["message"] = "Unqueued"
        await send_socket_msg()
        install_state["module_name"] = module_name_bak
        install_state["message"] = msg_bak
    return web.json_response("done")


async def get_tag_desc(_):
    return consts.module_tag_desc


async def update_remote(request):
    from ..module.cache import get_module_cache
    from ..store.db import fetch_ov_store_cache
    from ..module.remote import make_remote_manifest

    global install_queue
    if servermode and server_ready and cravat_multiuser:
        r = await cravat_multiuser.is_admin_loggedin(request)
        if r == False:
            response = "notadmin"
            return web.json_response(response)
    module_cache = get_module_cache()
    fetch_ov_store_cache()
    module_cache.update_local()
    content = make_remote_manifest(install_queue)
    save_remote_manifest_cache(content)
    return web.json_response("done")


def handle_modules_changed():
    from ..module.cache import get_module_cache

    if local_modules_changed and local_modules_changed.is_set():
        get_module_cache().update_local()
        local_modules_changed.clear()


async def get_remote_manifest_from_local(request):
    from ..module.local import get_remote_manifest_from_local

    queries = request.rel_url.query
    module = queries.get("module", None)
    if module is None:
        return web.json_response({})
    rmi = get_remote_manifest_from_local(module)
    return web.json_response(rmi)


async def local_module_logo_exists(request):
    from ..module.cache import get_module_cache
    from os.path import exists
    module_name = request.match_info["module_name"]
    module_info = get_module_cache().local[module_name]
    module_dir = module_info.directory
    logo_path = os.path.join(module_dir, "logo.png")
    if exists(logo_path):
        return web.json_response("success")
    else:
        return web.json_response("fail")

async def get_local_module_logo(request):
    from ..module.cache import get_module_cache
    from os.path import exists
    queries = request.rel_url.query
    module = queries.get("module", None)
    module_info = get_module_cache().local[module]
    module_dir = module_info.directory
    logo_path = os.path.join(module_dir, "logo.png")
    if exists(logo_path):
        return web.FileResponse(logo_path)
    else:
        #p = join(dirname(abspath(__file__)), "images", "genericmodulelogo.png")
        #return web.FileResponse(p)
        return web.HTTPNotFound()


async def get_logo(request):
    from ..system import get_logo_path

    module_name = request.match_info["module_name"]
    store = request.match_info["store"]
    logo_path = get_logo_path(module_name, store)
    return web.FileResponse(logo_path)


routes = []
routes.append(["GET", "/store/remote", get_remote_manifest])
routes.append(["GET", "/store/installwidgetsformodule", install_widgets_for_module])
routes.append(["GET", "/store/getstoreurl", get_storeurl])
routes.append(["GET", "/store/local", get_local_manifest])
routes.append(["GET", "/store/uninstall", uninstall_module])
routes.append(["GET", "/store/connectwebsocket", connect_websocket])
routes.append(["GET", "/store/queueinstall", queue_install])
routes.append(["GET", "/store/modules/{module}/{version}/readme", get_module_readme])
routes.append(["GET", "/store/getbasemodules", get_base_modules])
routes.append(["GET", "/store/installbasemodules", install_base_modules])
routes.append(["GET", "/store/remotemoduleconfig", get_remote_module_output_columns])
routes.append(["GET", "/store/getmd", get_md])
routes.append(["GET", "/store/updates", get_module_updates])
routes.append(["GET", "/store/freemodulesspace", get_free_modules_space])
routes.append(["GET", "/store/killinstall", kill_install])
routes.append(["GET", "/store/unqueue", unqueue_install])
routes.append(["GET", "/store/tagdesc", get_tag_desc])
routes.append(["GET", "/store/updateremote", update_remote])
routes.append(["GET", "/store/localasremote", get_remote_manifest_from_local])
routes.append(["GET", "/store/locallogo", get_local_module_logo])
routes.append(["GET", "/store/locallogoexists/{module_name}", local_module_logo_exists])
routes.append(["GET", "/store/logo/{store}/{module_name}", get_logo])
