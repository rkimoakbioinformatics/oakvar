from typing import Tuple
from typing import Optional


def get_valid_email_pw(args=None, pwconfirm=False) -> Tuple:
    from ....util.util import email_is_valid
    from ....util.util import pw_is_valid
    from ....exceptions import WrongInput
    from ....system import get_user_conf
    from ....store.consts import ov_store_email_key
    from ....store.consts import ov_store_pw_key
    from getpass import getpass

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
    if not email:
        email = input("Email: ")
    if not pw:
        if pwconfirm:
            pwagain = None
            while not pw or pw != pwagain:
                while not pw:
                    pw = getpass("Password (alphabets, numbers, and !?&@-+): ")
                pwagain = getpass("Confirm password: ")
                if pw != pwagain:
                    print("Password mismatch")
                    pw = None
                    pwagain = None
        else:
            pw = getpass()
    if not email or not pw:
        raise WrongInput("no email or password")
    if not email_is_valid(email):
        raise WrongInput("invalid email")
    if not pw_is_valid(pw):
        raise WrongInput("invalid password")
    if newpw:
        if not pw_is_valid(newpw):
            raise WrongInput("invalid new password")
    if args.get("newpw"):
        return email, pw, newpw
    else:
        return email, pw


def create(email=None, pw=None, args={}, quiet=None) -> bool:
    from requests import post
    from ....system import get_system_conf
    from ....util.util import quiet_print
    from ....util.util import get_email_pw_from_input

    if not email or not pw:
        email = args.get("email")
        pw = args.get("pw")
        if not email or not pw:
            email, pw = get_email_pw_from_input(email=email, pw=pw, pwconfirm=True)
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
        r = post(create_account_url, data=params)
        status_code = r.status_code
        if status_code == 403:
            quiet_print(f"User already exists.", args=args, quiet=quiet)
            return True
        elif status_code == 202:
            quiet_print(
                f"Check your inbox for a verification email.", args=args, quiet=quiet
            )
            return True
        elif status_code == 201:
            quiet_print(
                f"Account has been created. Check your inbox for a verification email.",
                args=args,
                quiet=quiet,
            )
            return True
        else:
            quiet_print(f"fail. {r.text}", args=args, quiet=quiet)
            return False
    except Exception as e:
        quiet_print(f"fail. {e}", args=args, quiet=quiet)
        return False


def delete(args={}) -> bool:
    from requests import post
    from ...ov import get_store_url
    from ....util.util import quiet_print

    token_set = get_token_set()
    if not token_set:
        quiet_print(f"log in first", args=args)
        return False
    store_url = get_store_url()
    url = store_url + "/account/delete"
    params = {"idToken": token_set["idToken"]}
    r = post(url, data=params)
    status_code = r.status_code
    if status_code == 200:
        quiet_print(f"success", args=args)
        return True
    else:
        quiet_print(f"fail. {r.text}", args=args)
        return False


def check(args={}) -> bool:
    from ....util.util import quiet_print

    id_token = get_id_token()
    if not id_token:
        quiet_print(f"not logged in", args=args)
        return False
    valid, expired = id_token_is_valid()
    if valid:
        if expired:
            refresh_token_set()
        token_set = get_token_set() or {}
        email = token_set["email"]
        quiet_print(f"logged in as {email}", args=args)
        return True
    else:
        quiet_print(f"not logged in", args=args)
        return False


def reset(args={}) -> bool:
    from ....util.util import quiet_print
    from ...ov import get_store_url
    from ....util.util import email_is_valid
    from requests import post

    email = args.get("email")
    if not email:
        return False
    if not email_is_valid(email):
        quiet_print(f"invalid email", args=args)
        return False
    url = get_store_url() + "/account/reset"
    params = {"email": email}
    res = post(url, data=params)
    if res.status_code == 200:
        quiet_print("success", args=args)
        return True
    else:
        quiet_print(f"fail. {res.text}", args=args)
        return False


def get_email_from_token_set() -> Optional[str]:
    token_set = get_token_set() or {}
    email = token_set.get("email")
    return email


def login(email=None, pw=None, args={}, quiet=None) -> bool:
    from requests import post
    from ....util.util import quiet_print
    from ....util.util import get_email_from_args
    from ...ov import get_store_url

    id_token = get_id_token()
    if id_token:
        if check(args={"quiet": True}):
            token_set_email = get_email_from_token_set()
            args_email = get_email_from_args(args=args)
            if email:
                if token_set_email == email:
                    quiet_print(f"logged in as {email}", args=args, quiet=quiet)
                    return True
            elif args_email:
                if token_set_email == args_email:
                    quiet_print(f"logged in as {args_email}", args=args, quiet=quiet)
                    return True
    if not email or not pw:
        email, pw = get_valid_email_pw(args=args)
    change_account_url = get_store_url() + "/account/login"
    params = {"email": email, "pw": pw}
    try:
        r = post(change_account_url, data=params)
        status_code = r.status_code
        if status_code == 200:
            save_token_set(r.json())
            quiet_print(f"logged in as {email}", args=args, quiet=quiet)
            return True
        else:
            quiet_print(f"fail. {r.text}", args=args, quiet=quiet)
            return False
    except:
        quiet_print(f"server error", args=args, quiet=quiet)
        return False


