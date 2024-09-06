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
from typing import List
from typing import Tuple
from . import account as account


def module_data_url(module_name: str, version=None) -> Optional[str]:
    from requests import Session
    from .account import get_current_id_token
    from ...exceptions import AuthorizationError
    from ...exceptions import StoreServerError

    id_token = get_current_id_token()
    if not id_token:
        raise AuthorizationError()
    s = Session()
    s.headers["User-Agent"] = "oakvar"
    url = get_store_url() + f"/data_url/{module_name}/{version}"
    params = {"idToken": id_token}
    res = s.post(url, json=params)
    if res.status_code == 200:
        data_url = res.text
        return data_url
    elif res.status_code == 401:
        raise AuthorizationError()
    elif res.status_code == 500:
        raise StoreServerError()
    else:
        return None


def setup_ov_store_cache(
    refresh_db: bool = False,
    clean_cache_files: bool = False,
    clean: bool = False,
    publish_time: str = "",
    outer=None,
):
    from ..db import fetch_ov_store_cache

    fetch_ov_store_cache(
        refresh_db=refresh_db,
        clean_cache_files=clean_cache_files,
        clean=clean,
        publish_time=publish_time,
        outer=outer,
    )


def url_is_valid(url: str) -> bool:
    from requests import head

    res = head(url)
    status_code = res.status_code
    if status_code >= 200 and status_code < 400:
        return True
    else:
        return False


def get_register_args_of_module(
    module_name: str,
    url_file: Optional[str] = None,
    code_url: List[str] = [],
    data_url: List[str] = [],
    overwrite: bool = False,
    outer=None,
) -> Optional[dict]:
    from json import dumps
    from oyaml import safe_load
    from pathlib import Path
    from ...module.local import get_remote_manifest_from_local
    from ...exceptions import ArgumentError
    from ...util.util import is_url
    from ...module.local import get_local_module_info
    from ..ov import module_data_url

    rmi = get_remote_manifest_from_local(module_name, outer=outer)
    if not rmi:
        return None
    data_version = rmi.get("data_version")
    no_data = rmi.get("no_data")
    if not data_version and not no_data:
        mi = get_local_module_info(module_name)
        if mi and outer:
            outer.error(
                "data_version should be given or no_data should "
                + f"be set to true in {mi.conf_path}.\n",
            )
        return None
    if url_file and Path(url_file).exists():
        with open(url_file) as f:
            j = safe_load(f)
            rmi["code_url"] = j.get("code_url", [])
            rmi["data_url"] = j.get("data_url", [])
    else:
        rmi["code_url"] = code_url
        rmi["data_url"] = data_url
    if not rmi["code_url"]:
        if outer:
            outer.error(
                "--code-url or -f with a file having code_url should be given.\n"
            )
        return None
    for kind in ["code", "data"]:
        k = f"{kind}_url"
        if rmi[k] and len(rmi[k]) > 0:
            for url in rmi[k]:
                if outer:
                    outer.write(f"Validating {url}...")
                try:
                    valid = is_url(url) and url_is_valid(url)
                except Exception:
                    valid = False
                if not valid:
                    raise ArgumentError(msg=f"invalid {kind} URL: {url}")
                if outer:
                    outer.write("Validated")
    if not rmi.get("data_url") and no_data and data_version:
        data_url_s = module_data_url(module_name, version=data_version)
        if not data_url_s:
            raise ArgumentError(msg="--data-url should be given for new data.")
    rmi["code_url"] = dumps(rmi["code_url"])
    rmi["data_url"] = dumps(rmi["data_url"])
    rmi["overwrite"] = overwrite
    rmi["conf"] = dumps(rmi["conf"])
    rmi["developer"] = dumps(rmi["developer"])
    del rmi["output_columns"]
    del rmi["groups"]
    del rmi["requires"]
    del rmi["tags"]
    return rmi


def get_server_last_updated() -> Tuple[str, int]:
    from requests import Session
    from .account import get_current_id_token

    id_token = get_current_id_token()
    s = Session()
    s.headers["User-Agent"] = "oakvar"
    url = get_store_url() + "/last_updated"
    params = {"idToken": id_token}
    res = s.post(url, json=params)
    if res.status_code != 200:
        return res.text, res.status_code
    server_last_updated = res.text
    return server_last_updated, res.status_code


def set_store_url(url: str):
    from ...system import set_sys_conf_value
    from ...store.consts import store_url_key

    set_sys_conf_value(store_url_key, url, "str")


def get_store_url() -> str:
    from ...system import get_system_conf
    from ...store.consts import store_url_key

    sys_conf = get_system_conf()
    store_url = sys_conf[store_url_key]
    return store_url


def register(
    module_name: str,
    url_file: Optional[str] = None,
    code_url: List[str] = [],
    data_url: List[str] = [],
    overwrite: bool = False,
    outer=None,
) -> bool:
    from requests import post
    from .account import get_current_id_token
    from ...module.local import get_logo_b64
    from ...module.local import get_readme
    from ...module.local import get_code_size
    from ...module.local import get_data_size
    from ...consts import publish_time_fmt
    from datetime import datetime

    id_token = get_current_id_token()
    url = get_store_url() + "/register_module"
    try:
        params = get_register_args_of_module(
            module_name,
            url_file=url_file,
            code_url=code_url,
            data_url=data_url,
            overwrite=overwrite,
            outer=outer,
        )
    except Exception as e:
        if outer:
            outer.error(e)
        return False
    try:
        if not params:
            return False
        params["idToken"] = id_token
        params["name"] = module_name
        params["readme"] = get_readme(module_name) or ""
        params["logo"] = get_logo_b64(module_name) or ""
        params["code_size"] = get_code_size(module_name)
        params["data_size"] = get_data_size(module_name)
        params["overwrite"] = overwrite
        params["publish_time"] = datetime.now().strftime(publish_time_fmt)
        if not params["conf"]:
            if outer:
                outer.error(f"No configuration file exists for {module_name}.\n")
            return False
        res = post(url, json=params)
        if res.status_code == 200:
            if outer:
                outer.write("Success")
            return True
        else:
            if outer:
                outer.write(
                    f"Error from the store server: {res.status_code} {res.text}\n"
                )
            return False
    except Exception:
        import traceback

        traceback.print_exc()
        return False


def delete(
    module_name: str,
    code_version: Optional[str] = None,
    all: bool = False,
    keep_only_latest: bool = False,
    outer=None,
):
    from requests import post
    from .account import get_current_id_token

    id_token = get_current_id_token()
    if not code_version and not keep_only_latest and not all:
        if outer:
            outer.write(
                "Either --version, --all, or --keep-only-latest should be given.\n"
            )
        return False
    url = get_store_url() + "/delete_module"
    try:
        params = {}
        params["idToken"] = id_token
        params["name"] = module_name
        params["code_version"] = code_version
        params["all"] = all
        params["keep_only_latest"] = keep_only_latest
        res = post(url, json=params)
        if res.status_code == 200:
            if outer:
                outer.write("Success")
            return True
        else:
            if outer:
                outer.write(
                    "Error from the store server: {res.status_code}: {res.text}\n"
                )
            return False
    except Exception as e:
        if outer:
            outer.error(e)
        return False
