from typing import Tuple


def get_valid_email_pw(args=None) -> Tuple:
    from ....util.util import is_valid_email
    from ....util.util import is_valid_pw
    from ....exceptions import WrongInput
    from ....system import get_user_conf
    from ....store.consts import ov_store_email_key
    from ....store.consts import ov_store_pw_key

    if not args:
        raise WrongInput()
    email = args.get("email")
    pw = args.get("pw")
    newpw = args.get("newpw")
    if not email or not pw:
        user_conf = get_user_conf()
        if not email:
            email = user_conf.get(ov_store_email_key)
        if not pw:
            pw = user_conf.get(ov_store_pw_key)
    if not email or not pw:
        raise WrongInput("no email or password")
    if not is_valid_email(email):
        raise WrongInput("invalid email")
    if not is_valid_pw(pw):
        raise WrongInput("invalid password")
    if newpw:
        if not is_valid_pw(newpw):
            raise WrongInput("invalid new password")
    if args.get("newpw"):
        return email, pw, newpw
    else:
        return email, pw


def create(args=None) -> bool:
    from requests import get
    from ....system import get_system_conf
    from ....util.util import quiet_print

    email, pw = get_valid_email_pw(args=args)
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
        if status_code == 403:
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


def delete(args={}) -> bool:
    from os.path import exists
    from json import load
    from requests import post
    from ...ov import get_store_url
    from ....util.util import quiet_print

    token_path = get_id_token_path()
    if not exists(token_path):
        if not login(args=args):
            quiet_print(f"log in first", args=args)
            return False
    with open(token_path) as f:
        id_token = f.readline().strip()
    store_url = get_store_url()
    url = store_url + "/account/delete"
    params = {"idToken": id_token}
    print(f"@ params={params}")
    r = post(url, data=params)
    status_code = r.status_code
    if status_code == 200:
        quiet_print(f"success", args=args)
        return True
    else:
        quiet_print(f"fail. {r.text}", args=args)
        return False


def check(args={}) -> bool:
    from requests import get
    from ....util.util import quiet_print
    from ...ov import get_store_url

    email, pw = get_valid_email_pw(args=args)
    if not email:
        quiet_print(f"invalid", args=args)
        return False
    store_url = get_store_url()
    check_account_url = store_url + "/account/check"
    params = {
        "email": email,
        "pw": pw,
    }
    try:
        r = get(check_account_url, params=params)
        status_code = r.status_code
        if status_code == 200:
            quiet_print(f"valid", args=args)
            return True
        else:
            quiet_print(f"invalid", args=args)
            return False
    except:
        quiet_print(f"invalid", args=args)
        return False


def change(args={}) -> bool:
    from requests import get
    from ....system import get_system_conf
    from ....util.util import quiet_print

    email, pw, newpw = get_valid_email_pw(args=args)
    if not email:
        quiet_print(f"invalid", args=args)
        return False
    sys_conf = get_system_conf()
    store_url = sys_conf["store_url"]
    change_account_url = store_url + "/account/change"
    params = {"email": email, "pw": pw, "newpw": newpw}
    try:
        r = get(change_account_url, params=params)
        status_code = r.status_code
        if status_code == 200:
            quiet_print(f"success", args=args)
            return True
        elif status_code == 202:
            quiet_print(f"unverified email", args=args)
            return False
        elif status_code == 401:
            quiet_print(f"authorization failure", args=args)
            return False
        else:
            quiet_print(f"fail", args=args)
            return False
    except:
        quiet_print(f"server error", args=args)
        return False


def login(args={}) -> bool:
    from requests import post
    from ....system import get_system_conf
    from ....util.util import quiet_print

    email, pw = get_valid_email_pw(args=args)
    sys_conf = get_system_conf()
    store_url = sys_conf["store_url"]
    change_account_url = store_url + "/account/login"
    params = {"email": email, "pw": pw}
    try:
        r = post(change_account_url, data=params)
        status_code = r.status_code
        if status_code == 200:
            save_id_token(r.json())
            quiet_print(f"success", args=args)
            return True
        else:
            quiet_print(f"fail. {r.text}", args=args)
            return False
    except:
        quiet_print(f"server error", args=args)
        return False


def get_id_token_path():
    from os.path import join
    from ....system import get_user_conf_dir
    from ....store.consts import ov_store_id_token_fname

    user_conf_dir = get_user_conf_dir()
    token_path = join(user_conf_dir, ov_store_id_token_fname)
    return token_path


def save_id_token(id_token):
    from json import dump

    token_path = get_id_token_path()
    print(f"@ token_path={token_path}")
    with open(token_path, "w") as wf:
        dump(id_token, wf)


# def save(email: str, pw: str, args={}):
#    from ....system import get_user_conf
#    from ....system import get_user_conf_path
#    from ....store.consts import ov_store_email_key
#    from ....store.consts import ov_store_pw_key
#    from ....system import save_user_conf
#    from ....util.util import quiet_print
#
#    user_conf = get_user_conf()
#    user_conf_path = get_user_conf_path()
#    user_conf[ov_store_email_key] = email
#    user_conf[ov_store_pw_key] = pw
#    save_user_conf(user_conf)
#    quiet_print(f"Email and password saved: {user_conf_path}", args=args)


# def delete(args=None) -> bool:
#    from requests import get
#    from ....system import get_system_conf
#    from ....util.util import quiet_print
#
#    if not args:
#        return False
#    email, pw = get_valid_email_pw(args=args)
#    sys_conf = get_system_conf()
#    store_url = sys_conf["store_url"]
#    delete_account_url = store_url + "/account/delete"
#    params = {
#        "email": email,
#        "pw": pw,
#    }
#    r = get(delete_account_url, params=params)
#    if r.status_code == 200:
#        quiet_print(
#            f"Account has been deleted.",
#            args=args,
#        )
#        return True
#    else:
#        quiet_print(
#            f"Deleting the account failed. The reason was: {r.reason}", args=args
#        )
#        return False
