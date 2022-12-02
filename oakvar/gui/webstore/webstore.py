from multiprocessing.managers import ListProxy
from multiprocessing.managers import DictProxy
from typing import Optional
import time
from ...system import get_system_conf
from ...module import InstallProgressHandler

system_conf = get_system_conf()
install_manager = None
install_queue: Optional[ListProxy] = None
install_state = None
wss = {}
install_worker = None
local_modules_changed = None
server_ready = False
servermode = None
logger = None
mu = None
local_manifest = None


class InstallProgressMpDict(InstallProgressHandler):
    def __init__(self, module_name, module_version, install_state, quiet=True):
        super().__init__(module_name, module_version)
        self.module_name = module_name
        self.module_version = module_version
        self.install_state = install_state
        self.quiet = quiet

    def _reset_progress(self, update_time=False):
        self.install_state["cur_chunk"] = 0
        self.install_state["cur_size"] = 0
        self.install_state["total_size"] = 0
        if update_time:
            self.install_state["update_time"] = time.time()

    def stage_start(self, stage):
        from ...util.util import quiet_print

        global install_worker
        global last_update_time
        self.cur_stage = stage
        initialize_install_state(self.install_state)
        self.install_state["module_name"] = self.module_name
        self.install_state["module_version"] = self.module_version
        self.install_state["stage"] = self.cur_stage
        self.install_state["message"] = self._stage_msg(self.cur_stage)
        self.install_state["kill_signal"] = False
        self._reset_progress(update_time=True)
        quiet_print(self.install_state["message"], {"quiet": self.quiet})


def fetch_install_queue(install_queue: ListProxy, install_state: Optional[DictProxy], local_modules_changed):
    from time import sleep
    from ...module import install_module
    from ...exceptions import ModuleToSkipInstallation

    while True:
        try:
            if install_queue:
                data = install_queue[0]
                module_name = data["module"]
                module_version = data["version"]
                initialize_install_state(install_state, module_name=module_name, module_version=module_version)
                stage_handler = InstallProgressMpDict(
                    module_name, module_version, install_state, quiet=False
                )
                try:
                    install_module(
                        module_name,
                        version=module_version,
                        stage_handler=stage_handler,
                        args={"overwrite": True},
                        fresh=True,
                    )
                    unqueue(module_name)
                    local_modules_changed.set()
                except ModuleToSkipInstallation:
                    unqueue(module_name)
                    stage_handler.stage_start("skip")
                except:
                    unqueue(module_name)
                    stage_handler.stage_start("error")
                    raise
            sleep(1)
        except KeyboardInterrupt:
            break
        except Exception as _:
            import traceback
            traceback.print_exc()
            local_modules_changed.set()


def get_remote_manifest_cache_path():
    from ...system import get_conf_dir
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
    else:
        return None


def make_remote_manifest():
    from ...module.remote import make_remote_manifest
    content = make_remote_manifest()
    install_queue: Optional[ListProxy[dict]] = get_install_queue()
    if install_queue:
        for queue_data in install_queue:
            module_name: Optional[str] = queue_data.get("module")
            if not module_name:
                continue
            data = content.get("data", {}).get(module_name)
            if not data:
                continue
            content["data"][module_name]["queued"] = True
    return content

async def get_remote_manifest(_):
    from aiohttp.web import json_response

    content = get_remote_manifest_cache()
    if content:
        return json_response(content)
    content = make_remote_manifest()
    save_remote_manifest_cache(content)
    return json_response(content)


async def get_remote_module_output_columns(request):
    from aiohttp.web import json_response
    from ...module.remote import get_conf

    queries = request.rel_url.query
    module = queries["module"]
    conf = get_conf(module_name=module) or {}
    output_columns = conf.get("output_columns") or []
    return json_response(output_columns)


def update_local_manifest():
    from ...module.cache import get_module_cache
    global local_manifest
    local_manifest = {}
    local_cache = get_module_cache().get_local()
    for k, v in local_cache.items():
        m = v.serialize()
        local_manifest[k] = m

async def get_local_manifest(_):
    from aiohttp.web import json_response

    global local_manifest
    handle_modules_changed()
    return json_response(local_manifest)


