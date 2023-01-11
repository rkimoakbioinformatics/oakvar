from . import cli_entry
from . import cli_func


@cli_entry
def cli_util_test(args):
    return test(args)


@cli_func
def test(args, __name__="util test"):
    from ..api.test import test

    ret = test(**args)
    if ret:
        num_failed: int = ret.get("num_failed", 0)
        if num_failed > 0:
            return False
        else:
            return True
    return True


def get_parser_cli_util_test():
    from argparse import ArgumentParser

    parser_cli_util_test = ArgumentParser()
    parser_cli_util_test.add_argument("-d", "--rundir", help="Directory for output")
    parser_cli_util_test.add_argument(
        "-m", "--modules", nargs="+", help="Name of module(s) to test. (e.g. gnomad)"
    )
    parser_cli_util_test.add_argument(
        "--quiet", action="store_true", default=None, help="run quietly"
    )
    parser_cli_util_test.set_defaults(func=cli_util_test)
    return parser_cli_util_test


def main():
    args = get_parser_cli_util_test().parse_args()
    cli_util_test(args)


if __name__ == "__main__":
    main()
