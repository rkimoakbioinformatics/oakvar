from ....decorators import cli_entry
from ....decorators import cli_func


@cli_entry
def cli_store_createaccount(args):
    return create(args)


@cli_func
def create(args, __name__="store account create"):
    from ....store.ov.account import create

    ret = create(args)
    return ret


@cli_entry
def cli_store_deleteaccount(args):
    return store_deleteaccount(args)


@cli_func
def store_deleteaccount(args):
    from ....store.ov.account import delete_account

    ret = delete_account(args)
    return ret


@cli_entry
def cli_store_changepassword(args):
    return change(args)


@cli_func
def change(args, __name__="store account change"):
    from ....store.oc import change_password

    ret = change_password(
        args.get("username"), args.get("current_password"), args.get("new_password")
    )
    return ret


@cli_entry
def cli_store_resetpassword(args):
    return reset(args)


@cli_func
def reset(args, __name__="store account reset"):
    from ....store.oc import send_reset_email

    ret = send_reset_email(args.get("username"), args=args)
    return ret


@cli_entry
def cli_store_verifyemail(args):
    return verify(args)


@cli_func
def verify(args, __name__="store account verify"):
    from ....store.oc import send_verify_email

    ret = send_verify_email(args.get("username"), args=args)
    return ret


@cli_entry
def cli_store_checklogin(args):
    return verify(args)


@cli_func
def check(args, __name__="store account check"):
    from ....store.oc import check_login

    ret = check_login(args.get("username"), args.get("password"))
    return ret


@cli_entry
def cli_store_saveaccount(args):
    return save(args)


@cli_func
def save(args=None, email=None, pw=None):
    from ....store.ov.account import save

    if not email and args:
        email = args.get("email")
    if not pw and args:
        pw = args.get("pw")
    if not email or not pw:
        return False
    save(email, pw)


def get_parser_fn_store_account():
    from argparse import ArgumentParser

    parser_fn_store_account = ArgumentParser()
    subparsers = parser_fn_store_account.add_subparsers(
        title="Commands", dest="command"
    )
    get_parser_fn_store_account_create(subparsers)
    get_parser_fn_store_account_delete(subparsers)
    get_parser_fn_store_account_change(subparsers)
    get_parser_fn_store_account_check(subparsers)
    get_parser_fn_store_account_reset(subparsers)
    get_parser_fn_store_account_verify(subparsers)
    get_parser_fn_store_account_save(subparsers)
    return parser_fn_store_account


def get_parser_fn_store_account_create(subparsers):
    # create-account
    parser_cli_store_createaccount = subparsers.add_parser(
        "create", help="creates a OakVar store developer account."
    )
    parser_cli_store_createaccount.add_argument(
        "--email", help="An email address is used as the account user name."
    )
    parser_cli_store_createaccount.add_argument("--pw", help="Password")
    parser_cli_store_createaccount.add_argument(
        "--quiet", action="store_true", default=None, help="Run quietly"
    )
    parser_cli_store_createaccount.set_defaults(func=cli_store_createaccount)
    parser_cli_store_createaccount.r_return = "A boolean. TRUE if successful, FALSE if not."  # type: ignore
    parser_cli_store_createaccount.r_examples = [  # type: ignore
        "# Create a store account",
        '#roakvar::store.createaccount(username="user1", password="password")',
    ]


def get_parser_fn_store_account_delete(subparsers):
    # create-account
    parser_cli_store_deleteaccount = subparsers.add_parser(
        "delete", help="creates a OakVar store developer account."
    )
    parser_cli_store_deleteaccount.add_argument(
        "--email", help="An email address is used as the account user name."
    )
    parser_cli_store_deleteaccount.add_argument("--pw", help="Password")
    parser_cli_store_deleteaccount.add_argument(
        "--quiet", action="store_true", default=None, help="Run quietly"
    )
    parser_cli_store_deleteaccount.set_defaults(func=cli_store_deleteaccount)
    parser_cli_store_deleteaccount.r_return = "A boolean. TRUE if successful, FALSE if not."  # type: ignore
    parser_cli_store_deleteaccount.r_examples = [  # type: ignore
        "# Create a store account",
        '#roakvar::store.deleteaccount(username="user1", password="password")',
    ]


