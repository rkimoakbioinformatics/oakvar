def cli_system_setup(args):
    from .util import get_dict_from_namespace
    args = get_dict_from_namespace(args)
    args["quiet"] = False
    fn_system_setup(args)

def fn_system_setup(args):
    from .sysadmin import setup_system
    setup_system(args)


def cli_system_md(args):
    from .util import get_dict_from_namespace
    args = get_dict_from_namespace(args)
    args["quiet"] = False
    args["to"] = "stdout"
    return fn_system_md(args)

def fn_system_md(args):
    from .sysadmin import set_modules_dir, get_modules_dir
    from .util import quiet_print
    d = args.get("directory")
    if d:
        set_modules_dir(d)
    d = get_modules_dir()
    if args.get("to") == "stdout":
        if d is not None:
            quiet_print(d, args=args)
    else:
        return d


def cli_system_config(args):
    from .util import get_dict_from_namespace
    args = get_dict_from_namespace(args)
    args["quiet"] = False
    args["fmt"] = "yaml"
    args["to"] = "stdout"
    return fn_system_config(args)

def fn_system_config(args):
    from .sysadmin import show_system_conf
    from .util import get_dict_from_namespace
    args = get_dict_from_namespace(args)
    ret = show_system_conf(args)
    return ret


def get_parser_fn_system():
    from argparse import ArgumentParser
    # opens issue report
    parser_fn_system = ArgumentParser()
    _subparsers = parser_fn_system.add_subparsers(title="Commands")
    parser_cli_system_setup = _subparsers.add_parser(
        "setup",
        help="Sets up OakVar system",
        description="Sets up OakVar system")
    parser_cli_system_setup.add_argument("-f",
                                        dest="setup_file",
                                        default=None,
                                        help="setup file to use")
    parser_cli_system_setup.add_argument("--quiet", default=True, help="Run quietly")
    parser_cli_system_setup.set_defaults(func=cli_system_setup)
    parser_cli_system_setup.r_return = "A boolean. TRUE if successful, FALSE if not" # type: ignore
    parser_cli_system_setup.r_examples = [ # type: ignore
        "# Set up OakVar with defaults",
        "ov.system.setup()",
        "# Set up OakVar with a setup file",
        "ov.system.setup(setup_file=\"setup.yml\")"
    ]

    # md
    parser_cli_system_md = _subparsers.add_parser(
        "md",
        help="displays or changes OakVar modules directory.",
        description="displays or changes OakVar modules directory.",
    )
    parser_cli_system_md.add_argument("directory",
                                     nargs="?",
                                     help="sets modules directory.")
    parser_cli_system_md.add_argument(
        "--to",
        default="return",
        help="'stdout' to print. 'return' to return.")
    parser_cli_system_md.add_argument("--quiet", default=True, help="Run quietly")
    parser_cli_system_md.set_defaults(func=cli_system_md)
    parser_cli_system_md.r_return = "A string. OakVar modules directory" # type: ignore
    parser_cli_system_md.r_examples = [ # type: ignore
        "# Get the OakVar modules directory",
        "ov.system.md()",
        "# Set the OakVar modules directory to /home/user1/.oakvar/modules",
        "ov.system.md(directory=\"/home/user1/.oakvar/modules\")"
    ]

    # shows system conf content.
    parser_cli_system_config = _subparsers.add_parser(
        "config", help="show or change system configuration.")
    parser_cli_system_config.add_argument(
        "--fmt", default="json", help="Format of output. json or yaml.")
    parser_cli_system_config.add_argument(
        "--to", default="return", help='"stdout" to print. "return" to return')
    parser_cli_system_config.add_argument("--quiet", default=True, help="Run quietly")
    parser_cli_system_config.set_defaults(func=cli_system_config)
    parser_cli_system_config.r_return = "A named list. System config information" # type: ignore
    parser_cli_system_config.r_examples = [ # type: ignore
        "# Get named list of the OakVar system configuration",
        "ov.system.config()",
        "# Get the OakVar system configuration in YAML text",
        "ov.system.config(fmt=\"yaml\")"
        "# Print to stdout the OakVar system configuration in YAML text",
        "ov.system.config(fmt=\"yaml\", to=\"stdout\")"
    ]
    return parser_fn_system
