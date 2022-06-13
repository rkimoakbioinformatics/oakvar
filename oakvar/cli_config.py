from .decorators import cli_entry
from .decorators import cli_func


@cli_entry
def cli_ov_config_oakvar(args):
    args.fmt = "yaml"
    args.to = "stdout"
    return ov_config_oakvar(args)


@cli_func
def ov_config_oakvar(args):
    from .admin_util import show_main_conf

    ret = show_main_conf(args)
    return ret


def get_parser_fn_config():
    from argparse import ArgumentParser, RawDescriptionHelpFormatter

    parser_fn_config = ArgumentParser(formatter_class=RawDescriptionHelpFormatter)
    _subparsers = parser_fn_config.add_subparsers(title="Commands")

    # shows oakvar conf content.
    parser_cli_config_oakvar = _subparsers.add_parser(
        "oakvar",
        epilog="A dictionary. content of OakVar configuration file",
        help="shows oakvar configuration.",
    )
    parser_cli_config_oakvar.add_argument(
        "--fmt", default="json", help="Format of output. json or yaml."
    )
    parser_cli_config_oakvar.add_argument(
        "--to", default="return", help='"stdout" to print. "return" to return'
    )
    parser_cli_config_oakvar.add_argument(
        "--quiet", action="store_true", default=None, help="Run quietly"
    )
    parser_cli_config_oakvar.set_defaults(func=cli_ov_config_oakvar)
    parser_cli_config_oakvar.r_return = "A named list. OakVar config information"  # type: ignore
    parser_cli_config_oakvar.r_examples = [  # type: ignore
        "# Get the named list of the OakVar configuration",
        "ov.config.oakvar()",
    ]
    return parser_fn_config
