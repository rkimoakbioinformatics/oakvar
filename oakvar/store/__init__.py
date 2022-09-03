from typing import Optional
from ..module.remote import RemoteModule
from ..module.remote import RemoteModuleLs


def blank_stage_handler(*__args__, **__kwargs__):
    pass


class ProgressStager(object):
    """
    Calls stage_handler when total_size passes a total_size/total_stages
    increment.
    stage_handler must handle the following positional arguments:
        cur_stage, total_stages, cur_size, total_size
    """

    def __init__(self, total_size, total_stages=100, stage_handler=blank_stage_handler):
        self.first_block = True
        self.total_size = total_size
        self.total_stages = total_stages
        self.cur_size = 0
        self.cur_stage = 0
        self.stage_handler = stage_handler

    def get_cur_state(self):
        return (self.cur_stage, self.total_stages, self.cur_size, self.total_size)

    def increase_cur_size(self, dsize):
        self.cur_size += dsize
        self._update_stage()

    def set_cur_size(self, cur_size):
        self.cur_size = cur_size
        self._update_stage()

    def _update_stage(self):
        from math import floor

        old_stage = self.cur_stage
        self.cur_stage = floor(self.cur_size / self.total_size * self.total_stages)
        if self.cur_stage != old_stage or self.first_block:
            self.first_block = False
            self.stage_handler(*self.get_cur_state())


def stream_multipart_post(url, fields, stage_handler=None, stages=50, **kwargs):
    """
    Post the fields in fields to the url in url using a streamed
    multipart/form-data request. Optionally pass in a callback function which
    is called when the uploaded size passes each of total_size/stages.
    """
    from requests_toolbelt.multipart.encoder import (
        MultipartEncoder,
        MultipartEncoderMonitor,
    )
    from requests import post

    encoder = MultipartEncoder(fields=fields)
    stager = ProgressStager(
        encoder.len, total_stages=stages, stage_handler=stage_handler
    )

    def stager_caller(monitor):
        stager.set_cur_size(monitor.bytes_read)

    monitor = MultipartEncoderMonitor(encoder, stager_caller)
    headers = {"Content-Type": monitor.content_type}
    r = post(url, data=monitor, headers=headers, **kwargs)  # type: ignore
    return r


def fetch_file_content_to_string(url):
    from requests import get
    from urllib.error import HTTPError

    try:
        r = get(url, timeout=(3, None))
        if r.status_code == 200:
            return r.text
        else:
            raise HTTPError(url, r.status_code, "", None, None)  # type: ignore
    except Exception as _:
        return ""


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


class ModuleArchiveBuilder(object):
    def __init__(self, archive_path, base_path=None):
        from os import getcwd
        from zipfile import ZipFile, ZIP_DEFLATED

        if base_path is None:
            base_path = getcwd()
        self._archive = ZipFile(archive_path, compression=ZIP_DEFLATED, mode="w")
        self._base_path = base_path
        self._manifest = {}

    def add_item(self, item_path):
        from os.path import relpath, isdir, join
        from os import listdir, sep

        rel_path = relpath(item_path, start=self._base_path)
        self._archive.write(item_path, str(rel_path))
        if isdir(item_path):
            for child_name in listdir(item_path):
                child_path = join(item_path, child_name)
                self.add_item(child_path)
        else:
            checksum = file_checksum(item_path)
            path_list = rel_path.split(sep)  # type: ignore
            nest_value_in_dict(self._manifest, checksum, path_list)

    def get_manifest(self):
        return self._manifest

    def close(self):
        self._archive.close()


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


def hash_password(password):
    from hashlib import sha256

    return sha256(password.encode()).hexdigest()


def client_error_json(error_class):
    from json import dumps

    return dumps({"code": error_class.code, "message": error_class.message})


def remote_module_latest_version(module_name) -> Optional[str]:
    from .db import module_latest_code_version

    version = module_latest_code_version(module_name)
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


def url(args={}):
    from .ov import get_store_url
    from ..util.util import quiet_print

    u = get_store_url()
    quiet_print(f"{u}", args=args)
    return u
