from .decorators import cli_func
from .decorators import cli_entry


@cli_entry
def cli_version(args):
    return ov_version(args)


@cli_func
def ov_version(args):
    from .admin_util import oakvar_version
    from .util import quiet_print
    ret = oakvar_version()
    if args["to"] == "stdout":
        quiet_print(ret, args=args)
    else:
        return ret


def get_parser_cli_version():
    from argparse import ArgumentParser
    # shows version
    parser_cli_version = ArgumentParser()
    parser_cli_version.add_argument(
        "--to", default="return", help='"stdout" to print. "return" to return')
    parser_cli_version.add_argument("--quiet",
                                    default=True,
                                    help="Run quietly")
    parser_cli_version.set_defaults(func=cli_version)
    return parser_cli_version
