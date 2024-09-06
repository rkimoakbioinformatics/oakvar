# OakVar
#
# Copyright (c) 2024 Oak Bioinformatics, LLC
#
# All rights reserved.
#
# Do not distribute or use this software without obtaining
# a license from Oak Bioinformatics, LLC.
#
# Do not use this software to develop another software
# which competes with the products by Oak Bioinformatics, LLC,
# without obtaining a license for such use from Oak Bioinformatics, LLC.
#
# For personal use of non-commercial nature, you may use this software
# after registering with `ov store account create`.
#
# For research use of non-commercial nature, you may use this software
# after registering with `ov store account create`.
#
# For use by commercial entities, you must obtain a commercial license
# from Oak Bioinformatics, LLC. Please write to info@oakbioinformatics.com
# to obtain the commercial license.
# ================
# OpenCRAVAT
#
# MIT License
#
# Copyright (c) 2021 KarchinLab
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from typing import Optional
from typing import Any
from typing import Tuple
from typing import Dict
from pathlib import Path


def get_email_pw_from_user_conf(email: Optional[str] = None, pw: Optional[str] = None):
    from ....system import get_user_conf
    from ....store.consts import OV_STORE_EMAIL_KEY
    from ....store.consts import OV_STORE_PW_KEY

    user_conf = get_user_conf()
    if not email:
        email = user_conf.get(OV_STORE_EMAIL_KEY)
    if not pw:
        pw = user_conf.get(OV_STORE_PW_KEY)
    return email, pw


def get_email_pw_interactively(
    email: Optional[str] = None, pw: Optional[str] = None, pwconfirm=False, outer=None
) -> Tuple:
    from ....util.util import email_is_valid
    from ....util.util import pw_is_valid
    from ....util.util import is_in_jupyter_notebook
    from getpass import getpass

    if not email:
        while True:
            if is_in_jupyter_notebook():
                print(
                    "Interactive mode not supported in Jupyter notebook. Please provide email and password as arguments."
                )
                return email, pw
            else:
                email = input("Email: ")
            if email_is_valid(email):
                break
            if outer:
                outer.error("Email is not vaild.")
    if not pw:
        while True:
            pw = getpass("Password (alphabets, numbers, and !?&@-+): ")
            if not pw_is_valid(pw):
                print("Password is invalid")
                pw = None
            if pw and pwconfirm:
                pwagain = getpass("Confirm password: ")
                if pw != pwagain:
                    print("Password mismatch")
                    pw = None
            if pw:
                break
    return email, pw


def create(
    email: Optional[str] = None,
    pw: Optional[str] = None,
    pwconfirm=True,
    interactive: bool = False,
    outer=None,
) -> dict:
    from requests import post
    from ....system import get_system_conf
    from ....store.consts import store_url_key
    from ....util.util import is_in_jupyter_notebook

    if (not email or not pw) and interactive:
        if is_in_jupyter_notebook():
            return {
                "status_code": 403,
                "msg": "Interactive mode not supported in Jupyter notebook. Please provide email and password as arguments.",
                "success": False,
                "email": email,
            }
        else:
            email, pw = get_email_pw_interactively(
                email=email, pw=pw, pwconfirm=pwconfirm
            )
    if not email:
        return {"msg": "no email", "success": False, "email": email}
    sys_conf = get_system_conf()
    store_url = sys_conf[store_url_key]
    create_account_url = store_url + "/account/create"
    params = {
        "email": email,
        "pw": pw,
    }
    msg = ""
    success = False
    status_code = 0
    try:
        r = post(create_account_url, json=params)
        status_code = r.status_code
        if status_code == 200:
            msg = ""
            success = True
        elif status_code == 500:
            msg = "Server error"
            success = False
        elif status_code == 403:
            msg = "account-exists"
            success = False
        elif status_code == 202:
            msg = "Check your inbox for a verification email."
            success = True
        elif status_code == 201:
            msg = "Account has been created. Check your inbox for a verification email."
            success = True
        else:
            msg = f"{r.text}"
            success = False
    except Exception as e:
        status_code = 500
        msg = f"Fail ({e})"
        success = False
    finally:
        if outer:
            outer.write(msg)
        return {
            "status_code": status_code,
            "msg": msg,
            "success": success,
            "email": email,
        }


def delete(outer=None) -> bool:
    from requests import post
    from ...ov import get_store_url

    token_set = get_token_set()
    if not token_set:
        if outer:
            outer.write("Log in first")
        return False
    store_url = get_store_url()
    url = store_url + "/account/delete"
    params = {"idToken": token_set["idToken"]}
    r = post(url, json=params)
    status_code = r.status_code
    if status_code == 200:
        if outer:
            outer.write("Success")
        return True
    else:
        if outer:
            outer.write(f"Fail ({r.text})")
        return False


