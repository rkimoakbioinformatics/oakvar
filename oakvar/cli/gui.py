from os.path import join
from ..system import get_system_conf
from aiohttp import web, web_runner
import logging
from ..system.consts import log_dir_key, modules_dir_key
from ..decorators import cli_func
from ..decorators import cli_entry
from importlib import import_module
from importlib.util import find_spec

SERVER_ALREADY_RUNNING = -1
headless = None
servermode = None
server_ready = None
ssl_enabled = None
protocol = None
http_only = None
sc = None
loop = None
debug = False
loop = None
sysconf = None
log_dir = None
modules_dir = None
log_path = None
logger = None
if find_spec("cravat_multiuser"):
    cravat_multiuser = import_module("cravat_multiuser")
else:
    cravat_multiuser = None


def setup(args):
    from sys import platform as sysplatform
    from ..webresult import webresult as wr
    from ..webstore import webstore as ws
    from ..websubmit import websubmit as wu
    from asyncio import get_event_loop, set_event_loop
    from os.path import join, exists

    if logger is None or sysconf is None:
        from ..exceptions import SetupError

        raise SetupError()
    try:
        global loop
        if sysplatform == "win32":  # Required to use asyncio subprocesses
            from asyncio import ProactorEventLoop  # type: ignore

            loop = ProactorEventLoop()
            set_event_loop(loop)
        else:
            loop = get_event_loop()
        global headless
        headless = args["headless"]
        global servermode
        servermode = args["servermode"]
        global debug
        debug = args["debug"]
        if servermode and cravat_multiuser:
            try:
                loop.create_task(cravat_multiuser.setup_module())
                global server_ready
                server_ready = True
            except Exception as e:
                from sys import stderr

                logger.exception(e)
                logger.info("Exiting...")
                stderr.write(
                    "Error occurred while loading oakvar-multiuser.\nCheck {} for details.\n".format(
                        log_path
                    )
                )
                exit()
        else:
            servermode = False
            server_ready = False
        wu.logger = logger
        ws.logger = logger
        wr.logger = logger
        wu.servermode = args["servermode"]
        ws.servermode = args["servermode"]
        wr.servermode = args["servermode"]
        wu.filerouter.servermode = args["servermode"]
        wu.server_ready = server_ready
        ws.server_ready = server_ready
        wr.server_ready = server_ready
        wu.filerouter.server_ready = server_ready
        wr.wu = wu
        if server_ready and cravat_multiuser:
            setattr(cravat_multiuser, "servermode", servermode)
            setattr(cravat_multiuser, "server_ready", server_ready)
            setattr(cravat_multiuser, "logger" ,logger)
            setattr(cravat_multiuser, "noguest" ,args["noguest"])
            wu.cravat_multiuser = cravat_multiuser
            ws.cravat_multiuser = cravat_multiuser
        if servermode and server_ready == False:
            from sys import stderr

            msg = 'oakvar-multiuser package is required to run OakVar Server.\nRun "pip install oakvar-multiuser" to get the package.'
            logger.info(msg)
            logger.info("Exiting...")
            stderr.write(msg + "\n")
            exit()
        global ssl_enabled
        ssl_enabled = False
        global protocol
        global http_only
        http_only = args["http_only"]
        if "conf_dir" in sysconf:
            pem_path = join(sysconf["conf_dir"], "cert.pem")
            if exists(pem_path) and http_only == False:
                ssl_enabled = True
                global sc
                from ssl import create_default_context, Purpose

                sc = create_default_context(Purpose.CLIENT_AUTH)
                sc.load_cert_chain(pem_path)
        if ssl_enabled:
            protocol = "https://"
        else:
            protocol = "http://"
    except Exception as e:
        from traceback import print_exc
        from sys import stderr

        logger.exception(e)
        if debug:
            print_exc()
        logger.info("Exiting...")
        stderr.write(
            "Error occurred while starting OakVar server.\nCheck {} for details.\n".format(
                log_path
            )
        )
        exit()


@cli_entry
def cli_gui(args):
    return gui(args)


