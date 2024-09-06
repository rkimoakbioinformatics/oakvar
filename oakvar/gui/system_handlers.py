# OakVar
#
# Copyright (c) 2024 Oak Bioinformatics, LLC
#
# All rights reserved.
#
# Do not distribute or use this software without obtaining
# a license from Oak Bioinformatics, LLC.
#
# Do not use this software to develop another software
# which competes with the products by Oak Bioinformatics, LLC,
# without obtaining a license for such use from Oak Bioinformatics, LLC.
#
# For personal use of non-commercial nature, you may use this software
# after registering with `ov store account create`.
#
# For research use of non-commercial nature, you may use this software
# after registering with `ov store account create`.
#
# For use by commercial entities, you must obtain a commercial license
# from Oak Bioinformatics, LLC. Please write to info@oakbioinformatics.com
# to obtain the commercial license.
# ================
# OpenCRAVAT
#
# MIT License
#
# Copyright (c) 2021 KarchinLab
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from typing import List


class SystemHandlers:
    def __init__(
        self,
        servermode=False,
        mu=None,
        logger=None,
        system_queue=None,
        system_worker_state=None,
    ):
        self.servermode = servermode
        self.mu = mu
        self.logger = logger
        self.system_queue = system_queue
        self.system_worker_state = system_worker_state
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
        self.routes.append(["GET", "/submit/basemodules", self.get_base_modules])
        self.routes.append(
            ["GET", "/submit/localmodules/{module}", self.get_local_module_info_web]
        )
        self.routes.append(["GET", "/system/ez", self.get_ez])

    async def get_ez(self, _):
        from aiohttp.web import json_response
        from ..lib.system import get_conf_dir
        from ..lib.store.ov.account import get_token_set

        conf_dir = get_conf_dir()
        token_set = get_token_set()
        if token_set is None:
            return json_response({"ez": "", "email": ""})
        email = token_set.get("email", "")
        id_token = token_set.get("idToken", "")
        if conf_dir is None:
            return json_response({"ez": "", "email": ""})
        ez_path = conf_dir / "ez"
        if not ez_path.exists():
            return json_response({"ez": "", "email": ""})
        with open(ez_path) as f:
            ez = f.read().strip()
            return json_response({"ez": ez, "email": email, "idToken": id_token})

    async def get_base_modules(self, request):
        from aiohttp.web import json_response
        from ..lib.system import get_system_conf
        from ..lib.system.consts import base_modules_key

        _ = request
        sys_conf = get_system_conf()
        base_modules: List[str] = sys_conf.get(base_modules_key, [])
        return json_response(base_modules)

    async def get_local_module_info_web(self, request):
        from aiohttp.web import json_response
        from ..lib.module.local import get_local_module_info

        module_name = request.match_info["module"]
        mi = get_local_module_info(module_name)
        if mi:
            return json_response(mi.serialize())
        else:
            return json_response({})

    async def start_setup(self, request):
        from aiohttp.web import Response
        from ..lib.system.consts import root_dir_key
        from ..lib.system.consts import modules_dir_key
        from ..lib.system.consts import jobs_dir_key
        from ..lib.system.consts import log_dir_key
        from .consts import WS_COOKIE_KEY
        from .consts import SYSTEM_STATE_SETUP_KEY

        # from .consts import SYSTEM_MSG_KEY

        data = await request.json()
        args = {
            "email": data.get("email"),
            "pw": data.get("pw"),
            "custom_system_conf": {
                root_dir_key: data.get(root_dir_key),
                modules_dir_key: data.get(modules_dir_key),
                jobs_dir_key: data.get(jobs_dir_key),
                log_dir_key: data.get(log_dir_key),
            },
        }
        ws_id = request.cookies.get(WS_COOKIE_KEY)
        args["install_mode"] = "web"
        args["ws_id"] = ws_id
        args["system_worker_state"] = self.system_worker_state
        # args[SYSTEM_MSG_KEY] = SYSTEM_STATE_SETUP_KEY
        data = {}
        data["work_type"] = SYSTEM_STATE_SETUP_KEY
        data["args"] = args
        self.system_queue.append(data)  # type: ignore
        return Response(status=200)

    async def get_modules_dir(self, _):
        from aiohttp.web import json_response
        from ..lib.system import get_modules_dir
        from ..lib.system import get_default_modules_dir
        from ..lib.system.consts import modules_dir_key

        modules_dir = get_modules_dir()
        if not modules_dir:
            modules_dir = get_default_modules_dir()
        return json_response({modules_dir_key: str(modules_dir)})

    async def get_jobs_dir(self, _):
        from aiohttp.web import json_response
        from ..lib.system import get_jobs_dir
        from ..lib.system import get_default_jobs_dir
        from ..lib.system.consts import jobs_dir_key

        jobs_dir = get_jobs_dir()
        if not jobs_dir:
            jobs_dir = get_default_jobs_dir()
        return json_response({jobs_dir_key: str(jobs_dir)})

    async def get_log_dir(self, _):
        from aiohttp.web import json_response
        from ..lib.system import get_log_dir
        from ..lib.system import get_default_log_dir
        from ..lib.system.consts import log_dir_key

        log_dir = get_log_dir()
        if not log_dir:
            log_dir = get_default_log_dir()
        return json_response({log_dir_key: str(log_dir)})

    async def check_server_dir(self, request):
        from pathlib import Path
        from aiohttp.web import json_response

        queries = request.rel_url.query
        d = queries.get("dir")
        if not d or not Path(d).exists():
            content = {"exists": False}
        else:
            content = {"exists": True}
        return json_response(content)

    async def get_root_dir(self, _):
        from aiohttp.web import json_response
        from ..lib.system import get_root_dir
        from ..lib.system import get_default_root_dir
        from ..lib.system.consts import root_dir_key

        root_dir = get_root_dir()
        if not root_dir:
            root_dir = get_default_root_dir()
        return json_response({root_dir_key: str(root_dir)})

    async def get_package_versions(self, _):
        from aiohttp.web import json_response
        from ..lib.util.admin_util import get_current_package_version

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
