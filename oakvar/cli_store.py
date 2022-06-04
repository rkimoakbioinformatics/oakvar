from .decorators import cli_func
from .decorators import cli_entry


@cli_entry
def cli_ov_store_publish(args):
    return ov_store_publish(args)


@cli_func
def ov_store_publish(args):
    from .sysadmin import get_system_conf
    from .admin_util import publish_module
    from getpass import getpass
    if args.get("md"):
        from . import sysadmin_const
        sysadmin_const.custom_modules_dir = args.get("md")
    sys_conf = get_system_conf()
    if args.get("user") is None:
        if "publish_username" in sys_conf:
            args["user"] = sys_conf["publish_username"]
        else:
            args["user"] = input("Username: ")
    if args.get("password") is None:
        if "publish_password" in sys_conf:
            args["password"] = sys_conf["publish_password"]
        else:
            args["password"] = getpass()
    return publish_module(args.get("module"),
                          args.get("user"),
                          args.get("password"),
                          overwrite=args.get("overwrite"),
                          include_data=args.get("data"),
                          quiet=args.get("quiet"))


@cli_entry
def cli_ov_store_createaccount(args):
    return ov_store_createaccount(args)


@cli_func
def ov_store_createaccount(args):
    from .admin_util import create_account
    ret = create_account(args.get("username"), args.get("password"))
    return ret


@cli_entry
def cli_ov_store_changepassword(args):
    return ov_store_changepassword(args)


@cli_func
def ov_store_changepassword(args):
    from .admin_util import change_password
    ret = change_password(args.get("username"), args.get("current_password"),
                          args.get("new_password"))
    return ret


@cli_entry
def cli_ov_store_resetpassword(args):
    return ov_store_resetpassword(args)


@cli_func
def ov_store_resetpassword(args):
    from .admin_util import send_reset_email
    ret = send_reset_email(args.get("username"), args=args)
    return ret


@cli_entry
def cli_ov_store_verifyemail(args):
    return ov_store_verifyemail(args)


@cli_func
def ov_store_verifyemail(args):
    from .admin_util import send_verify_email
    ret = send_verify_email(args.get("username"), args=args)
    return ret


@cli_entry
def cli_ov_store_checklogin(args):
    return ov_store_verifyemail(args)


@cli_func
def ov_store_checklogin(args):
    from .admin_util import check_login
    ret = check_login(args.get("username"), args.get("password"))
    return ret