async def uninstall_module(request):
    from aiohttp.web import json_response
    from aiohttp.web import Response
    from oakvar.module import uninstall_module
    from ...exceptions import ServerError
    from ...module.cache import get_module_cache

    global servermode
    global local_modules_changed
    if servermode and mu:
        if not await mu.is_admin_loggedin(request):
            return Response(status=403)
    queries = request.rel_url.query
    module_name = queries["moduleName"]
    try:
        uninstall_module(module_name)
    except:
        raise ServerError()
    mc = get_module_cache()
    mc.update_local()
    if local_modules_changed:
        local_modules_changed.set()
    return json_response({"status": "success", "msg": "uninstalled" + module_name})


def start_worker():
    from multiprocessing import Process
    from multiprocessing import Manager

    global install_worker
    global install_queue
    global install_state
    global install_manager
    global local_modules_changed
    install_manager = Manager()
    install_queue = get_install_queue()
    install_state = get_install_state()
    local_modules_changed = install_manager.Event()
    if install_worker == None:
        install_worker = Process(
            target=fetch_install_queue,
            args=(install_queue, install_state, local_modules_changed),
        )
        install_worker.start()


async def send_socket_msg(ws=None):
    install_state = get_install_state()
    if not install_state or ws is None:
        return
    data = install_state.copy()
    last_update_time = install_state["update_time"]
    await ws.send_json(data)
    if install_state["stage"] in ["finish", "error", "skip", "killed"]:
        install_state.clear()
        install_state["update_time"] = last_update_time
    return last_update_time


async def connect_websocket(request):
    import asyncio
    from aiohttp.web import WebSocketResponse
    import concurrent.futures
    from uuid import uuid4
    global wss
    install_state = get_install_state()
    assert install_state is not None
    WS_COOKIE_KEY = "ws_id"
    ws_id = request.cookies.get(WS_COOKIE_KEY)
    if ws_id and ws_id in wss:
        del wss[ws_id]
    ws_id = str(uuid4())
    ws = WebSocketResponse(timeout=60 * 60 * 24 * 365)
    wss[ws_id] = ws
    await ws.prepare(request)
    last_update_time = install_state["update_time"]
    try:
        await ws.send_json({WS_COOKIE_KEY: ws_id})
    except ConnectionResetError:
        raise
    except:
        raise
    to_dels = []
    for ws_id in wss:
        ws_t = wss[ws_id]
        if ws_t.closed:
            to_dels.append(ws_id)
    for ws_id in to_dels:
        del wss[ws_id]
    while True:
        await asyncio.sleep(1)
        if ws.closed:
            break
        if not last_update_time or last_update_time < install_state["update_time"]:
            try:
                last_update_time = await send_socket_msg(ws=ws)
            except concurrent.futures._base.CancelledError:
                pass
            except ConnectionResetError:
                break
            except:
                import traceback
                traceback.print_exc()
    return ws


def get_install_queue():
    global install_queue
    global install_manager
    if install_queue is not None:
        return install_queue
    if not install_manager:
        return None
    install_queue = install_manager.list()
    return install_queue

def get_install_state():
    global install_state
    global install_manager
    if install_state is not None:
        return install_state
    if not install_manager:
        return None
    install_state = install_manager.dict()
    initialize_install_state(install_state)
    return install_state

def initialize_install_state(install_state: Optional[DictProxy], module_name="", module_version=""):
    from time import time
    if install_state is None:
        return
    d = {}
    d["stage"] = ""
    d["message"] = ""
    d["module_name"] = module_name
    d["module_version"] = module_version
    d["cur_chunk"] = 0
    d["total_chunk"] = 0
    d["cur_size"] = 0
    d["total_size"] = 0
    d["update_time"] = time()
    d["kill"] = False
    for k, v in d.items():
        install_state[k] = v

async def queue_install(request):
    from aiohttp.web import Response
    global servermode
    if servermode and mu:
        if not await mu.is_admin_loggedin(request):
            return Response(status=403)
    queries = request.rel_url.query
    if "version" in queries:
        module_version = queries["version"]
    else:
        module_version = None
    module_name = queries["module"]
    data = {"module": module_name, "version": module_version}
    install_queue = get_install_queue()
    if install_queue is not None:
        install_queue.append(data)
    return Response(status=200)


