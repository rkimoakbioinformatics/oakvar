from ...decorators import cli_func
from ...decorators import cli_entry


@cli_entry
def cli_store_register(args):
    return register(args)


@cli_func
def register(args, __name__="store register"):
    from ...store.ov import register

    ret = register(args=args)
    return ret


@cli_entry
def cli_store_fetch(args):
    return fetch(args)


@cli_func
def fetch(args, __name__="store fetch"):
    from ...store.db import fetch_ov_store_cache

    ret = fetch_ov_store_cache(args=args)
    return ret


@cli_entry
def cli_store_url(args):
    return url(args)


@cli_func
def url(args, __name__="store url"):
    from ...store import url

    ret = url(args=args)
    return ret


def get_parser_fn_store():
    from argparse import ArgumentParser, RawDescriptionHelpFormatter

    parser_fn_store = ArgumentParser(formatter_class=RawDescriptionHelpFormatter)
    subparsers = parser_fn_store.add_subparsers(title="Commands")
    add_parser_store_account(subparsers)
    add_parser_fn_store_register(subparsers)
    add_parser_fn_store_fetch(subparsers)
    add_parser_fn_store_url(subparsers)
    add_parser_fn_store_oc(subparsers)
    return parser_fn_store


def add_parser_store_account(subparsers):
    from ..store.account import add_parser_fn_store_account

    add_parser_fn_store_account(subparsers)


def add_parser_fn_store_register(subparsers):
    # publish
    parser_cli_store_register = subparsers.add_parser(
        "register", help="registers a module at the OakVar Store."
    )
    parser_cli_store_register.add_argument("module_name", help="module to register")
    parser_cli_store_register.add_argument(
        "--md", default=None, help="custom modules root directory"
    )
    parser_cli_store_register.add_argument(
        "--quiet", action="store_true", default=None, help="run quietly"
    )
    parser_cli_store_register.add_argument(
        "--code-url",
        required=True,
        help="url of a code pack (made with `ov store pack`)",
    )
    parser_cli_store_register.add_argument(
        "--data-url",
        help="url of a data pack (made with `ov store pack`)",
    )
    parser_cli_store_register.add_argument(
        "--overwrite", action="store_true", help="overwrite if the same version exists"
    )
    parser_cli_store_register.set_defaults(func=cli_store_register)
    parser_cli_store_register.r_return = "A boolean. A boolean. TRUE if successful, FALSE if not"  # type: ignore
    parser_cli_store_register.r_examples = [  # type: ignore
        '# Publish "customannot" module to the store',
        '#roakvar::store.publish(module="customannot", ',
        '# code_url="https://test.com/customannot__1.0.0__code.zip", ',
        '# data_url="https://test.com/customannot__1.0.0__data.zip")',
    ]


def add_parser_fn_store_fetch(subparsers):
    # fetch
    parser_cli_store_fetch = subparsers.add_parser("fetch", help="fetch store cache")
    parser_cli_store_fetch.add_argument(
        "--quiet", action="store_true", default=None, help="run quietly"
    )
    parser_cli_store_fetch.add_argument(
        "--email", default=None, help="email of OakVar store account"
    )
    parser_cli_store_fetch.add_argument(
        "--pw", default=None, help="password of OakVar store account"
    )
    parser_cli_store_fetch.add_argument(
        "--clean", action="store_true", help="erase cache and fetch afresh"
    )
    parser_cli_store_fetch.set_defaults(func=cli_store_fetch)
    parser_cli_store_fetch.r_return = "A boolean. A boolean. TRUE if successful, FALSE if not"  # type: ignore
    parser_cli_store_fetch.r_examples = [  # type: ignore
        "# Fetch the store information",
        "#roakvar::store.fetch()",
    ]


def add_parser_fn_store_url(subparsers):
    # verify-email
    parser_cli_store_verifyemail = subparsers.add_parser(
        "url", help="returns the URL of the OakVar store"
    )
    parser_cli_store_verifyemail.add_argument(
        "--quiet", action="store_true", default=None, help="run quietly"
    )
    parser_cli_store_verifyemail.set_defaults(func=cli_store_url)
    parser_cli_store_verifyemail.r_return = "character"  # type: ignore
    parser_cli_store_verifyemail.r_examples = [  # type: ignore
        "# Returns the URL of the OakVar store.",
        "#roakvar::store.account.url()",
    ]


def add_parser_fn_store_oc(subparsers):
    from ..store.oc import add_parser_fn_store_oc

    add_parser_fn_store_oc(subparsers)