def check_logged_in_with_token(outer=None) -> bool:
    from ....exceptions import StoreServerError

    id_token = get_id_token()
    if not id_token:
        if outer:
            outer.write("not logged in")
        return False
    valid, expired = id_token_is_valid()
    if valid:
        if expired:
            status_code, text = refresh_token_set()
            if status_code != 200:
                raise StoreServerError(status_code=status_code, text=text)
        token_set = get_token_set() or {}
        email = token_set["email"]
        if outer:
            outer.write(f"logged in as {email}")
        return True
    else:
        if outer:
            outer.write("not logged in")
        return False


def reset(email: Optional[str] = None, outer=None) -> bool:
    from ...ov import get_store_url
    from ....util.util import email_is_valid
    from requests import post

    if not email:
        return False
    if not email_is_valid(email):
        if outer:
            outer.write("Invalid email")
        return False
    url = get_store_url() + "/account/reset"
    params = {"email": email}
    res = post(url, json=params)
    if res.status_code == 200:
        if outer:
            outer.write(
                "Success. Check your email for instruction to reset your password."
            )
        return True
    else:
        if outer:
            outer.write(f"Fail ({res.text})")
        return False


def get_email_from_token_set() -> Optional[str]:
    token_set = get_token_set() or {}
    email = token_set.get("email")
    return email


def try_login_with_token(email: Optional[str] = None, outer=None) -> Tuple[bool, str]:
    if not check_logged_in_with_token(outer=outer):
        return False, ""
    token_set_email = get_email_from_token_set()
    if not token_set_email:
        return False, ""
    if not email or token_set_email == email:
        if outer:
            outer.write(f"Logged in as {token_set_email}")
        return True, token_set_email
    else:
        return False, email


def login(
    email: Optional[str] = None,
    pw: Optional[str] = None,
    interactive: bool = False,
    relogin: bool = False,
    outer=None,
) -> Dict[str, Any]:
    from requests import post
    from ...ov import get_store_url
    from ....util.util import is_in_jupyter_notebook

    if not relogin and not email:
        ret, token_set_email = try_login_with_token(email=email)
        if ret is True:
            return {
                "success": True,
                "msg": f"Logged in as {token_set_email}",
                "email": token_set_email,
            }
    if not email or not pw:
        email, pw = get_email_pw_from_user_conf(email=email, pw=pw)
    if (not email or not pw) and interactive:
        if is_in_jupyter_notebook():
            return {
                "status_code": 403,
                "msg": "Interactive mode not supported in Jupyter notebook. Please provide email and password as arguments.",
                "success": False,
                "email": email,
            }
        else:
            email, pw = get_email_pw_interactively(email=email, pw=pw)
    if not email:
        return {"success": False, "msg": "No email", "email": email}
    if not pw:
        return {"success": False, "msg": "No password", "email": email}
    login_url = get_store_url() + "/account/login"
    params = {"email": email, "pw": pw}
    try:
        r = post(login_url, json=params)
        status_code = r.status_code
        if status_code == 200:
            save_token_set(r.json())
            if outer:
                outer.write(f"Logged in as {email}")
            return {"success": True, "email": email}
        else:
            if outer:
                outer.write(f"fail. {r.text}")
            d = {
                "success": False,
                "status_code": status_code,
                "mgs": "Login failed.",
                "email": email,
            }
            return d
    except Exception:
        import traceback

        msg = traceback.format_exc()
        if outer:
            outer.write("server error")
        return {"success": False, "status_code": 500, "msg": msg, "email": email}


def get_token_set_path() -> Path:
    from ....system import get_root_dir
    from ....system import get_system_conf_path
    from ....exceptions import SystemMissingException
    from ....store.consts import ov_store_id_token_fname

    root_dir = get_root_dir()
    if not root_dir:
        sys_conf_path = get_system_conf_path()
        raise SystemMissingException(
            "root_dir does not exist in the system configuration "
            + f"file at {sys_conf_path}. Please consider running `ov system setup`."
        )
    token_path = root_dir / ov_store_id_token_fname
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


def delete_id_token(outer=None):
    from os import remove
    from os.path import exists

    token_path = get_token_set_path()
    if exists(token_path):
        remove(token_path)
        return True
    else:
        if outer:
            outer.write("Not logged in")
        return False


