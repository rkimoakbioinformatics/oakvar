from collections.abc import MutableMapping


class InstallProgressHandler(object):
    def __init__(self, module_name, module_version):
        self.module_name = module_name
        self.module_version = module_version
        self._make_display_name()
        self.cur_stage = None

    def _make_display_name(self):
        ver_str = self.module_version if self.module_version is not None else ""
        self.display_name = ":".join([self.module_name, ver_str])

    def stage_start(self, stage):
        pass

    def stage_progress(self, cur_chunk, total_chunks, cur_size, total_size):
        pass

    def set_module_version(self, module_version):
        self.module_version = module_version
        self._make_display_name()

    def set_module_name(self, module_name):
        self.module_name = module_name
        self._make_display_name()

    def _stage_msg(self, stage):
        from oakvar.util import get_current_time_str

        if stage is None or stage == "":
            return ""
        elif stage == "start":
            return (
                f"[{get_current_time_str()}] Starting to install {self.display_name}..."
            )
        elif stage == "download_code":
            return f"[{get_current_time_str()}] Downloading code archive of {self.display_name}..."
        elif stage == "extract_code":
            return f"[{get_current_time_str()}] Extracting code archive of {self.display_name}..."
        elif stage == "verify_code":
            return f"[{get_current_time_str()}] Verifying code integrity of {self.display_name}..."
        elif stage == "download_data":
            return (
                f"[{get_current_time_str()}] Downloading data of {self.display_name}..."
            )
        elif stage == "extract_data":
            return (
                f"[{get_current_time_str()}] Extracting data of {self.display_name}..."
            )
        elif stage == "verify_data":
            return f"[{get_current_time_str()}] Verifying data integrity of {self.display_name}..."
        elif stage == "finish":
            return f"[{get_current_time_str()}] Finished installation of {self.display_name}"
        elif stage == "killed":
            return f"[{get_current_time_str()}] Aborted installation of {self.display_name}"
        elif stage == "Unqueued":
            return f"Unqueued {self.display_name} from installation"
        else:
            raise ValueError(stage)


class LocalInfoCache(MutableMapping):
    """
    LocalInfoCache will initially store the paths to modules. When a module info
    is requested, the module info will be created from the path, stored, and returned.
    LocalInfoCache exposes the same interface as a dictionary.
    """

    def __init__(self, *args, **kwargs):
        self.store = dict()
        self.update(dict(*args, **kwargs))  # use the free update to set keys

    def __getitem__(self, key):
        if key not in self.store:
            raise KeyError(key)
        if not isinstance(self.store[key], LocalModuleInfo):
            self.store[key] = LocalModuleInfo(self.store[key])
        return self.store[key]

    def __setitem__(self, key, value):
        import os

        if not (isinstance(value, LocalModuleInfo) or os.path.isdir(value)):
            raise ValueError(value)
        self.store[key] = value

    def __delitem__(self, key):
        del self.store[key]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)


class LocalModuleInfo(object):
    def __init__(self, dir_path, module_type=None, name=None):
        import os

        self.directory = dir_path
        if name is None:
            self.name = os.path.basename(self.directory)
        else:
            self.name = name
        self.script_path = os.path.join(self.directory, self.name + ".py")
        self.script_exists = os.path.exists(self.script_path)
        self.conf_path = os.path.join(self.directory, self.name + ".yml")
        self.conf_exists = os.path.exists(self.conf_path)
        self.exists = self.conf_exists
        startofinstall_path = os.path.join(self.directory, "startofinstall")
        if os.path.exists(startofinstall_path):
            endofinstall_path = os.path.join(self.directory, "endofinstall")
            if os.path.exists(endofinstall_path):
                self.exists = True
            else:
                self.exists = False
        self.data_dir = os.path.join(dir_path, "data")
        self.data_dir_exists = os.path.isdir(self.data_dir)
        self.has_data = self.data_dir_exists and len(os.listdir(self.data_dir)) > 0
        self.test_dir = os.path.join(dir_path, "test")
        self.test_dir_exists = os.path.isdir(self.test_dir)
        self.tests = self.get_tests()
        self.has_test = len(self.tests) > 0
        self.readme_path = os.path.join(self.directory, self.name + ".md")
        self.readme_exists = os.path.exists(self.readme_path)
        if self.readme_exists:
            with open(self.readme_path, encoding="utf-8") as f:
                self.readme = f.read()
        else:
            self.readme = ""
        self.helphtml_path = os.path.join(self.directory, "help.html")
        self.helphtml_exists = os.path.exists(self.helphtml_path)
        self.conf = {}
        if self.conf_exists:
            self.conf = load_yml_conf(self.conf_path)
        self.type = self.conf.get("type")
        self.version = self.conf.get("version")
        self.description = self.conf.get("description")
        self.hidden = self.conf.get("hidden", False)
        dev_dict = self.conf.get("developer")
        if not (type(dev_dict) == dict):
            dev_dict = {}
        self.developer = get_developer_dict(**dev_dict)
        if "type" not in self.conf:
            self.conf["type"] = "unknown"
        self.type = self.conf["type"]
        self.level = self.conf.get("level")
        self.input_format = self.conf.get("input_format")
        self.secondary_module_names = list(self.conf.get("secondary_inputs", {}))
        if self.type == "annotator":
            if self.level == "variant":
                self.output_suffix = self.name + ".var"
            elif self.level == "gene":
                self.output_suffix = self.name + ".gen"
            else:
                self.output_suffix = self.name + "." + self.type
        self.title = self.conf.get("title", self.name)
        self.disk_size = None
        self.tags = self.conf.get("tags", [])
        self.datasource = str(self.conf.get("datasource", ""))
        self.smartfilters = self.conf.get("smartfilters")
        self.groups = self.conf.get("groups", [])

    def is_valid_module(self):
        r = self.exists
        r = r and self.name is not None
        r = r and self.conf_path is not None
        r = r and self.version is not None
        r = r and self.type is not None
        return r

    def get_size(self):
        """
        Gets the total installed size of a module
        """
        from oakvar.util import get_directory_size

        if self.disk_size is None:
            self.disk_size = get_directory_size(self.directory)
        return self.disk_size

    def get_tests(self):
        """
        Gets the module test input file(s) if the module has tests.  A test is a input file / key file pair.
        """
        import os

        tests = []
        if self.test_dir_exists:
            for i in os.listdir(self.test_dir):
                if (
                    "input" in i
                    and os.path.isfile(os.path.join(self.test_dir, i))
                    and os.path.isfile(
                        os.path.join(self.test_dir, i.replace("input", "key"))
                    )
                ):
                    tests.append(i)
        return tests

    def serialize(self):
        return self.__dict__


