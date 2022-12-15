def oc_publish(args, __name__="store oc publish"):
    from getpass import getpass
    from ...lib.system import get_system_conf
    from ...lib.store.oc import publish_module
    from ...lib.system import consts

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


def oc_newaccount(args, __name__="store oc newaccount"):
    from ...lib.store.oc import create_account

    ret = create_account(args=args)
    return ret


def oc_changepw(args, __name__="store oc changepw"):
    from ...lib.store.oc import change_password

    ret = change_password(args=args)
    return ret


def oc_resetpw(args, __name__="store oc resetpw"):
    from ...lib.store.oc import send_reset_email

    ret = send_reset_email(args=args)
    return ret


def oc_verifyemail(args, __name__="store oc verifyemail"):
    from ...lib.store.oc import send_reset_email

    ret = send_reset_email(args=args)
    return ret


def oc_checklogin(args, __name__="store oc checklogin"):
    from ...lib.store.oc import check_login

    ret = check_login(args=args)
    return ret