@cli_func
def gui(args, __name__="gui"):
    from ..util.util import is_compatible_version
    from logging.handlers import TimedRotatingFileHandler
    from os.path import abspath, exists
    from sys import stderr

    global sysconf, log_dir, modules_dir, log_path, logger

    sysconf = get_system_conf()
    log_dir = sysconf[log_dir_key]
    modules_dir = sysconf[modules_dir_key]
    log_path = join(log_dir, "wcravat.log")
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    log_handler = TimedRotatingFileHandler(log_path, when="d", backupCount=30)
    log_formatter = logging.Formatter("%(asctime)s: %(message)s", "%Y/%m/%d %H:%M:%S")
    log_handler.setFormatter(log_formatter)
    logger.addHandler(log_handler)
    if args["servermode"]:
        args["headless"] = True
    if args["result"]:
        args["headless"] = False
        args["result"] = abspath(args["result"])
    try:
        setup(args)
        global headless
        global server_ready
        global servermode
        url = None
        server = get_server()
        host = server.get("host")
        port = None
        if args["port"] is not None:
            try:
                port = int(args["port"])
            except:
                port = None
        if port is None:
            port = server.get("port")
        if not headless:
            if args["webapp"] is not None:
                index_path = join(modules_dir, "webapps", args["webapp"], "index.html")
                if exists(index_path) == False:
                    stderr.write(f"Webapp {args['webapp']} does not exist. Exiting.\n")
                    return
                url = f"{host}:{port}/webapps/{args['webapp']}/index.html"
            elif args["result"]:
                dbpath = args["result"]
                if exists(dbpath) == False:
                    stderr.write(f"{dbpath} does not exist. Exiting.\n")
                    return
                (
                    compatible_version,
                    db_version,
                    oc_version,
                ) = is_compatible_version(dbpath)
                if not compatible_version:
                    stderr.write(
                        f"DB version {db_version} of {dbpath} is not compatible with the current OakVar ({oc_version}).\n"
                    )
                    stderr.write(
                        f'Consider running "oc util update-result {dbpath}" and running "oc gui {dbpath}" again.\n'
                    )
                    return
                else:
                    url = f"{host}:{port}/result/index.html?dbpath={args['result']}"
            else:
                if server_ready and servermode:
                    url = f"{host}:{port}/server/nocache/login.html"
                else:
                    url = f"{host}:{port}/submit/nocache/index.html"
            global protocol
            if protocol is None:
                from ..exceptions import SetupError

                raise SetupError()
            url = protocol + url
        main(url=url, host=host, port=port, args=args)
    except Exception as e:
        from traceback import print_exc

        logger.exception(e)
        if debug:
            print_exc()
        logger.info("Exiting...")
        stderr.write(
            "Error occurred while starting OakVar server.\nCheck {} for details.\n".format(
                log_path
            )
        )
    finally:
        for handler in logger.handlers:
            handler.close()
            logger.removeHandler(handler)


def get_server():
    from ..system import get_system_conf
    import platform

    if sysconf is None or logger is None:
        from ..exceptions import SetupError

        raise SetupError()
    global args
    try:
        server = {}
        pl = platform.platform()
        if pl.startswith("Windows"):
            def_host = "localhost"
        elif pl.startswith("Linux"):
            if "Microsoft" in pl:
                def_host = "localhost"
            else:
                def_host = "0.0.0.0"
        elif pl.startswith("Darwin"):
            def_host = "0.0.0.0"
        else:
            def_host = "localhost"
        if ssl_enabled:
            if "gui_host_ssl" in sysconf:
                host = sysconf["gui_host_ssl"]
            elif "gui_host" in sysconf:
                host = sysconf["gui_host"]
            else:
                host = def_host
            if "gui_port_ssl" in sysconf:
                port = sysconf["gui_port_ssl"]
            elif "gui_port" in sysconf:
                port = sysconf["gui_port"]
            else:
                port = 8443
        else:
            host = get_system_conf().get("gui_host", def_host)
            port = get_system_conf().get("gui_port", 8080)
        server["host"] = host
        server["port"] = port
        return server
    except Exception as e:
        from traceback import print_exc
        from sys import stderr

        logger.exception(e)
        if debug:
            print_exc()
        logger.info("Exiting...")
        stderr.write(
            "Error occurred while OakVar server.\nCheck {} for details.\n".format(
                log_path
            )
        )
        exit()


class TCPSitePatched(web_runner.BaseSite):
    __slots__ = ("loop", "_host", "_port", "_reuse_address", "_reuse_port")

    def __init__(
        self,
        runner,
        host=None,
        port=None,
        *,
        shutdown_timeout=60.0,
        ssl_context=None,
        backlog=128,
        reuse_address=None,
        reuse_port=None,
        loop=None,
    ):
        from asyncio import get_event_loop

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
    def name(self):
        from yarl import URL

        global ssl_enabled
        scheme = "https" if ssl_enabled else "http"
        return str(URL.build(scheme=scheme, host=self._host, port=self._port))

    async def start(self):
        await super().start()
        if self._runner.server is None:
            from ..exceptions import SetupError

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


