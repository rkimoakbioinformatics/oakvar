from ..decorators import cli_entry
from ..decorators import cli_func


@cli_entry
def cli_config_user(args):
    args.fmt = "yaml"
    args.to = "stdout"
    return user(args)


@cli_func
def user(args, __name__="config user"):
    from ..util.admin_util import show_main_conf

    ret = show_main_conf(args)
    return ret


@cli_entry
def cli_config_system(args):
    args.fmt = "yaml"
    args.to = "stdout"
    return system(args)


@cli_func
def system(args, __name__="config system"):
    from ..system import show_system_conf

    ret = show_system_conf(args)
    return ret


def get_parser_fn_config():
    from argparse import ArgumentParser, RawDescriptionHelpFormatter

    parser_fn_config = ArgumentParser(formatter_class=RawDescriptionHelpFormatter)
    subparsers = parser_fn_config.add_subparsers(title="Commands")
    add_parser_ov_config_user(subparsers)
    add_parser_ov_config_system(subparsers)
    return parser_fn_config


def add_parser_ov_config_user(subparsers):
    # shows oakvar conf content.
    parser_cli_config_oakvar = subparsers.add_parser(
        "user",
        epilog="A dictionary. content of OakVar user configuration file",
        help="shows oakvar user configuration",
    )
    parser_cli_config_oakvar.add_argument(
        "--fmt", default="json", help="Format of output. json or yaml."
    )
    parser_cli_config_oakvar.add_argument(
        "--to", default="return", help='"stdout" to print. "return" to return'
    )
    parser_cli_config_oakvar.add_argument(
        "--quiet", action="store_true", default=None, help="run quietly"
    )
    parser_cli_config_oakvar.set_defaults(func=cli_config_user)
    parser_cli_config_oakvar.r_return = "A named list. OakVar user config information"  # type: ignore
    parser_cli_config_oakvar.r_examples = [  # type: ignore
        "# Get the named list of the OakVar user configuration",
        "#roakvar::config.user()",
    ]


def add_parser_ov_config_system(subparsers):
    # shows oakvar conf content.
    parser_cli_config_oakvar = subparsers.add_parser(
        "system",
        epilog="A dictionary. content of OakVar system configuration file",
        help="shows oakvar system configuration",
    )
    parser_cli_config_oakvar.add_argument(
        "--fmt", default="json", help="Format of output. json or yaml."
    )
    parser_cli_config_oakvar.add_argument(
        "--to", default="return", help='"stdout" to print. "return" to return'
    )
    parser_cli_config_oakvar.add_argument(
        "--quiet", action="store_true", default=None, help="run quietly"
    )
    parser_cli_config_oakvar.set_defaults(func=cli_config_system)
    parser_cli_config_oakvar.r_return = "A named list. OakVar system config information"  # type: ignore
    parser_cli_config_oakvar.r_examples = [  # type: ignore
        "# Get the named list of the OakVar system configuration",
        "#roakvar::config.system()",
    ]
