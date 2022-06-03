def cli_config_md(args):
    args.to = "stdout"
    return fn_config_md(args)


def fn_config_md(args):
    from .sysadmin import set_modules_dir, get_modules_dir
    from .util import quiet_print
    if args["directory"]:
        set_modules_dir(args["directory"])
    modules_dir = get_modules_dir()
    if args.get("to") == "stdout":
        quiet_print(modules_dir, args=args)
    return modules_dir


def cli_config_system(args):
    args.fmt = "yaml"
    args.to = "stdout"
    return fn_config_system(args)


def fn_config_system(args):
    from .sysadmin import show_system_conf
    ret = show_system_conf(args)
    return ret


def cli_config_oakvar(args):
    args.fmt = "yaml"
    args.to = "stdout"
    return fn_config_oakvar(args)


def fn_config_oakvar(args):
    from .admin_util import show_main_conf
    ret = show_main_conf(args)
    return ret


def get_parser_fn_config():
    from argparse import ArgumentParser, RawDescriptionHelpFormatter
    parser_fn_config = ArgumentParser(
        formatter_class=RawDescriptionHelpFormatter)
    _subparsers = parser_fn_config.add_subparsers(title="Commands")
    from .cli_system import get_parser_ov_system

    # shows oakvar conf content.
    parser_cli_config_oakvar = _subparsers.add_parser(
        "oakvar",
        epilog="A dictionary. content of OakVar configuration file",
        help="shows oakvar configuration.")
    parser_cli_config_oakvar.add_argument(
        "--fmt", default="json", help="Format of output. json or yaml.")
    parser_cli_config_oakvar.add_argument(
        "--to", default="return", help='"stdout" to print. "return" to return')
    parser_cli_config_oakvar.add_argument("--quiet",
                                          default=True,
                                          help="Run quietly")
    parser_cli_config_oakvar.set_defaults(func=cli_config_oakvar)
    parser_cli_config_oakvar.r_return = "A named list. OakVar config information"  # type: ignore
    parser_cli_config_oakvar.r_examples = [  # type: ignore
        "# Get the named list of the OakVar configuration",
        "ov.config.oakvar()"
    ]
    return parser_fn_config
