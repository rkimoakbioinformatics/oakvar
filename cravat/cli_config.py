def fn_config_md(args):
    from .sysadmin import set_modules_dir, get_modules_dir
    from .util import get_dict_from_namespace

    args = get_dict_from_namespace(args)
    if args["directory"]:
        set_modules_dir(args["directory"])
    print(get_modules_dir())


def fn_config_system(args):
    from .sysadmin import show_system_conf
    from .util import get_dict_from_namespace

    args = get_dict_from_namespace(args)
    ret = show_system_conf(**args)
    return ret


def fn_config_oakvar(args):
    from .admin_util import show_oakvar_conf
    from .util import get_dict_from_namespace

    args = get_dict_from_namespace(args)
    ret = show_oakvar_conf(**args)
    return ret


def get_parser_fn_config():
    from argparse import ArgumentParser, RawDescriptionHelpFormatter

    parser_fn_config = ArgumentParser(
        formatter_class=RawDescriptionHelpFormatter)
    _subparsers = parser_fn_config.add_subparsers(title="Commands")

    # md
    parser_fn_config_md = _subparsers.add_parser(
        "md",
        help="displays or changes OakVar modules directory.",
        description="displays or changes OakVar modules directory.",
        formatter_class=RawDescriptionHelpFormatter,
    )
    parser_fn_config_md.add_argument("directory",
                                     nargs="?",
                                     help="sets modules directory.")
    parser_fn_config_md.set_defaults(func=fn_config_md)

    # shows system conf content.
    parser_fn_config_system = _subparsers.add_parser(
        "system", help="shows system configuration.")
    parser_fn_config_system.add_argument(
        "--fmt", default="yaml", help="Format of output. json or yaml.")
    parser_fn_config_system.add_argument(
        "--to", default="stdout", help='"stdout" to print. "return" to return')
    parser_fn_config_system.set_defaults(func=fn_config_system)

    # shows oakvar conf content.
    parser_fn_config_oakvar = _subparsers.add_parser(
        "oakvar", help="shows oakvar configuration.")
    parser_fn_config_oakvar.add_argument(
        "--fmt", default="yaml", help="Format of output. json or yaml.")
    parser_fn_config_oakvar.add_argument(
        "--to", default="stdout", help='"stdout" to print. "return" to return')
    parser_fn_config_oakvar.set_defaults(func=fn_config_oakvar)
    return parser_fn_config
