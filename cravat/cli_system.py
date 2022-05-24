def fn_system_setup(args):
    from .sysadmin import setup_system
    from .util import get_dict_from_namespace
    args = get_dict_from_namespace(args)
    setup_system(args)


def fn_system_md(args):
    from .sysadmin import set_modules_dir, get_modules_dir
    from .util import get_dict_from_namespace
    args = get_dict_from_namespace(args)
    args.setdefault("to", "return")
    d = args.get("directory")
    if d:
        set_modules_dir(d)
    d = get_modules_dir()
    if args.get("to") == "stdout":
        if d is not None:
            print(d)
    else:
        return d

def fn_system_config(args):
    from .sysadmin import show_system_conf
    from .util import get_dict_from_namespace
    args = get_dict_from_namespace(args)
    args["to"] = "stdout"
    ret = show_system_conf(args)
    return ret

def get_parser_fn_system():
    from argparse import ArgumentParser
    # opens issue report
    parser_fn_system = ArgumentParser()
    _subparsers = parser_fn_system.add_subparsers(title="Commands")
    parser_fn_system_setup = _subparsers.add_parser("setup", help="Sets up OakVar system", description="Sets up OakVar system")
    parser_fn_system_setup.add_argument("-f", dest="setup_file", default=None, help="setup file to use")
    parser_fn_system_setup.set_defaults(func=fn_system_setup)
    # md
    parser_fn_system_md = _subparsers.add_parser(
        "md",
        help="displays or changes OakVar modules directory.",
        description="displays or changes OakVar modules directory.",
    )
    parser_fn_system_md.add_argument("directory", nargs="?", help="sets modules directory.")
    parser_fn_system_md.add_argument("--to", default="stdout", help="'stdout' to print. 'return' to return.")
    parser_fn_system_md.set_defaults(func=fn_system_md)
    # shows system conf content.
    parser_fn_system_config = _subparsers.add_parser(
        "config", help="show or change system configuration."
    )
    parser_fn_system_config.add_argument(
        "--fmt", default="yaml", help="Format of output. json or yaml."
    )
    parser_fn_system_config.add_argument(
        "--to", default="stdout", help='"stdout" to print. "return" to return'
    )
    parser_fn_system_config.set_defaults(func=fn_system_config)
    return parser_fn_system
