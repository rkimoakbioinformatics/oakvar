from ...decorators import cli_func
from ...decorators import cli_entry


@cli_entry
def cli_store_oc_publish(args):
    return oc_publish(args)


@cli_func
def oc_publish(args, __name__="store oc publish"):
    from ...system import get_system_conf
    from ...store.oc import publish_module
    from getpass import getpass
    from ...system import consts

    if args.get("md"):
        consts.custom_modules_dir = args.get("md")
    sys_conf = get_system_conf()
    if not args.get("user"):
        if "publish_username" in sys_conf:
            args["user"] = sys_conf["publish_username"]
        else:
            args["user"] = input("Email: ")
    if not args.get("password"):
        if "publish_password" in sys_conf:
            args["password"] = sys_conf["publish_password"]
        else:
            args["password"] = getpass()
    return publish_module(
        args.get("module"),
        args.get("user"),
        args.get("password"),
        overwrite=args.get("overwrite"),
        include_data=args.get("data"),
        quiet=args.get("quiet"),
    )


@cli_entry
def cli_store_oc_newaccount(args):
    return oc_newaccount(args)


@cli_func
def oc_newaccount(args, __name__="store oc newaccount"):
    from ...store.oc import create_account

    ret = create_account(args=args)
    return ret


@cli_entry
def cli_store_oc_changepw(args):
    return oc_changepw(args)


@cli_func
def oc_changepw(args, __name__="store oc changepw"):
    from ...store.oc import change_password

    ret = change_password(args=args)
    return ret


@cli_entry
def cli_store_oc_resetpw(args):
    return oc_resetpw(args)


@cli_func
def oc_resetpw(args, __name__="store oc resetpw"):
    from ...store.oc import send_reset_email

    ret = send_reset_email(args=args)
    return ret


@cli_entry
def cli_store_oc_verifyemail(args):
    return oc_verifyemail(args)


@cli_func
def oc_verifyemail(args, __name__="store oc verifyemail"):
    from ...store.oc import send_reset_email

    ret = send_reset_email(args=args)
    return ret


@cli_entry
def cli_store_oc_checklogin(args):
    return oc_checklogin(args)


@cli_func
def oc_checklogin(args, __name__="store oc checklogin"):
    from ...store.oc import check_login

    ret = check_login(args=args)
    return ret


def add_parser_fn_store_oc(subparsers):
    parser_fn_store_oc = subparsers.add_parser(
        "oc",
        description="Operate on the OpenCRAVAT store",
        help="Operate on the OpenCRAVAT store",
    )
    subparsers = parser_fn_store_oc.add_subparsers(title="Commands", dest="command")
    add_parser_fn_store_oc_publish(subparsers)
    add_parser_fn_store_oc_newaccount(subparsers)
    add_parser_fn_store_oc_changepw(subparsers)
    add_parser_fn_store_oc_resetpw(subparsers)
    add_parser_fn_store_oc_verifyemail(subparsers)
    add_parser_fn_store_oc_checklogin(subparsers)


def add_parser_fn_store_oc_checklogin(subparsers):
    parser_cli_store_oc_checklogin = subparsers.add_parser(
        "checklogin", help="checks username and password."
    )
    parser_cli_store_oc_checklogin.add_argument("username", help="username")
    parser_cli_store_oc_checklogin.add_argument("password", help="password")
    parser_cli_store_oc_checklogin.set_defaults(func=cli_store_oc_checklogin)
    parser_cli_store_oc_checklogin.r_return = "A boolean. TRUE if successful, FALSE if not."  # type: ignore
    parser_cli_store_oc_checklogin.r_examples = [  # type: ignore
        "# Check the username and password of a developer account at the OpenCRAVAT store",
        '#roakvar::store.oc.checklogin(username="user1")',
    ]


def add_parser_fn_store_oc_verifyemail(subparsers):
    parser_cli_store_oc_verifyemail = subparsers.add_parser(
        "verifyemail", help="sends a verification email."
    )
    parser_cli_store_oc_verifyemail.add_argument("username", help="username")
    parser_cli_store_oc_verifyemail.set_defaults(func=cli_store_oc_verifyemail)
    parser_cli_store_oc_verifyemail.r_return = "A boolean. TRUE if successful, FALSE if not."  # type: ignore
    parser_cli_store_oc_verifyemail.r_examples = [  # type: ignore
        "# Sends a verification email for a developer account at the OpenCRAVAT store",
        '#roakvar::store.oc.verifyemail(username="user1")',
    ]


