from typing import Optional
from typing import Tuple


def module_code_url(module_name: str, version=None) -> Optional[str]:
    from requests import Session
    from .account import get_current_id_token
    from ...exceptions import AuthorizationError
    from ...exceptions import StoreServerError

    id_token = get_current_id_token(args={"quiet": True})
    s = Session()
    s.headers["User-Agent"] = "oakvar"
    url = get_store_url() + f"/moduleurls/{module_name}/{version}/code"
    params = {"idToken": id_token}
    res = s.post(url, data=params)
    if res.status_code == 200:
        code_url = res.text
        return code_url
    elif res.status_code == 401:
        raise AuthorizationError()
    elif res.status_code == 500:
        raise StoreServerError()
    else:
        return None


def module_data_url(module_name: str, version=None) -> Optional[str]:
    from requests import Session
    from .account import get_current_id_token
    from ...exceptions import AuthorizationError
    from ...exceptions import StoreServerError

    id_token = get_current_id_token(args={"quiet": True})
    s = Session()
    s.headers["User-Agent"] = "oakvar"
    url = get_store_url() + f"/moduleurls/{module_name}/{version}/data"
    params = {"idToken": id_token}
    res = s.post(url, data=params)
    if res.status_code == 200:
        data_url = res.text
        return data_url
    elif res.status_code == 401:
        raise AuthorizationError()
    elif res.status_code == 500:
        raise StoreServerError()
    else:
        return None


def setup_ov_store_cache(conf=None, args=None):
    from ..db import drop_ov_store_cache
    from ..db import create_ov_store_cache
    from ..db import fetch_ov_store_cache

    drop_ov_store_cache(conf=conf, args=args)
    create_ov_store_cache(conf=conf, args=args)
    fetch_ov_store_cache(args=args)


def url_is_valid(url: str) -> bool:
    from requests import head

    res = head(url)
    if res.status_code in [200, 301]:
        return True
    else:
        return False


def get_version_from_url(url: str):
    basename = url.split("/")[-1]
    words = basename.split("__")
    return words[1]


def get_register_args_of_module(module_name: str, args={}) -> Optional[dict]:
    from ...module.local import get_remote_manifest_from_local
    from ...exceptions import ArgumentError
    from ...util.util import is_url
    from json import dumps
    from oyaml import safe_load
    from ...util.util import quiet_print
    from ...module.local import get_local_module_info
    from os.path import exists

    rmi = get_remote_manifest_from_local(module_name, args=args)
    if not rmi or not args:
        return None
    if not rmi.get("data_version") and not rmi.get("no_data"):
        mi = get_local_module_info(module_name)
        if mi:
            quiet_print(
                f"data_version should be given or no_data should be set to true in {mi.conf_path}",
                args=args,
            )
        return None
    if args.get("url_file") and exists(args.get("url_file")):
        with open(args.get("url_file")) as f:
            j = safe_load(f)
            rmi["code_url"] = j.get("code_url", [])
            rmi["data_url"] = j.get("data_url", [])
    else:
        rmi["code_url"] = args.get("code_url")
        rmi["data_url"] = args.get("data_url") or []
    if not rmi["code_url"]:
        quiet_print(f"--code-url or -f with a file having code_url should be given.", args=args)
        return None
    for kind in ["code", "data"]:
        k = f"{kind}_url"
        if len(rmi[k]) > 0:
            for url in rmi[k]:
                try:
                    valid = is_url(url) and url_is_valid(url)
                except:
                    valid = False
                if not valid:
                    raise ArgumentError(msg=f"invalid {kind} URL: {url}")
    rmi["code_url"] = dumps(rmi["code_url"])
    rmi["data_url"] = dumps(rmi["data_url"])
    rmi["overwrite"] = args.get("overwrite")
    rmi["conf"] = dumps(rmi["conf"])
    rmi["developer"] = dumps(rmi["developer"])
    del rmi["output_columns"]
    del rmi["groups"]
    del rmi["requires"]
    del rmi["tags"]
    return rmi


def make_remote_module_info_from_local(module_name: str) -> Optional[dict]:
    from ...module.local import get_local_module_info
    from ...consts import publish_time_fmt
    from datetime import datetime

    mi = get_local_module_info(module_name)
    if not mi:
        return None
    versions = {}
    latest_version = ""
    ty = mi.type
    title = mi.title
    description = mi.description
    size = mi.size
    code_size = 0
    data_size = 0
    datasource = mi.data_source
    hidden = mi.conf.get("hidden", False)
    developer = mi.developer
    data_versions = {}
    data_sources = {}
    tags = mi.tags
    publish_time = datetime.now().strftime(publish_time_fmt)
    rmi = {
        "versions": versions,
        "latest_version": latest_version,
        "type": ty,
        "title": title,
        "description": description,
        "size": size,
        "code_size": code_size,
        "data_size": data_size,
        "datasource": datasource,
        "hidden": hidden,
        "developer": developer,
        "data_versions": data_versions,
        "data_sources": data_sources,
        "tags": tags,
        "publish_time": publish_time,
    }
    return rmi


