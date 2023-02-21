from typing import Optional


class StoreHandlers:
    def __init__(
        self,
        servermode=False,
        manager=None,
        mu=None,
        local_modules_changed=None,
        system_worker_state=None,
        system_queue=None,
        logger=None,
    ):
        self.servermode = servermode
        self.mu = mu
        self.local_modules_changed = local_modules_changed
        self.local_manifest = {}
        self.system_worker_state = system_worker_state
        self.manager = manager
        self.system_queue = system_queue
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
        self.routes.append(["GET", "/store/addlocal", self.add_local_module_info])
        self.routes.append(["GET", "/store/uninstall", self.uninstall_module])
        self.routes.append(["GET", "/store/getqueue", self.get_queue])
        self.routes.append(
            ["GET", "/store/getinstallstate", self.get_system_worker_state_web]
        )
        self.routes.append(["GET", "/store/unqueue", self.unqueue_install])
        self.routes.append(["GET", "/store/getreadme", self.get_readme])
        self.routes.append(["GET", "/store/getmoduleimg", self.get_module_img])
        self.routes.append(
            [
                "GET",
                "/store/locallogoexists/{module_name}",
                self.local_module_logo_exists,
            ]
        )

    async def local_module_logo_exists(self, request):
        from aiohttp.web import json_response
        from ..lib.module.cache import get_module_cache
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
        from ..lib.module.cache import get_module_cache

        if not self.local_manifest or (
            self.local_modules_changed and self.local_modules_changed.is_set()
        ):
            get_module_cache().update_local()
            if self.local_modules_changed:
                self.local_modules_changed.clear()
            self.update_local_manifest()

    def update_local_manifest(self):
        from ..lib.module.cache import get_module_cache

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
        from ..lib.module.cache import get_module_cache
        from ..lib.system import get_default_logo_path
        from pathlib import Path

        queries = request.rel_url.query
        module = queries.get("module", None)
        if not module:
            return FileResponse(get_default_logo_path())
        module_info = get_module_cache().local[module]
        module_dir = module_info.directory
        logo_path = Path(module_dir) / "logo.png"
        if logo_path.exists():
            res = FileResponse(logo_path)
            return res
        else:
            return FileResponse(get_default_logo_path())

    def get_remote_manifest_cache(self) -> Optional[dict]:
        from os.path import exists
        from json import load
        from ..lib.store.db import get_remote_manifest_cache_path

        cache_path = get_remote_manifest_cache_path()
        if cache_path and exists(cache_path):
            with open(cache_path) as f:
                content = load(f)
                return content
        else:
            return None

    def make_remote_manifest(self):
        from ..lib.module.remote import make_remote_manifest

        content = make_remote_manifest()
        assert self.system_queue is not None
        for queue_data in self.system_queue:
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
        from ..lib.store.db import save_remote_manifest_cache

        content = self.get_remote_manifest_cache()
        if content:
            return json_response(content)
        content = self.make_remote_manifest()
        save_remote_manifest_cache(content)
        return json_response(content)

    async def get_remote_module_logo(self, request):
        from aiohttp.web import FileResponse
        from os.path import getsize
        from ..lib.system import get_logo_path
        from ..lib.system import get_default_logo_path

        queries = request.rel_url.query
        module_name = queries.get("module", None)
        store = queries.get("store", None)
        logo_path = get_logo_path(module_name, store)
        if not logo_path or not logo_path.exists() or getsize(logo_path) == 0:
            if store == "ov":
                logo_path = get_logo_path(module_name, "oc")
        if logo_path and logo_path.exists() and getsize(logo_path) > 0:
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
        data = {
            "work_type": "install_module",
            "module": module_name,
            "version": module_version,
        }
        if self.system_queue is not None:
            self.system_queue.append(data)
        self.initialize_system_worker_state_for_install(module_name, module_version)
        return Response(status=200)

    async def add_local_module_info(self, request):
        from aiohttp.web import Response
        from aiohttp.web import json_response

        # from ...module.local import get_local_module_info
        from ..lib.module.cache import get_module_cache

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
        from oakvar.lib.module import uninstall_module
        from ..lib.exceptions import ServerError
        from ..lib.module.cache import get_module_cache

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
        from .consts import SYSTEM_STATE_INSTALL_QUEUE_KEY

        content = []
        if (
            self.system_worker_state
            and self.system_worker_state[SYSTEM_STATE_INSTALL_QUEUE_KEY]
        ):
            for module_name in self.system_worker_state[SYSTEM_STATE_INSTALL_QUEUE_KEY]:
                content.append(module_name)
        return json_response(content)

    async def get_system_worker_state_web(self, _):
        from aiohttp.web import json_response
        from .util import copy_state
        from .consts import SYSTEM_STATE_INSTALL_KEY

        content = copy_state(self.system_worker_state[SYSTEM_STATE_INSTALL_KEY])
        return json_response(content)

    def send_kill_install_signal(self, module_name: Optional[str]):
        from .consts import SYSTEM_STATE_INSTALL_KEY
        from .consts import INSTALL_KILL_SIGNAL

        if not self.system_worker_state or not module_name:
            return
        if module_name in self.system_worker_state:
            self.system_worker_state[SYSTEM_STATE_INSTALL_KEY][module_name][
                INSTALL_KILL_SIGNAL
            ] = True

    async def unqueue_install(self, request):
        from aiohttp.web import Response
        from .consts import SYSTEM_STATE_INSTALL_KEY

        if self.servermode and self.mu:
            if not await self.mu.is_admin_loggedin(request):
                return Response(status=403)
        queries = request.rel_url.query
        module_name = queries.get("module_name")
        if not module_name:
            return Response(status=404)
        if not self.system_worker_state:
            return Response(status=404)
        if module_name in self.system_worker_state[SYSTEM_STATE_INSTALL_KEY]:
            self.send_kill_install_signal(module_name)
        self.unqueue(module_name)
        return Response(status=200)

    def unqueue(self, module_name):
        from .consts import SYSTEM_STATE_INSTALL_KEY
        from .consts import SYSTEM_STATE_INSTALL_QUEUE_KEY

        to_del = None
        for i in range(len(self.system_queue)):
            if self.system_queue[i].get("module") == module_name:
                to_del = i
                break
        if to_del is not None:
            self.system_queue.pop(to_del)
        if module_name in self.system_worker_state[SYSTEM_STATE_INSTALL_QUEUE_KEY]:
            self.system_worker_state[SYSTEM_STATE_INSTALL_QUEUE_KEY].remove(module_name)
        if module_name in self.system_worker_state[SYSTEM_STATE_INSTALL_KEY]:
            del self.system_worker_state[SYSTEM_STATE_INSTALL_KEY][module_name]

    async def get_readme(self, request):
        from aiohttp.web import Response
        from ..lib.module.remote import get_readme

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
        from ..lib.module.local import get_module_dir

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

    def initialize_system_worker_state_for_install(
        self,
        module_name: str = "",
        module_version: Optional[str] = None,
    ):
        from .consts import SYSTEM_STATE_INSTALL_KEY
        from .consts import SYSTEM_STATE_INSTALL_QUEUE_KEY

        if self.system_worker_state is None:
            return
        if self.manager is None:
            return
        d = self.manager.dict()
        d["stage"] = ""
        d["module_name"] = module_name
        d["module_version"] = module_version
        d["cur_size"] = 0
        d["total_size"] = 0
        d["kill"] = False
        self.system_worker_state[SYSTEM_STATE_INSTALL_KEY][module_name] = d
        self.system_worker_state[SYSTEM_STATE_INSTALL_QUEUE_KEY].append(module_name)