def add_parser_fn_store_oc_resetpw(subparsers):
    parser_cli_store_oc_resetpw = subparsers.add_parser(
        "resetpw", help="resets CRAVAT store account password."
    )
    parser_cli_store_oc_resetpw.add_argument("username", help="username")
    parser_cli_store_oc_resetpw.set_defaults(func=cli_store_oc_resetpw)
    parser_cli_store_oc_resetpw.r_return = "A boolean. TRUE if successful, FALSE if not."  # type: ignore
    parser_cli_store_oc_resetpw.r_examples = [  # type: ignore
        "# Reset the password of a developer account at the OpenCRAVAT store",
        '#roakvar::store.oc.resetpw(username="user1")',
    ]


def add_parser_fn_store_oc_changepw(subparsers):
    parser_cli_store_oc_changepassword = subparsers.add_parser(
        "changepw", help="changes CRAVAT store account password."
    )
    parser_cli_store_oc_changepassword.add_argument("username", help="username")
    parser_cli_store_oc_changepassword.add_argument("cur_pw", help="current password")
    parser_cli_store_oc_changepassword.add_argument("new_pw", help="new password")
    parser_cli_store_oc_changepassword.set_defaults(func=cli_store_oc_changepw)
    parser_cli_store_oc_changepassword.r_return = "A boolean. TRUE if successful, FALSE if not."  # type: ignore
    parser_cli_store_oc_changepassword.r_examples = [  # type: ignore
        "# Change the password of a developer account at the OpenCRAVAT store",
        '#roakvar::store.oc.changepw(username="user1", cur_pw="password", new_pw="newpassword")',
    ]


def add_parser_fn_store_oc_newaccount(subparsers):
    parser_cli_store_oc_createaccount = subparsers.add_parser(
        "newaccount", help="creates a CRAVAT store developer account."
    )
    parser_cli_store_oc_createaccount.add_argument(
        "username", help="use your email as your username."
    )
    parser_cli_store_oc_createaccount.add_argument(
        "password", help="this is your password."
    )
    parser_cli_store_oc_createaccount.set_defaults(func=cli_store_oc_newaccount)
    parser_cli_store_oc_createaccount.r_return = "A boolean. TRUE if successful, FALSE if not."  # type: ignore
    parser_cli_store_oc_createaccount.r_examples = [  # type: ignore
        "# Create a developer account at the OpenCRAVAT store",
        '#roakvar::store.oc.newaccount(username="user1", password="password")',
    ]


def add_parser_fn_store_oc_publish(subparsers):
    parser_cli_store_oc_publish = subparsers.add_parser(
        "publish", help="publish a module"
    )
    parser_cli_store_oc_publish.add_argument("module", help="module to publish")
    data_group = parser_cli_store_oc_publish.add_mutually_exclusive_group(required=True)
    data_group.add_argument(
        "-d",
        "--data",
        action="store_true",
        default=False,
        help="publishes module with data.",
    )
    data_group.add_argument(
        "-c", "--code", action="store_true", help="publishes module without data."
    )
    parser_cli_store_oc_publish.add_argument(
        "-u", "--user", default=None, help="user to publish as. Typically your email."
    )
    parser_cli_store_oc_publish.add_argument(
        "-p",
        "--password",
        default=None,
        help="password for the user. Enter at prompt if missing.",
    )
    parser_cli_store_oc_publish.add_argument(
        "--force-yes",
        default=False,
        action="store_true",
        help="overrides yes to overwrite question",
    )
    parser_cli_store_oc_publish.add_argument(
        "--overwrite",
        default=False,
        action="store_true",
        help="overwrites a published module/version",
    )
    parser_cli_store_oc_publish.add_argument(
        "--md", default=None, help="Specify the root directory of OpenCRAVAT modules"
    )
    parser_cli_store_oc_publish.add_argument(
        "--quiet", action="store_true", default=None, help="run quietly"
    )
    parser_cli_store_oc_publish.set_defaults(func=cli_store_oc_publish)
    parser_cli_store_oc_publish.r_return = "A boolean. TRUE if successful, FALSE if not."  # type: ignore
    parser_cli_store_oc_publish.r_examples = [  # type: ignore
        "# Publish a module to the OpenCRAVAT store",
        '#roakvar::store.oc.publish(module="clinvar", user="user1", password="password", code=TRUE)',
    ]
