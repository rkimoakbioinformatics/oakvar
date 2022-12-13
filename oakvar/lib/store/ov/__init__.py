from typing import Optional
from typing import Tuple


def module_code_url(module_name: str, version=None) -> Optional[str]:
    from requests import Session
    from .account import get_current_id_token
    from ...exceptions import AuthorizationError
    from ...exceptions import StoreServerError

    id_token = get_current_id_token(args={"quiet": True})
    if not id_token:
        raise AuthorizationError()
    s = Session()
    s.headers["User-Agent"] = "oakvar"
    url = get_store_url() + f"/code_url/{module_name}/{version}"
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
    if not id_token:
        raise AuthorizationError()
    s = Session()
    s.headers["User-Agent"] = "oakvar"
    url = get_store_url() + f"/data_url/{module_name}/{version}"
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


def setup_ov_store_cache(args=None):
    from ..db import fetch_ov_store_cache

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
    from json import dumps
    from oyaml import safe_load
    from os.path import exists
    from ...module.local import get_remote_manifest_from_local
    from ...exceptions import ArgumentError
    from ...util.util import is_url
    from ...util.util import quiet_print
    from ...module.local import get_local_module_info
    from ..ov import module_data_url

    rmi = get_remote_manifest_from_local(module_name, args=args)
    if not rmi or not args:
        return None
    data_version = rmi.get("data_version")
    no_data = rmi.get("no_data")
    if not data_version and not no_data:
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
        quiet_print(
            f"--code-url or -f with a file having code_url should be given.", args=args
        )
        return None
    for kind in ["code", "data"]:
        k = f"{kind}_url"
        if len(rmi[k]) > 0:
            for url in rmi[k]:
                quiet_print(f"Validating {url}...", args=args)
                try:
                    valid = is_url(url) and url_is_valid(url)
                except:
                    valid = False
                if not valid:
                    raise ArgumentError(msg=f"invalid {kind} URL: {url}")
                quiet_print(f"Validated", args=args)
    if not rmi.get("data_url") and no_data and data_version:
        data_url_s = module_data_url(module_name, version=data_version)
        if not data_url_s:
            raise ArgumentError(msg=f"--data-url should be given for new data.")
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
    from ...store.consts import store_url_key

    sys_conf = get_system_conf()
    store_url = sys_conf[store_url_key]
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
            quiet_print(f"Error from the store server: {res.status_code} {res.text}", args=args)
            return False
    except Exception:
        import traceback
        traceback.print_exc()
        return False