async def install_base_modules(request):
    from aiohttp.web import Response
    from ...system.consts import base_modules_key
    global servermode
    if servermode and mu:
        if not await mu.is_admin_loggedin(request):
            return Response(status=403)
    base_modules = system_conf.get(base_modules_key, [])
    install_queue = get_install_queue()
    for module in base_modules:
        if install_queue is not None:
            install_queue.append({"module": module, "version": None})
    return Response(status=200)


async def get_readme(request):
    from aiohttp.web import Response
    from ...module.remote import get_readme

    queries = request.rel_url.query
    module_name = queries.get("module_name")
    if not module_name:
        return Response(status=404)
    readme = get_readme(module_name)
    if readme is None:
        return Response(status=404)
    return Response(text=readme)


async def get_module_updates(request):
    from aiohttp.web import json_response
    from ...util.admin_util import get_updatable_async
    handle_modules_changed()
    queries = request.rel_url.query
    smodules = queries.get("modules", "")
    if smodules:
        modules = smodules.split(",")
    else:
        modules = []
    ret = await get_updatable_async(modules=modules)
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
    return json_response(out)


async def get_free_modules_space(_):
    from aiohttp.web import json_response
    from ...system import get_modules_dir
    import shutil

    modules_dir = get_modules_dir()
    free_space = shutil.disk_usage(modules_dir).free
    return json_response(free_space)


def send_kill_install_signal(module_name: Optional[str]):
    install_state = get_install_state()
    if not install_state or not module_name:
        return
    if install_state.get("module_name") == module_name:
        install_state["kill_signal"] = True


def unqueue(module_name: Optional[str]):
    install_queue = get_install_queue()
    if not install_queue or not module_name:
        return
    data_to_del = None
    for data in install_queue:
        if data.get("module") == module_name:
            data_to_del = data
            break
    if data_to_del:
        install_queue.remove(data_to_del)


async def unqueue_install(request):
    from aiohttp.web import Response
    if servermode and mu:
        if not await mu.is_admin_loggedin(request):
            return Response(status=403)
    queries = request.rel_url.query
    module_name = queries.get("module_name")
    if not module_name:
        return Response(status=404)
    install_state = get_install_state()
    if not install_state:
        return Response(status=404)
    if module_name == install_state.get("module_name"):
        send_kill_install_signal(module_name)
    unqueue(module_name)
    return Response(status=200)


async def get_tag_desc(_):
    from ...consts import module_tag_desc
    return module_tag_desc


async def update_remote(request):
    from aiohttp.web import json_response
    from aiohttp.web import Response
    from ...module.cache import get_module_cache
    from ...store.db import fetch_ov_store_cache

    if servermode and mu:
        if not await mu.is_admin_loggedin(request):
            return Response(status=403)
    module_cache = get_module_cache()
    fetch_ov_store_cache()
    module_cache.update_local()
    content = make_remote_manifest()
    save_remote_manifest_cache(content)
    return json_response("done")


def handle_modules_changed():
    from ...module.cache import get_module_cache

    global local_manifest
    if not local_manifest or (local_modules_changed and local_modules_changed.is_set()):
        get_module_cache().update_local()
        if local_modules_changed:
            local_modules_changed.clear()
        update_local_manifest()


async def get_remote_manifest_from_local(request):
    from aiohttp.web import json_response
    from ...module.local import get_remote_manifest_from_local

    queries = request.rel_url.query
    module = queries.get("module", None)
    if module is None:
        return json_response({})
    rmi = get_remote_manifest_from_local(module)
    return json_response(rmi)


async def local_module_logo_exists(request):
    from aiohttp.web import json_response
    from ...module.cache import get_module_cache
    from pathlib import Path

    module_name = request.match_info["module_name"]
    module_info = get_module_cache().local[module_name]
    module_dir = module_info.directory
    logo_path = Path(module_dir) / "logo.png"
    if logo_path.exists():
        return json_response("success")
    else:
        return json_response("fail")