def get_token_set_path():
    from os.path import join
    from ....system import get_user_conf_dir
    from ....store.consts import ov_store_id_token_fname

    user_conf_dir = get_user_conf_dir()
    token_path = join(user_conf_dir, ov_store_id_token_fname)
    return token_path


def get_token_set() -> Optional[dict]:
    from os.path import exists
    from json import load

    token_set_path = get_token_set_path()
    if not token_set_path or not exists(token_set_path):
        return None
    with open(token_set_path) as f:
        return load(f)


def get_id_token() -> Optional[str]:
    token_set = get_token_set()
    if not token_set:
        return None
    else:
        return token_set["idToken"]


def get_refresh_token() -> Optional[str]:
    token_set = get_token_set()
    if not token_set:
        return None
    else:
        return token_set["refreshToken"]


def save_token_set(token_set: dict):
    from json import dump

    for k in list(token_set.keys()):
        if "_" in k:
            words = k.split("_")
            newk = words[0] + words[1].capitalize()
            token_set[newk] = token_set[k]
            del token_set[k]
    token_path = get_token_set_path()
    with open(token_path, "w") as wf:
        dump(token_set, wf)


def delete_id_token(args={}):
    from os import remove
    from os.path import exists
    from ....util.util import quiet_print

    token_path = get_token_set_path()
    if exists(token_path):
        remove(token_path)
        return True
    else:
        quiet_print(f"not logged in", args=args)
        return False


def id_token_is_valid() -> Tuple[bool, bool]:  # valid, expired
    from ...ov import get_store_url
    from requests import post

    id_token = get_id_token()
    if not id_token:
        return False, True
    params = {"idToken": id_token}
    url = get_store_url() + "/account/id_token_verified"
    res = post(url, data=params)
    st = res.status_code
    if st == 460:  # valid but expired
        return True, True
    elif res.status_code == 200:
        return True, False
    else:
        return False, True


def refresh_token_set() -> bool:
    from ...ov import get_store_url
    from requests import post

    refresh_token = get_refresh_token()
    url = get_store_url() + "/account/refresh"
    params = {"refreshToken": refresh_token}
    res = post(url, data=params)
    if res.status_code == 200:
        token_set = get_token_set()
        if token_set:
            j = res.json()
            id_token = j["id_token"]
            refresh_token = j["refresh_token"]
            token_set["idToken"] = id_token
            token_set["refreshToken"] = refresh_token
            save_token_set(token_set)
            return True
        else:
            return False
    else:
        return False


def change(args={}) -> bool:
    from ....util.util import quiet_print
    from requests import post
    from ...ov import get_store_url
    from getpass import getpass
    from ....util.util import pw_is_valid

    id_token = get_id_token()
    if not id_token:
        quiet_print(f"not logged in", args=args)
        return False
    valid, expired = id_token_is_valid()
    if valid and not expired:
        id_token = None
        refresh_token = get_refresh_token()
        if refresh_token:
            if refresh_token_set():
                token_set = get_token_set()
                if token_set:
                    id_token = token_set["id_token"]
        if not id_token:
            quiet_print(f"not logged in", args=args)
            return False
    newpw = args.get("newpw")
    if not newpw:
        newpw = ""
        while not pw_is_valid(newpw):
            newpw = getpass("New password: ")
    refresh_token = get_refresh_token()
    url = get_store_url() + "/account/change"
    params = {"idToken": id_token, "refreshToken": refresh_token, "newpw": newpw}
    res = post(url, data=params)
    status_code = res.status_code
    if status_code != 200:
        quiet_print(f"{res.text}", args=args)
        return False
    else:
        token_set = get_token_set()
        if not token_set:
            quiet_print(f"password changed but re-login failed")
            return False
        email = token_set["email"]
        args["email"] = email
        args["pw"] = newpw
        if login(args=args):
            return True
        else:
            quiet_print(f"password changed but re-login failed", args=args)
            return True


def logout(args={}) -> bool:
    from ....util.util import quiet_print

    ret = delete_id_token(args=args)
    if ret:
        quiet_print(f"success", args=args)
    return ret


def get_current_id_token(args={}) -> Optional[str]:
    token_set = get_current_token_set(args=args)
    if token_set:
        return token_set["idToken"]
    else:
        return None


def get_current_token_set(args={}) -> Optional[dict]:
    token_set = None
    token_set = get_token_set()
    newargs = args.copy()
    newargs["quiet"] = True
    if token_set:
        valid, expired = id_token_is_valid()
        if not valid:
            token_set = None
        elif expired:
            refresh_token_set()
            token_set = get_token_set()
    if not token_set:
        login(args=newargs)
        token_set = get_token_set()
    return token_set


