from multiprocessing.managers import ListProxy
from multiprocessing.managers import DictProxy
from typing import Optional
from ..module import InstallProgressHandler

class InstallProgressMpDict(InstallProgressHandler):
    def __init__(self, module_name=None, module_version=None, install_state=None, quiet=True):
        super().__init__(module_name, module_version)
        self.module_name = module_name
        self.module_version = module_version
        self.install_state = install_state
        self.quiet = quiet

    def _reset_progress(self, update_time=False):
        from time import time
        self.install_state["cur_chunk"] = 0
        self.install_state["cur_size"] = 0
        self.install_state["total_size"] = 0
        if update_time:
            self.install_state["update_time"] = time()

    def stage_start(self, stage):
        from ..util.util import quiet_print

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
    from ..module import install_module
    from ..exceptions import ModuleToSkipInstallation

    while True:
        try:
            if install_queue:
                data = install_queue[0]
                module_name = data["module"]
                module_version = data["version"]
                initialize_install_state(install_state, module_name=module_name, module_version=module_version)
                stage_handler = InstallProgressMpDict(
                    module_name=module_name, module_version=module_version, install_state=install_state, quiet=False
                )
                try:
                    install_module(
                        module_name,
                        version=module_version,
                        stage_handler=stage_handler,
                        args={"overwrite": True},
                        fresh=True,
                    )
                    unqueue(module_name, install_queue)
                    local_modules_changed.set()
                except ModuleToSkipInstallation:
                    unqueue(module_name, install_queue)
                    stage_handler.stage_start("skip")
                except:
                    unqueue(module_name, install_queue)
                    stage_handler.stage_start("error")
                    raise
            sleep(1)
        except KeyboardInterrupt:
            break
        except Exception as _:
            import traceback
            traceback.print_exc()
            local_modules_changed.set()

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

def unqueue(module_name: Optional[str], install_queue):
    if not install_queue or not module_name:
        return
    data_to_del = None
    for data in install_queue:
        if data.get("module") == module_name:
            data_to_del = data
            break
    if data_to_del:
        install_queue.remove(data_to_del)

