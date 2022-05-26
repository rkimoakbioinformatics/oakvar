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
    args["fmt"] = "yaml"
    args["to"] = "stdout"
    ret = show_system_conf(args)
    return ret


def fn_config_oakvar(args):
    from .admin_util import show_oakvar_conf
    from .util import get_dict_from_namespace

    args = get_dict_from_namespace(args)
    args["fmt"] = "yaml"
    args["to"] = "stdout"
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
        epilog="A string. location of OakVar modules directory",
        help="displays or changes OakVar modules directory.",
        description="displays or changes OakVar modules directory.",
        formatter_class=RawDescriptionHelpFormatter,
    )
    parser_fn_config_md.add_argument("directory",
                                     nargs="?",
                                     help="sets modules directory.")
    parser_fn_config_md.set_defaults(func=fn_config_md)
    parser_fn_config_md.r_return = "A string. Location of the OakVar modules directory"
    parser_fn_config_md.r_examples = [
        "# Get the OakVar modules directory",
        "ov.config.md()",
        "# Set the OakVar modules directory to /home/user1/.oakvar/modules",
        "ov.config.md(directory=\"/home/user1/.oakvar/modules\")"
    ]

    # shows system conf content.
    parser_fn_config_system = _subparsers.add_parser(
        "system", epilog="A dictionary. module information", help="shows system configuration.")
    parser_fn_config_system.add_argument(
        "--fmt", default="json", help="Format of output. json or yaml.")
    parser_fn_config_system.add_argument(
        "--to", default="return", help='"stdout" to print. "return" to return')
    parser_fn_config_system.set_defaults(func=fn_config_system)
    parser_fn_config_system.r_return = "A named list. System config information"
    parser_fn_config_system.r_examples = [
        "# Get named list of the OakVar system configuration",
        "ov.config.system()",
        "# Get the OakVar system configuration in YAML text",
        "ov.config.system(fmt=\"yaml\")"
        "# Print to stdout the OakVar system configuration in YAML text",
        "ov.config.system(fmt=\"yaml\", to=\"stdout\")"
    ]

    # shows oakvar conf content.
    parser_fn_config_oakvar = _subparsers.add_parser(
        "oakvar", epilog="A dictionary. content of OakVar configuration file", help="shows oakvar configuration.")
    parser_fn_config_oakvar.add_argument(
        "--fmt", default="json", help="Format of output. json or yaml.")
    parser_fn_config_oakvar.add_argument(
        "--to", default="return", help='"stdout" to print. "return" to return')
    parser_fn_config_oakvar.set_defaults(func=fn_config_oakvar)
    parser_fn_config_oakvar.r_return = "A named list. OakVar config information"
    parser_fn_config_oakvar.r_examples = [
        "# Get the named list of the OakVar configuration",
        "ov.config.oakvar()"
    ]
    return parser_fn_config