def get_server_last_updated(args={}) -> Tuple[str, int]:
    from requests import Session
    from .account import get_current_id_token

    id_token = get_current_id_token(args=args)
    s = Session()
    s.headers["User-Agent"] = "oakvar"
    url = get_store_url() + "/last_updated"
    params = {"idToken": id_token}
    res = s.post(url, data=params)
    if res.status_code != 200:
        return "", res.status_code
    server_last_updated = res.text
    return server_last_updated, res.status_code


def make_module_info_from_table_row(row: dict) -> dict:
    d = {
        "name": row["name"],
        "type": row["type"],
        "code_version": row["code_version"],
        "data_version": row["data_version"],
        "tags": row["tags"],
        "code_size": row["code_size"],
        "data_size": row["data_size"],
        "logo_url": row["logo_url"],
        "description": row["description"],
        "readme": row["readme"],
        "logo": row["logo"],
        "conf": row["conf"],
        "store": row["store"],
    }
    return d


def get_store_url() -> str:
    from ...system import get_system_conf

    sys_conf = get_system_conf()
    store_url = sys_conf["store_url"]
    return store_url


def register(args={}) -> bool:
    from requests import post
    from .account import get_current_id_token
    from ...util.util import quiet_print
    from ...module.local import get_logo_b64
    from ...module.local import get_readme
    from ...module.local import get_code_size
    from ...module.local import get_data_size
    from ...consts import publish_time_fmt
    from datetime import datetime

    id_token = get_current_id_token()
    module_name = args.get("module_name")
    url = get_store_url() + "/register_module"
    try:
        params = get_register_args_of_module(module_name, args=args)
        if not params:
            return False
        params["idToken"] = id_token
        params["name"] = module_name
        params["readme"] = get_readme(module_name) or ""
        params["logo"] = get_logo_b64(module_name) or ""
        params["code_size"] = get_code_size(module_name)
        params["data_size"] = get_data_size(module_name) or 0
        params["overwrite"] = args.get("overwrite")
        params["publish_time"] = datetime.now().strftime(publish_time_fmt)
        if not params["conf"]:
            quiet_print(f"no configuration file exists for {module_name}", args=args)
            return False
        res = post(url, data=params)
        if res.status_code == 200:
            quiet_print(f"success", args=args)
            return True
        else:
            quiet_print(f"{res.text}", args=args)
            return False
    except Exception as e:
        quiet_print(f"{e}", args=args)
        return False


# @db_func
# def fetch_ov_store_cache(
#    email: Optional[str] = None,
#    pw: Optional[str] = None,
#    conn=None,
#    cursor=None,
#    args={},
# ):
#    from ..consts import ov_store_email_key
#    from ..consts import ov_store_pw_key
#    from ..consts import ov_store_last_updated_col
#    from ...system import get_sys_conf_value
#    from ...system import get_user_conf
#    from requests import Session
#    from ...util.util import quiet_print
#    from ...exceptions import StoreServerError
#    from ...exceptions import AuthorizationError
#
#    if not conn or not cursor:
#        return False
#    if not email and args:
#        email = args.get("email")
#        pw = args.get("pw")
#    if not email:
#        user_conf = get_user_conf()
#        email = user_conf.get(ov_store_email_key)
#        pw = user_conf.get(ov_store_pw_key)
#    if not email or not pw:
#        return False
#    params = {"email": email, "pw": pw}
#    s = Session()
#    s.headers["User-Agent"] = "oakvar"
#    store_url = get_sys_conf_value("store_url")
#    if not store_url:
#        return False
#    server_last_updated, status_code = get_server_last_updated(email, pw)
#    local_last_updated = get_local_last_updated()
#    clean = args.get("clean")
#    if not server_last_updated:
#        if status_code == 401:
#            raise AuthorizationError()
#        elif status_code == 500:
#            raise StoreServerError()
#        return False
#    if not clean and local_last_updated and local_last_updated >= server_last_updated:
#        quiet_print("No store update to fetch", args=args)
#        return True
#    url = f"{store_url}/fetch"
#    res = s.get(url, params=params)
#    if res.status_code != 200:
#        if res.status_code == 401:
#            raise AuthorizationError()
#        elif res.status_code == 500:
#            raise StoreServerError()
#        return False
#    q = f"delete from modules"
#    cursor.execute(q)
#    conn.commit()
#    res = res.json()
#    cols = res["cols"]
#    for row in res["data"]:
#        q = f"insert into modules ( {', '.join(cols)} ) values ( {', '.join(['?'] * len(cols))} )"
#        cursor.execute(q, row)
#    q = f"insert or replace into info ( key, value ) values ( ?, ? )"
#    cursor.execute(q, (ov_store_last_updated_col, str(server_last_updated)))
#    conn.commit()
#    quiet_print("OakVar store cache has been fetched.", args=args)
