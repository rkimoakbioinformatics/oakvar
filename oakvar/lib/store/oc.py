from typing import Optional


def oc_module_url(module_name: str) -> str:
    from .consts import oc_store_module_url

    return "/".join([oc_store_module_url, "modules", module_name])


def oc_module_download_counts_url() -> str:
    from .consts import oc_store_module_url

    return "/".join([oc_store_module_url, "download-counts.yml"])


def oc_module_version_url(module_name: str, version: str) -> str:
    return "/".join([oc_module_url(module_name), version])


def oc_module_conf_url(module_name: str, version: str) -> str:
    return "/".join([oc_module_version_url(module_name, version), module_name + ".yml"])


def oc_module_readme_url(module_name: str, version: str) -> str:
    return "/".join([oc_module_version_url(module_name, version), module_name + ".md"])


def oc_module_code_url(module_name: str, version: str) -> str:
    return "/".join(
        [oc_module_version_url(module_name, version), module_name + ".code.zip"]
    )


def oc_module_code_manifest_url(module_name: str, version: str):
    return "/".join(
        [
            oc_module_version_url(module_name, version),
            module_name + ".code.manifest.yml",
        ]
    )


def oc_module_data_url(module_name: str, version: str) -> str:
    return "/".join(
        [oc_module_version_url(module_name, version), module_name + ".data.zip"]
    )


def oc_module_data_manifest_url(module_name: str, version: str) -> str:
    return "/".join(
        [
            oc_module_version_url(module_name, version),
            module_name + ".data.manifest.yml",
        ]
    )


def oc_module_logo_url(module_name: str, version: str) -> str:
    return "/".join([oc_module_version_url(module_name, version), "logo.png"])


def oc_module_meta_url(module_name: str, version: str) -> str:
    return "/".join([oc_module_version_url(module_name, version), "meta.yml"])


def module_config(module_name, version=None):
    import oyaml as yaml
    from . import fetch_file_content_to_string
    from . import remote_module_latest_version

    if version == None:
        version = remote_module_latest_version(module_name)
    if not version:
        return None
    config_url = oc_module_conf_url(module_name, version)
    config = yaml.safe_load(fetch_file_content_to_string(config_url))
    return config


def get_oc_manifest_path() -> str:
    from os.path import join
    from .consts import oc_manifest_fn
    from ..system import get_conf_dir

    conf_dir = get_conf_dir()
    oc_manifest_path = join(conf_dir, oc_manifest_fn)
    return oc_manifest_path


def fetch_oc_manifest_response():
    from requests import get
    from .consts import oc_manifest_url

    response = get(oc_manifest_url)
    if response.status_code == 200:
        return response
    else:
        return None


def get_remote_oc_manifest_timestamp() -> Optional[float]:
    from requests import head
    from dateutil.parser import parse
    from .consts import oc_manifest_url

    response = head(oc_manifest_url)
    if response.status_code == 200:
        ts = parse(response.headers["Last-Modified"]).timestamp()
        return float(ts)
    else:
        return None


def has_newer_remote_oc_manifest(path: Optional[str] = None) -> bool:
    if not path:
        path = get_oc_manifest_path()
    if not path:
        return False
    from os.path import exists

    if not exists(path):
        return True
    from os.path import getmtime

    local_oc_manifest_ts = getmtime(path)
    remote_oc_manifest_ts = get_remote_oc_manifest_timestamp()
    if not remote_oc_manifest_ts:
        return False
    if remote_oc_manifest_ts > local_oc_manifest_ts:
        return True
    else:
        return False


def get_oc_manifest() -> dict:
    path = get_oc_manifest_path()
    if not path:
        return {}
    with open(path) as f:
        from json import load

        manifest = load(f)
        return manifest


def fetch_and_save_oc_manifest(path: Optional[str] = None, args={}):
    from ..util.util import quiet_print

    if not path:
        path = get_oc_manifest_path()
    if not path:
        return
    if has_newer_remote_oc_manifest(path=path):
        oc_manifest_response = fetch_oc_manifest_response()
        if oc_manifest_response:
            with open(path, "w") as wf:
                wf.write(oc_manifest_response.text)
                quiet_print(f"Saved {path}", args=args)


def change_password(args={}):
    from requests import post
    from .consts import oc_publish_url
    from ..exceptions import StoreServerError
    from ..exceptions import StoreIncorrectLogin

    username = args.get("username")
    cur_pw = args.get("cur_pw")
    new_pw = args.get("new_pw")
    change_pw_url = oc_publish_url + "/change-password"
    r = post(change_pw_url, auth=(username, cur_pw), json={"newPassword": new_pw})
    if r.status_code == 500:
        raise StoreServerError()
    elif r.status_code == 401:
        raise StoreIncorrectLogin()
    if r.text:
        return r.text


def check_login(args={}):
    from requests import get
    from .consts import oc_publish_url
    from ..exceptions import StoreServerError
    from ..util.util import quiet_print

    username = args.get("username")
    password = args.get("password")
    login_url = oc_publish_url + "/login"
    r = get(login_url, auth=(username, password))
    if r.status_code == 200:
        return True
    elif r.status_code == 500:
        raise StoreServerError()
    else:
        quiet_print(f"{r.text}", args=args)
        return False


