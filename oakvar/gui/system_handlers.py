class SystemHandlers:
    def __init__(self, servermode=False, mu=None, logger=None):
        self.servermode = servermode
        self.mu = mu
        self.logger = logger
        self.add_routes()

    def add_routes(self):
        self.routes = []
        self.routes.append(["GET", "/submit/systemlog", self.get_system_log])
        self.routes.append(["GET", "/submit/servermode", self.get_servermode])
        self.routes.append(["GET", "/submit/loginstate", self.get_login_state])
        self.routes.append(["GET", "/submit/pkgver", self.get_package_versions])
        self.routes.append(["GET", "/submit/rootdir", self.get_root_dir])
        self.routes.append(["GET", "/submit/modulesdir", self.get_modules_dir])
        self.routes.append(["GET", "/submit/jobsdir", self.get_jobs_dir])
        self.routes.append(["GET", "/submit/logdir", self.get_log_dir])
        self.routes.append(["GET", "/submit/checkserverdir", self.check_server_dir])
        self.routes.append(["POST", "/submit/startsetup", self.start_setup])
        self.routes.append(["GET", "/submit/localmodules/{module}", self.get_local_module_info_web])

    async def get_local_module_info_web(self, request):
        from aiohttp.web import json_response
        from ..module.local import get_local_module_info

        module_name = request.match_info["module"]
        mi = get_local_module_info(module_name)
        if mi:
            return json_response(mi.serialize())
        else:
            return json_response({})

    async def start_setup(self, request):
        from aiohttp.web import Response
        from ..system import setup_system
        from ..system.consts import root_dir_key
        from ..system.consts import modules_dir_key
        from ..system.consts import jobs_dir_key
        from ..system.consts import log_dir_key
        data = await request.json()
        args = {
            "email": data.get("email"),
            "pw": data.get("pw"),
            "quiet": False,
            "custom_system_conf": {
                root_dir_key: data.get(root_dir_key),
                modules_dir_key: data.get(modules_dir_key),
                jobs_dir_key: data.get(jobs_dir_key),
                log_dir_key: data.get(log_dir_key),
            },
        }
        #setup_system(args=args)
        ws_id = request.cookies.get("ws_id")
        return Response(status=200)

    async def get_modules_dir(self, _):
        from aiohttp.web import json_response
        from ..system import get_modules_dir
        from ..system import get_default_modules_dir
        from ..system.consts import modules_dir_key

        modules_dir = get_modules_dir()
        if not modules_dir:
            modules_dir = get_default_modules_dir()
        return json_response({modules_dir_key: modules_dir})

    async def get_jobs_dir(self, _):
        from aiohttp.web import json_response
        from ..system import get_jobs_dir
        from ..system import get_default_jobs_dir
        from ..system.consts import jobs_dir_key

        jobs_dir = get_jobs_dir()
        if not jobs_dir:
            jobs_dir = get_default_jobs_dir()
        return json_response({jobs_dir_key: jobs_dir})

    async def get_log_dir(self, _):
        from aiohttp.web import json_response
        from ..system import get_log_dir
        from ..system import get_default_log_dir
        from ..system.consts import log_dir_key

        log_dir = get_log_dir()
        if not log_dir:
            log_dir = get_default_log_dir()
        return json_response({log_dir_key: log_dir})

    async def check_server_dir(self, request):
        from pathlib import Path
        from aiohttp.web import Response
        queries = request.rel_url.query
        d = queries.get("dir")
        if not d:
            return Response(status=404)
        if not Path(d).exists():
            return Response(status=404)
        return Response(status=200)

    async def get_root_dir(self, _):
        from aiohttp.web import json_response
        from ..system import get_root_dir
        from ..system import get_default_root_dir
        from ..system.consts import root_dir_key

        root_dir = get_root_dir()
        if not root_dir:
            root_dir = get_default_root_dir()
        return json_response({root_dir_key: root_dir})

    async def get_package_versions(self, _):
        from aiohttp.web import json_response
        from ..util.admin_util import get_current_package_version

        cur_ver = get_current_package_version()
        d = {"pkg_ver": cur_ver}
        return json_response(d)

    async def get_login_state(self, request):
        from aiohttp.web import json_response
        from .util import is_loggedin

        if not self.servermode or not self.mu:
            state = True
        else:
            state = await is_loggedin(request, self.servermode)
        return json_response({"loggedin": state})

    def get_servermode(self, _):
        from aiohttp.web import json_response

        return json_response({"servermode": self.servermode})

    async def get_system_log(self, _):
        from aiohttp import web
        from aiohttp.web import Response
        from .util import get_log_path
        from .consts import LOG_FN

        log_path = get_log_path()
        if not log_path:
            return Response(status=404)
        headers = {
            "Content-Disposition": "Attachment; filename=" + LOG_FN,
            "Content-Type": "text/plain",
        }
        return web.FileResponse(log_path, headers=headers)


