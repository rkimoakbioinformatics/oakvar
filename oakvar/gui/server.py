from typing import Optional
from typing import Any
from aiohttp import web
from aiohttp import web_runner

class WebServer(object):
    def __init__(self, loop=None, url=None, args={}):
        from ..util.asyn import get_event_loop

        self.args = args
        self.logger = args.get("logger")
        self.app = None
        self.cors = Optional[Any]
        self.runner = None
        self.site = None
        self.host = args.get("host")
        self.port = args.get("port")
        if loop is None:
            loop = get_event_loop()
        self.ssl_context = args.get("ssl_context")
        self.loop = loop
        self.server_started = False
        task = loop.create_task(self.start())
        task.add_done_callback(self.server_done)
        if args.get("headless") == False and url:
            self.loop.create_task(self.open_url(url))

    @web.middleware
    async def middleware(self, request, handler):
        from json import dumps
        from traceback import print_exc
        from sys import stderr
        from aiohttp.web_exceptions import HTTPNotFound

        global loop
        try:
            url_parts = request.url.parts
            response = await handler(request)
            nocache = False
            if url_parts[0] == "/":
                if len(url_parts) >= 3 and url_parts[2] == "nocache":
                    nocache = True
            elif url_parts[0] == "nocache":
                nocache = True
            if nocache:
                response.headers["Cache-Control"] = "no-cache"
                response.headers["Access-Control-Allow-Origin"] = "*"
            return response
        except Exception as e:
            msg = "Exception with {}".format(request.rel_url)
            if self.logger:
                self.logger.info(msg)
                self.logger.exception(e)
            if self.args.get("debug"):
                if not isinstance(e, HTTPNotFound):
                    stderr.write(msg + "\n")
                    print_exc()
            return web.HTTPInternalServerError(
                text=dumps({"status": "error", "msg": str(e)})
            )

    def server_done(self, task):
        from traceback import print_exc

        try:
            task.result()
        except Exception as e:
            if self.logger:
                self.logger.exception(e)
            if self.args.get("debug"):
                print_exc()
            self.server_started = None
            exit(1)

    async def open_url(self, url):
        from webbrowser import open as webbrowseropen
        from asyncio import sleep

        while self.server_started == False:
            await sleep(0.2)
        if self.server_started:
            webbrowseropen(url)

    def start_workers(self):
        from .webstore import webstore as ws
        from .websubmit import websubmit as wu

        ws.start_worker()
        wu.start_worker()

    async def start(self):
        global server_ready
        from aiohttp import web
        import aiohttp_cors

        self.app = web.Application(loop=self.loop, middlewares=[self.middleware], client_max_size=1024*1024*1024*1024)
        self.cors = aiohttp_cors.setup(self.app) # type: ignore
        self.setup_routes()
        self.start_workers()
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = TCPSitePatched(
            self.runner,
            host=self.host,
            port=self.port,
            loop=self.loop,
            ssl_context=self.ssl_context,
        )
        await self.site.start()
        self.server_started = True

    def setup_webapp_routes(self):
        from ..exceptions import ModuleLoadingError
        from importlib.util import spec_from_file_location, module_from_spec
        from os.path import join, exists
        from os import listdir
        from ..exceptions import ModuleLoadingError
        from ..exceptions import SetupError
        from ..system import get_modules_dir

        modules_dir = get_modules_dir()
        if modules_dir is None:
            return False
        webapps_dir = join(modules_dir, "webapps")
        if exists(webapps_dir) == False:
            return False
        module_names = listdir(webapps_dir)
        for module_name in module_names:
            try:
                module_dir = join(webapps_dir, module_name)
                pypath = join(module_dir, "route.py")
                if exists(pypath):
                    spec = spec_from_file_location("route", pypath)
                    if spec is None:
                        raise ModuleLoadingError(module_name)
                    module = module_from_spec(spec)
                    if spec.loader is None:
                        raise ModuleLoadingError(module_name)
                    spec.loader.exec_module(module)
                    if self.app is None:
                        raise SetupError()
                    for route in module.routes:
                        method, path, func_name = route
                        path = f"/webapps/{module_name}/" + path
                        self.app.router.add_route(method, path, func_name)
            except Exception as e:
                if self.logger:
                    self.logger.error(f"error loading webapp {module_name}")
                    self.logger.exception(e)
        return True

    def setup_routes(self):
        from .webresult import webresult as wr
        from .webstore import webstore as ws
        from .websubmit import websubmit as wu
        from .websubmit import multiuser as mu
        from ..exceptions import SetupError
        from ..system import get_modules_dir
        from os.path import dirname
        from os.path import realpath
        from os.path import join
        from os.path import exists
        from aiohttp_cors import ResourceOptions

        if self.app is None:
            raise SetupError()
        source_dir = dirname(realpath(__file__))
        routes = list()
        routes.extend(ws.routes)
        routes.extend(wr.routes)
        routes.extend(wu.routes)
        mu.add_routes(self.app.router)
        for route in routes:
            method, path, func_name = route
            self.app.router.add_route(method, path, func_name)
        self.setup_webapp_routes()
        self.app.router.add_static("/store", join(source_dir, "..", "gui", "webstore"))
        self.app.router.add_static(
            "/result", join(source_dir, "..", "gui", "webresult")
        )
        self.app.router.add_static("/submit", join(source_dir, "websubmit"))
        self.app.router.add_static("/", join(source_dir, "www"))
        modules_dir = get_modules_dir()
        if modules_dir:
            if exists(join(modules_dir, "annotators")):
                self.app.router.add_static(
                    "/modules/annotators/", join(modules_dir, "annotators")
                )
            if exists(join(modules_dir, "webapps")):
                self.app.router.add_static("/webapps", join(modules_dir, "webapps"))
        if self.cors:
            for resource in list(self.app.router.resources()):
                self.cors.add(
                    resource,
                    {
                        "*": ResourceOptions(
                            allow_credentials=True,
                            expose_headers="*",
                            allow_headers="*",
                            allow_methods="*",
                        ),
                    },
                )


class TCPSitePatched(web_runner.BaseSite):
    __slots__ = ("loop", "_host", "_port", "_reuse_address", "_reuse_port")

    def __init__(
        self,
        runner,
        host=None,
        port=None,
        shutdown_timeout=60.0,
        ssl_context=None,
        backlog=128,
        reuse_address=None,
        reuse_port=None,
        loop=None,
    ):
        from ..util.asyn import get_event_loop

        super().__init__(
            runner,
            shutdown_timeout=shutdown_timeout,
            ssl_context=ssl_context,
            backlog=backlog,
        )
        if loop is None:
            loop = get_event_loop()
        self.loop = loop
        if host is None:
            host = "0.0.0.0"
        self._host = host
        if port is None:
            port = 8443 if self._ssl_context else 8060
        self._port = port
        self._reuse_address = reuse_address
        self._reuse_port = reuse_port

    @property
    def name(self, args={}):
        from yarl import URL

        scheme = "https" if args.get("ssl_enabled", False) else "http"
        return str(URL.build(scheme=scheme, host=self._host, port=self._port))

    async def start(self):
        from ..exceptions import SetupError

        await super().start()
        if self._runner.server is None:
            raise SetupError()
        self._server = await self.loop.create_server(
            self._runner.server,
            self._host,
            self._port,
            ssl=self._ssl_context,  # type: ignore
            backlog=self._backlog,
            reuse_address=self._reuse_address,
            reuse_port=self._reuse_port,
        )