def token_set_exists() -> bool:
    token_set = get_token_set()
    if token_set:
        return True
    else:
        return False


def delete_token_set():
    from os.path import exists
    from os import remove

    token_set_path = get_token_set_path()
    if exists(token_set_path):
        remove(token_set_path)


def get_email_pw_from_settings(
    email=None, pw=None, conf=None, args={}
) -> Optional[Tuple[str, str]]:
    from ...consts import ov_store_email_key
    from ...consts import ov_store_pw_key
    from ....system import get_user_conf

    # if not given directly, check direct arguments.
    if not email or not pw:
        email = args.get("email")
        pw = args.get("pw")
    # if not, use conf.
    if (not email or not pw) and conf:
        email = conf.get(ov_store_email_key)
        pw = conf.get(ov_store_pw_key)
    # if not, oakvar.yml
    user_conf = get_user_conf()
    if ov_store_email_key in user_conf and ov_store_pw_key in user_conf:
        email = user_conf[ov_store_email_key]
        pw = user_conf[ov_store_pw_key]
    if email and pw:
        return email, pw
    else:
        return None


def emailpw_are_valid(emailpw: Tuple[str, str]) -> bool:
    from ....util.util import email_is_valid
    from ....util.util import pw_is_valid

    email = emailpw[0]
    pw = emailpw[1]
    return email_is_valid(email) and pw_is_valid(pw)


def email_is_verified(email: str, args={}, quiet=None) -> bool:
    from ....util.util import quiet_print
    from ...ov import get_store_url
    from requests import post

    url = get_store_url() + "/account/email_verified"
    params = {"email": email}
    res = post(url, data=params)
    if res.status_code == 200:
        return True
    elif res.status_code == 404:
        quiet_print(f"user not found", args=args, quiet=quiet)
        return False
    else:
        quiet_print(f"email not verified. {res.text}", args=args, quiet=quiet)
        return False


def wait_for_email_verified(email: str, args={}, quiet=None):
    from ....system import show_email_verify_action_banner

    while True:
        if email_is_verified(email, args=args, quiet=quiet):
            break
        show_email_verify_action_banner()
        input()


def login_with_token_set(args={}) -> bool:
    token_set = get_token_set()
    if token_set:
        email = token_set["email"]
        correct, expired = id_token_is_valid()
        email_verified = email_is_verified(email, args=args)
        if not email_verified:
            delete_token_set()
        else:
            if correct:
                if expired:
                    if refresh_token_set():
                        return True
                    else:
                        delete_token_set()
                else:
                    return True
            else:
                delete_token_set()
    return False


def login_with_email_pw(email=None, pw=None, args={}, conf={}) -> bool:
    emailpw = get_email_pw_from_settings(email=email, pw=pw, args=args, conf=conf)
    if emailpw:
        if emailpw_are_valid(emailpw):
            email = emailpw[0]
            pw = emailpw[1]
            while True:
                if create(email=email, pw=pw, quiet=False):
                    break
            wait_for_email_verified(email, args=args)
            login(email=email, pw=pw, args=args)
            return True
    return False


def total_login(email=None, pw=None, args={}, conf=None) -> bool:
    from ....util.util import get_email_pw_from_input
    from ....system import show_no_user_account_prelude

    if login_with_token_set(args=args):
        return True
    if login_with_email_pw(email=email, pw=pw, args=args, conf=conf):
        return True
    # if not already logged in nor email and pw in settings did not work, get manual input.
    show_no_user_account_prelude()
    while True:
        email, pw = get_email_pw_from_input(pwconfirm=True)
        if create(email=email, pw=pw, quiet=False):
            break
    wait_for_email_verified(email, args=args)
    ret = login(email=email, pw=pw, args=args)
    return ret


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

# def change(args={}) -> bool:
#    from requests import get
#    from ....system import get_system_conf
#    from ....util.util import quiet_print
#
#    email, pw, newpw = get_valid_email_pw(args=args)
#    if not email:
#        quiet_print(f"invalid", args=args)
#        return False
#    sys_conf = get_system_conf()
#    store_url = sys_conf["store_url"]
#    change_account_url = store_url + "/account/change"
#    params = {"email": email, "pw": pw, "newpw": newpw}
#    try:
#        r = get(change_account_url, params=params)
#        status_code = r.status_code
#        if status_code == 200:
#            quiet_print(f"success", args=args)
#            return True
#        elif status_code == 202:
#            quiet_print(f"unverified email", args=args)
#            return False
#        elif status_code == 401:
#            quiet_print(f"authorization failure", args=args)
#            return False
#        else:
#            quiet_print(f"fail", args=args)
#            return False
#    except:
#        quiet_print(f"server error", args=args)
#        return False
