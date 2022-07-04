from typing import Optional


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


def stream_to_file(
    url, fpath, stage_handler=None, stages=50, install_state=None, **__kwargs__
):
    """
    Stream the content at a url to a file. Optionally pass in a callback
    function which is called when the uploaded size passes each of
    total_size/stages.
    """
    from requests import get
    from requests.exceptions import ConnectionError
    from ..exceptions import KillInstallException
    from types import SimpleNamespace

    try:
        r = get(url, stream=True, timeout=(3, None))
    except ConnectionError:
        r = SimpleNamespace()
        r.status_code = 503
    if r.status_code == 200:
        total_size = int(r.headers.get("content-length", 0))
        chunk_size = 8192
        stager = ProgressStager(
            total_size, total_stages=stages, stage_handler=stage_handler
        )
        with open(fpath, "wb") as wf:
            for chunk in r.iter_content(chunk_size):
                if install_state is not None and install_state["kill_signal"] == True:
                    raise KillInstallException()
                wf.write(chunk)
                stager.increase_cur_size(len(chunk))
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
    from .ov import module_latest_version

    version = module_latest_version(module_name)
    return version


def remote_module_info_latest_version(module_name) -> Optional[dict]:
    from .ov import module_info_latest_version

    module_info = module_info_latest_version(module_name)
    return module_info


def get_module_piece_url(
    module_name: str, kind=None, version=None, channel=None
) -> Optional[str]:
    if kind == None:
        return None
    if not version:
        version = remote_module_latest_version(module_name)
    if not version:
        return None
    from .ov import module_code_url
    from .ov import module_data_url
    from .ov import module_conf_url
    from .oc import oc_module_code_url
    from .oc import oc_module_data_url
    from .oc import oc_module_conf_url

    routes = {
        "code": {
            "ov": module_code_url,
            "oc": oc_module_code_url,
        },
        "data": {
            "ov": module_data_url,
            "oc": oc_module_data_url,
        },
        "config": {
            "ov": module_conf_url,
            "oc": oc_module_conf_url,
        },
    }
    funcs = routes.get(kind)
    if not funcs:
        return None
    if channel != "oc":
        # ov store
        print(f"@@ {funcs.get('ov')}")
        func = funcs.get("ov")
        print(f"@@")
        if not func:
            return None
        url = func(module_name, version=version)
        print(f"@ url={url}")
        if url or channel == "ov":
            return url
    # oc store
    func = funcs.get("oc")
    if not func:
        return None
    url = func(module_name, version=version)
    if url or channel == "ov":
        return url


def get_developer_dict(**kwargs):
    kwargs.setdefault("name", "")
    kwargs.setdefault("email", "")
    kwargs.setdefault("organization", "")
    kwargs.setdefault("citation", "")
    kwargs.setdefault("website", "")
    return {
        "name": kwargs["name"],
        "email": kwargs["email"],
        "organization": kwargs["organization"],
        "citation": kwargs["citation"],
        "website": kwargs["website"],
    }
