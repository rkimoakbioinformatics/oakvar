def get_host_port(args):
    serv = get_server(args)
    host = serv.get("host")
    port = None
    if args["port"]:
        try:
            port = int(args["port"])
        except:
            port = None
    if not port:
        port = serv.get("port")
    return host, port


def get_server(args):
    from ..system import get_system_conf
    import platform
    from ..exceptions import SetupError


    sysconf = get_system_conf()
    if not sysconf:
        raise SetupError()
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
        if args.get("ssl_enabled", False):
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
        raise e

