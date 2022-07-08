from typing import Optional
from typing import Tuple


class RemoteModuleInfo(object):
    def to_dict(self):
        d = {
            "groups": self.groups,
            "output_columns": self.output_columns,
            "developer": self.developer,
            "title": self.title,
            "type": self.type,
            "tags": self.tags,
            "logo": self.logo,
            "size": self.size,
            "publish_time": self.publish_time,
        }
        return d

    def __init__(self, __name__, **kwargs):
        from ..store import get_developer_dict
        from ..util.util import get_latest_version
        from json import loads

        self.data = kwargs
        self.conf = loads(self.data.get("conf") or "{}")
        self.groups = self.conf.get("groups", {})
        self.output_columns = self.conf.get("output_columns", [])
        self.code_sizes = loads(self.data.get("code_sizes", "{}"))
        self.data_sizes = loads(self.data.get("data_sizes", "{}"))
        self.data_sources = loads(self.data.get("data_sources", "{}"))
        self.data_versions = loads(self.data.get("data_versions", "{}"))
        self.logo = self.data.get("logo", "")
        self.name = self.data.get("name")
        self.versions = self.data.get("versions", [])
        self.code_versions = loads(self.data.get("code_versions", "[]"))
        self.latest_version = get_latest_version(self.code_versions)
        self.type = self.data.get("type")
        self.title = self.data.get("title")
        self.description = self.conf.get("description", "")
        self.code_size = self.code_sizes.get(self.latest_version, 0)
        self.data_size = self.data_sizes.get(self.latest_version, 0)
        self.size = self.code_size + self.data_size
        self.datasource = self.data_sources.get(self.latest_version, "")
        self.hidden = self.conf.get("hidden")
        self.tags = loads(self.data.get("tags", "[]"))
        self.publish_time = self.data.get("publish_time")
        self.developer = self.conf.get("developer", {})
        self.developer = get_developer_dict(**self.developer)
        self.installed: Optional[str] = None
        self.local_version: Optional[str] = None
        self.local_datasource: Optional[str] = None

    def has_version(self, version):
        return version in self.versions


def get_install_deps(
    module_name, version=None, skip_installed=True
) -> Tuple[dict, dict]:
    from distutils.version import LooseVersion
    from pkg_resources import Requirement
    from .local import get_local_module_info
    from .cache import get_module_cache
    from ..store import remote_module_latest_version

    # If input module version not provided, set to highest
    if version is None:
        version = remote_module_latest_version(module_name)
    config = get_module_cache().get_remote_module_piece_content(
        module_name, "config", version=version
    )
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


def search_remote(*patterns):
    from re import fullmatch
    from . import list_remote

    matching_names = []
    l = list_remote()
    for module_name in l:
        if any([fullmatch(pattern, module_name) for pattern in patterns]):
            matching_names.append(module_name)
    return matching_names


def get_remote_module_info(module_name, version=None) -> Optional[RemoteModuleInfo]:
    from .cache import get_module_cache
    from ..store import remote_module_info_latest_version

    mc = get_module_cache()
    if module_name not in mc.remote:
        mc.remote[module_name] = {}
    if version in mc.remote[module_name]:
        return mc.remote[module_name][version]
    else:
        module_info = remote_module_info_latest_version(module_name)
        """
        if module_info:
            module_info = RemoteModuleInfo(module_name, **module_info)
        else:
            module_info = RemoteModuleInfo(module_name)
        module_info.name = module_name
        """
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