async def get_local_module_logo(request):
    from aiohttp.web import FileResponse
    from ...module.cache import get_module_cache
    from ...system import get_default_logo_path
    from pathlib import Path

    queries = request.rel_url.query
    module = queries.get("module", None)
    module_info = get_module_cache().local[module]
    module_dir = module_info.directory
    logo_path = Path(module_dir) / "logo.png"
    if logo_path.exists():
        return FileResponse(logo_path)
    else:
        return FileResponse(get_default_logo_path())


async def get_remote_module_logo(request):
    from aiohttp.web import FileResponse
    from os.path import exists
    from os.path import getsize
    from ...system import get_logo_path
    from ...system import get_default_logo_path

    queries = request.rel_url.query
    module_name = queries.get("module", None)
    store = queries.get("store", None)
    logo_path = get_logo_path(module_name, store)
    if not exists(logo_path) or getsize(logo_path) == 0:
        if store == "ov":
            logo_path = get_logo_path(module_name, "oc")
    if exists(logo_path) and getsize(logo_path) > 0:
        return FileResponse(logo_path)
    else:
        return FileResponse(get_default_logo_path())


async def add_local_module_info(request):
    from aiohttp.web import Response
    from aiohttp.web import json_response
    #from ...module.local import get_local_module_info
    from ...module.cache import get_module_cache

    queries = request.rel_url.query
    module_name = queries.get("moduleName")
    if not module_name:
        return Response(status=404)
    mc = get_module_cache()
    mdir = mc.add_local(module_name)
    if not mdir:
        return Response(status=404)
    module_info = mc.get_local()[module_name]
    return json_response(module_info.serialize())

async def get_queue(_):
    from aiohttp.web import json_response
    install_queue = get_install_queue()
    content = []
    if install_queue:
        for data in install_queue:
            content.append(data.get("module"))
    return json_response(content)

async def get_install_state_web(_):
    from aiohttp.web import json_response
    install_state = get_install_state()
    content = {}
    if install_state:
        for k, v in install_state.items():
            content[k] = v
    return json_response(content)

async def get_module_img(request):
    from pathlib import Path
    from aiohttp.web import Response
    from aiohttp.web import FileResponse
    from ...module.local import get_module_dir
    queries = request.rel_url.query
    module_name = queries.get("module_name")
    fname = queries.get("file")
    if not module_name:
        return Response(status=404)
    module_dir = get_module_dir(module_name)
    if not module_dir:
        return Response(status=404)
    p = Path(module_dir) / fname
    if not p.exists():
        return Response(status=404)
    return FileResponse(p)

routes = []
routes.append(["GET", "/store/installbasemodules", install_base_modules])
routes.append(["GET", "/store/remotemoduleconfig", get_remote_module_output_columns])
routes.append(["GET", "/store/updates", get_module_updates])
routes.append(["GET", "/store/freemodulesspace", get_free_modules_space])
routes.append(["GET", "/store/tagdesc", get_tag_desc])
routes.append(["GET", "/store/updateremote", update_remote])
routes.append(["GET", "/store/localasremote", get_remote_manifest_from_local])
routes.append(["GET", "/store/locallogoexists/{module_name}", local_module_logo_exists])
# for new gui.
routes.append(["GET", "/store/local", get_local_manifest])
routes.append(["GET", "/store/locallogo", get_local_module_logo])
routes.append(["GET", "/store/remote", get_remote_manifest])
routes.append(["GET", "/store/remotelogo", get_remote_module_logo])
routes.append(["GET", "/store/queueinstall", queue_install])
routes.append(["GET", "/store/connectwebsocket", connect_websocket])
routes.append(["GET", "/store/addlocal", add_local_module_info])
routes.append(["GET", "/store/uninstall", uninstall_module])
routes.append(["GET", "/store/getqueue", get_queue])
routes.append(["GET", "/store/getinstallstate", get_install_state_web])
routes.append(["GET", "/store/unqueue", unqueue_install])
routes.append(["GET", "/store/getreadme", get_readme])
routes.append(["GET", "/store/getmoduleimg", get_module_img])