class ModuleInfoCache(object):
    def __init__(self):
        from oakvar.store_utils import PathBuilder

        self._sys_conf = get_system_conf()
        self._modules_dir = get_modules_dir()
        self.local = LocalInfoCache()
        self._remote_url = None
        self.remote = {}
        self._remote_fetched = False
        self.remote_readme = {}
        self.remote_config = {}
        self.update_local()
        self._store_path_builder = PathBuilder(self._sys_conf["store_url"], "url")
        self.download_counts = {}
        self._counts_fetched = False

    def get_local(self):
        modules_dir = get_modules_dir()
        if self._modules_dir != modules_dir:
            self._modules_dir = modules_dir
            self.update_local()
        return self.local

    def update_download_counts(self, force=False):
        import oyaml as yaml
        from oakvar.store_utils import get_file_to_string

        if force or not (self._counts_fetched):
            counts_url = self._store_path_builder.download_counts()
            counts_str = get_file_to_string(counts_url)
            if counts_str != "" and type(counts_str) != str:
                self.download_counts = yaml.safe_load(counts_str).get("modules", {})
                self._counts_fetched = True
            else:
                self._counts_fetched = False

    def update_local(self):
        import os
        from .constants import install_tempdir_name

        self.local = LocalInfoCache()
        self._modules_dir = get_modules_dir()
        if not (os.path.exists(self._modules_dir)):
            return None
        for mg in os.listdir(self._modules_dir):
            if mg == install_tempdir_name:
                continue
            mg_path = os.path.join(self._modules_dir, mg)
            basename = os.path.basename(mg_path)
            if (
                not (os.path.isdir(mg_path))
                or basename.startswith(".")
                or basename.startswith("_")
            ):
                continue
            for module_name in os.listdir(mg_path):
                if module_name == "hgvs":  # deprecate hgvs
                    continue
                module_dir = os.path.join(mg_path, module_name)
                if (
                    module_dir.startswith(".") == False
                    and os.path.isdir(module_dir)
                    and not module_name.startswith(".")
                    and not module_name.startswith("_")
                    and os.path.exists(os.path.join(module_dir, module_name + ".yml"))
                ):
                    self.local[module_name] = module_dir

    def update_remote(self, force=False):
        import sys
        import oyaml as yaml
        from oakvar.store_utils import get_file_to_string

        if force or not (self._remote_fetched):
            if self._remote_url is None:
                self._remote_url = self._store_path_builder.manifest()
                manifest_str = get_file_to_string(self._remote_url)
                # Current version may not have a manifest if it's a dev version
                if not manifest_str:
                    self._remote_url = self._store_path_builder.manifest_nover()
                    manifest_str = get_file_to_string(self._remote_url)
            else:
                manifest_str = get_file_to_string(self._remote_url)
            self.remote = {}
            if manifest_str != "" and type(manifest_str) == str:
                self.remote = yaml.safe_load(manifest_str)
                self.remote.pop("hgvs", None)  # deprecate hgvs annotator
            else:
                msg = f"WARNING: Could not list modules from {self._remote_url}. The store or the internet connection can be off-line."
                print(msg, file=sys.stderr)
            self._remote_fetched = True

    def get_remote_readme(self, module_name, version=None):
        from oakvar.store_utils import get_file_to_string

        self.update_remote()
        # Resolve name and version
        if module_name not in self.remote:
            raise LookupError(module_name)
        if version != None and version not in self.remote[module_name]["versions"]:
            raise LookupError(version)
        if version == None:
            version = self.remote[module_name]["latest_version"]
        # Try for cache hit
        try:
            readme = self.remote_readme[module_name][version]
            return readme
        except LookupError:
            readme_url = self._store_path_builder.module_readme(module_name, version)
            readme = get_file_to_string(readme_url)
            # add to cache
            if module_name not in self.remote_readme:
                self.remote_readme[module_name] = {}
            self.remote_readme[module_name][version] = readme
        return readme

    def get_remote_config(self, module_name, version=None):
        import oyaml as yaml
        from oakvar.store_utils import get_file_to_string

        self.update_remote()
        if version == None:
            version = self.remote[module_name]["latest_version"]
        # Check cache
        try:
            config = self.remote_config[module_name][version]
            return config
        except LookupError:
            config_url = self._store_path_builder.module_conf(module_name, version)
            config = yaml.safe_load(get_file_to_string(config_url))
            # add to cache
            if module_name not in self.remote_config:
                self.remote_config[module_name] = {}
            self.remote_config[module_name][version] = config
        return config


class ReadyState(object):

    READY = 0
    MISSING_MD = 1
    UPDATE_NEEDED = 2
    NO_BASE_MODULES = 3

    messages = {
        0: "",
        1: "Modules directory not found",
        2: 'Update on system modules needed. Run "oc module install-base"',
        3: "Base modules do not exist.",
    }

    def __init__(self, code=READY):
        if code not in self.messages:
            raise ValueError(code)
        self.code = code

    @property
    def message(self):
        return self.messages[self.code]

    def __bool__(self):
        return self.code == self.READY

    def __iter__(self):
        yield "ready", bool(self)
        yield "code", self.code
        yield "message", self.message


class RemoteModuleInfo(object):
    def __init__(self, name, **kwargs):
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
        self.versions = self.data.get("versions")
        self.latest_version = self.data.get("latest_version")
        self.type = self.data.get("type")
        self.title = self.data.get("title")
        self.description = self.data.get("description")
        self.size = self.data.get("size")
        self.data_size = self.data.get("data_size")
        self.code_size = self.data.get("code_size")
        self.datasource = self.data.get("datasource")
        self.data_versions = self.data.get("data_versions")
        self.hidden = self.data.get("hidden")
        self.tags = self.data.get("tags")
        self.publish_time = self.data.get("publish_time")
        # if self.datasource == None:
        #    self.datasource = ""
        dev_dict = self.data.get("developer")
        # if not (type(dev_dict) == dict):
        #    dev_dict = {}
        self.developer = get_developer_dict(**dev_dict)
        self.data_sources = {
            x: str(y) for x, y in self.data.get("data_sources").items()
        }

    def has_version(self, version):
        return version in self.versions


def change_password(username, cur_pw, new_pw):
    from requests import post

    sys_conf = get_system_conf()
    publish_url = sys_conf["publish_url"]
    change_pw_url = publish_url + "/change-password"
    r = post(change_pw_url, auth=(username, cur_pw), json={"newPassword": new_pw})
    if r.status_code == 500:
        print("Server error")
    elif r.status_code == 401:
        print("Incorrect username and password")
    if r.text:
        print(r.text)


def check_login(username, password):
    from requests import get

    sys_conf = get_system_conf()
    publish_url = sys_conf["publish_url"]
    login_url = publish_url + "/login"
    r = get(login_url, auth=(username, password))
    if r.status_code == 200:
        print("Correct username and password")
    elif r.status_code == 500:
        print("Server error")
    else:
        print("Incorrect username and password")


def compare_version(v1, v2):
    from distutils.version import LooseVersion

    sv1 = LooseVersion(v1)
    sv2 = LooseVersion(v2)
    if sv1 == sv2:
        return 0
    elif sv1 > sv2:
        return 1
    else:
        return -1


def create_account(username, password):
    from requests import post

    sys_conf = get_system_conf()
    publish_url = sys_conf["publish_url"]
    create_account_url = publish_url + "/create-account"
    d = {
        "username": username,
        "password": password,
    }
    r = post(create_account_url, json=d)
    if r.status_code == 500:
        print("Server error")
        return "server error"
    if r.text:
        print(r.text)
        return r.text