@web.middleware
async def middleware(request, handler):
    from json import dumps

    if logger is None:
        from ..exceptions import SetupError

        raise SetupError()
    global loop
    global args
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
        return response
    except Exception as e:
        from traceback import print_exc
        from sys import stderr

        msg = "Exception with {}".format(request.rel_url)
        logger.info(msg)
        logger.exception(e)
        if debug:
            from aiohttp.web_exceptions import HTTPNotFound

            if not isinstance(e, HTTPNotFound):
                stderr.write(msg + "\n")
                print_exc()
        return web.HTTPInternalServerError(
            text=dumps({"status": "error", "msg": str(e)})
        )


class WebServer(object):
    def __init__(self, host=None, port=None, loop=None, ssl_context=None, url=None):
        from asyncio import get_event_loop

        self.app = None
        self.runner = None
        self.site = None
        serv = get_server()
        if host is None:
            host = serv["host"]
        if port is None:
            port = serv["port"]
        self.host = host
        self.port = port
        if loop is None:
            loop = get_event_loop()
        self.ssl_context = ssl_context
        self.loop = loop
        self.server_started = False
        task = loop.create_task(self.start())
        task.add_done_callback(self.server_done)
        global headless
        if headless == False and url is not None:
            self.loop.create_task(self.open_url(url))

    def server_done(self, task):
        if logger is None:
            from ..exceptions import LoggerError

            raise LoggerError()
        try:
            task.result()
        except Exception as e:
            if logger:
                logger.exception(e)
            if debug:
                from traceback import print_exc

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

    async def start(self):
        global middleware
        global server_ready
        self.app = web.Application(loop=self.loop, middlewares=[middleware])
        if server_ready and cravat_multiuser:
            cravat_multiuser.setup(self.app)
        self.setup_routes()
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        self.site = TCPSitePatched(
            self.runner,
            self.host,
            self.port,
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
        from ..exceptions import LoggerError
        from ..exceptions import ModuleLoadingError
        from ..exceptions import SetupError

        if logger is None:
            raise LoggerError()
        global modules_dir
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
                logger.error(f"error loading webapp {module_name}")
                logger.exception(e)
        return True

    def setup_routes(self):
        from ..webresult import webresult as wr
        from ..webstore import webstore as ws
        from ..websubmit import websubmit as wu
        from os.path import dirname, realpath, join, exists

        if self.app is None:
            from ..exceptions import SetupError

            raise SetupError()
        source_dir = dirname(realpath(__file__))
        routes = list()
        routes.extend(ws.routes)
        routes.extend(wr.routes)
        routes.extend(wu.routes)
        global server_ready
        if server_ready and cravat_multiuser:
            cravat_multiuser.add_routes(self.app.router)
        for route in routes:
            method, path, func_name = route
            self.app.router.add_route(method, path, func_name)
        self.app.router.add_get("/heartbeat", heartbeat)
        self.app.router.add_get("/issystemready", is_system_ready)
        self.app.router.add_get("/favicon.ico", serve_favicon)
        self.app.router.add_get("/webapps/{module}", get_webapp_index)
        self.setup_webapp_routes()
        self.app.router.add_static("/store", join(source_dir, "..", "webstore"))
        self.app.router.add_static("/result", join(source_dir, "..", "webresult"))
        self.app.router.add_static("/submit", join(source_dir, "..", "websubmit"))
        if modules_dir:
            if exists(join(modules_dir, "annotators")):
                self.app.router.add_static(
                    "/modules/annotators/", join(modules_dir, "annotators")
                )
            if exists(join(modules_dir, "webapps")):
                self.app.router.add_static("/webapps", join(modules_dir, "webapps"))
        ws.start_worker()
        wu.start_worker()


async def get_webapp_index(request):
    url = request.path + "/index.html"
    if len(request.query) > 0:
        url = url + "?"
        for k, v in request.query.items():
            url += k + "=" + v + "&"
        url = url.rstrip("&")
    return web.HTTPFound(url)


async def serve_favicon(__request__):
    from os.path import dirname, realpath, join

    source_dir = dirname(realpath(__file__))
    return web.FileResponse(join(source_dir, "..", "favicon.ico"))


async def heartbeat(request):
    from ..webstore import webstore as ws
    from asyncio import get_event_loop
    from concurrent.futures._base import CancelledError

    ws = web.WebSocketResponse(timeout=60 * 60 * 24 * 365)
    if servermode and server_ready and cravat_multiuser:
        get_event_loop().create_task(cravat_multiuser.update_last_active(request))
    await ws.prepare(request)
    try:
        async for _ in ws:
            pass
    except CancelledError:
        pass
    return ws


async def is_system_ready(__request__):
    from ..util.admin_util import system_ready

    return web.json_response(dict(system_ready()))


def main(url=None, host=None, port=None, args={}):
    from ..webstore import webstore as ws
    import socket
    from asyncio import get_event_loop, sleep
    from requests.exceptions import ConnectionError
    from webbrowser import open as webbrowseropen
    from ..util.util import quiet_print
    from ..util.util import show_logo

    global logger
    if not logger:
        from ..exceptions import SetupError

        raise SetupError()
    try:
        global loop
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)

        def wakeup():
            if loop is None:
                from ..exceptions import SetupError

                raise SetupError()
            loop.call_later(0.1, wakeup)

        def check_local_update(interval):
            if loop is None:
                from ..exceptions import SetupError

                raise SetupError()
            try:
                ws.handle_modules_changed()
            except:
                from traceback import print_exc

                print_exc()
            finally:
                loop.call_later(interval, check_local_update, interval)

        serv = get_server()
        global protocol
        if host is None:
            host = serv.get("host")
        if port is None:
            port = serv.get("port")
        try:
            sr = s.connect_ex((host, port))
            s.close()
            if sr == 0:
                msg = "OakVar is already running at {}{}:{}.".format(
                    protocol, host, port
                )
                logger.info(msg)
                quiet_print(msg, args)
                global SERVER_ALREADY_RUNNING
                if url and not headless:
                    webbrowseropen(url)
                return SERVER_ALREADY_RUNNING
        except ConnectionError:
            pass
        show_logo()
        print("OakVar Server is served at {}:{}".format(host, port))
        logger.info("Serving OakVar server at {}:{}".format(host, port))
        print(
            "(To quit: Press Ctrl-C or Ctrl-Break)",
            flush=True,
        )
        loop = get_event_loop()
        loop.call_later(0.1, wakeup)
        loop.call_later(1, check_local_update, 5)

        async def clean_sessions():
            """
            Clean sessions periodically.
            """
            if logger is None:
                from ..exceptions import SetupError

                raise SetupError()
            from ..system import get_system_conf
            try:
                max_age = get_system_conf().get(
                    "max_session_age", 604800
                )  # default 1 week
                interval = get_system_conf().get(
                    "session_clean_interval", 3600
                )  # default 1 hr
                while True:
                    if cravat_multiuser:
                        await cravat_multiuser.admindb.clean_sessions(max_age)
                    await sleep(interval)
            except Exception as e:
                from traceback import print_exc

                logger.exception(e)
                if debug:
                    print_exc()

        if servermode and server_ready:
            if "max_session_age" in get_system_conf():
                loop.create_task(clean_sessions())
        global ssl_enabled
        if ssl_enabled:
            global sc
            _ = WebServer(loop=loop, ssl_context=sc, url=url, host=host, port=port)
        else:
            _ = WebServer(loop=loop, url=url, host=host, port=port)
        loop.run_forever()
    except Exception as e:
        from sys import stderr

        logger.exception(e)
        if debug:
            from traceback import print_exc

            print_exc()
        logger.info("Exiting...")
        stderr.write(
            "Error occurred while starting OakVar server.\nCheck {} for details.\n".format(
                log_path
            )
        )
        exit()


