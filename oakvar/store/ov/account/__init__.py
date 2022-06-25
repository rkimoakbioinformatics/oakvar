from typing import Tuple


def check_email_pw(args=None) -> Tuple[str, str]:
    from ....util.util import is_valid_email
    from ....util.util import is_valid_pw
    from ....exceptions import WrongInput

    if not args:
        raise WrongInput()
    email = args.get("email")
    pw = args.get("pw")
    if not email or not pw:
        raise WrongInput("no email or password")
    if not is_valid_email(email):
        raise WrongInput("invalid email")
    if not is_valid_pw(pw):
        raise WrongInput("invalid password")
    return email, pw


def create(args=None) -> bool:
    from requests import get
    from ....system import get_system_conf
    from ....util.util import quiet_print

    email, pw = check_email_pw(args=args)
    if not email:
        return False
    sys_conf = get_system_conf()
    store_url = sys_conf["store_url"]
    create_account_url = store_url + "/account/create"
    params = {
        "email": email,
        "pw": pw,
    }
    try:
        r = get(create_account_url, params=params)
        status_code = r.status_code
        if status_code == 200:
            quiet_print(f"User already exists.", args=args)
            return True
        elif status_code == 202:
            quiet_print(f"Check your inbox for a verification email.", args=args)
            return True
        elif status_code == 201:
            quiet_print(
                f"Account has been created. Check your inbox for a verification email.",
                args=args,
            )
            return True
        else:
            quiet_print(
                f"Creating an account failed. The reason was:\n{r.reason}", args=args
            )
            return False
    except Exception as e:
        quiet_print(f"Creating an account failed. The reason was: {e}", args=args)
        return False


def delete_account(args=None) -> bool:
    from requests import get
    from ....system import get_system_conf
    from ....util.util import quiet_print

    if not args:
        return False
    email, pw = check_email_pw(args=args)
    sys_conf = get_system_conf()
    store_url = sys_conf["store_url"]
    delete_account_url = store_url + "/account/delete"
    params = {
        "email": email,
        "pw": pw,
    }
    r = get(delete_account_url, params=params)
    if r.status_code == 200:
        quiet_print(
            f"Account has been deleted.",
            args=args,
        )
        return True
    else:
        quiet_print(
            f"Deleting the account failed. The reason was: {r.reason}", args=args
        )
        return False


def save(email: str, pw: str, args={}):
    from ....system import get_user_conf
    from ....system import get_user_conf_path
    from ....system.consts import ov_store_email_key
    from ....system.consts import ov_store_pw_key
    from ....system import save_user_conf
    from ....util.util import quiet_print

    user_conf = get_user_conf()
    user_conf_path = get_user_conf_path()
    user_conf[ov_store_email_key] = email
    user_conf[ov_store_pw_key] = pw
    save_user_conf(user_conf)
    quiet_print(f"Email and password saved: {user_conf_path}", args=args)


def check(args=None) -> bool:
    from requests import get
    from ....system import get_system_conf

    email, pw = check_email_pw(args=args)
    if not email:
        return False
    sys_conf = get_system_conf()
    store_url = sys_conf["store_url"]
    check_account_url = store_url + "/account/check"
    params = {
        "email": email,
        "pw": pw,
    }
    try:
        r = get(check_account_url, params=params)
        status_code = r.status_code
        if status_code == 200:
            return True
        else:
            return False
    except:
        return False