def get_annotator_dir(module_name):
    import os

    module_dir = os.path.join(get_modules_dir(), "annotators", module_name)
    if os.path.exists(module_dir) == False:
        module_dir = None
    return module_dir


def get_annotator_script_path(module_name):
    import os

    module_path = os.path.join(
        get_modules_dir(), "annotators", module_name, module_name + ".py"
    )
    if os.path.exists(module_path) == False:
        module_path = None
    return module_path


def get_conf_dir():
    from .constants import conf_dir_key

    conf = get_system_conf()
    conf_dir = conf[conf_dir_key]
    return conf_dir


def get_cravat_conf():
    from oakvar.config_loader import ConfigLoader

    confpath = get_main_conf_path()
    conf = ConfigLoader()
    cravat_conf = conf.get_cravat_conf()
    return cravat_conf


def get_cravat_conf_info():
    cravat_conf = get_cravat_conf()
    cravat_conf.update({"cravat_conf_path": get_main_conf_path()})
    return cravat_conf


def get_current_package_version():
    from pkg_resources import get_distribution

    version = get_distribution("oakvar").version
    return version


def get_default_assembly():
    conf = get_cravat_conf()
    default_assembly = conf.get("default_assembly", None)
    return default_assembly


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


def get_download_counts():
    get_mic().update_download_counts()
    counts = get_mic().download_counts
    return counts


def get_install_deps(module_name, version=None, skip_installed=True):
    from distutils.version import LooseVersion
    from pkg_resources import Requirement

    get_mic().update_remote()
    # If input module version not provided, set to highest
    if version is None:
        version = get_remote_latest_version(module_name)
    config = get_mic().get_remote_config(module_name, version=version)
    req_list = config.get("requires", [])
    deps = {}
    for req_string in req_list:
        req = Requirement(req_string)
        rem_info = get_remote_module_info(req.name)
        # Skip if module does not exist
        if rem_info is None and get_local_module_info(req.name) is None:
            continue
        if skip_installed:
            # Skip if a matching version is installed
            local_info = get_local_module_info(req.name)
            if local_info and local_info.version in req:
                continue
        # Select the highest matching version
        lvers = [LooseVersion(v) for v in rem_info.versions]
        lvers.sort(reverse=True)
        highest_matching = None
        for lv in lvers:
            if lv.vstring in req:
                highest_matching = lv.vstring
                break
        # Dont include if no matching version exists
        if highest_matching is not None:
            deps[req.name] = highest_matching
    req_pypi_list = config.get("requires_pypi", [])
    req_pypi_list.extend(config.get("pypi_dependency", []))
    deps_pypi = {}
    for req_pypi in req_pypi_list:
        deps_pypi[req_pypi] = True
    return deps, deps_pypi


def get_jobs_dir():
    from .constants import jobs_dir_key

    conf = get_system_conf()
    jobs_dir = conf[jobs_dir_key]
    return jobs_dir


def get_last_assembly():
    conf = get_cravat_conf()
    last_assembly = conf.get("last_assembly")
    return last_assembly


def get_latest_package_version():
    """
    Return latest oakvar version on pypi
    """
    all_vers = get_package_versions()
    if all_vers:
        return all_vers[-1]
    else:
        return None


def get_local_module_info(module_name):
    """
    Returns a LocalModuleInfo object for a module.
    """
    import os

    if module_name in get_mic().get_local():
        return get_mic().get_local()[module_name]
    else:
        if os.path.exists(module_name):
            module_info = LocalModuleInfo(module_name)
            return module_info
        return None


def get_local_module_infos(types=[], names=[]):
    all_infos = list(get_mic().get_local().values())
    return_infos = []
    for minfo in all_infos:
        if types and minfo.type not in types:
            continue
        elif names and minfo.name not in names:
            continue
        elif minfo.exists == False:
            continue
        else:
            return_infos.append(minfo)
    return return_infos


def get_local_module_infos_by_names(module_names):
    modules = {}
    for module_name in module_names:
        module = get_local_module_info(module_name)
        if module is not None:
            modules[module.name] = module
    return modules


def get_local_module_info_by_name(module_name):
    return get_local_module_info(module_name)


def get_local_reporter_module_infos_by_names(module_names):
    modules = {}
    for module_name in module_names:
        if not module_name.endswith("reporter"):
            module_name += "reporter"
        module = get_local_module_info(module_name)
        if module is not None:
            modules[module.name] = module
    return modules


def get_local_module_infos_of_type(t, update=False):
    modules = {}
    if update:
        get_mic().update_local()
    for module_name in get_mic().get_local():
        if get_mic().get_local()[module_name].type == t:
            modules[module_name] = get_mic().get_local()[module_name]
    return modules


def get_local_module_types():
    types = []
    for module in get_mic().get_local():
        if get_mic().get_local()[module].type not in types:
            types.append(get_mic().get_local()[module].type)
    return types


def get_main_conf_path():
    """
    Get the path to where the main oakvar config (cravat.yml) should be.
    """
    import os
    from .constants import main_conf_fname

    return os.path.join(get_conf_dir(), main_conf_fname)


def get_main_default_path():
    """
    Get the path to the default main oakvar config.(backup lives in the pip package)
    """
    import os
    from .constants import main_conf_fname

    return os.path.join(get_packagedir(), main_conf_fname)


def get_mapper_script_path(module_name):
    import os

    module_path = os.path.join(
        get_modules_dir(), "mappers", module_name, module_name + ".py"
    )
    if os.path.exists(module_path) == False:
        module_path = None
    return module_path


def get_max_num_concurrent_annotators_per_job():
    return get_system_conf()["max_num_concurrent_annotators_per_job"]


def get_module_conf_path(module_name, module_type=None):
    import os

    conf_path = None
    modules_dir = get_modules_dir()
    yml_fn = os.path.basename(module_name) + ".yml"
    p = os.path.join(module_name, yml_fn)
    if os.path.exists(p):  # module folder is given.
        conf_path = p
    else:
        if module_type is not None:  # module name and type are given.
            p = os.path.join(modules_dir, module_type, module_name, yml_fn)
            if os.path.exists(p):
                conf_path = p
        else:  # module folder should be searched.
            typefns = os.listdir(modules_dir)
            conf_path = None
            for typefn in typefns:
                typepath = os.path.join(modules_dir, typefn)
                if os.path.isdir(typepath) == False:
                    continue
                modulefns = os.listdir(typepath)
                for modulefn in modulefns:
                    if os.path.basename(modulefn) != module_name:
                        continue
                    modulepath = os.path.join(typepath, modulefn)
                    if os.path.isdir(modulepath):
                        path = os.path.join(modulepath, module_name + ".yml")
                        if os.path.exists(path):
                            conf_path = path
                            break
                if conf_path is not None:
                    break
    return conf_path


