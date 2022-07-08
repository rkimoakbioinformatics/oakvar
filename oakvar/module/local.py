from typing import Optional


class LocalModuleInfo(object):
    def __init__(self, dir_path, __module_type__=None, name=None):
        import os
        from ..util.util import load_yml_conf
        from ..store import get_developer_dict

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
        dev_dict = self.conf.get("developer", {})
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
        self.size = None
        self.code_size = None
        self.data_size = None
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
        from ..util.util import get_directory_size

        if self.size is None:
            self.size = get_directory_size(self.directory)
        return self.size

    def get_data_size(self):
        from ..util.util import get_directory_size
        from os.path import join

        if self.data_size is None:
            self.data_size = get_directory_size(join(self.directory, "data"))
        return self.data_size

    def get_code_size(self):
        self.code_size = self.get_size() - self.get_data_size()
        return self.code_size

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


def get_local_module_info(module_name):
    """
    Returns a LocalModuleInfo object for a module.
    """
    from os.path import exists
    from .cache import get_module_cache

    if module_name in get_module_cache().get_local():
        module_info = get_module_cache().get_local()[module_name]
    else:
        if exists(module_name):
            module_info = LocalModuleInfo(module_name)
        else:
            module_info = None
    return module_info


def get_local_module_infos(types=[], names=[]):
    from .cache import get_module_cache

    all_infos = list(get_module_cache().get_local().values())
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
    from .cache import get_module_cache

    modules = {}
    if update:
        get_module_cache().update_local()
    for module_name in get_module_cache().get_local():
        if get_module_cache().get_local()[module_name].type == t:
            modules[module_name] = get_module_cache().get_local()[module_name]
    return modules


def get_local_module_types():
    from .cache import get_module_cache

    types = []
    for module in get_module_cache().get_local():
        if get_module_cache().get_local()[module].type not in types:
            types.append(get_module_cache().get_local()[module].type)
    return types


def get_annotator_dir(module_name):
    import os
    from ..system import get_modules_dir

    module_dir = os.path.join(get_modules_dir(), "annotators", module_name)
    if os.path.exists(module_dir) == False:
        module_dir = None
    return module_dir


def get_annotator_script_path(module_name):
    import os
    from ..system import get_modules_dir

    module_path = os.path.join(
        get_modules_dir(), "annotators", module_name, module_name + ".py"
    )
    if os.path.exists(module_path) == False:
        module_path = None
    return module_path


def get_mapper_script_path(module_name):
    import os
    from ..system import get_modules_dir

    module_path = os.path.join(
        get_modules_dir(), "mappers", module_name, module_name + ".py"
    )
    if os.path.exists(module_path) == False:
        module_path = None
    return module_path


def get_module_version(module_name: str) -> str:
    module_conf = get_module_conf(module_name)
    if not module_conf:
        from ..exceptions import ModuleLoadingError

        raise ModuleLoadingError(module_name)
    version = module_conf.get("version", None)
    if not version:
        from ..exceptions import ModuleVersionError

        raise ModuleVersionError(module_name, "unknown")
    return version


def get_module_dir(module_name, module_type=None) -> Optional[str]:
    from os import listdir
    from os.path import join
    from os.path import exists
    from os.path import isdir
    from ..system import get_modules_dir

    if exists(module_name):
        return module_name
    modules_dir = get_modules_dir()
    if module_type:  # module name and type are given.
        p = join(modules_dir, module_type + "s", module_name)
        if exists(p):
            return p
    else:  # module folder should be searched.
        type_fns = listdir(modules_dir)
        for type_fn in type_fns:
            type_dir = join(modules_dir, type_fn)
            if isdir(type_dir) == False:
                continue
            module_fns = listdir(type_dir)
            for module_fn in module_fns:
                if module_fn == module_name:
                    return join(modules_dir, type_fn, module_fn)
    return None


def get_module_conf(module_name, module_type=None):
    from ..util.util import load_yml_conf

    conf_path = get_module_conf_path(module_name, module_type=module_type)
    if conf_path:
        return load_yml_conf(conf_path)
    else:
        return None


def get_module_conf_path(module_name, module_type=None):
    from os.path import join
    from os.path import basename

    module_dir = get_module_dir(module_name, module_type=module_type)
    if not module_dir:
        return None
    # module_name can be a folder path.
    yml_fn = basename(module_name) + ".yml"
    return join(module_dir, yml_fn)


def search_local(*patterns):
    """
    Return local module names which match any of supplied patterns
    """
    from re import fullmatch
    from ..system import get_modules_dir
    from . import list_local
    from .cache import get_module_cache

    mic = get_module_cache()
    modules_dir = get_modules_dir()
    if mic._modules_dir != modules_dir:
        mic._modules_dir = modules_dir
        mic.update_local()
    matching_names = []
    l = list_local()
    for module_name in l:
        if any([fullmatch(pattern, module_name) for pattern in patterns]):
            matching_names.append(module_name)
    return matching_names


def module_exists_local(module_name):
    from os.path import exists
    from os.path import basename
    from os.path import join
    from .cache import get_module_cache

    if module_name in get_module_cache().get_local():
        return True
    else:
        if exists(module_name):
            if exists(join(module_name, basename(module_name) + ".yml")):
                return True
    return False


def get_logo_b64(module_info) -> str:
    from base64 import b64encode
    from os.path import join
    from os.path import exists
    from PIL import Image
    from ..store.consts import logo_size
    from io import BytesIO

    p = join(module_info.directory, "logo.png")
    if exists(p):
        im = Image.open(p)
        im.thumbnail(logo_size)
        buf = BytesIO()
        im.save(buf, format="png")
        s = b64encode(buf.getvalue()).decode()
        return s
    return ""


def get_remote_manifest_from_local(module_name: str):
    from os.path import exists
    from datetime import datetime
    from json import dumps

    module_info = get_local_module_info(module_name)
    if not module_info:
        return None
    module_conf = module_info.conf
    rmi = {}
    rmi["commercial_warning"] = module_conf.get("commercial_warning", None)
    if exists(module_info.data_dir) == False:
        rmi["data_size"] = 0
    else:
        rmi["data_size"] = module_info.get_data_size()
    rmi["code_size"] = module_info.get_code_size()
    rmi["description"] = module_conf.get("description")
    rmi["developer"] = module_conf.get("developer")
    rmi["downloads"] = 0
    rmi["groups"] = module_conf.get("groups")
    rmi["output_columns"] = module_conf.get("output_columns")
    rmi["publish_time"] = str(datetime.now())
    rmi["requires"] = module_conf.get("requires", [])
    rmi["size"] = rmi["code_size"] + rmi["data_size"]
    rmi["title"] = module_conf.get("title", "")
    rmi["type"] = module_conf.get("type", "")
    rmi["tags"] = module_conf.get("tags", [])
    rmi["version"] = module_conf.get("version")
    rmi["code_version"] = module_conf.get("version")
    rmi["data_version"] = module_conf.get("datasource")
    rmi["readme"] = module_info.readme
    rmi["conf"] = dumps(module_conf)
    rmi["logo"] = get_logo_b64(module_info)
    return rmi
