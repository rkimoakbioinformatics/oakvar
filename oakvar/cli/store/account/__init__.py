from ... import cli_entry
from ... import cli_func


@cli_entry
def cli_store_createaccount(args):
    return create(args)


@cli_func
def create(args, __name__="store account create"):
    from ....api.store.account import create

    args["interactive"] = True
    ret = create(**args)
    return ret


@cli_entry
def cli_store_deleteaccount(args):
    return store_deleteaccount(args)


@cli_func
def store_deleteaccount(args, __name__="store account delete"):
    from ....api.store.account import delete

    ret = delete(**args)
    return ret


@cli_entry
def cli_store_changepassword(args):
    return change(args)


@cli_func
def change(args, __name__="store account change") -> bool:
    from ....api.store.account import change

    ret = change(**args)
    return ret


@cli_entry
def cli_store_account_reset(args):
    return reset(args)


@cli_func
def reset(args, __name__="store account reset"):
    from ....api.store.account import reset

    ret = reset(**args)
    return ret


@cli_entry
def cli_store_check(args):
    return check(args)


@cli_func
def check(args, __name__="store account check"):
    from ....api.store.account import check

    ret = check(**args)
    return ret


def add_parser_fn_store_account(subparsers):
    parser_cli_store_account = subparsers.add_parser(
        "account",
        description="Manage OakVar accounts.",
        help="Manage OakVar accounts.",
    )
    parser_cli_store_account.r_return = "A boolean. TRUE if successful, FALSE if not."  # type: ignore
    parser_cli_store_account.r_examples = [  # type: ignore
        "# Create a store account",
        '#roakvar::store.createaccount(email="user1", password="password")',
    ]
    subparsers = parser_cli_store_account.add_subparsers()
    add_parser_fn_store_account_create(subparsers)
    add_parser_fn_store_account_delete(subparsers)
    add_parser_fn_store_account_change(subparsers)
    add_parser_fn_store_account_check(subparsers)
    add_parser_fn_store_account_reset(subparsers)
    return parser_cli_store_account


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