def get_modules_dir():
    """
    Get the current modules directory
    """
    import os
    from .constants import custom_modules_dir, modules_dir_env_key, modules_dir_key

    if custom_modules_dir is not None:
        modules_dir = custom_modules_dir
    else:
        modules_dir = os.environ.get(modules_dir_env_key, None)
        if modules_dir is not None and modules_dir != "":
            modules_dir = os.environ.get(modules_dir_env_key)
        else:
            conf = get_system_conf()
            modules_dir = conf[modules_dir_key]
    modules_dir = os.path.abspath(modules_dir)
    return modules_dir


def get_package_versions():
    """
    Return available oakvar versions from pypi, sorted asc
    """
    import json
    from requests import get
    from requests.exceptions import ConnectionError
    from distutils.version import LooseVersion

    try:
        r = get("https://pypi.org/pypi/oakvar/json", timeout=(3, None))
    except ConnectionError:
        print("Internet connection is not available.")
        return None
    if r.status_code == 200:
        d = json.loads(r.text)
        all_vers = list(d["releases"].keys())
        all_vers.sort(key=LooseVersion)
        return all_vers
    else:
        return None


def get_readme(module_name, version=None):
    """
    Get the readme. Use local if available.
    """
    import os

    exists_remote = module_exists_remote(module_name, version=version)
    exists_local = module_exists_local(module_name)
    if exists_remote:
        remote_readme = get_mic().get_remote_readme(module_name)
    else:
        remote_readme = ""
    if exists_local:
        local_info = get_local_module_info(module_name)
        if os.path.exists(local_info.readme_path):
            local_readme = open(local_info.readme_path).read()
        else:
            local_readme = ""
    else:
        local_readme = ""
    if exists_remote == True:
        if exists_local:
            remote_version = get_remote_latest_version(module_name)
            local_version = local_info.version
            if compare_version(remote_version, local_version) > 0:
                return remote_readme
            else:
                return local_readme
        else:
            return remote_readme
    else:
        return local_readme


def get_remote_data_version(module_name, version):
    """
    Get the data version to install for a module.
    Return the input version if module_name or version is not found.
    """
    get_mic().update_remote()
    try:
        manifest_entry = get_mic().remote[module_name]
    except KeyError:
        return version
    try:
        return manifest_entry["data_versions"][version]
    except KeyError:
        return version


def get_remote_latest_version(module_name):
    """
    Returns latest remotely available version of a module.
    """
    get_mic().update_remote()
    return get_mic().remote[module_name]["latest_version"]


def get_remote_manifest():
    if len(get_mic().remote) == 0:
        get_mic().update_remote()
    return get_mic().remote


def get_remote_module_config(module_name):
    conf = get_mic().get_remote_config(module_name)
    return conf


def get_remote_module_info(module_name):
    """
    Returns a RemoteModuleInfo object for a module.
    """
    get_mic().update_remote()
    if module_exists_remote(module_name, version=None):
        mdict = get_mic().remote[module_name]
        module = RemoteModuleInfo(module_name, **mdict)
        return module
    else:
        return None


def get_remote_module_infos_of_type(t):
    modules = {}
    get_mic().update_remote()
    for module_name in get_mic().remote:
        if get_mic().remote[module_name]["type"] == t:
            modules[module_name] = get_mic().remote[module_name]
    return modules


def get_remote_module_readme(module_name, version=None):
    """
    Get the detailed description file about a module as a string.
    """
    return get_mic().get_remote_readme(module_name, version=version)


def get_system_conf(custom_system_conf_path=None, file_only=False):
    """
    Get the system config. Fill in the default modules dir if not set.
    """
    import os
    from .constants import (
        system_conf_path_env_key,
        modules_dir_key,
        conf_dir_key,
        jobs_dir_key,
        log_dir_key,
        default_num_input_line_warning_cutoff,
        default_settings_gui_input_size_limit,
        default_max_num_concurrent_jobs,
        default_max_num_concurrent_annotators_per_job,
    )

    if custom_system_conf_path is not None:
        conf = load_yml_conf(custom_system_conf_path)
    elif os.environ.get(system_conf_path_env_key) is not None:
        conf = load_yml_conf(os.environ.get(system_conf_path_env_key))
    else:
        conf = load_yml_conf(get_system_conf_path())
    if file_only:
        return conf
    if modules_dir_key not in conf:
        conf[modules_dir_key] = get_default_modules_dir()
    if conf_dir_key not in conf:
        conf[conf_dir_key] = get_default_conf_dir()
    if jobs_dir_key not in conf:
        conf[jobs_dir_key] = get_default_jobs_dir()
    if log_dir_key not in conf:
        conf[log_dir_key] = get_default_log_dir()
    key = "num_input_line_warning_cutoff"
    if key not in conf:
        conf[key] = default_num_input_line_warning_cutoff
    key = "gui_input_size_limit"
    if key not in conf:
        conf[key] = default_settings_gui_input_size_limit
    key = "max_num_concurrent_jobs"
    if key not in conf:
        conf[key] = default_max_num_concurrent_jobs
    key = "max_num_concurrent_annotators_per_job"
    if key not in conf:
        conf[key] = default_max_num_concurrent_annotators_per_job
    if "custom_system_conf" in globals():
        global custom_system_conf
        for k, v in custom_system_conf.items():
            conf[k] = v
    return conf


def get_system_conf_info(**kwargs):
    import os

    confpath = get_system_conf_path()
    if os.path.exists(confpath):
        conf = get_system_conf()
        confexists = True
    else:
        conf = {}
        confexists = False
    conf["package_path"] = os.path.dirname(os.path.abspath(__file__))
    system_conf_info = conf
    system_conf_info.update({"conf_path": confpath, "conf_exists": confexists})
    return system_conf_info


async def get_updatable_async(modules=[], strategy="consensus"):
    update_vers, resolution_applied, resolution_failed = get_updatable(
        modules=modules, strategy=strategy
    )
    return [update_vers, resolution_applied, resolution_failed]


def get_updatable(modules=[], strategy="consensus"):
    from distutils.version import LooseVersion
    from pkg_resources import Requirement
    from collections import defaultdict
    from types import SimpleNamespace

    if strategy not in ("consensus", "force", "skip"):
        raise ValueError('Unknown strategy "{}"'.format(strategy))
    if not modules:
        modules = list_local()
    reqs_by_dep = defaultdict(dict)
    all_versions = {}
    for mname in list_local():
        local_info = get_local_module_info(mname)
        remote_info = get_remote_module_info(mname)
        if remote_info:
            all_versions[mname] = sorted(remote_info.versions, key=LooseVersion)
        req_strings = local_info.conf.get("requires", [])
        reqs = [Requirement(s) for s in req_strings]
        for req in reqs:
            dep = req.name
            reqs_by_dep[dep][mname] = req
    update_vers = {}
    resolution_applied = {}
    resolution_failed = {}
    for mname in modules:
        if mname not in list_local():
            continue
        local_info = get_local_module_info(mname)
        remote_info = get_remote_module_info(mname)
        reqs = reqs_by_dep[mname]
        versions = all_versions.get(mname, [])
        if not versions:
            continue
        selected_version = versions[-1]
        if (
            selected_version
            and local_info.version
            and LooseVersion(selected_version) <= LooseVersion(local_info.version)
        ):
            continue
        if reqs:
            resolution_applied[mname] = reqs
            if strategy == "force":
                pass
            elif strategy == "skip":
                selected_version = None
            elif strategy == "consensus":
                passing_versions = []
                for version in versions:
                    version_passes = True
                    for requester, requirement in reqs.items():
                        version_passes = version in requirement
                        if not version_passes:
                            break
                    if version_passes:
                        passing_versions.append(version)
                selected_version = passing_versions[-1] if passing_versions else None
        if (
            selected_version
            and local_info.version
            and LooseVersion(selected_version) > LooseVersion(local_info.version)
        ):
            update_data_version = get_remote_data_version(mname, selected_version)
            installed_data_version = get_remote_data_version(mname, local_info.version)
            if (
                update_data_version is not None
                and update_data_version != installed_data_version
            ):
                update_size = remote_info.size
            else:
                update_size = remote_info.code_size
            update_vers[mname] = SimpleNamespace(
                version=selected_version, size=update_size
            )
        else:
            resolution_failed[mname] = reqs
    return update_vers, resolution_applied, resolution_failed


