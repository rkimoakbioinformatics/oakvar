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
def cli_store_createaccount(args):
    return create(args)


@cli_func
def create(args, __name__="store account create"):
    from ...lib.store.ov.account import create

    ret = create(**args)
    ret = ret.get("success")
    return ret


@cli_entry
def cli_store_deleteaccount(args):
    return store_deleteaccount(args)


@cli_func
def store_deleteaccount(args, __name__="store account delete"):
    from ...lib.store.ov.account import delete

    ret = delete(**args)
    return ret


@cli_entry
def cli_store_changepassword(args):
    return change(args)


@cli_func
def change(args, __name__="store account change"):
    from ...lib.store.ov.account import change

    ret = change(**args)
    return ret


@cli_entry
def cli_store_account_reset(args):
    return reset(args)


@cli_func
def reset(args, __name__="store account reset"):
    from ...lib.store.ov.account import reset

    ret = reset(**args)
    return ret


@cli_entry
def cli_store_check(args):
    return check(args)


@cli_func
def check(args, __name__="store account check"):
    from ...lib.store.ov.account import check_logged_in_with_token

    ret = check_logged_in_with_token(**args)
    return ret


@cli_entry
def cli_store_account_login(args):
    return login(args)


@cli_func
def login(args, __name__="store account login"):
    from ...lib.store.ov.account import login

    outer = args.get("outer")
    ret = login(**args)
    msg = ret.get("msg")
    if outer and msg:
        outer.write(msg)
    return ret


@cli_entry
def cli_store_account_logout(args):
    return logout(args)


@cli_func
def logout(args, __name__="store account logout"):
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
    add_parser_fn_store_account(subparsers)
    return parser_fn_store


def add_parser_store_account(subparsers):
    from ..store.account import add_parser_fn_store_account as add_sub

    add_sub(subparsers)


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
        "--refresh-db", action="store_true", help="Refresh cache database."
    )
    parser_cli_store_fetch.add_argument(
        "--clean-cache-files", action="store_true", help="clean cache files"
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
    parser_cli_store_verifyemail.set_defaults(func=cli_store_url)
    parser_cli_store_verifyemail.r_return = "character"  # type: ignore
    parser_cli_store_verifyemail.r_examples = [  # type: ignore
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
        "--version", default=None, help="Version of the module to delete"
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


def add_parser_fn_store_account(subparsers):
    add_parser_fn_store_account_login(subparsers)
    add_parser_fn_store_account_logout(subparsers)


def add_parser_fn_store_account_create(subparsers):
    # create-account
    parser_cli_store_createaccount = subparsers.add_parser(
        "create", help="create an OakVar Store account."
    )
    parser_cli_store_createaccount.add_argument(
        "--email",
        help="An email address is used as the account user name.",
    )
    parser_cli_store_createaccount.add_argument("--pw", help="Password")
    parser_cli_store_createaccount.add_argument(
        "--quiet", action="store_true", default=None, help="run quietly"
    )
    parser_cli_store_createaccount.set_defaults(func=cli_store_createaccount)
    parser_cli_store_createaccount.r_return = "A boolean. TRUE if successful, FALSE if not."  # type: ignore
    parser_cli_store_createaccount.r_examples = [  # type: ignore
        "# Create a store account",
        '#roakvar::store.createaccount(email="user1", password="password")',
    ]


def add_parser_fn_store_account_delete(subparsers):
    # create-account
    parser_cli_store_deleteaccount = subparsers.add_parser(
        "delete", help="delete an OakVar Store account."
    )
    parser_cli_store_deleteaccount.add_argument(
        "--quiet", action="store_true", default=None, help="run quietly"
    )
    parser_cli_store_deleteaccount.set_defaults(func=cli_store_deleteaccount)
    parser_cli_store_deleteaccount.r_return = "A boolean. TRUE if successful, FALSE if not."  # type: ignore
    parser_cli_store_deleteaccount.r_examples = [  # type: ignore
        "# Create a store account",
        '#roakvar::store.deleteaccount(email="user1", password="password")',
    ]


def add_parser_fn_store_account_change(subparsers):
    # change-password
    parser_cli_store_changepassword = subparsers.add_parser(
        "change", help="changes OakVar store account password."
    )
    parser_cli_store_changepassword.add_argument("--newpw", help="new password")
    parser_cli_store_changepassword.add_argument(
        "--quiet", action="store_true", default=None, help="run quietly"
    )
    parser_cli_store_changepassword.set_defaults(func=cli_store_changepassword)
    parser_cli_store_changepassword.r_return = "A string. Response from the store server"  # type: ignore
    parser_cli_store_changepassword.r_examples = [  # type: ignore
        "# Change the password of a store account",
        '#roakvar::store.changepassword(email="user1", ',
        '# current_password="password", new_password="newpassword")',
    ]


def add_parser_fn_store_account_reset(subparsers):
    # reset-password
    parser_cli_store_resetpassword = subparsers.add_parser(
        "reset", help="resets OakVar store account password."
    )
    parser_cli_store_resetpassword.add_argument(
        "--quiet", action="store_true", default=None, help="run quietly"
    )
    parser_cli_store_resetpassword.add_argument("--email", required=True, help="email")
    parser_cli_store_resetpassword.set_defaults(func=cli_store_account_reset)
    parser_cli_store_resetpassword.r_return = "A boolean. A boolean. TRUE if successful, FALSE if not"  # type: ignore
    parser_cli_store_resetpassword.r_examples = [  # type: ignore
        "# Ask the store to send an email to reset the password of a store account",
        '#roakvar::store.account.reset(email="user1")',
    ]


def add_parser_fn_store_account_check(subparsers):
    # check-login
    parser_cli_store_checklogin = subparsers.add_parser(
        "check", help="checks email and password."
    )
    parser_cli_store_checklogin.add_argument(
        "--quiet", action="store_true", default=None, help="run quietly"
    )
    parser_cli_store_checklogin.set_defaults(func=cli_store_check)
    parser_cli_store_checklogin.r_return = "A boolean. A boolean. TRUE if successful, FALSE if not"  # type: ignore
    parser_cli_store_checklogin.r_examples = [  # type: ignore
        "# Check if the current is logged in the OakVar Store nor not. ",
        '#roakvar::store.checklogin(email="user1", password="password")',
    ]


def add_parser_fn_store_account_login(subparsers):
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


def add_parser_fn_store_account_logout(subparsers):
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
