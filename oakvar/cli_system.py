from .decorators import cli_func
from .decorators import cli_entry


@cli_entry
def cli_ov_system_setup(args):
    ov_system_setup(args)


@cli_func
def ov_system_setup(args):
    from .sysadmin import setup_system
    setup_system(args)


@cli_entry
def cli_ov_system_md(args):
    return ov_system_md(args)


@cli_func
def ov_system_md(args):
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


@cli_entry
def cli_ov_system_config(args):
    args.fmt = "yaml"
    return ov_system_config(args)


@cli_func
def ov_system_config(args):
    from .sysadmin import show_system_conf
    ret = show_system_conf(args)
    return ret


def add_parser_ov_system_setup(subparsers):
    parser_cli_ov_system_setup = subparsers.add_parser(
        "setup",
        help="Sets up OakVar system",
        description="Sets up OakVar system")
    parser_cli_ov_system_setup.add_argument("-f",
                                         dest="setup_file",
                                         default=None,
                                         help="setup file to use")
    parser_cli_ov_system_setup.add_argument("--quiet",
                                         default=False,
                                         help="Run quietly")
    parser_cli_ov_system_setup.set_defaults(func=cli_ov_system_setup)
    parser_cli_ov_system_setup.r_return = "A boolean. TRUE if successful, FALSE if not"  # type: ignore
    parser_cli_ov_system_setup.r_examples = [  # type: ignore
        "# Set up OakVar with defaults", "ov.system.setup()",
        "# Set up OakVar with a setup file",
        "ov.system.setup(setup_file=\"setup.yml\")"
    ]

def get_parser_ov_system():
    from argparse import ArgumentParser
    # opens issue report
    parser_ov_system = ArgumentParser()
    subparsers = parser_ov_system.add_subparsers(title="Commands", dest="commands")
    add_parser_ov_system_setup(subparsers)
    """parser_cli_system_setup.add_argument("-f",
                                         dest="setup_file",
                                         default=None,
                                         help="setup file to use")
    parser_cli_system_setup.add_argument("--quiet",
                                         default=True,
                                         help="Run quietly")
    parser_cli_system_setup.set_defaults(func=cli_ov_system_setup)
    parser_cli_system_setup.r_return = "A boolean. TRUE if successful, FALSE if not"  # type: ignore
    parser_cli_system_setup.r_examples = [  # type: ignore
        "# Set up OakVar with defaults", "ov.system.setup()",
        "# Set up OakVar with a setup file",
        "ov.system.setup(setup_file=\"setup.yml\")"
    ]"""

    # md
    parser_cli_system_md = subparsers.add_parser(
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
    parser_cli_system_md.add_argument("--quiet",
                                      default=False,
                                      help="Run quietly")
    parser_cli_system_md.set_defaults(func=cli_ov_system_md)
    parser_cli_system_md.r_return = "A string. OakVar modules directory"  # type: ignore
    parser_cli_system_md.r_examples = [  # type: ignore
        "# Get the OakVar modules directory", "ov.system.md()",
        "# Set the OakVar modules directory to /home/user1/.oakvar/modules",
        "ov.system.md(directory=\"/home/user1/.oakvar/modules\")"
    ]

    # shows system conf content.
    parser_cli_system_config = subparsers.add_parser(
        "config", help="show or change system configuration.")
    parser_cli_system_config.add_argument(
        "--fmt", default="json", help="Format of output. json or yaml.")
    parser_cli_system_config.add_argument(
        "--to", default="return", help='"stdout" to print. "return" to return')
    parser_cli_system_config.add_argument("--quiet",
                                          default=False,
                                          help="Run quietly")
    parser_cli_system_config.set_defaults(func=cli_ov_system_config)
    parser_cli_system_config.r_return = "A named list. System config information"  # type: ignore
    parser_cli_system_config.r_examples = [  # type: ignore
        "# Get named list of the OakVar system configuration",
        "ov.system.config()",
        "# Get the OakVar system configuration in YAML text",
        "ov.system.config(fmt=\"yaml\")"
        "# Print to stdout the OakVar system configuration in YAML text",
        "ov.system.config(fmt=\"yaml\", to=\"stdout\")"
    ]
    return parser_ov_system
