from typing import Optional
from ..module.remote import RemoteModule
from ..module.remote import RemoteModuleLs
from . import ov as ov
from . import consts as consts
from . import db as db


def file_checksum(path):
    """
    Get the md5 checksum of a file.
    """
    from hashlib import md5
    from os.path import isdir

    if isdir(path):
        raise IsADirectoryError(path)
    hasher = md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(256 * hasher.block_size), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def nest_value_in_dict(d, v, keys):
    """
    Put the value v, into dictionary d at the location defined by the list of
    keys in keys.

    Ex: d = {'a':{'b':{'c':1}}}, v = 2, keys = ['a','b','d']
        results in:
        d = {'a':{'b':{'c':1,'d':2}}}
    """
    top_key = keys[0]
    if len(keys) == 1:
        d[top_key] = v
    else:
        if top_key not in d:
            d[top_key] = {}
        nest_value_in_dict(d[top_key], v, keys[1:])


def verify_against_manifest(dirpath, manifest):
    """
    Verify that the files in manifest exist and have the right cksum.
    Return True if all pass, throw FileIntegrityError otherwise.
    """
    from os.path import join, exists, isdir
    from ..exceptions import FileIntegrityError

    correct = True
    for item_name, v in manifest.items():
        item_path = join(dirpath, item_name)
        if exists(item_path):
            if type(v) == dict:
                correct = isdir(item_path) and verify_against_manifest(item_path, v)
            else:
                correct = v == file_checksum(item_path)
        else:
            correct = False
        if not (correct):
            raise (FileIntegrityError(item_path))
    return correct


def remote_module_latest_version(module_name) -> Optional[str]:
    from .db import get_latest_module_code_version

    version = get_latest_module_code_version(module_name)
    return version


def remote_module_info_ls_latest_version(module_name) -> Optional[RemoteModuleLs]:
    from .db import module_info_ls

    module_info = module_info_ls(module_name)
    return module_info


def remote_module_info_latest_version(module_name) -> Optional[RemoteModule]:
    from .db import module_info

    module_info = module_info(module_name)
    return module_info


def get_module_urls(module_name: str, code_version=None) -> Optional[dict]:
    from .db import get_urls

    if not code_version:
        code_version = remote_module_latest_version(module_name)
    if not code_version:
        return None
    return get_urls(module_name, code_version)


def get_developer_dict(kwargs):
    if "module" in kwargs:
        return {
            "module": {
                "name": kwargs.get("module", {}).get("name", ""),
                "email": kwargs.get("module", {}).get("email", ""),
                "organization": kwargs.get("module", {}).get("organization", ""),
                "citation": kwargs.get("module", {}).get("citation", ""),
                "website": kwargs.get("module", {}).get("website", ""),
            },
            "data": {
                "name": kwargs.get("data", {}).get("name", ""),
                "email": kwargs.get("data", {}).get("email", ""),
                "organization": kwargs.get("data", {}).get("organization", ""),
                "citation": kwargs.get("data", {}).get("citation", ""),
                "website": kwargs.get("data", {}).get("website", ""),
            },
        }
    else:
        return {
            "module": {
                "name": kwargs.get("name", ""),
                "email": kwargs.get("email", ""),
                "organization": kwargs.get("organization", ""),
                "citation": kwargs.get("citation", ""),
                "website": kwargs.get("website", ""),
            },
            "data": {
                "name": "",
                "email": "",
                "organization": "",
                "citation": "",
                "website": "",
            },
        }


def url(url: str = "", outer=None) -> str:
    from .ov import get_store_url
    from .ov import set_store_url

    if url:
        set_store_url(url)
        u = url
    else:
        u = get_store_url()
        if outer:
            outer.write(f"{u}")
    return u