def get_parser_fn_gui():
    from argparse import ArgumentParser

    parser_fn_gui = ArgumentParser()
    parser_fn_gui.add_argument(
        "--multiuser",
        dest="servermode",
        action="store_true",
        default=False,
        help="Runs in multiuser mode",
    )
    parser_fn_gui.add_argument(
        "--headless",
        action="store_true",
        default=False,
        help="do not open the OakVar web page",
    )
    parser_fn_gui.add_argument(
        "--http-only",
        action="store_true",
        default=False,
        help="Force not to accept https connection",
    )
    parser_fn_gui.add_argument(
        "--debug",
        dest="debug",
        action="store_true",
        default=False,
        help="Console echoes exceptions written to log file.",
    )
    parser_fn_gui.add_argument(
        "result", nargs="?", help="Path to a OakVar result SQLite file"
    )
    parser_fn_gui.add_argument(
        "--webapp",
        dest="webapp",
        default=None,
        help="Name of OakVar webapp module to run",
    )
    parser_fn_gui.add_argument(
        "--port",
        dest="port",
        default=None,
        help="Port number for OakVar graphical user interface",
    )
    parser_fn_gui.add_argument(
        "--noguest",
        dest="noguest",
        default=False,
        action="store_true",
        help="Disables guest mode",
    )
    parser_fn_gui.add_argument(
        "--quiet", action="store_true", default=None, help="run quietly"
    )
    parser_fn_gui.add_argument("--to", default="return", help="run quietly")
    parser_fn_gui.set_defaults(func=cli_gui)
    return parser_fn_gui


if __name__ == "__main__":
    main()