def get_parser_fn_store():
    from argparse import ArgumentParser, RawDescriptionHelpFormatter
    parser_fn_store = ArgumentParser(
        formatter_class=RawDescriptionHelpFormatter)
    _subparsers = parser_fn_store.add_subparsers(title="Commands")

    # publish
    parser_cli_store_publish = _subparsers.add_parser(
        "publish", help="publishes a module.")
    parser_cli_store_publish.add_argument("module", help="module to publish")
    data_group = parser_cli_store_publish.add_mutually_exclusive_group(
        required=True)
    data_group.add_argument(
        "-d",
        "--data",
        action="store_true",
        default=False,
        help="publishes module with data.",
    )
    data_group.add_argument("-c",
                            "--code",
                            action="store_true",
                            help="publishes module without data.")
    parser_cli_store_publish.add_argument(
        "-u",
        "--user",
        default=None,
        help="user to publish as. Typically your email.")
    parser_cli_store_publish.add_argument(
        "-p",
        "--password",
        default=None,
        help="password for the user. Enter at prompt if missing.",
    )
    parser_cli_store_publish.add_argument(
        "--force-yes",
        default=False,
        action="store_true",
        help="overrides yes to overwrite question",
    )
    parser_cli_store_publish.add_argument(
        "--overwrite",
        default=False,
        action="store_true",
        help="overwrites a published module/version",
    )
    parser_cli_store_publish.add_argument(
        "--md",
        default=None,
        help="Specify the root directory of OakVar modules")
    parser_cli_store_publish.add_argument("--quiet",
                                          default=True,
                                          help="Run quietly")
    parser_cli_store_publish.set_defaults(func=cli_ov_store_publish)
    parser_cli_store_publish.r_return = "A boolean. A boolean. TRUE if successful, FALSE if not"  # type: ignore
    parser_cli_store_publish.r_examples = [  # type: ignore
        "# Publish \"customannot\" module to the store",
        "ov.store.publish(module=\"customannot\", user=\"user1\", password=\"password\")"
    ]

    # create-account
    parser_cli_store_createaccount = _subparsers.add_parser(
        "createaccount", help="creates a OakVar store developer account.")
    parser_cli_store_createaccount.add_argument(
        "username", help="use your email as your username.")
    parser_cli_store_createaccount.add_argument("password",
                                                help="this is your password.")
    parser_cli_store_createaccount.add_argument("--quiet",
                                                default=True,
                                                help="Run quietly")
    parser_cli_store_createaccount.set_defaults(func=cli_ov_store_createaccount)
    parser_cli_store_createaccount.r_return = "A string. Response from the store server"  # type: ignore
    parser_cli_store_createaccount.r_examples = [  # type: ignore
        "# Create a store account",
        "ov.store.newaccount(username=\"user1\", password=\"password\")"
    ]

    # change-password
    parser_cli_store_changepassword = _subparsers.add_parser(
        "changepassword", help="changes OakVar store account password.")
    parser_cli_store_changepassword.add_argument("username", help="username")
    parser_cli_store_changepassword.add_argument("current_password",
                                                 help="current password")
    parser_cli_store_changepassword.add_argument("new_password",
                                                 help="new password")
    parser_cli_store_changepassword.add_argument("--quiet",
                                                 default=True,
                                                 help="Run quietly")
    parser_cli_store_changepassword.set_defaults(func=cli_ov_store_changepassword)
    parser_cli_store_changepassword.r_return = "A string. Response from the store server"  # type: ignore
    parser_cli_store_changepassword.r_examples = [  # type: ignore
        "# Change the password of a store account",
        "ov.store.changepassword(username=\"user1\", current_password=\"password\", new_password=\"newpassword\")"
    ]

    # reset-password
    parser_cli_store_resetpassword = _subparsers.add_parser(
        "resetpassword", help="resets OakVar store account password.")
    parser_cli_store_resetpassword.add_argument("--quiet",
                                                default=True,
                                                help="Run quietly")
    parser_cli_store_resetpassword.add_argument("username", help="username")
    parser_cli_store_resetpassword.set_defaults(func=cli_ov_store_resetpassword)
    parser_cli_store_resetpassword.r_return = "A boolean. A boolean. TRUE if successful, FALSE if not"  # type: ignore
    parser_cli_store_resetpassword.r_examples = [  # type: ignore
        "# Ask the store to send an email to reset the password of a store account",
        "ov.store.resetpassword(username=\"user1\")"
    ]

    # verify-email
    parser_cli_store_verifyemail = _subparsers.add_parser(
        "verifyemail", help="sends a verification email.")
    parser_cli_store_verifyemail.add_argument("username", help="username")
    parser_cli_store_verifyemail.add_argument("--quiet",
                                              default=True,
                                              help="Run quietly")
    parser_cli_store_verifyemail.set_defaults(func=cli_ov_store_verifyemail)
    parser_cli_store_verifyemail.r_return = "`NULL`"  # type: ignore
    parser_cli_store_verifyemail.r_examples = [  # type: ignore
        "# Ask the store to send an email to verify the email of a user account",
        "ov.store.verifyemail(username=\"user1\")"
    ]

    # check-login
    parser_cli_store_checklogin = _subparsers.add_parser(
        "checklogin", help="checks username and password.")
    parser_cli_store_checklogin.add_argument("username", help="username")
    parser_cli_store_checklogin.add_argument("password", help="password")
    parser_cli_store_checklogin.add_argument("--quiet",
                                             default=True,
                                             help="Run quietly")
    parser_cli_store_checklogin.set_defaults(func=cli_ov_store_checklogin)
    parser_cli_store_checklogin.r_return = "A boolean. A boolean. TRUE if successful, FALSE if not"  # type: ignore
    parser_cli_store_checklogin.r_examples = [  # type: ignore
        "# Check if the login information of a user is correct",
        "ov.store.checklogin(username=\"user1\", password=\"password\")"
    ]
    return parser_fn_store
