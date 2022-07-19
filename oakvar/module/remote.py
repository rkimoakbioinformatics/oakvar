from typing import Optional
from typing import Tuple


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
        }
        return d

    def to_dict(self):
        d = {
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

    def __init__(self, __name__, **kwargs):
        from ..store import get_developer_dict
        from ..util.util import get_latest_version
        from ..store.db import module_code_versions
        from ..store.db import module_data_versions
        from ..store.db import module_data_sources
        from ..store.db import module_sizes
        from ..system import get_logo_path
        from os.path import exists

        self.name = kwargs.get("name") or ""
        self.store = kwargs.get("store") or "ov"
        self.conf = get_conf(self.name)
        if not self.conf:
            return
        self.groups = self.conf.get("groups", {})
        self.output_columns = self.conf.get("output_columns", [])
        self.code_versions = module_code_versions(self.name) or []
        self.data_versions = module_data_versions(self.name) or []
        self.data_sources = module_data_sources(self.name) or []
        self.make_versions()
        self.latest_code_version = get_latest_version(self.code_versions)
        self.latest_data_version = self.versions[self.latest_code_version][
            "data_version"
        ]
        self.latest_data_source = self.versions[self.latest_code_version]["data_source"]
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
        self.has_logo = exists(get_logo_path(self.name, self.store))


def get_conf(module_name: str) -> Optional[dict]:
    from ..system import get_cache_dir
    from os.path import join
    from os.path import exists
    from json import load

    for store in ["ov", "oc"]:
        fpath = join(get_cache_dir("conf"), store, module_name + ".json")
        if exists(fpath):
            with open(fpath) as f:
                conf = load(f)
                return conf
    return None


def get_readme(module_name: str) -> Optional[str]:
    from ..system import get_cache_dir
    from os.path import join
    from os.path import exists

    for store in ["ov", "oc"]:
        fpath = join(get_cache_dir("readme"), store, module_name)
        if exists(fpath):
            with open(fpath) as f:
                out = "\n".join(f.readlines())
                return out
    return None


def get_install_deps(
    module_name, version=None, skip_installed=True
) -> Tuple[dict, dict]:
    from distutils.version import LooseVersion
    from pkg_resources import Requirement
    from .local import get_local_module_info
    from ..store import remote_module_latest_version

    # If input module version not provided, set to highest
    if version is None:
        version = remote_module_latest_version(module_name)
    config = get_conf(module_name) or {}
    if not config:
        return {}, {}
    req_list = config.get("requires", [])
    deps = {}
    for req_string in req_list:
        req = Requirement.parse(req_string)
        rem_info = get_remote_module_info(req.unsafe_name)
        # Skip if module does not exist
        if rem_info and get_local_module_info(req.unsafe_name) is None:
            continue
        if skip_installed:
            # Skip if a matching version is installed
            local_info = get_local_module_info(req.unsafe_name)
            if local_info and local_info.version and local_info.version in req:
                continue
        # Select the highest matching version
        lvers = []
        if rem_info and rem_info.versions is not None:
            lvers = [LooseVersion(v) for v in rem_info.versions]
        lvers.sort(reverse=True)
        highest_matching = None
        for lv in lvers:
            if lv.vstring in req:
                highest_matching = lv.vstring
                break
        # Dont include if no matching version exists
        if highest_matching:
            deps[req.unsafe_name] = highest_matching
    req_pypi_list = config.get("requires_pypi", [])
    req_pypi_list.extend(config.get("pypi_dependency", []))
    deps_pypi = {}
    for req_pypi in req_pypi_list:
        deps_pypi[req_pypi] = True
    return deps, deps_pypi


def search_remote(*patterns, module_type=None):
    from re import fullmatch
    from . import list_remote

    matching_names = []
    l = list_remote(module_type=module_type)
    for module_name in l:
        if any([fullmatch(pattern, module_name) for pattern in patterns]):
            matching_names.append(module_name)
    matching_names.sort()
    return matching_names


def get_remote_module_info(module_name, version=None) -> Optional[RemoteModule]:
    from .cache import get_module_cache
    from ..store import remote_module_info_latest_version

    mc = get_module_cache()
    if module_name not in mc.remote:
        mc.remote[module_name] = {}
    if version in mc.remote[module_name]:
        return mc.remote[module_name][version]
    else:
        module_info = remote_module_info_latest_version(module_name)
        return module_info


def get_remote_module_readme(module_name, version=None):
    from .cache import get_module_cache

    return get_module_cache().get_remote_readme(module_name, version=version)


def get_remote_module_infos_of_type(t):
    from .cache import get_module_cache

    mic = get_module_cache()
    if mic and mic.remote:
        modules = {}
        for module_name in mic.remote:
            if mic.remote[module_name]["type"] == t:
                modules[module_name] = mic.remote[module_name]
        return modules
    return None
