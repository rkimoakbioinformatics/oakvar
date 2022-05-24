def fn_setup(args):
    from .admin_util import setup_system

    setup_system()


def get_parser_fn_setup():
    from argparse import ArgumentParser

    # opens issue report
    parser_fn_setup = (
        ArgumentParser()
    )
    parser_fn_setup.set_defaults(func=fn_setup)
    return parser_fn_setup

