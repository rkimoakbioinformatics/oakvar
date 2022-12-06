from typing import Optional
from typing import Any
from aiohttp import web
from aiohttp import web_runner

system_setup_needed = False

class WebServer(object):
    def __init__(self, loop=None, url=None, args={}):
        from ..util.asyn import get_event_loop
        from . import multiuser as mu

        global system_setup_needed
        self.manager = None
        self.install_queue = None
        self.install_state = None
        self.info_of_running_jobs = None
        self.report_generation_ps = None
        self.args = args
        self.logger = args.get("logger")
        self.app = None
        self.cors = Optional[Any]
        self.runner = None
        self.site = None
        self.servermode = args.get("servermode", False)
        self.mu = mu
        self.host = args.get("host")
        self.port = args.get("port")
        if loop is None:
            loop = get_event_loop()
        self.ssl_context = args.get("ssl_context")
        self.loop = loop
        self.server_started = False
        self.system_setup_needed = system_setup_needed
        if args.get("headless") == False and url:
            self.loop.create_task(self.open_url(url))
        task = loop.create_task(self.start())
        task.add_done_callback(self.server_done)

    @web.middleware
    async def middleware(self, request, handler):
        from json import dumps
        from traceback import print_exc
        from sys import stderr
        from aiohttp.web_exceptions import HTTPNotFound
        from aiohttp.web import Response
        from ..exceptions import SystemMissingException

        global loop
        try:
            url_parts = request.url.parts
            print(f"@ request={request}")
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
        except SystemMissingException as e:
            if self.logger:
                self.logger.exception(e)
            self.system_setup_needed = True
            return Response(status=500, reason="system_setup_needed")
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
        self.start_job_worker()
        self.start_install_worker()

    def start_job_worker(self):
        from multiprocessing import Process
        from .job_handlers import fetch_job_queue

        self.job_worker = Process(
            target=fetch_job_queue, args=(self.job_queue, self.info_of_running_jobs, self.report_generation_ps)
        )
        self.job_worker.start()

    def start_install_worker(self):
        from multiprocessing import Process
        from .store_handlers import fetch_install_queue
        assert self.manager is not None
        self.install_worker = Process(
            target=fetch_install_queue,
            args=(self.install_queue, self.install_state, self.local_modules_changed),
        )
        self.install_worker.start()

    def make_install_queue(self):
        if self.install_queue is not None:
            return self.install_queue
        if not self.manager:
            return None
        self.install_queue = self.manager.list()

    def make_install_state(self):
        if self.install_state is not None:
            return self.install_state
        if not self.manager:
            return None
        self.install_state = self.manager.dict()
        self.initialize_install_state()

    def initialize_install_state(self, module_name="", module_version=""):
        from time import time
        if self.install_state is None:
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
            self.install_state[k] = v

    def make_job_queue_states(self):
        from multiprocessing import Queue
        assert self.manager is not None
        self.job_queue = Queue()
        self.info_of_running_jobs = self.manager.list()
        self.report_generation_ps = self.manager.list()
        self.report_generation_ps.append("initial")

    def make_shared_states(self):
        from multiprocessing import Manager
        self.manager = Manager()
        self.make_install_queue()
        self.make_install_state()
        self.local_modules_changed = self.manager.Event()
        self.make_job_queue_states()

    def make_store_handlers(self):
        from .store_handlers import StoreHandlers
        self.store_handlers = StoreHandlers(servermode=self.servermode, mu=self.mu, local_modules_changed=self.local_modules_changed, install_state=self.install_state, install_queue=self.install_queue, logger=self.logger)

    def make_job_handlers(self):
        from .job_handlers import JobHandlers
        self.job_handlers = JobHandlers(servermode=self.servermode, mu=self.mu, logger=self.logger, job_queue=self.job_queue, info_of_running_jobs=self.info_of_running_jobs, report_generation_ps=self.report_generation_ps)

    def make_multiuser_handlers(self):
        from .multiuser import MultiuserHandlers
        self.multiuser_handlers = MultiuserHandlers(servermode=self.servermode)

    def make_system_handlers(self):
        from .system_handlers import SystemHandlers
        self.system_handlers = SystemHandlers(servermode=self.servermode, mu=self.mu, logger=self.logger)

    def make_handlers(self):
        self.make_job_handlers()
        self.make_store_handlers()
        self.make_multiuser_handlers()
        self.make_system_handlers()

    async def start(self):
        global server_ready
        from aiohttp import web
        import aiohttp_cors

        self.app = web.Application(loop=self.loop, middlewares=[self.middleware], client_max_size=1024*1024*1024*1024)
        self.cors = aiohttp_cors.setup(self.app) # type: ignore
        self.make_shared_states()
        self.make_handlers()
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

    def add_static_routes(self):
        from pathlib import Path
        assert self.app is not None
        source_dir = Path(__file__).absolute().parent
        self.app.router.add_static("/store", source_dir / "webstore")
        self.app.router.add_static("/result", source_dir / "webresult")
        self.app.router.add_static("/submit", source_dir / "websubmit")
        self.app.router.add_static("/", source_dir / "www")

    def setup_cors(self):
        from aiohttp_cors import ResourceOptions
        assert self.app is not None
        if not self.cors:
            return
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

    def setup_routes(self):
        from .webresult import webresult
        from ..exceptions import SetupError
        from ..system import get_modules_dir
        from os.path import join
        from os.path import exists

        if self.app is None:
            raise SetupError()
        self.routes = list()
        self.routes.extend(self.store_handlers.routes)
        self.routes.extend(self.job_handlers.routes)
        self.routes.extend(self.multiuser_handlers.routes)
        self.routes.extend(self.system_handlers.routes)
        self.routes.extend(webresult.routes)
        for route in self.routes:
            method, path, func_name = route
            self.app.router.add_route(method, path, func_name)
        self.add_static_routes()
        self.setup_webapp_routes()
        modules_dir = get_modules_dir()
        if modules_dir:
            if exists(join(modules_dir, "annotators")):
                self.app.router.add_static(
                    "/modules/annotators/", join(modules_dir, "annotators")
                )
            if exists(join(modules_dir, "webapps")):
                self.app.router.add_static("/webapps", join(modules_dir, "webapps"))
        self.setup_cors()

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
            port = 8443 if self._ssl_context else 8080
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