def print_stage_handler(cur_stage, total_stages, __cur_size__, __total_size__):
    import sys

    rem_stages = total_stages - cur_stage
    perc = cur_stage / total_stages * 100
    out = "\r[{1}{2}] {0:.0f}% ".format(perc, "*" * cur_stage, " " * rem_stages)
    sys.stdout.write(out)
    if cur_stage == total_stages:
        print()


def publish_module(
    module_name, user, password, overwrite=False, include_data=True, quiet=True
):
    import os
    import json
    from ..exceptions import VersionExists
    from ..store import ModuleArchiveBuilder
    from ..store import stream_multipart_post
    from requests import get
    from ..system import get_modules_dir
    from ..util.util import quiet_print
    from ..module.cache import get_module_cache
    from ..module.local import get_local_module_info
    from .consts import oc_publish_url
    from ..exceptions import ModuleNotExist
    from ..exceptions import StoreIncorrectLogin
    from ..exceptions import NormalExit
    from ..exceptions import ModuleVersionError
    from ..exceptions import StoreServerError
    from ..exceptions import StoreServerError
    from ..exceptions import StoreServerError

    quiet_args = {"quiet": quiet}
    get_module_cache().update_local()
    local_info = get_local_module_info(module_name)
    if local_info == None:
        raise ModuleNotExist(module_name)
    check_url = oc_publish_url + "/%s/%s/check" % (module_name, local_info.version)
    r = get(check_url, auth=(user, password))
    if r.status_code != 200:
        if r.status_code == 401:
            raise StoreIncorrectLogin()
        elif r.status_code == 400:
            err = json.loads(r.text)
            if err["code"] == VersionExists.code:
                while True:
                    if overwrite:
                        break
                    resp = input("Version exists. Do you wish to overwrite (y/n)? ")
                    if resp == "y":
                        overwrite = True
                        break
                    if resp == "n":
                        raise NormalExit()
                    else:
                        continue
            else:
                raise ModuleVersionError(module_name, local_info.version)
        elif r.status_code == 500:
            raise StoreServerError(500)
        else:
            raise StoreServerError(r.status_code)
    zf_name = "%s.%s.zip" % (module_name, local_info.version)
    zf_path = os.path.join(get_modules_dir(), zf_name)
    quiet_print("Zipping module and generating checksums", args=quiet_args)
    zip_builder = ModuleArchiveBuilder(zf_path, base_path=local_info.directory)
    for item_name in os.listdir(local_info.directory):
        item_path = os.path.join(local_info.directory, item_name)
        if item_name.endswith("ofinstall"):
            continue
        elif item_name == "__pycache__":
            continue
        elif item_path == local_info.data_dir and not (include_data):
            continue
        else:
            zip_builder.add_item(item_path)
    manifest = zip_builder.get_manifest()
    zip_builder.close()
    if local_info.version is None:
        post_url = "/".join([oc_publish_url, module_name])
    else:
        post_url = "/".join([oc_publish_url, module_name, local_info.version])
    if overwrite:
        post_url += "?overwrite=1"
    with open(zf_path, "rb") as zf:
        fields = {
            "manifest": ("manifest.json", json.dumps(manifest), "application/json"),
            "archive": (zf_name, zf, "application/octet-stream"),
        }
        quiet_print("Uploading to store", args=quiet_args)
        r = stream_multipart_post(
            post_url, fields, stage_handler=print_stage_handler, auth=(user, password)
        )
    if r.status_code != 200:
        raise StoreServerError(status_code=r.status_code, text=r.text)
    if r.text:
        quiet_print(r.text, args=quiet_args)
    os.remove(zf_path)


def send_reset_email(args={}):
    from requests import post
    from ..util.util import quiet_print
    from .consts import oc_publish_url
    from ..exceptions import StoreServerError

    username = args.get("username")
    reset_pw_url = oc_publish_url + "/reset-password"
    r = post(reset_pw_url, params={"username": username})
    if r.status_code == 500:
        raise StoreServerError(status_code=r.status_code)
    if r.text:
        quiet_print(r.text, args=args)


def send_verify_email(args={}):
    from requests import post
    from ..util.util import quiet_print
    from .consts import oc_publish_url
    from ..exceptions import StoreServerError

    username = args.get("email")
    reset_pw_url = oc_publish_url + "/verify-email"
    r = post(reset_pw_url, params={"username": username})
    if r.status_code == 500:
        raise StoreServerError(status_code=r.status_code)
    if r.text:
        quiet_print(r.text, args=args)


def create_account(args={}):
    from .consts import oc_publish_url
    from ..util.util import quiet_print
    from requests import post

    create_account_url = oc_publish_url + "/create-account"
    username = args.get("username")
    password = args.get("password")
    if not username or not password:
        return
    d = {"username": username, "password": password}
    r = post(create_account_url, json=d)
    if r.status_code == 200:
        quiet_print(f"success", args=args)
        return True
    quiet_print(f"fail. {r.text}", args=args)
    return False
