from ..decorators import cli_func
from ..decorators import cli_entry
from aiohttp import web

SERVER_ALREADY_RUNNING = -1
servermode = None
server_ready = None
protocol = None
http_only = None
sc = None
loop = None
loop = None
log_dir = None
modules_dir = None
log_path = None


def get_event_loop():
    from sys import platform as sysplatform
    from asyncio import get_event_loop
    from asyncio import set_event_loop
    if sysplatform == "win32":  # Required to use asyncio subprocesses
        from asyncio import ProactorEventLoop  # type: ignore

        loop = ProactorEventLoop()
        set_event_loop(loop)
    else:
        loop = get_event_loop()
    return loop

def setup(args={}, logger=None):
    from ..gui.webresult import webresult as wr
    from ..gui.webstore import webstore as ws
    from ..gui.websubmit import websubmit as wu
    from ..gui.websubmit import multiuser as mu
    from os.path import join, exists
    from traceback import print_exc
    from sys import stderr


    try:
        global loop
        global servermode
        loop = get_event_loop()
        servermode = args["servermode"]
        loop.run_until_complete(mu.setup_module())
        wu.logger = logger
        ws.logger = logger
        wr.logger = logger
        mu.logger = logger
        wu.servermode = servermode
        ws.servermode = servermode
        wr.servermode = servermode
        mu.servermode = servermode
        wu.filerouter.servermode = servermode
        mu.noguest = args["noguest"]
        wr.wu = wu
        wu.mu = mu
        ws.mu = mu
        args["ssl_enabled"] = False
        global protocol
        global http_only
        http_only = args["http_only"]
        sysconf = args.get("sysconf", {})
        if "conf_dir" in sysconf:
            pem_path = join(sysconf["conf_dir"], "cert.pem")
            if exists(pem_path) and http_only == False:
                args["ssl_enabled"] = True
                global sc
                from ssl import create_default_context, Purpose

                sc = create_default_context(Purpose.CLIENT_AUTH)
                sc.load_cert_chain(pem_path)
        if args["ssl_enabled"]:
            protocol = "https://"
        else:
            protocol = "http://"
    except Exception as e:
        if logger:
            logger.exception(e)
            logger.info("Exiting...")
        if args["debug"]:
            print_exc()
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
    import logging
    from logging.handlers import TimedRotatingFileHandler
    from os.path import abspath, exists
    from sys import stderr
    from os.path import join
    from traceback import print_exc
    from ..exceptions import SetupError
    from ..system import get_system_conf
    from ..system.consts import log_dir_key, modules_dir_key
    from ..gui.util import get_host_port

    sysconf = get_system_conf()
    args["sysconf"] = sysconf
    log_dir = sysconf[log_dir_key]
    modules_dir = sysconf[modules_dir_key]
    log_path = join(log_dir, "wcravat.log")
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    log_handler = TimedRotatingFileHandler(log_path, when="d", backupCount=30)
    log_formatter = logging.Formatter("%(asctime)s: %(message)s", "%Y/%m/%d %H:%M:%S")
    log_handler.setFormatter(log_formatter)
    logger.addHandler(log_handler)
    args["headless"] = args["servermode"]
    if args["result"]:
        args["headless"] = False
        args["result"] = abspath(args["result"])
    try:
        setup(args, logger=logger)
        global server_ready
        global servermode
        print(f"@ args={args}")
        url = None
        host, port = get_host_port(args)
        if not args["headless"]:
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
                raise SetupError()
            url = protocol + url
        main(url=url, host=host, port=port, args=args)
    except Exception as e:
        logger.exception(e)
        if args["debug"]:
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


async def is_system_ready(__request__):
    from ..util.admin_util import system_ready

    return web.json_response(dict(system_ready()))


def check_local_update(interval):
    from ..exceptions import SetupError
    from traceback import print_exc
    from ..gui.webstore import webstore as ws


    if loop is None:
        raise SetupError()
    try:
        ws.handle_modules_changed()
    except:
        print_exc()
    finally:
        loop.call_later(interval, check_local_update, interval)

async def clean_sessions(args={}, logger=None):
    from ..system import get_system_conf
    from ..gui.websubmit import multiuser as mu
    from traceback import print_exc
    from asyncio import sleep


    try:
        max_age = get_system_conf().get(
            "max_session_age", 604800
        )  # default 1 week
        interval = get_system_conf().get(
            "session_clean_interval", 3600
        )  # default 1 hr
        while True:
            await mu.admindb.clean_sessions(max_age)
            await sleep(interval)
    except Exception as e:
        if logger:
            logger.exception(e)
        if args.get("debug"):
            print_exc()

def main(url=None, host=None, port=None, logger=None, args={}):
    import socket
    from requests.exceptions import ConnectionError
    from webbrowser import open as webbrowseropen
    from sys import stderr
    from traceback import print_exc
    from ..util.util import quiet_print
    from ..util.util import show_logo
    from ..system import get_system_conf
    from ..gui.server import WebServer
    from ..gui.util import get_host_port


    try:
        global loop
        global protocol
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        host, port = get_host_port(args)
        try:
            sr = s.connect_ex((host, port))
            s.close()
            if sr == 0:
                msg = "OakVar is already running at {}{}:{}.".format(
                    protocol, host, port
                )
                if logger:
                    logger.info(msg)
                quiet_print(msg, args)
                global SERVER_ALREADY_RUNNING
                if url and not args["headless"]:
                    webbrowseropen(url)
                return SERVER_ALREADY_RUNNING
        except ConnectionError:
            pass
        show_logo()
        print("OakVar Server is served at {}:{}".format(host, port))
        if logger:
            logger.info("Serving OakVar server at {}:{}".format(host, port))
        print(
            "(To quit: Press Ctrl-C or Ctrl-Break)",
            flush=True,
        )
        loop = get_event_loop()
        loop.call_later(1, check_local_update, 5)
        if servermode and server_ready:
            if "max_session_age" in get_system_conf():
                loop.create_task(clean_sessions(args=args, logger=logger))
        if args["ssl_enabled"]:
            global sc
            _ = WebServer(loop=loop, ssl_context=sc, url=url, host=host, port=port, args=args)
        else:
            _ = WebServer(loop=loop, url=url, host=host, port=port, args=args)
        loop.run_forever()
    except Exception as e:
        if logger:
            logger.exception(e)
            logger.info("Exiting...")
        if args.get("debug"):
            print_exc()
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

