def fn_store_publish(args):
    from .admin_util import get_system_conf, publish_module
    from .util import get_dict_from_namespace
    from .constants import custom_modules_dir
    from getpass import getpass
    args = get_dict_from_namespace(args)
    if args["md"] is not None:
        custom_modules_dir = args["md"]
    sys_conf = get_system_conf()
    if args["user"] is None:
        if "publish_username" in sys_conf:
            args["user"] = sys_conf["publish_username"]
        else:
            args["user"] = input("Username: ")
    if args["password"] is None:
        if "publish_password" in sys_conf:
            args["password"] = sys_conf["publish_password"]
        else:
            args["password"] = getpass()
    publish_module(
        args["module"],
        args["user"],
        args["password"],
        overwrite=args["overwrite"],
        include_data=args["data"],
    )

def fn_store_newaccount(args):
    from .admin_util import create_account
    from .util import get_dict_from_namespace
    args = get_dict_from_namespace(args)
    ret = create_account(args["username"], args["password"])
    return ret

def fn_store_changepassword(args):
    from .admin_util import change_password
    from .util import get_dict_from_namespace
    args = get_dict_from_namespace(args)
    ret = change_password(args["username"], args["current_password"], args["new_password"])
    return ret


def fn_store_resetpassword(args):
    from .admin_util import send_reset_email
    from .util import get_dict_from_namespace
    args = get_dict_from_namespace(args)
    ret = send_reset_email(args["username"])
    return ret


def fn_store_verifyemail(args):
    from .admin_util import send_verify_email
    from .util import get_dict_from_namespace
    args = get_dict_from_namespace(args)
    ret = send_verify_email(args["username"])
    return ret

def fn_store_checklogin(args):
    from .admin_util import check_login
    from .util import get_dict_from_namespace
    args = get_dict_from_namespace(args)
    ret = check_login(args.username, args["password"])
    return ret

from argparse import ArgumentParser, RawDescriptionHelpFormatter
parser_fn_store = ArgumentParser(formatter_class=RawDescriptionHelpFormatter)
_subparsers = parser_fn_store.add_subparsers(title="Commands")

# publish
parser_fn_store_publish = _subparsers.add_parser("publish", help="publishes a module.")
parser_fn_store_publish.add_argument("module", help="module to publish")
data_group = parser_fn_store_publish.add_mutually_exclusive_group(required=True)
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
parser_fn_store_publish.add_argument(
    "-u", "--user", default=None, help="user to publish as. Typically your email."
)
parser_fn_store_publish.add_argument(
    "-p",
    "--password",
    default=None,
    help="password for the user. Enter at prompt if missing.",
)
parser_fn_store_publish.add_argument(
    "--force-yes",
    default=False,
    action="store_true",
    help="overrides yes to overwrite question",
)
parser_fn_store_publish.add_argument(
    "--overwrite",
    default=False,
    action="store_true",
    help="overwrites a published module/version",
)
parser_fn_store_publish.add_argument(
    "--md", default=None, help="Specify the root directory of OakVar modules"
)
parser_fn_store_publish.set_defaults(func=fn_store_publish)

# create-account
parser_fn_store_newaccount = _subparsers.add_parser(
    "createaccount", help="creates a OakVar store developer account."
)
parser_fn_store_newaccount.add_argument("username", help="use your email as your username.")
parser_fn_store_newaccount.add_argument("password", help="this is your password.")
parser_fn_store_newaccount.set_defaults(func=fn_store_newaccount)

# change-password
parser_fn_store_changepassword = _subparsers.add_parser(
    "changepassword", help="changes OakVar store account password."
)
parser_fn_store_changepassword.add_argument("username", help="username")
parser_fn_store_changepassword.add_argument("current_password", help="current password")
parser_fn_store_changepassword.add_argument("new_password", help="new password")
parser_fn_store_changepassword.set_defaults(func=fn_store_changepassword)

# reset-password
parser_fn_store_resetpassword = _subparsers.add_parser(
    "resetpassword", help="resets OakVar store account password."
)
parser_fn_store_resetpassword.add_argument("username", help="username")
parser_fn_store_resetpassword.set_defaults(func=fn_store_resetpassword)

# verify-email
parser_fn_store_verifyemail = _subparsers.add_parser(
    "verifyemail", help="sends a verification email."
)
parser_fn_store_verifyemail.add_argument("username", help="username")
parser_fn_store_verifyemail.set_defaults(func=fn_store_verifyemail)

# check-login
parser_fn_store_checklogin = _subparsers.add_parser(
    "checklogin", help="checks username and password."
)
parser_fn_store_checklogin.add_argument("username", help="username")
parser_fn_store_checklogin.add_argument("password", help="password")
parser_fn_store_checklogin.set_defaults(func=fn_store_checklogin)

