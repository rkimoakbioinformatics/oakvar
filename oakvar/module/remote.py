from typing import Optional
from typing import Tuple


class RemoteModuleInfo(object):
    def __init__(self, __name__, **kwargs):
        from ..store import get_developer_dict

        self.data = kwargs
        self.data.setdefault("versions", [])
        self.data.setdefault("latest_version", "")
        self.data.setdefault("type", "")
        self.data.setdefault("title", "")
        self.data.setdefault("description", "")
        self.data.setdefault("size", "")
        self.data.setdefault("data_size", 0)
        self.data.setdefault("code_size", 0)
        self.data.setdefault("datasource", "")
        self.data.setdefault("hidden", False)
        self.data.setdefault("developer", {})
        self.data.setdefault("data_versions", {})
        self.data.setdefault("data_sources", {})
        self.data.setdefault("tags", [])
        self.data.setdefault("publish_time", None)
        self.name = self.data.get("name")
        self.versions = self.data.get("versions", [])
        self.latest_version = self.data.get("latest_version", "")
        self.type = self.data.get("type")
        self.title = self.data.get("title")
        self.description = self.data.get("description")
        self.size = self.data.get("size")
        self.data_size = self.data.get("data_size")
        self.code_size = self.data.get("code_size")
        self.datasource = self.data.get("datasource")
        self.data_versions = self.data.get("data_versions", {})
        self.hidden = self.data.get("hidden")
        self.tags = self.data.get("tags")
        self.publish_time = self.data.get("publish_time")
        dev_dict = self.data.get("developer", {})
        self.developer = get_developer_dict(**dev_dict)
        self.data_sources = {
            x: str(y) for x, y in self.data.get("data_sources").items()  # type: ignore
        }
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


def get_remote_module_info(module_name, version=None) -> RemoteModuleInfo:
    from .cache import get_module_cache
    from ..store import remote_module_info_latest_version

    mc = get_module_cache()
    if module_name not in mc.remote:
        mc.remote[module_name] = {}
    if version in mc.remote[module_name]:
        return mc.remote[module_name][version]
    else:
        module_info = remote_module_info_latest_version(module_name)
        if module_info:
            module_info = RemoteModuleInfo(module_name, **module_info)
        else:
            module_info = RemoteModuleInfo(module_name)
        module_info.name = module_name
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