def id_token_is_valid() -> Tuple[bool, bool]:  # valid, expired
    from ...ov import get_store_url
    from requests import post

    id_token = get_id_token()
    if not id_token:
        return False, True
    params = {"idToken": id_token}
    url = get_store_url() + "/account/id_token_verified"
    res = post(url, json=params)
    st = res.status_code
    if st == 460:  # valid but expired
        return True, True
    elif st == 200:
        return True, False
    else:
        msg = res.text
        print(f"Unknown idToken error: {msg}")
        return False, True


def refresh_token_set() -> Tuple[int, str]:
    from ...ov import get_store_url
    from requests import post

    refresh_token = get_refresh_token()
    url = get_store_url() + "/account/refresh"
    params = {"refreshToken": refresh_token}
    res = post(url, json=params)
    if res.status_code == 200:
        token_set = get_token_set()
        if token_set:
            j = res.json()
            id_token = j.get("id_token", j.get("idToken"))
            refresh_token = j.get("refresh_token", j.get("refreshToken"))
            token_set["idToken"] = id_token
            token_set["refreshToken"] = refresh_token
            save_token_set(token_set)
            return (200, "")
        else:
            return (res.status_code, res.text)
    else:
        return (res.status_code, res.text)


def change(newpw: Optional[str] = None, outer=None) -> bool:
    from requests import post
    from ...ov import get_store_url
    from getpass import getpass
    from ....util.util import pw_is_valid
    from ....exceptions import StoreServerError

    id_token = get_id_token()
    if not id_token:
        if outer:
            outer.write("Not logged in")
        return False
    valid, expired = id_token_is_valid()
    if not valid:
        if outer:
            outer.write("Not logged in")
        return False
    if expired:
        id_token = None
        refresh_token = get_refresh_token()
        if refresh_token:
            status_code, text = refresh_token_set()
            if status_code != 200:
                raise StoreServerError(status_code=status_code, text=text)
            token_set = get_token_set()
            if token_set:
                id_token = token_set["idToken"]
        if not id_token:
            if outer:
                outer.write("Not logged in")
            return False
    if not newpw:
        while not pw_is_valid(newpw):
            newpw = getpass("New password: ")
    refresh_token = get_refresh_token()
    url = get_store_url() + "/account/change"
    params = {"idToken": id_token, "refreshToken": refresh_token, "newpw": newpw}
    res = post(url, json=params)
    status_code = res.status_code
    if status_code != 200:
        if outer:
            outer.write(f"{res.text}")
        return False
    else:
        token_set = get_token_set()
        if not token_set:
            if outer:
                outer.write("Password changed but re-login failed")
            return False
        email = token_set["email"]
        if login(email=email, pw=newpw):
            return True
        else:
            if outer:
                outer.write("Password changed but re-login failed")
            return True


def logout(outer=None) -> bool:
    ret = delete_id_token(outer=outer)
    if ret and outer:
        outer.write("Success")
    return ret


def get_current_id_token() -> Optional[str]:
    token_set = get_current_token_set()
    if token_set:
        return token_set["idToken"]
    else:
        return None


def get_current_token_set() -> Optional[dict]:
    from ....exceptions import StoreServerError

    token_set = get_token_set()
    if token_set:
        valid, expired = id_token_is_valid()
        if not valid:
            token_set = None
        elif expired:
            status_code, text = refresh_token_set()
            if status_code != 200:
                raise StoreServerError(status_code=status_code, text=text)
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
    email=None,
    pw=None,
    conf=None,
) -> Tuple[Optional[str], Optional[str]]:
    from os import environ
    from ...consts import OV_STORE_EMAIL_KEY
    from ...consts import OV_STORE_PW_KEY
    from ....system import get_user_conf
    from ....system import get_env_key

    if email and pw:
        return email, pw
    # if email or pw not given, use conf.
    if conf:
        if not email:
            email = conf.get(OV_STORE_EMAIL_KEY)
        if not pw:
            pw = conf.get(OV_STORE_PW_KEY)
    if email and pw:
        return email, pw
    # if not, check environmental variables.
    if not email:
        k = get_env_key(OV_STORE_EMAIL_KEY)
        if k in environ:
            email = environ.get(k)
    if not pw:
        k = get_env_key(OV_STORE_PW_KEY)
        if k in environ:
            pw = environ.get(k)
    if email and pw:
        return email, pw
    # if not, oakvar.yml
    user_conf = get_user_conf()
    if not email and OV_STORE_EMAIL_KEY in user_conf:
        email = user_conf[OV_STORE_EMAIL_KEY]
    if not pw and OV_STORE_PW_KEY in user_conf:
        pw = user_conf[OV_STORE_PW_KEY]
    return email, pw


def emailpw_are_valid(email: str = "", pw: str = "") -> bool:
    from ....util.util import email_is_valid
    from ....util.util import pw_is_valid

    return email_is_valid(email) and pw_is_valid(pw)