def get_widgets_for_annotator(annotator_name, skip_installed=False):
    """
    Get webviewer widgets that require an annotator. Optionally skip the
    widgets that are already installed.
    """
    linked_widgets = []
    for widget_name in list_remote():
        widget_info = get_remote_module_info(widget_name)
        if widget_info.type == "webviewerwidget":
            widget_config = get_mic().get_remote_config(widget_name)
            linked_annotator = widget_config.get("required_annotator")
            if linked_annotator == annotator_name:
                if skip_installed and module_exists_local(widget_name):
                    continue
                else:
                    linked_widgets.append(widget_info)
    return linked_widgets


def input_formats():
    import os

    formats = set()
    d = os.path.join(get_modules_dir(), "converters")
    if os.path.exists(d):
        fns = os.listdir(d)
        for fn in fns:
            if fn.endswith("-converter"):
                formats.add(fn.split("-")[0])
    return formats


def install_module(
    module_name,
    version=None,
    force_data=False,
    skip_data=False,
    stage_handler=None,
    **kwargs,
):
    import zipfile
    import shutil
    import os
    import oyaml as yaml
    from .constants import install_tempdir_name
    from oakvar.store_utils import (
        PathBuilder,
        stream_to_file,
        get_file_to_string,
        verify_against_manifest,
    )
    from requests import HTTPError
    from .exceptions import KillInstallException
    import signal
    import subprocess

    modules_dir = get_modules_dir()
    temp_dir = os.path.join(modules_dir, install_tempdir_name, module_name)
    shutil.rmtree(temp_dir, ignore_errors=True)
    os.makedirs(temp_dir)
    try:
        # Ctrl-c in this func must be caught to delete temp_dir
        def raise_kbi(a, b):
            raise KeyboardInterrupt

        original_sigint = signal.signal(signal.SIGINT, raise_kbi)
        if stage_handler is None:
            stage_handler = InstallProgressHandler(module_name, version)
        if version is None:
            version = get_remote_latest_version(module_name)
            stage_handler.set_module_version(version)
        if hasattr(stage_handler, "install_state") == True:
            install_state = stage_handler.install_state
        else:
            install_state = None
        stage_handler.stage_start("start")
        # Checks and installs pip packages.
        config = get_mic().get_remote_config(module_name, version=version)
        pypi_deps = config.get("requires_pypi", [])
        pypi_deps.extend(config.get("pypi_dependency", []))
        idx = 0
        while idx < len(pypi_deps):
            dep = pypi_deps[idx]
            r = subprocess.run(
                ["pip", "show", dep],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            if r.returncode == 0:
                pypi_deps.remove(dep)
            else:
                idx += 1
        if len(pypi_deps) > 0:
            print(
                f"Following PyPI dependencies should be met before installing {module_name}."
            )
            for dep in pypi_deps:
                print(f"- {dep}")
            print(f"Installing required PyPI packages...")
            idx = 0
            while idx < len(pypi_deps):
                dep = pypi_deps[idx]
                r = subprocess.run(["pip", "install", dep])
                if r.returncode == 0:
                    pypi_deps.remove(dep)
                else:
                    idx += 1
            if len(pypi_deps) > 0:
                print(f"Following PyPI dependencies could not be installed.")
                for dep in pypi_deps:
                    print(f"- {dep}")
        if len(pypi_deps) > 0:
            if version is not None:
                print(
                    f"Skipping installation of {module_name}=={version} due to unmet requirement for PyPI packages"
                )
            else:
                print(
                    f"Skipping installation of {module_name} due to unmet requirement for PyPI packages"
                )
            return False
        sys_conf = get_system_conf()
        store_url = sys_conf["store_url"]
        store_path_builder = PathBuilder(store_url, "url")
        remote_data_version = get_remote_data_version(module_name, version)
        if module_name in list_local():
            local_info = get_local_module_info(module_name)
            if local_info.has_data:
                local_data_version = get_remote_data_version(
                    module_name, local_info.version
                )
            else:
                local_data_version = None
        else:
            local_data_version = None
        code_url = store_path_builder.module_code(module_name, version)
        zipfile_fname = module_name + ".zip"
        remote_info = get_remote_module_info(module_name)
        if remote_info is not None:
            module_type = remote_info.type
        else:
            # Private module. Fallback to remote config.
            remote_config = get_mic().get_remote_config(module_name, version)
            module_type = remote_config["type"]
        if install_state:
            if (
                install_state["module_name"] == module_name
                and install_state["kill_signal"] == True
            ):
                raise KillInstallException
        zipfile_path = os.path.join(temp_dir, zipfile_fname)
        stage_handler.stage_start("download_code")
        r = stream_to_file(
            code_url,
            zipfile_path,
            stage_handler=stage_handler.stage_progress,
            install_state=install_state,
            **kwargs,
        )
        if r.status_code != 200:
            raise (HTTPError(r))
        if install_state:
            if (
                install_state["module_name"] == module_name
                and install_state["kill_signal"] == True
            ):
                raise KillInstallException
        stage_handler.stage_start("extract_code")
        zf = zipfile.ZipFile(zipfile_path)
        zf.extractall(temp_dir)
        zf.close()
        if install_state:
            if (
                install_state["module_name"] == module_name
                and install_state["kill_signal"] == True
            ):
                raise KillInstallException
        stage_handler.stage_start("verify_code")
        code_manifest_url = store_path_builder.module_code_manifest(
            module_name, version
        )
        code_manifest = yaml.safe_load(get_file_to_string(code_manifest_url))
        verify_against_manifest(temp_dir, code_manifest)
        os.remove(zipfile_path)
        if install_state:
            if (
                install_state["module_name"] == module_name
                and install_state["kill_signal"] == True
            ):
                raise KillInstallException
        data_installed = False
        if (
            not (skip_data)
            and (remote_data_version is not None)
            and (remote_data_version != local_data_version or force_data)
        ):
            data_installed = True
            data_url = store_path_builder.module_data(module_name, remote_data_version)
            data_fname = ".".join([module_name, "data", "zip"])
            data_path = os.path.join(temp_dir, data_fname)
            stage_handler.stage_start("download_data")
            r = stream_to_file(
                data_url,
                data_path,
                stage_handler=stage_handler.stage_progress,
                install_state=install_state,
                **kwargs,
            )
            if install_state:
                if (
                    install_state["module_name"] == module_name
                    and install_state["kill_signal"] == True
                ):
                    raise KillInstallException
            if r.status_code == 200:
                stage_handler.stage_start("extract_data")
                zf = zipfile.ZipFile(data_path)
                zf.extractall(temp_dir)
                zf.close()
                if install_state:
                    if (
                        install_state["module_name"] == module_name
                        and install_state["kill_signal"] == True
                    ):
                        raise KillInstallException
                stage_handler.stage_start("verify_data")
                data_manifest_url = store_path_builder.module_data_manifest(
                    module_name, remote_data_version
                )
                data_manifest = yaml.safe_load(get_file_to_string(data_manifest_url))
                verify_against_manifest(temp_dir, data_manifest)
                os.remove(data_path)
                if install_state:
                    if (
                        install_state["module_name"] == module_name
                        and install_state["kill_signal"] == True
                    ):
                        raise KillInstallException
            elif r.status_code == 404:
                # Probably a private module that does not have data
                pass
            else:
                raise (HTTPError(r))
        if install_state:
            if (
                install_state["module_name"] == module_name
                and install_state["kill_signal"] == True
            ):
                raise KillInstallException
        module_dir = os.path.join(modules_dir, module_type + "s", module_name)
        if os.path.isdir(module_dir):
            # Module being updated
            if data_installed:
                # Overwrite the whole module
                shutil.rmtree(module_dir)
                shutil.move(temp_dir, module_dir)
            else:
                # Remove all code items
                for item in os.listdir(module_dir):
                    item_path = os.path.join(module_dir, item)
                    if item != "data":
                        if os.path.isdir(item_path):
                            shutil.rmtree(item_path)
                        else:
                            os.remove(item_path)
                # Copy in new code items
                for item in os.listdir(temp_dir):
                    old_path = os.path.join(temp_dir, item)
                    new_path = os.path.join(module_dir, item)
                    if item != "data":
                        shutil.move(old_path, new_path)
                shutil.rmtree(temp_dir)
        else:
            # Move the module to the right place
            shutil.move(temp_dir, module_dir)
        wf = open(os.path.join(module_dir, "startofinstall"), "w")
        wf.close()
        wf = open(os.path.join(module_dir, "endofinstall"), "w")
        wf.close()
        get_mic().update_local()
        stage_handler.stage_start("finish")
    except (Exception, KeyboardInterrupt, SystemExit) as e:
        shutil.rmtree(temp_dir, ignore_errors=True)
        if type(e) == KillInstallException:
            stage_handler.stage_start("killed")
        elif type(e) in (KeyboardInterrupt, SystemExit):
            pass
        else:
            raise e
    finally:
        signal.signal(signal.SIGINT, original_sigint)


def install_widgets_for_module(module_name):
    widget_name = "wg" + module_name
    install_module(widget_name)


def list_local():
    """
    Returns a list of locally installed modules.
    """
    modules_dir = get_modules_dir()
    if get_mic()._modules_dir != modules_dir:
        get_mic()._modules_dir = modules_dir
        get_mic().update_local()
    return sorted(list(get_mic().get_local().keys()))


def list_remote(force=False):
    """
    Returns a list of remotely available modules.
    """
    get_mic().update_remote(force=force)
    return sorted(list(get_mic().remote.keys()))


def load_yml_conf(yml_conf_path):
    """
    Load a .yml file into a dictionary. Return an empty dictionary if file is
    empty.
    """
    import oyaml as yaml

    with open(yml_conf_path, encoding="utf-8") as f:
        conf = yaml.safe_load(f)
    if conf == None:
        conf = {}
    return conf


def fn_new_exampleinput(d):
    import shutil
    import os

    try:
        fn = "exampleinput"
        ifn = os.path.join(get_packagedir(), fn)
        ofn = os.path.join(d, fn)
        shutil.copyfile(ifn, ofn)
        return True
    except Exception as e:
        raise e


def module_exists_local(module_name):
    """
    Returns True if a module exists locally. False otherwise.
    """
    import os

    if module_name in get_mic().get_local():
        return True
    else:
        if os.path.exists(module_name):
            if os.path.exists(
                os.path.join(module_name, os.path.basename(module_name) + ".yml")
            ):
                return True
    return False


def module_exists_remote(module_name, version=None, private=False):
    """
    Returns true if a module (optionally versioned) exists in remote
    """
    from oakvar.store_utils import PathBuilder
    from requests import get

    get_mic().update_remote()
    found = False
    if module_name in get_mic().remote:
        if version is None:
            found = True
        else:
            found = version in get_mic().remote[module_name]["versions"]
    if private and not found:
        sys_conf = get_system_conf()
        path_builder = PathBuilder(sys_conf["store_url"], "url")
        if version is None:
            check_url = path_builder.module_dir(module_name)
        else:
            check_url = path_builder.module_version_dir(module_name, version)
        r = get(check_url)
        found = r.status_code != 404 and r.status_code < 500
    return found


def new_annotator(annot_name):
    import shutil
    import os

    annot_root = os.path.join(get_modules_dir(), "annotators", annot_name)
    template_root = os.path.join(get_packagedir(), "annotator_template")
    shutil.copytree(template_root, annot_root)
    for dir_path, _, fnames in os.walk(annot_root):
        for old_fname in fnames:
            old_fpath = os.path.join(dir_path, old_fname)
            new_fname = old_fname.replace("annotator_template", annot_name, 1)
            new_fpath = os.path.join(dir_path, new_fname)
            os.rename(old_fpath, new_fpath)
    get_mic().update_local()


def print_stage_handler(cur_stage, total_stages, cur_size, total_size):
    import sys

    rem_stages = total_stages - cur_stage
    perc = cur_stage / total_stages * 100
    out = "\r[{1}{2}] {0:.0f}% ".format(perc, "*" * cur_stage, " " * rem_stages)
    sys.stdout.write(out)
    if cur_stage == total_stages:
        print()


def publish_module(module_name, user, password, overwrite=False, include_data=True):
    import os
    import json
    from oakvar.store_utils import (
        VersionExists,
        ModuleArchiveBuilder,
        stream_multipart_post,
    )
    from requests import get

    sys_conf = get_system_conf()
    publish_url = sys_conf["publish_url"]
    get_mic().update_local()
    local_info = get_local_module_info(module_name)
    if local_info == None:
        print(module_name + " does not exist.")
        return
    check_url = publish_url + "/%s/%s/check" % (module_name, local_info.version)
    r = get(check_url, auth=(user, password))
    if r.status_code != 200:
        print("Cannot upload")
        if r.status_code == 401:
            print("Incorrect username or password")
            exit()
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
                        exit()
                    else:
                        print(
                            "Your response ('%s') was not one of the expected responses: y, n"
                            % resp
                        )
                        continue
            else:
                print(err["message"])
                exit()
        elif r.status_code == 500:
            print("Server error")
            exit()
        else:
            print("HTTP response status code: %d" % r.status_code)
            exit()
    zf_name = "%s.%s.zip" % (module_name, local_info.version)
    zf_path = os.path.join(get_modules_dir(), zf_name)
    print("Zipping module and generating checksums")
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
    post_url = "/".join([publish_url, module_name, local_info.version])
    if overwrite:
        post_url += "?overwrite=1"
    with open(zf_path, "rb") as zf:
        fields = {
            "manifest": ("manifest.json", json.dumps(manifest), "application/json"),
            "archive": (zf_name, zf, "application/octet-stream"),
        }
        print("Uploading to store")
        r = stream_multipart_post(
            post_url, fields, stage_handler=print_stage_handler, auth=(user, password)
        )
    if r.status_code != 200:
        print("Upload failed")
        print(r.status_code)
        print(r.text)
    if r.text:
        print(r.text)
    os.remove(zf_path)


def read_system_conf_template():
    import oyaml as yaml
    from .constants import system_conf_template_path

    with open(system_conf_template_path) as f:
        d = yaml.safe_load(f)
        return d


def ready_resolution_console():
    import os
    from types import SimpleNamespace

    rs = system_ready()
    if rs:
        return
    print(rs.message)
    if rs.code == ReadyState.MISSING_MD:
        msg = "Current modules directory is {}.\nInput a new modules directory, or press enter to exit.\n> ".format(
            get_modules_dir()
        )
        new_md = input(msg)
        if new_md:
            full_path = os.path.abspath(new_md)
            set_modules_dir(full_path)
            print(full_path)
        else:
            print("Please manually recreate/reattach the modules directory.")
            exit()
    elif rs.code == ReadyState.NO_BASE_MODULES:
        yn = input("Do you want to install base modules now? (y/n)>")
        if yn == "y":
            args = SimpleNamespace(force_data=False, force=False, md=None)
            from .cli_admin import install_base

            install_base(args)
            print("Base modules have been installed.")
    exit()


def recursive_update(d1, d2):
    """
    Recursively merge two dictionaries and return a copy.
    d1 is merged into d2. Keys in d1 that are not present in d2 are preserved
    at all levels. The default Dict.update() only preserved keys at the top
    level.
    """
    import copy

    d3 = copy.deepcopy(d1)  # Copy perhaps not needed. Test.
    for k, v in d2.items():
        if k in d3:
            orig_v = d3[k]
            if isinstance(v, dict):
                if isinstance(orig_v, dict) == False:
                    d3[k] = v
                else:
                    t = recursive_update(d3.get(k, {}), v)
                    d3[k] = t
            else:
                d3[k] = d2[k]
        else:
            d3[k] = v
    return d3


def refresh_cache():
    """
    Refresh the local modules cache
    """
    global mic
    mic = ModuleInfoCache()


def report_issue():
    import webbrowser

    webbrowser.open("http://github.com/rkimoakbioinformatics/oakvar/issues")


def search_local(*patterns):
    """
    Return local module names which match any of supplied patterns
    """
    from re import fullmatch

    modules_dir = get_modules_dir()
    if get_mic()._modules_dir != modules_dir:
        get_mic()._modules_dir = modules_dir
        get_mic().update_local()
    matching_names = []
    for module_name in list_local():
        if any([fullmatch(pattern, module_name) for pattern in patterns]):
            matching_names.append(module_name)
    return matching_names


def search_remote(*patterns):
    """
    Return remote module names which match any of supplied patterns
    """
    from re import fullmatch

    matching_names = []
    for module_name in list_remote():
        if any([fullmatch(pattern, module_name) for pattern in patterns]):
            matching_names.append(module_name)
    return matching_names


def send_reset_email(username):
    from requests import post

    sys_conf = get_system_conf()
    publish_url = sys_conf["publish_url"]
    reset_pw_url = publish_url + "/reset-password"
    r = post(reset_pw_url, params={"username": username})
    if r.status_code == 500:
        print("Server error")
    if r.text:
        print(r.text)


def send_verify_email(username):
    from requests import post

    sys_conf = get_system_conf()
    publish_url = sys_conf["publish_url"]
    reset_pw_url = publish_url + "/verify-email"
    r = post(reset_pw_url, params={"username": username})
    if r.status_code == 500:
        print("Server error")
    if r.text:
        print(r.text)


def set_cravat_conf_prop(key, val):
    import oyaml as yaml

    conf = get_cravat_conf()
    conf[key] = val
    wf = open(get_main_conf_path(), "w")
    yaml.dump(conf, wf, default_flow_style=False)
    wf.close()


def set_jobs_dir(d):
    update_system_conf_file({"jobs_dir": d})


def set_modules_dir(path, overwrite=False):
    """
    Set the modules_dir to the directory in path.
    """
    import shutil
    import os
    from .constants import modules_dir_key

    path = os.path.abspath(os.path.expanduser(path))
    if not (os.path.isdir(path)):
        os.makedirs(path)
    old_conf_path = get_main_conf_path()
    update_system_conf_file({modules_dir_key: path})
    if not (os.path.exists(get_main_conf_path())):
        if os.path.exists(old_conf_path):
            overwrite_conf_path = old_conf_path
        else:
            overwrite_conf_path = get_main_default_path()
        shutil.copy(overwrite_conf_path, get_main_conf_path())


# return a list of module types (e.g. annotators) in the local install
def show_oakvar_conf(**kwargs):
    import oyaml as yaml

    kwargs.setdefault("fmt", "yaml")
    kwargs.setdefault("to", "stdout")
    conf = get_cravat_conf_info()
    if kwargs["fmt"] == "yaml":
        conf = yaml.dump(conf, default_flow_style=False)
    if kwargs["to"] == "stdout":
        print(conf)
    else:
        return conf


def oakvar_version():
    version = get_current_package_version()
    return version


def show_system_conf(**kwargs):
    import oyaml as yaml

    kwargs.setdefault("fmt", "yaml")
    kwargs.setdefault("to", "stdout")
    system_conf_info = get_system_conf_info(**kwargs)
    if kwargs["fmt"] == "yaml":
        system_conf_info = yaml.dump(system_conf_info, default_flow_style=False)
    if kwargs["to"] == "stdout":
        print(system_conf_info)
    else:
        return system_conf_info


def system_ready():
    import os

    modules_dir = get_modules_dir()
    if not (os.path.exists(modules_dir)):
        return ReadyState(code=ReadyState.MISSING_MD)
    elif not (os.path.exists(os.path.join(modules_dir, "converters", "vcf-converter"))):
        return ReadyState(code=ReadyState.NO_BASE_MODULES)
    else:
        return ReadyState()


def uninstall_module(module_name):
    """
    Uninstalls a module.
    """
    import shutil

    uninstalled_modules = False
    if module_name in list_local():
        local_info = get_local_module_info(module_name)
        shutil.rmtree(local_info.directory)
        uninstalled_modules = True
    if uninstalled_modules:
        get_mic().update_local()


def update_system_conf_file(d):
    """
    Recursively update the system config and re-write to disk.
    """
    sys_conf = get_system_conf(file_only=True)
    sys_conf = recursive_update(sys_conf, d)
    write_system_conf_file(sys_conf)
    refresh_cache()
    return True


def write_cravat_conf(cravat_conf):
    import oyaml as yaml

    confpath = get_main_conf_path()
    wf = open(confpath, "w")
    yaml.dump(cravat_conf, wf, default_flow_style=False)
    wf.close()


def write_system_conf_file(d):
    """
    Fully overwrite the system config file with a new system config.
    """
    import oyaml as yaml

    with open(get_system_conf_path(), "w") as wf:
        wf.write(yaml.dump(d, default_flow_style=False))


def update_mic():
    global mic
    global custom_system_conf
    mic = ModuleInfoCache()


def get_liftover_chain_paths():
    from os.path import join

    liftover_chains_dir = get_liftover_chains_dir()
    liftover_chain_paths = {
        "hg19": join(liftover_chains_dir, "hg19ToHg38.over.chain"),
        "hg18": join(liftover_chains_dir, "hg18ToHg38.over.chain"),
    }
    return liftover_chain_paths


def get_packagedir():
    from os.path import dirname, abspath

    return dirname(abspath(__file__))


def get_platform():
    from platform import platform

    pl = platform()
    if pl.startswith("Windows"):
        pl = "windows"
    elif pl.startswith("Darwin") or pl.startswith("macOS"):
        pl = "macos"
    elif pl.startswith("Linux"):
        pl = "linux"
    else:
        pl = "linux"
    return pl


def get_ov_root_dir():
    from os.path import exists as pathexists
    from os.path import join as pathjoin
    from os.path import expandvars as pathexpandvars
    from os import sep
    from os import mkdir
    from os import environ

    pl = get_platform()
    root_dir = None
    if pl == "windows":
        root_dir = pathjoin(pathexpandvars("%systemdrive%"), sep, "open-cravat")
        if pathexists(root_dir) == False:  # OakVar first installation
            root_dir = pathjoin(pathexpandvars("%systemdrive%"), sep, "oakvar")
    elif pl == "linux":
        root_dir = packagedir
        if pathexists(pathjoin(root_dir, "conf")) == False:  # OakVar first installation
            if "SUDO_USER" in environ:
                root_dir = pathjoin("/home", environ["SUDO_USER"], ".oakvar")
            else:
                root_dir = path.join("/home", environ["USER"], ".oakvar")
    elif pl == "macos":
        root_dir = "/Users/Shared/open-cravat"
        if pathexists(root_dir) == False:  # OakVar first installation
            root_dir = "Users/Shared/oakvar"
    if pathexists(root_dir) == False:
        mkdir(root_dir)
    return root_dir


def setup_system():
    from os.path import exists as pathexists
    from os.path import join as pathjoin
    from os import mkdir

    if pathexists(default_conf_dir) == False:
        mkdir(default_conf_dir)
    linux_first_time = False
    # conf
    main_conf_path = get_main_conf_path()
    if pathexists(main_conf_path) == False:
        import shutil

        shutil.copyfile(pathjoin(packagedir, main_conf_fname), main_conf_path)
    f = open(system_conf_path)
    conf = yaml.safe_load(f)
    f.close()
    default_modules_dir = get_default_modules_dir()
    if not modules_dir_key in conf:
        if pathexists(default_modules_dir) == False:
            mkdir(default_modules_dir)
        conf[modules_dir_key] = default_modules_dir
        if linux_first_time:
            import subprocess

            subprocess.call(["sudo", "chmod", "777", get_system_conf_path()])
        wf = open(get_system_conf_path(), "w")
        yaml.dump(conf, wf, default_flow_style=False)
        wf.close()
        if linux_first_time:
            import subprocess

            subprocess.call(["sudo", "chmod", "644", get_system_conf_path()])
            print(
                """
    System configuration file and folders have been set up.

Remember to run `ov module installbase` to install
base modules before running any job.

===
"""
            )
    system_conf_path = get_system_conf_path()
    if pathexists(system_conf_path) == False:
        try:
            import shutil

            shutil.copyfile(system_conf_template_path, system_conf_path)
        except PermissionError:
            if pl == "linux":
                print(
                    """
    It seems that OakVar has been installed as root 
    and that you are running it for the first time. 
    To configure OakVar properly, you can do one of 
    the following:

    1) Stop at this point with Ctrl-C and run 
    `sudo oc` just once to create a system configration 
    file and system folders.

    OR

    2) Type Enter and continue. OakVar will need to 
    access `sudo` three times, once to create a system
    configration file, then to modify it, and then to
    change its file permission back. 

    Either way, afterwards, normal users will be able 
    to use `oc` commands without sudo privilege, 
    except when making changes to system settings.
    """
                )
                _ = input("Ctrl-C to stop or Enter to continue>")
                linux_first_time = True
                import subprocess

                subprocess.call(
                    ["sudo", "cp", system_conf_template_path, system_conf_path]
                )
            else:
                raise
    if not jobs_dir_key in conf:
        if pathexists(default_jobs_dir) == False:
            mkdir(default_jobs_dir)
        conf[jobs_dir_key] = default_jobs_dir
    if not log_dir_key in conf:
        if pathexists(default_log_dir) == False:
            mkdir(default_log_dir)
        conf[log_dir_key] = default_log_dir


def get_default_conf_dir():
    from os.path import join as pathjoin
    from .constants import conf_dir_name

    return pathjoin(get_ov_root_dir(), conf_dir_name)


def get_default_modules_dir():
    from os.path import join as pathjoin
    from .constants import modules_dir_name

    return pathjoin(get_ov_root_dir(), modules_dir_name)


def get_default_jobs_dir():
    from os.path import join as pathjoin
    from .constants import jobs_dir_name

    return pathjoin(get_ov_root_dir(), jobs_dir_name)


def get_default_log_dir():
    from os.path import join as pathjoin
    from .constants import log_dir_name

    return pathjoin(get_ov_root_dir(), log_dir_name)


def get_admindb_path():
    from os.path import join as pathjoin

    return pathjoin(get_default_conf_dir(), "admin.sqlite")


def get_system_conf_path():
    from .constants import system_conf_fname
    from os.path import join as pathjoin
    from .constants import system_conf_fname

    pl = get_platform()
    if pl in ["windows", "macos"]:
        return pathjoin(get_default_conf_dir(), system_conf_fname)
    else:
        return pathjoin(get_packagedir(), system_conf_fname)


def get_system_conf_template_path():
    from .constants import system_conf_template_fname
    from .constants import system_conf_template_fname
    from os.path import join as pathjoin

    return pathjoin(get_packagedir(), system_conf_template_fname)


def get_liftover_chains_dir():
    from os.path import join as pathjoin

    return pathjoin(get_packagedir(), "liftover")


def get_mic():
    global mic
    if mic is None:
        mic = ModuleInfoCache()
    return mic


def get_max_version_supported_for_migration():
    from distutils.version import LooseVersion

    return LooseVersion("1.7.0")


mic = None
