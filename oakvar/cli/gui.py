from . import cli_entry
from . import cli_func

protocol = None
log_path = None
loop = None

def inject_module_variables(args={}):
    from ..gui.webresult import webresult as wr
    from ..gui.webstore import webstore as ws
    from ..gui.websubmit import websubmit as wu
    from ..gui.websubmit import multiuser as mu

    logger = args.get("logger")
    wu.logger = logger
    ws.logger = logger
    wr.logger = logger
    mu.logger = logger
    wu.servermode = args.get("servermode")
    ws.servermode = args.get("servermode")
    wr.servermode = args.get("servermode")
    mu.servermode = args.get("servermode")
    wr.wu = wu
    wu.mu = mu
    ws.mu = mu


def get_protocol(args={}):
    global protocol
    if not protocol:
        if args.get("ssl_enabled"):
            protocol = "https://"
        else:
            protocol = "http://"
    return protocol


def setup(args={}):
    from os.path import abspath
    from ..gui.websubmit import multiuser as mu
    from ..util.asyn import get_event_loop

    if args.get("result"):
        args["headless"] = False
        args["result"] = abspath(args.get("result"))
    elif args.get("servermode"):
        args["headless"] = True
    inject_module_variables(args=args)
    loop = get_event_loop()
    loop.run_until_complete(mu.get_serveradmindb())
    args["ssl_enabled"] = False


def is_port_occupied(args={}):
    import socket
    from ..gui.util import get_host_port

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    host, port = get_host_port(args=args)
    sr = -1
    try:
        sr = s.connect_ex((host, port))
        s.close()
    except ConnectionError:
        pass
    return sr == 0


def get_pem_path(args={}):
    from os.path import join

    sysconf = args.get("sysconf", {})
    if "conf_dir" in sysconf:
        pem_path = join(sysconf.get("conf_dir"), "cert.pem")
    else:
        pem_path = None
    return pem_path


def get_ssl_context(args={}):
    from os.path import exists
    from ssl import create_default_context, Purpose

    pem_path = get_pem_path(args=args)
    if pem_path and exists(pem_path) and args.get("http_only") == False:
        sc = create_default_context(Purpose.CLIENT_AUTH)
        sc.load_cert_chain(pem_path)
    else:
        sc = None
    return sc


def main(url=None, args={}):
    from webbrowser import open as open_browser
    from ..util.util import quiet_print
    from ..util.run import show_logo
    from ..gui.server import WebServer
    from ..gui.util import get_host_port
    from ..util.asyn import get_event_loop

    logger = args.get("logger")
    if is_port_occupied(args=args):
        msg = (
            f"OakVar or another program is already running at port {args.get('port')}."
        )
        if logger:
            logger.info(msg)
        quiet_print(msg, args)
        if url and not args.get("headless"):
            open_browser(url)
        return
    show_logo()
    host, port = get_host_port(args=args)
    msg = f"OakVar Server is served at {host}:{port}"
    if logger:
        logger.info(msg)
    quiet_print(msg, args=args)
    quiet_print("(To quit: Press Ctrl-C or Ctrl-Break)", args=args)
    loop = get_event_loop()
    if args["ssl_enabled"]:
        args["ssl_context"] = get_ssl_context(args=args)
    _ = WebServer(loop=loop, url=url, args=args)
    loop.run_forever()


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


def get_logger(args={}):
    from logging import getLogger
    from logging import INFO
    from logging import Formatter
    from logging.handlers import TimedRotatingFileHandler
    from ..system.consts import log_dir_key
    from ..gui.util import get_log_path

    global log_path
    log_dir = args.get("sysconf", {}).get(log_dir_key)
    log_path = get_log_path(log_dir=log_dir)
    logger = getLogger()
    logger.setLevel(INFO)
    log_handler = TimedRotatingFileHandler(log_path, when="d", backupCount=30)
    log_formatter = Formatter("%(asctime)s: %(message)s", "%Y/%m/%d %H:%M:%S")
    log_handler.setFormatter(log_formatter)
    logger.addHandler(log_handler)
    return logger


def get_webapp_url(args={}):
    from os.path import join
    from os.path import exists
    from sys import stderr
    from ..system.consts import modules_dir_key
    from ..gui.util import get_host_port

    host, port = get_host_port(args=args)
    sysconf = args.get("sysconf", {})
    index_path = join(
        sysconf.get(modules_dir_key), "webapps", args["webapp"], "index.html"
    )
    if exists(index_path) == False:
        stderr.write(f"Webapp {args['webapp']} does not exist. Exiting.\n")
        return
    url = f"{host}:{port}/webapps/{args['webapp']}/index.html"
    return url


def get_result_url(args={}):
    from os.path import exists
    from ..exceptions import NoInput
    from ..exceptions import ArgumentError
    from ..util.util import is_compatible_version
    from ..gui.util import get_host_port

    dbpath = args.get("result")
    if exists(dbpath) == False:
        raise NoInput()
    (compatible_version, db_version, oc_version) = is_compatible_version(dbpath)
    host, port = get_host_port(args=args)
    if not compatible_version:
        msg = f"DB version {db_version} of {dbpath} is not compatible with the current OakVar ({oc_version}). "
        msg += f'Consider running "oc util update-result {dbpath}" and running "oc gui {dbpath}" again.'
        raise ArgumentError(msg=msg)
    url = f"{host}:{port}/result/nocache/index.html?dbpath={args['result']}"
    return url


def get_login_url(args={}):
    from ..gui.util import get_host_port

    host, port = get_host_port(args=args)
    url = f"{host}:{port}/submit/nocache/login.html"
    return url


# def get_index_url(args={}):
#    from ..gui.util import get_host_port
#    host, port = get_host_port(args=args)
#    url = f"{host}:{port}/submit/nocache/index.html"
#    return url


def get_index_url(args={}):
    from ..gui.util import get_host_port

    host, port = get_host_port(args=args)
    url = f"{host}:{port}/index.html"
    return url


def get_url(args={}):
    if args.get("webapp"):
        url = get_webapp_url(args=args)
    elif args.get("result"):
        url = get_result_url(args=args)
    elif args.get("headless"):
        url = None
    else:
        if args.get("servermode"):
            url = get_login_url(args=args)
        else:
            url = get_index_url(args=args)
    if url:
        protocol = get_protocol(args=args)
        url = protocol + url
    return url


@cli_entry
def cli_gui(args):
    return gui(args)


@cli_func
def gui(args, __name__="gui"):
    from sys import stderr
    from traceback import print_exc
    from ..system import get_system_conf

    sysconf = get_system_conf()
    args["sysconf"] = sysconf
    args["logger"] = get_logger(args=args)
    try:
        setup(args=args)
        url = get_url(args=args)
        main(url=url, args=args)
    except Exception as e:
        # logger = args.get("logger")
        logger = get_logger(args=args)
        if logger:
            logger.exception(e)
        if args.get("debug"):
            print_exc()
        if logger:
            logger.info("Exiting...")
        stderr.write(f"{e}\nCheck {log_path} for details.\n")
    finally:
        logger = args.get("logger")
        if logger:
            for handler in logger.handlers:
                handler.close()
                logger.removeHandler(handler)