def email_is_verified(email: str, outer=None) -> bool:
    from ...ov import get_store_url
    from requests import post

    url = get_store_url() + "/account/email_verified"
    params = {"email": email}
    res = post(url, json=params)
    if res.status_code == 200:
        return True
    elif res.status_code == 404:
        if outer:
            outer.write("User not found")
        return False
    else:
        if outer:
            outer.write(f"{email} has not been verified. {res.text}")
        return False


def announce_on_email_verification_if_needed(email: str, outer=None):
    from ....system import show_email_verify_action_banner

    if not email_is_verified(email, outer=outer):
        show_email_verify_action_banner(email)


def login_with_token_set(email=None, outer=None) -> Tuple[bool, str]:
    from ....exceptions import StoreServerError

    token_set = get_token_set()
    if token_set:
        token_email = token_set["email"]
        if email and token_email != email:
            return False, token_email
        correct, expired = id_token_is_valid()
        email_verified = email_is_verified(token_email, outer=outer)
        if not email_verified:
            if outer:
                outer.write(
                    "Email not verified. A verification email should "
                    + "have been sent to your inbox.\n"
                )
            return True, token_email
        else:
            if correct:
                if expired:
                    status_code, text = refresh_token_set()
                    if status_code != 200:
                        delete_token_set()
                        raise StoreServerError(status_code=status_code, text=text)
                    return False, ""
                else:
                    return True, token_email
            else:
                delete_token_set()
    return False, ""


def login_with_email_pw(
    email: Optional[str] = None,
    pw: Optional[str] = None,
    conf: Optional[Dict] = None,
    outer=None,
) -> dict:
    email, pw = get_email_pw_from_settings(email=email, pw=pw, conf=conf)
    if not email or not pw:
        return {
            "status_code": 400,
            "success": False,
            "msg": "No email or password was provided",
            "email": email,
        }
    if emailpw_are_valid(email=email, pw=pw):
        announce_on_email_verification_if_needed(email, outer=outer)
        ret = login(email=email, pw=pw, outer=outer)
        return ret
    else:
        return {
            "status_code": 400,
            "success": False,
            "msg": "invalid email or password)",
            "email": email,
        }


def total_login(
    email=None,
    pw=None,
    create_account: bool = False,
    install_mode: str = "",
    conf: Optional[Dict] = None,
    outer=None,
) -> dict:
    from ....system import show_no_user_account_prelude
    from ....util.util import is_in_jupyter_notebook

    if not email or not pw:
        ret, logged_email = login_with_token_set(email=email, outer=outer)
        if ret is True:
            return {"success": True, "email": logged_email}
    ret = login_with_email_pw(email=email, pw=pw, conf=conf, outer=outer)
    if ret.get("success"):
        return {"success": True, "email": ret["email"]}
    elif ret.get("status_code") == 400 and email is not None and pw is not None:
        return {"success": False, "email": None}
    elif install_mode == "web":
        if outer:
            outer.write(ret)
        return ret
    if create_account:
        ret = create(email=email, pw=pw, outer=outer)
        if not ret.get("success"):
            if outer:
                outer.write(ret)
        return ret
    yn = None
    while True:
        if is_in_jupyter_notebook():
            print(
                "Interactive mode is not available in Jupyter notebook. Assuming that you have an OakVar account..."
            )
            break
        else:
            yn = input("Do you already have an OakVar store account? (y/N): ")
        if yn.lower() in ["y", "n", ""]:
            break
    if yn == "y":
        if is_in_jupyter_notebook():
            return {
                "status_code": 403,
                "msg": "Interactive mode not supported in Jupyter notebook. Please provide email and password as arguments.",
                "success": False,
                "email": email,
            }
        else:
            email, pw = get_email_pw_interactively(
                email=email, pw=pw, pwconfirm=False, outer=outer
            )
        ret = login_with_email_pw(email=email, pw=pw, conf=conf)
        return ret
    else:
        show_no_user_account_prelude()
        if is_in_jupyter_notebook():
            return {
                "status_code": 403,
                "msg": "Interactive mode not supported in Jupyter notebook. Please provide email and password as arguments.",
                "success": False,
                "email": email,
            }
        else:
            email, pw = get_email_pw_interactively(email=email, pw=pw, pwconfirm=True)
        ret = create(email=email, pw=pw, outer=outer)
        if not ret.get("success"):
            if outer:
                outer.write(ret)
            return ret
        announce_on_email_verification_if_needed(email, outer=outer)
        ret = login(email=email, pw=pw, outer=outer)
        return ret
