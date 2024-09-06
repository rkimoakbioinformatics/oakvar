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

from typing import Any
from typing import Optional
from typing import Dict
from typing import Tuple
from typing import List
from pathlib import Path


class RemoteModuleLs:
    def __init__(self, __name__, **kwargs):
        from json import loads
        from ..store.db import latest_module_version_size

        self.name = kwargs.get("name") or ""
        self.title = kwargs.get("title")
        self.type = kwargs.get("type")
        latest = latest_module_version_size(self.name)
        if not latest:
            return
        self.size = latest["code_size"] + latest["data_size"]
        self.latest_code_version = latest["code_version"]
        self.latest_data_source = latest["data_source"]
        self.latest_data_version = latest["data_version"]
        tags: str = kwargs.get("tags") or "[]"
        self.tags: List[str] = loads(tags)
        self.installed = False
        self.local_code_version = ""
        self.local_data_source = ""


class RemoteModule(object):
    def to_info(self):
        d = {
            "name": self.name,
            "title": self.title,
            "description": self.description,
            "type": self.type,
            "size": self.size,
            "tags": self.tags,
            "versions": self.versions,
            "developer": self.developer,
            "groups": self.groups,
            "output_columns": self.output_columns,
            "requires": self.requires,
            "latest_version": self.latest_code_version,
            "min_pkg_ver": self.min_pkg_ver,
        }
        return d

    def to_dict(self):
        d = {
            "name": self.name,
            "groups": self.groups,
            "output_columns": self.output_columns,
            "developer": self.developer,
            "title": self.title,
            "type": self.type,
            "tags": self.tags,
            "size": self.size,
            "publish_time": self.publish_time,
            "has_logo": self.has_logo,
            "store": self.store,
            "requires": self.requires,
            "latest_version": self.latest_code_version,
            "min_pkg_ver": self.min_pkg_ver,
            "conf": self.conf,
        }
        return d

    def make_versions(self):
        self.versions = {}
        for code_version in self.code_versions:
            self.versions[code_version] = {}
        if self.data_versions:
            for code_version, data_version in zip(
                self.code_versions, self.data_versions
            ):
                self.versions[code_version]["data_version"] = data_version
        else:
            for code_version in self.code_versions:
                self.versions[code_version]["data_version"] = ""
        if self.data_sources:
            for code_version, data_source in zip(self.code_versions, self.data_sources):
                self.versions[code_version]["data_source"] = data_source
        else:
            for code_version in self.code_versions:
                self.versions[code_version]["data_source"] = ""
        if self.min_pkg_vers:
            for code_version, min_pkg_ver in zip(self.code_versions, self.min_pkg_vers):
                self.versions[code_version]["min_pkg_ver"] = min_pkg_ver
        else:
            for code_version in self.min_pkg_vers:
                self.versions[code_version]["min_pkg_ver"] = ""

    def __init__(self, __name__, **kwargs):
        from ..store import get_developer_dict
        from ..util.util import get_latest_version
        from ..store.db import module_code_versions
        from ..store.db import module_data_versions
        from ..store.db import module_data_sources
        from ..store.db import module_min_pkg_vers
        from ..store.db import module_sizes
        from ..system import get_logo_path
        from os.path import exists
        from os.path import getsize

        self.name = kwargs.get("name") or ""
        self.store = kwargs.get("store") or "ov"
        self.conf = get_conf(module_name=self.name) or {}
        self.groups = self.conf.get("groups", [])
        self.output_columns = self.conf.get("output_columns", [])
        self.code_versions = module_code_versions(self.name) or []
        self.data_versions = module_data_versions(self.name) or []
        self.data_sources = module_data_sources(self.name) or []
        self.min_pkg_vers = module_min_pkg_vers(self.name) or []
        self.make_versions()
        self.latest_code_version = get_latest_version(self.code_versions)
        self.latest_data_version = self.versions[self.latest_code_version][
            "data_version"
        ]
        self.latest_data_source = self.versions[self.latest_code_version]["data_source"]
        self.min_pkg_ver = self.versions[self.latest_code_version]["min_pkg_ver"]
        self.code_size, self.data_size = module_sizes(
            self.name, self.latest_code_version
        ) or (0, 0)
        self.size = self.code_size + self.data_size
        self.type = kwargs.get("type")
        self.title = kwargs.get("title")
        self.description = self.conf.get("description", "")
        self.hidden = self.conf.get("hidden")
        self.tags = self.conf.get("tags", [])
        self.publish_time = kwargs.get("publish_time")
        self.developer = get_developer_dict(self.conf.get("developer", {}))
        self.requires = self.conf.get("requires", [])
        self.installed: Optional[str] = None
        self.local_code_version: Optional[str] = None
        self.local_data_source: Optional[str] = None
        logo_path = get_logo_path(self.name, self.store)
        self.has_logo = logo_path and exists(logo_path) and getsize(logo_path) > 0


