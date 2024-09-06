# OakVar
#
# Copyright (c) 2024 Oak Bioinformatics, LLC
#
# All rights reserved.
#
# Do not distribute or use this software without obtaining
# a license from Oak Bioinformatics, LLC.
#
# Do not use this software to develop another software
# which competes with the products by Oak Bioinformatics, LLC,
# without obtaining a license for such use from Oak Bioinformatics, LLC.
#
# For personal use of non-commercial nature, you may use this software
# after registering with `ov store account create`.
#
# For research use of non-commercial nature, you may use this software
# after registering with `ov store account create`.
#
# For use by commercial entities, you must obtain a commercial license
# from Oak Bioinformatics, LLC. Please write to info@oakbioinformatics.com
# to obtain the commercial license.
# ================
# OpenCRAVAT
#
# MIT License
#
# Copyright (c) 2021 KarchinLab
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from .. import cli_entry
from .. import cli_func


@cli_entry
def cli_store_register(args):
    return register(args)


@cli_func
def register(args, __name__="store register"):
    from ...api.store import register

    ret = register(**args)
    return ret


@cli_entry
def cli_store_fetch(args):
    return fetch(args)


@cli_func
def fetch(args, __name__="store fetch"):
    from ...api.store import fetch

    ret = fetch(**args)
    return ret


@cli_entry
def cli_store_url(args):
    return url(args)


@cli_func
def url(args, __name__="store url"):
    from ...api.store import url

    ret = url(**args)
    return ret


@cli_entry
def cli_store_delete(args):
    return delete(args)


@cli_func
def delete(args, __name__="store delete"):
    from ...api.store import delete

    return delete(**args)


@cli_entry
def cli_store_account_login(args):
    return login(args)


@cli_func
def login(args, __name__="store login"):
    from ...lib.store.ov.account import login

    outer = args.get("outer")
    ret = login(**args, interactive=True)
    msg = ret.get("msg")
    if outer and msg:
        outer.write(msg)
    return ret


@cli_entry
def cli_store_account_logout(args):
    return logout(args)


@cli_func
def logout(args, __name__="store logout"):
    from ...lib.store.ov.account import logout

    ret = logout(**args)
    return ret


def get_parser_fn_store():
    from argparse import ArgumentParser, RawDescriptionHelpFormatter

    parser_fn_store = ArgumentParser(formatter_class=RawDescriptionHelpFormatter)
    subparsers = parser_fn_store.add_subparsers(title="Commands")
    add_parser_store_account(subparsers)
    add_parser_fn_store_register(subparsers)
    add_parser_fn_store_fetch(subparsers)
    add_parser_fn_store_url(subparsers)
    add_parser_fn_store_delete(subparsers)
    add_parser_fn_store_login(subparsers)
    add_parser_fn_store_logout(subparsers)
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
        "--quiet", action="store_true", default=None, help="run quietly"
    )
    parser_cli_store_register.add_argument(
        "--code-url",
        nargs="+",
        default=[],
        help="url of a code pack (made with `ov store pack`)",
    )
    parser_cli_store_register.add_argument(
        "--data-url",
        nargs="+",
        default=[],
        help="url of a data pack (made with `ov store pack`)",
    )
    parser_cli_store_register.add_argument(
        "--overwrite", action="store_true", help="overwrite if the same version exists"
    )
    parser_cli_store_register.add_argument(
        "-f",
        dest="url_file",
        default=None,
        help="use a yaml file for code-url and data-url",
    )
    parser_cli_store_register.set_defaults(func=cli_store_register)
    parser_cli_store_register.r_return = (
        "A boolean. A boolean. TRUE if successful, FALSE if not"  # type: ignore
    )
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
        "--refresh-db", action="store_true", help="Refresh cache database."
    )
    parser_cli_store_fetch.add_argument(
        "--clean-cache-files", action="store_true", help="clean cache files"
    )
    parser_cli_store_fetch.set_defaults(func=cli_store_fetch)
    parser_cli_store_fetch.r_return = (
        "A boolean. A boolean. TRUE if successful, FALSE if not"  # type: ignore
    )
    parser_cli_store_fetch.r_examples = [  # type: ignore
        "# Fetch the store information",
        "#roakvar::store.fetch()",
    ]


def add_parser_fn_store_url(subparsers):
    # verify-email
    parser_cli_store_url = subparsers.add_parser(
        "url", help="returns the URL of the OakVar store"
    )
    parser_cli_store_url.add_argument(
        "--to", dest="url", default=None, help="New OakVar store URL to use"
    )
    parser_cli_store_url.set_defaults(func=cli_store_url)
    parser_cli_store_url.r_return = "character"  # type: ignore
    parser_cli_store_url.r_examples = [  # type: ignore
        "# Returns the URL of the OakVar store.",
        "#roakvar::store.account.url()",
    ]


def add_parser_fn_store_delete(subparsers):
    parser_cli_store_delete = subparsers.add_parser(
        "delete", help="Deletes a module of a version from the Oakvar store."
    )
    parser_cli_store_delete.add_argument(
        "module_name", help="Name of the module to delete"
    )
    parser_cli_store_delete.add_argument(
        "--version",
        dest="code_version",
        default=None,
        help="Version of the module to delete",
    )
    parser_cli_store_delete.add_argument(
        "--all",
        action="store_true",
        default=False,
        help="Deletes all versions of the module.",
    )
    parser_cli_store_delete.add_argument(
        "--keep-only-latest",
        action="store_true",
        default=False,
        help="Deletes all versions of the module except the latest.",
    )
    parser_cli_store_delete.set_defaults(func=cli_store_delete)
    parser_cli_store_delete.r_return = "A boolean. TRUE if successful, FALSE if not."
    parser_cli_store_delete.r_examples = [
        "# Deletes a module from the OakVar store",
        "#roakvar::store.delete(module_name='clinvar', version='1.0.0')",
    ]


def add_parser_fn_store_login(subparsers):
    # verify-email
    parser_cli_store_verifyemail = subparsers.add_parser(
        "login", help="log in to the OakVar Store"
    )
    parser_cli_store_verifyemail.add_argument("--email", help="email")
    parser_cli_store_verifyemail.add_argument("--pw", help="email")
    parser_cli_store_verifyemail.add_argument(
        "--quiet", action="store_true", default=None, help="run quietly"
    )
    parser_cli_store_verifyemail.set_defaults(func=cli_store_account_login)
    parser_cli_store_verifyemail.r_return = "`NULL`"  # type: ignore
    parser_cli_store_verifyemail.r_examples = [  # type: ignore
        "# Log in to the OakVar Store",
        '#roakvar::store.account.login(email="user1", pw="password")',
    ]


def add_parser_fn_store_logout(subparsers):
    # verify-email
    parser_cli_store_verifyemail = subparsers.add_parser(
        "logout", help="log out of the OakVar Store"
    )
    parser_cli_store_verifyemail.add_argument(
        "--quiet", action="store_true", default=None, help="run quietly"
    )
    parser_cli_store_verifyemail.set_defaults(func=cli_store_account_logout)
    parser_cli_store_verifyemail.r_return = "`NULL`"  # type: ignore
    parser_cli_store_verifyemail.r_examples = [  # type: ignore
        "# Log out from the OakVar Store",
        "#roakvar::store.account.logout()",
    ]
