from . import cli_entry
from . import cli_func


@cli_entry
def cli_update(args):
    return update(args)


@cli_func
def update(args, __name__="update"):
    from ..api import update

    return update(**args)


def get_parser_ov_update():
    from argparse import ArgumentParser

    parser_ov_update = ArgumentParser(
        description="Updates OakVar to the latest version.",
    )
    parser_ov_update.set_defaults(func=cli_update)
    return parser_ov_update