def get_conf(
    module_name: Optional[str] = None, conf_path: Optional[Path] = None
) -> Optional[dict]:
    from ..system import get_cache_dir
    from json import load
    from oyaml import safe_load

    fpath: Optional[Path] = None
    if not module_name and not conf_path:
        return fpath
    if conf_path and conf_path.exists():
        fpath = conf_path
    cache_dir = get_cache_dir("conf")
    if not cache_dir:
        return None
    if not fpath and module_name:
        for store in ["ov", "oc"]:
            tmp_fpath: Path = cache_dir / store / (module_name + ".json")
            if tmp_fpath.exists():
                fpath = tmp_fpath
                break
    if fpath and fpath.exists():
        with open(fpath) as f:
            conf: Optional[Dict[str, Any]] = None
            if fpath.suffix == ".yml":
                conf = safe_load(f)
            elif fpath.suffix == ".json":
                conf = load(f)
            if conf:
                conf["name"] = fpath.stem
            return conf
    return None


def get_readme(module_name: str) -> Optional[str]:
    from ..system import get_cache_dir
    from ..store.db import find_name_store
    from ..exceptions import SystemMissingException

    ret = find_name_store(module_name)
    if not ret:
        return None
    _, store = ret
    readme_dir = get_cache_dir("readme")
    if not readme_dir:
        raise SystemMissingException(
            msg="readme directory is missing. Consider running `ov system setup`?"
        )
    fpath = readme_dir / store / module_name
    if fpath.exists():
        with open(fpath, encoding="utf-8") as f:
            out = f.readlines()
            out = "".join(out)
            return out
    return None


def get_install_deps(
    module_name=None,
    version=None,
    conf_path: Optional[Path] = None,
    skip_installed=True,
) -> Tuple[dict, list]:
    from pkg_resources import Requirement
    from .local import get_local_module_info
    from ..store import remote_module_latest_version
    from ..util.util import get_latest_version
    from . import get_pypi_dependency_from_conf

    config = None
    if not module_name and not conf_path:
        return {}, []
    if not version:
        version = remote_module_latest_version(module_name)
    if conf_path:
        config = get_conf(conf_path=conf_path)
    elif module_name:
        config = get_conf(module_name=module_name) or {}
    if not config:
        return {}, []
    if not module_name:
        module_name = config.get("name")
    if not version:
        version = config.get("version")
    if not module_name:
        raise Exception(f"{module_name} cannot be found.")
    if not version:
        raise Exception(f"latest version of {module_name} cannot be found.")
    req_list = config.get("requires", []) or []
    deps = {}
    for req_string in req_list:
        req = Requirement.parse(req_string)
        rem_info = get_remote_module_info(req.unsafe_name)
        if not rem_info:
            continue
        local_info = get_local_module_info(req.unsafe_name)
        if skip_installed and local_info:
            continue
        if local_info and local_info.version and local_info.version in req:
            continue
        highest_matching = get_latest_version(rem_info.versions)
        if highest_matching:
            deps[req.unsafe_name] = highest_matching
    req_pypi_list = get_pypi_dependency_from_conf(config)
    deps_pypi = []
    for req_pypi in req_pypi_list:
        if req_pypi not in deps_pypi:
            deps_pypi.append(req_pypi)
    return deps, deps_pypi


def search_remote(*patterns, module_type=None):
    from re import fullmatch
    from . import list_remote

    matching_names = []
    module_names = list_remote(module_type=module_type)
    for module_name in module_names:
        if any([fullmatch(pattern, module_name) for pattern in patterns]):
            matching_names.append(module_name)
    matching_names.sort()
    return matching_names


def get_remote_module_info_ls(module_name, version=None) -> Optional[RemoteModuleLs]:
    from .cache import get_module_cache
    from ..store import remote_module_info_ls_latest_version

    mc = get_module_cache()
    if module_name not in mc.remote:
        mc.remote_ls[module_name] = {}
    if version in mc.remote_ls[module_name]:
        return mc.remote_ls[module_name][version]
    else:
        module_info = remote_module_info_ls_latest_version(module_name)
        return module_info


def get_remote_module_info(module_name) -> Optional[RemoteModule]:
    from .cache import get_module_cache
    from ..store import remote_module_info_latest_version

    mc = get_module_cache()
    if module_name not in mc.remote:
        module_info = remote_module_info_latest_version(module_name)
        mc.remote[module_name] = module_info
    return mc.remote[module_name]


def save_remote_manifest_cache(content):
    import pickle
    from ..store.db import get_remote_manifest_cache_path

    path = get_remote_manifest_cache_path()
    if path:
        with open(path, "wb") as wf:
            pickle.dump(content, wf)


def make_remote_manifest(refresh: bool = False):
    from ..store.db import get_manifest
    from ..store.db import get_remote_manifest_cache_path
    from ..consts import module_tag_desc
    from traceback import print_exc

    content = {}
    content["tagdesc"] = module_tag_desc
    try:
        manifest = get_manifest()
        if manifest:
            content["data"] = manifest
    except Exception:
        print_exc()
        content = {"data": {}}
    path = get_remote_manifest_cache_path()
    if refresh or path is None or not path.exists():
        save_remote_manifest_cache(content)
    return content
