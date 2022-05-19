class PathBuilder(object):
    """
    Used to get routes to certain resources in the cravat-store download area.
    Returns path string in either url or file format.
    """

    _valid_path_types = set(["url", "file"])

    def __init__(self, base, path_type):
        self._base = base
        if path_type in self._valid_path_types:
            self.path_type = path_type
        else:
            raise RuntimeError("Invalid path type: %s" % path_type)

    def _build_path(self, *path_toks):
        from os.path import join

        if self.path_type == "url":
            return "/".join(path_toks)
        elif self.path_type == "file":
            return join(*path_toks)

    def base(self):
        return self._build_path(self._base)

    def module_dir(self, module_name):
        return self._build_path(self.base(), "modules", module_name)

    def module_version_dir(self, module_name, version):
        return self._build_path(self.module_dir(module_name), version)

    def module_conf(self, module_name, version):
        return self._build_path(
            self.module_version_dir(module_name, version), module_name + ".yml"
        )

    def module_readme(self, module_name, version):
        return self._build_path(
            self.module_version_dir(module_name, version), module_name + ".md"
        )

    def module_code(self, module_name, version):
        return self._build_path(
            self.module_version_dir(module_name, version), module_name + ".code.zip"
        )

    def module_code_manifest(self, module_name, version):
        return self._build_path(
            self.module_version_dir(module_name, version),
            module_name + ".code.manifest.yml",
        )

    def module_data(self, module_name, version):
        return self._build_path(
            self.module_version_dir(module_name, version), module_name + ".data.zip"
        )

    def module_data_manifest(self, module_name, version):
        return self._build_path(
            self.module_version_dir(module_name, version),
            module_name + ".data.manifest.yml",
        )

    def module_logo(self, module_name, version):
        return self._build_path(
            self.module_version_dir(module_name, version), "logo.png"
        )

    def module_meta(self, module_name, version):
        return self._build_path(
            self.module_version_dir(module_name, version), "meta.yml"
        )

    def manifest(self, version=None):
        from pkg_resources import get_distribution

        if version is None:
            version = get_distribution("oakvar").version
        fname = "manifest-{}.yml".format(version)
        return self._build_path(self.base(), fname)

    def manifest_nover(self):
        return self._build_path(self.base(), "manifest.yml")

    def download_counts(self):
        return self._build_path(self.base(), "download-counts.yml")


def blank_stage_handler(*args, **kwargs):
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
    r = post(url, data=monitor, headers=headers, **kwargs)
    return r


def stream_to_file(
    url, fpath, stage_handler=None, stages=50, install_state=None, **kwargs
):
    """
    Stream the content at a url to a file. Optionally pass in a callback
    function which is called when the uploaded size passes each of
    total_size/stages.
    """
    from requests import get
    from requests.exceptions import ConnectionError
    from .constants import KillInstallException
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


def get_file_to_string(url):
    from requests import get
    from urllib.error import HTTPError

    try:
        r = get(url, timeout=(3, None))
        if r.status_code == 200:
            return r.text
        else:
            raise HTTPError(url, r.status_code, "", None, None)
    except Exception as e:
        return ""


def file_checksum(path):
    """
    Get the md5 checksum of a file.
    """
    from hashlib import md5

    if os.path.isdir(path):
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
        self._archive.write(item_path, rel_path)
        if isdir(item_path):
            for child_name in listdir(item_path):
                child_path = join(item_path, child_name)
                self.add_item(child_path)
        else:
            checksum = file_checksum(item_path)
            path_list = rel_path.split(sep)
            nest_value_in_dict(self._manifest, checksum, path_list)

    def get_manifest(self):
        return self._manifest

    def close(self):
        self._archive.close()


def add_to_zipfile(full_path, zf, start=None, compress_type=None):
    """
    Recursively add files to a zipfile. Optionally making the path within
    the zipfile relative to a base_path, default is curdir.
    """
    from os.path import relpath, isdir, join
    from os import curdir, listdir
    from zipfile import ZIP_DEFLATED

    if compress_type is None:
        compress_type = ZIP_DEFLATED
    if start is None:
        start = curdir
    rel_path = relpath(full_path, start=start)
    zf.write(full_path, arcname=rel_path, compress_type=compress_type)
    if isdir(full_path):
        for item_name in listdir(full_path):
            item_path = join(full_path, item_name)
            add_to_zipfile(item_path, zf, start=start, compress_type=compress_type)


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
    from .constants import FileIntegrityError

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


class ClientError(object):
    code = 0
    message = "Unspecified client error"


class InvalidModuleName(ClientError):
    code = 1
    message = "Invalid module name"


class InvalidVersionNumber(ClientError):
    code = 2
    message = "Invalid version number"


class WrongDeveloper(ClientError):
    code = 3
    message = "Developer does not have permission to edit this module"


class VersionExists(ClientError):
    code = 4
    message = "Version already exists"


class VersionDecrease(ClientError):
    code = 5
    message = "Version must increase"


class EmailUnverified(ClientError):
    code = 6
    message = "Email address unverified. Check your email for instructions to verify your email address"


class NoSuchModule(ClientError):
    code = 7
    message = "Module does not exist"


def client_error_json(error_class):
    from json import dumps

    return dumps({"code": error_class.code, "message": error_class.message})