def get_parser_fn_store_account_change(subparsers):
    # change-password
    parser_cli_store_changepassword = subparsers.add_parser(
        "change", help="changes OakVar store account password."
    )
    parser_cli_store_changepassword.add_argument("username", help="username")
    parser_cli_store_changepassword.add_argument(
        "current_password", help="current password"
    )
    parser_cli_store_changepassword.add_argument("new_password", help="new password")
    parser_cli_store_changepassword.add_argument(
        "--quiet", action="store_true", default=None, help="Run quietly"
    )
    parser_cli_store_changepassword.set_defaults(func=cli_store_changepassword)
    parser_cli_store_changepassword.r_return = "A string. Response from the store server"  # type: ignore
    parser_cli_store_changepassword.r_examples = [  # type: ignore
        "# Change the password of a store account",
        '#roakvar::store.changepassword(username="user1", current_password="password", new_password="newpassword")',
    ]


def get_parser_fn_store_account_reset(subparsers):
    # reset-password
    parser_cli_store_resetpassword = subparsers.add_parser(
        "reset", help="resets OakVar store account password."
    )
    parser_cli_store_resetpassword.add_argument(
        "--quiet", action="store_true", default=None, help="Run quietly"
    )
    parser_cli_store_resetpassword.add_argument("username", help="username")
    parser_cli_store_resetpassword.set_defaults(func=cli_store_resetpassword)
    parser_cli_store_resetpassword.r_return = "A boolean. A boolean. TRUE if successful, FALSE if not"  # type: ignore
    parser_cli_store_resetpassword.r_examples = [  # type: ignore
        "# Ask the store to send an email to reset the password of a store account",
        '#roakvar::store.resetpassword(username="user1")',
    ]


def get_parser_fn_store_account_verify(subparsers):
    # verify-email
    parser_cli_store_verifyemail = subparsers.add_parser(
        "verify", help="sends a verification email."
    )
    parser_cli_store_verifyemail.add_argument("username", help="username")
    parser_cli_store_verifyemail.add_argument(
        "--quiet", action="store_true", default=None, help="Run quietly"
    )
    parser_cli_store_verifyemail.set_defaults(func=cli_store_verifyemail)
    parser_cli_store_verifyemail.r_return = "`NULL`"  # type: ignore
    parser_cli_store_verifyemail.r_examples = [  # type: ignore
        "# Ask the store to send an email to verify the email of a user account",
        '#roakvar::store.verifyemail(username="user1")',
    ]


def get_parser_fn_store_account_check(subparsers):
    # check-login
    parser_cli_store_checklogin = subparsers.add_parser(
        "check", help="checks username and password."
    )
    parser_cli_store_checklogin.add_argument("username", help="username")
    parser_cli_store_checklogin.add_argument("password", help="password")
    parser_cli_store_checklogin.add_argument(
        "--quiet", action="store_true", default=None, help="Run quietly"
    )
    parser_cli_store_checklogin.set_defaults(func=cli_store_checklogin)
    parser_cli_store_checklogin.r_return = "A boolean. A boolean. TRUE if successful, FALSE if not"  # type: ignore
    parser_cli_store_checklogin.r_examples = [  # type: ignore
        "# Check if the login information of a user is correct",
        '#roakvar::store.checklogin(username="user1", password="password")',
    ]


def get_parser_fn_store_account_save(subparsers):
    # store login
    parser_cli_store_saveaccount = subparsers.add_parser(
        "save", help="Store the email and password for OakVar store"
    )
    parser_cli_store_saveaccount.add_argument(
        "--quiet", action="store_true", default=None, help="Run quietly"
    )
    parser_cli_store_saveaccount.add_argument(
        "--email", default=None, help="email of an OakVar store account"
    )
    parser_cli_store_saveaccount.add_argument(
        "--pw", default=None, help="password of an OakVar store account"
    )
    parser_cli_store_saveaccount.set_defaults(func=cli_store_saveaccount)
    parser_cli_store_saveaccount.r_return = "A boolean. A boolean. TRUE if successful, FALSE if not"  # type: ignore
    parser_cli_store_saveaccount.r_examples = [  # type: ignore
        "# Save the email and password of an OakVar account.",
        '#roakvar::store.saveaccount(email="test@test.com", pw="testpw")',
    ]
