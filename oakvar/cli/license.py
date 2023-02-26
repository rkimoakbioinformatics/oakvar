from . import cli_entry
from . import cli_func


@cli_entry
def cli_license(args):
    return license(args)


@cli_func
def license(args, __name__="license"):
    from ..api import license

    return license(**args)


def get_parser_ov_license():
    from argparse import ArgumentParser

    parser_ov_license = ArgumentParser(
        description="Shows license information.",
    )
    parser_ov_license.set_defaults(func=cli_license)
    return parser_ov_license
