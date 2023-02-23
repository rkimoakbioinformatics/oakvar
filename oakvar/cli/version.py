from . import cli_entry
from . import cli_func


@cli_entry
def cli_version(args):
    return version(args)


@cli_func
def version(args, __name__="version"):
    from ..api import version

    ret = version()
    outer = args.get("outer")
    if outer:
        outer.write(ret)
    else:
        return ret


def get_parser_fn_version():
    from argparse import ArgumentParser

    # shows version
    parser_cli_version = ArgumentParser()
    parser_cli_version.add_argument(
        "--quiet", action="store_true", default=None, help="run quietly"
    )
    parser_cli_version.set_defaults(func=cli_version)
    return parser_cli_version