class StoreHandlers:
    def __init__(self, servermode=False, mu=None, local_modules_changed=None, install_state=None, install_queue=None, logger=None):
        self.servermode = servermode
        self.mu = mu
        self.local_modules_changed = local_modules_changed
        self.local_manifest = {}
        self.install_state = install_state
        self.install_queue = install_queue
        self.logger = logger
        self.wss = {}
        self.add_routes()

    def add_routes(self):
        self.routes = []
        self.routes.append(["GET", "/store/local", self.get_local_manifest])
        self.routes.append(["GET", "/store/locallogo", self.get_local_module_logo])
        self.routes.append(["GET", "/store/remote", self.get_remote_manifest])
        self.routes.append(["GET", "/store/remotelogo", self.get_remote_module_logo])
        self.routes.append(["GET", "/store/queueinstall", self.queue_install])
        self.routes.append(["GET", "/store/connectwebsocket", self.connect_websocket])
        self.routes.append(["GET", "/store/addlocal", self.add_local_module_info])
        self.routes.append(["GET", "/store/uninstall", self.uninstall_module])
        self.routes.append(["GET", "/store/getqueue", self.get_queue])
        self.routes.append(["GET", "/store/getinstallstate", self.get_install_state_web])
        self.routes.append(["GET", "/store/unqueue", self.unqueue_install])
        self.routes.append(["GET", "/store/getreadme", self.get_readme])
        self.routes.append(["GET", "/store/getmoduleimg", self.get_module_img])
        self.routes.append(["GET", "/store/locallogoexists/{module_name}", self.local_module_logo_exists])

    async def local_module_logo_exists(self, request):
        from aiohttp.web import json_response
        from ..module.cache import get_module_cache
        from pathlib import Path

        module_name = request.match_info["module_name"]
        module_info = get_module_cache().local[module_name]
        module_dir = module_info.directory
        logo_path = Path(module_dir) / "logo.png"
        if logo_path.exists():
            return json_response("success")
        else:
            return json_response("fail")

    def handle_modules_changed(self):
        from ..module.cache import get_module_cache

        if not self.local_manifest or (self.local_modules_changed and self.local_modules_changed.is_set()):
            get_module_cache().update_local()
            if self.local_modules_changed:
                self.local_modules_changed.clear()
            self.update_local_manifest()

    def update_local_manifest(self):
        from ..module.cache import get_module_cache
        self.local_manifest = {}
        local_cache = get_module_cache().get_local()
        for k, v in local_cache.items():
            m = v.serialize()
            self.local_manifest[k] = m

    async def get_local_manifest(self, _):
        from aiohttp.web import json_response

        self.handle_modules_changed()
        return json_response(self.local_manifest)

    async def get_local_module_logo(self, request):
        from aiohttp.web import FileResponse
        from ..module.cache import get_module_cache
        from ..system import get_default_logo_path
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


    def get_remote_manifest_cache(self) -> Optional[dict]:
        from os.path import exists
        from json import load
        from ..store.db import get_remote_manifest_cache_path

        cache_path = get_remote_manifest_cache_path()
        if cache_path and exists(cache_path):
            with open(cache_path) as f:
                content = load(f)
                return content
        else:
            return None

    def make_remote_manifest(self):
        from ..module.remote import make_remote_manifest
        content = make_remote_manifest()
        assert self.install_queue is not None
        for queue_data in self.install_queue:
            module_name: Optional[str] = queue_data.get("module")
            if not module_name:
                continue
            data = content.get("data", {}).get(module_name)
            if not data:
                continue
            content["data"][module_name]["queued"] = True
        return content

    async def get_remote_manifest(self, _):
        from aiohttp.web import json_response
        from ..store.db import save_remote_manifest_cache

        content = self.get_remote_manifest_cache()
        if content:
            return json_response(content)
        content = self.make_remote_manifest()
        save_remote_manifest_cache(content)
        return json_response(content)


    async def get_remote_module_logo(self, request):
        from aiohttp.web import FileResponse
        from os.path import exists
        from os.path import getsize
        from ..system import get_logo_path
        from ..system import get_default_logo_path

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

    async def queue_install(self, request):
        from aiohttp.web import Response
        if self.servermode and self.mu:
            if not await self.mu.is_admin_loggedin(request):
                return Response(status=403)
        queries = request.rel_url.query
        if "version" in queries:
            module_version = queries["version"]
        else:
            module_version = None
        module_name = queries["module"]
        data = {"module": module_name, "version": module_version}
        if self.install_queue is not None:
            self.install_queue.append(data)
        return Response(status=200)

    async def connect_websocket(self, request):
        import asyncio
        from aiohttp.web import WebSocketResponse
        import concurrent.futures
        from uuid import uuid4
        assert self.install_state is not None
        WS_COOKIE_KEY = "ws_id"
        ws_id = request.cookies.get(WS_COOKIE_KEY)
        if ws_id and ws_id in self.wss:
            del self.wss[ws_id]
        ws_id = str(uuid4())
        ws = WebSocketResponse(timeout=60 * 60 * 24 * 365)
        self.wss[ws_id] = ws
        await ws.prepare(request)
        last_update_time = self.install_state["update_time"]
        try:
            await ws.send_json({WS_COOKIE_KEY: ws_id})
        except ConnectionResetError:
            raise
        except:
            raise
        to_dels = []
        for ws_id in self.wss:
            ws_t = self.wss[ws_id]
            if ws_t.closed:
                to_dels.append(ws_id)
        for ws_id in to_dels:
            del self.wss[ws_id]
        print(f"@ wss={self.wss}")
        while True:
            await asyncio.sleep(1)
            if ws.closed:
                break
            if not last_update_time or last_update_time < self.install_state["update_time"]:
                try:
                    last_update_time = await self.send_socket_msg(ws=ws)
                except concurrent.futures._base.CancelledError:
                    pass
                except ConnectionResetError:
                    break
                except:
                    import traceback
                    traceback.print_exc()
        return ws

    async def send_socket_msg(self, ws=None):
        if not self.install_state or ws is None:
            return
        data = self.install_state.copy()
        last_update_time = self.install_state["update_time"]
        await ws.send_json(data)
        if self.install_state["stage"] in ["finish", "error", "skip", "killed"]:
            self.install_state.clear()
            self.install_state["update_time"] = last_update_time
        return last_update_time

    async def add_local_module_info(self, request):
        from aiohttp.web import Response
        from aiohttp.web import json_response
        #from ...module.local import get_local_module_info
        from ..module.cache import get_module_cache

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

    async def uninstall_module(self, request):
        from aiohttp.web import json_response
        from aiohttp.web import Response
        from oakvar.module import uninstall_module
        from ..exceptions import ServerError
        from ..module.cache import get_module_cache

        if self.servermode and self.mu:
            if not await self.mu.is_admin_loggedin(request):
                return Response(status=403)
        queries = request.rel_url.query
        module_name = queries["moduleName"]
        try:
            uninstall_module(module_name)
        except:
            raise ServerError()
        mc = get_module_cache()
        mc.update_local()
        if self.local_modules_changed:
            self.local_modules_changed.set()
        return json_response({"status": "success", "msg": "uninstalled" + module_name})

    async def get_queue(self, _):
        from aiohttp.web import json_response
        content = []
        if self.install_queue:
            for data in self.install_queue:
                content.append(data.get("module"))
        return json_response(content)

    async def get_install_state_web(self, _):
        from aiohttp.web import json_response
        content = {}
        if self.install_state:
            for k, v in self.install_state.items():
                content[k] = v
        return json_response(content)

    def send_kill_install_signal(self, module_name: Optional[str]):
        if not self.install_state or not module_name:
            return
        if self.install_state.get("module_name") == module_name:
            self.install_state["kill_signal"] = True

    async def unqueue_install(self, request):
        from aiohttp.web import Response
        if self.servermode and self.mu:
            if not await self.mu.is_admin_loggedin(request):
                return Response(status=403)
        queries = request.rel_url.query
        module_name = queries.get("module_name")
        if not module_name:
            return Response(status=404)
        if not self.install_state:
            return Response(status=404)
        if module_name == self.install_state.get("module_name"):
            self.send_kill_install_signal(module_name)
        unqueue(module_name, self.install_queue)
        return Response(status=200)

    async def get_readme(self, request):
        from aiohttp.web import Response
        from ..module.remote import get_readme

        queries = request.rel_url.query
        module_name = queries.get("module_name")
        if not module_name:
            return Response(status=404)
        readme = get_readme(module_name)
        if readme is None:
            return Response(status=404)
        return Response(text=readme)

    async def get_module_img(self, request):
        from pathlib import Path
        from aiohttp.web import Response
        from aiohttp.web import FileResponse
        from ..module.local import get_module_dir
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


