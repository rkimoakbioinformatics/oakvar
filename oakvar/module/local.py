from typing import Optional
from typing import Tuple


class LocalModule(object):
    def __init__(self, dir_path, __module_type__=None, name=None):
        import os
        from ..util.util import load_yml_conf
        from ..store import get_developer_dict
        from os.path import abspath

        self.directory = abspath(dir_path)
        if not name:
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
        self.code_version = self.conf.get("code_version")
        if not self.code_version:
            self.code_version = self.conf.get("version")
        self.version = self.code_version
        self.latest_code_version = self.code_version
        self.latest_data_source = self.conf.get("datasource", "")
        self.description = self.conf.get("description")
        self.hidden = self.conf.get("hidden", False)
        self.developer = get_developer_dict(self.conf.get("developer", {}))
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
        self.data_source = str(self.conf.get("datasource", ""))
        self.smartfilters = self.conf.get("smartfilters")
        self.groups = self.conf.get("groups", [])
        self.installed = True
        self.local_code_version = self.code_version
        self.local_data_source = self.data_source

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


def get_local_module_info(module_name, force=False):
    from os.path import exists
    from .cache import get_module_cache

    if exists(module_name):
        module_info = LocalModule(module_name)
    else:
        mc = get_module_cache(force=force)
        if module_name in mc.get_local():
            module_info = mc.get_local()[module_name]
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


def get_module_code_version(module_name: str, module_dir=None) -> Optional[str]:
    module_conf = get_module_conf(module_name, module_dir=module_dir)
    if not module_conf:
        return None
    version = module_conf.get("code_version", None)
    if not version:
        version = module_conf.get("version", None)
    return version


def get_module_data_version(module_name: str, module_dir: Optional[str]=None) -> Optional[str]:
    module_conf = get_module_conf(module_name, module_dir=module_dir)
    if not module_conf:
        return None
    version = module_conf.get("data_version", None)
    return version


def get_new_module_dir(module_name: str, module_type: str, modules_dir: Optional[str]=None):
    from ..system import get_modules_dir
    from pathlib import Path
    if not modules_dir:
        modules_dir = get_modules_dir()
    if not modules_dir:
        return None
    module_dir = Path(modules_dir) / (module_type + "s") / module_name
    if not module_dir.exists():
        module_dir.mkdir(parents=True)
    return str(module_dir)


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
            if type_fn in ["temp"]:
                continue
            type_dir = join(modules_dir, type_fn)
            if isdir(type_dir) == False:
                continue
            module_fns = listdir(type_dir)
            for module_fn in module_fns:
                if module_fn == module_name:
                    return join(modules_dir, type_fn, module_fn)
    return None

def get_module_data_dir(module_name, module_type=None) -> Optional[str]:
    from os.path import join

    module_dir = get_module_dir(module_name, module_type=module_type)
    if not module_dir:
        return None
    return join(module_dir, "data")

def get_module_conf(module_name, module_type=None, module_dir=None):
    from ..util.util import load_yml_conf
    from pathlib import Path

    if module_dir:
        p = Path(module_dir)
        conf_path = p / (p.stem + ".yml")
    else:
        conf_path = get_module_conf_path(module_name, module_type=module_type)
    if conf_path:
        return load_yml_conf(conf_path)
    else:
        return None


def get_module_conf_path(module_name, module_type=None):
    from os.path import join
    from os.path import basename
    from pathlib import Path

    p = Path(module_name)
    if p.exists():
        return p.parent / (p.stem + ".yml")
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
        for pattern in patterns:
            try:
                ret = fullmatch(pattern, module_name)
                if ret:
                    matching_names.append(module_name)
                    break
            except:
                continue
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


def get_logo_b64_path(module_name: str, module_type=None, module_dir=None) -> Optional[str]:
    from os.path import join
    from os.path import exists

    if not module_dir:
        module_dir = get_module_dir(module_name, module_type=module_type)
    if module_dir:
        p = join(module_dir, "logo.png.b64")
        if exists(p):
            return p
    return ""

def get_logo_path(module_name: str, module_type=None, module_dir=None) -> Optional[str]:
    from os.path import join
    from os.path import exists

    if not module_dir:
        module_dir = get_module_dir(module_name, module_type=module_type)
    if module_dir:
        p = join(module_dir, "logo.png")
        if exists(p):
            return p
    return None


def get_logo_b64(module_name: str, module_type=None) -> Optional[str]:
    from base64 import b64encode
    from PIL import Image
    from ..store.consts import logo_size
    from io import BytesIO

    module_dir = get_module_dir(module_name, module_type=module_type)
    p = get_logo_b64_path(module_name, module_type=module_type, module_dir=module_dir)
    if not p:
        p = get_logo_path(module_name, module_type=module_type, module_dir=module_dir)
    if p:
        im = Image.open(p)
        im.thumbnail(logo_size)
        buf = BytesIO()
        im.save(buf, format="png")
        s = b64encode(buf.getvalue()).decode()
        return s
    return None


def get_remote_manifest_from_local(module_name: str, args={}):
    from os.path import exists
    from datetime import datetime
    from ..util.util import quiet_print
    from ..consts import publish_time_fmt

    module_info = get_local_module_info(module_name)
    if not module_info:
        return None
    module_conf = module_info.conf
    rmi = {}
    rmi["name"] = module_name
    rmi["commercial_warning"] = module_conf.get("commercial_warning", "")
    if exists(module_info.data_dir) == False:
        rmi["data_size"] = 0
    else:
        rmi["data_size"] = module_info.get_data_size()
    rmi["code_size"] = module_info.get_code_size()
    rmi["description"] = module_conf.get("description", "")
    rmi["developer"] = module_conf.get("developer", {})
    rmi["downloads"] = 0
    rmi["groups"] = module_conf.get("groups", [])
    rmi["output_columns"] = module_conf.get("output_columns", [])
    rmi["publish_time"] = datetime.now().strftime(publish_time_fmt)
    rmi["requires"] = module_conf.get("requires", [])
    rmi["size"] = rmi["code_size"] + rmi["data_size"]
    rmi["title"] = module_conf.get("title", "")
    rmi["type"] = module_conf.get("type", "")
    rmi["tags"] = module_conf.get("tags", [])
    rmi["version"] = module_conf.get("version", "")
    rmi["code_version"] = module_conf.get("code_version", "")
    if not rmi["code_version"]:
        rmi["code_version"] = module_conf.get("version", "")
    if not rmi["code_version"]:
        quiet_print(f"code_version should be defined in {module_name}.yml", args=args)
        return None
    rmi["data_version"] = module_conf.get("data_version", "")
    rmi["data_source"] = module_info.latest_data_source
    rmi["no_data"] = module_conf.get("no_data", False)
    rmi["readme"] = module_info.readme
    rmi["conf"] = module_conf
    rmi["logo"] = get_logo_b64(module_name)
    return rmi


def get_conf_path(module_name, module_type=None) -> Optional[str]:
    from os.path import join
    from os.path import exists

    module_dir = get_module_dir(module_name, module_type=module_type)
    if module_dir:
        conf_path = join(module_dir, module_name + ".yml")
        if exists(conf_path):
            return conf_path
    return None


def get_conf_str(module_name, module_type=None) -> Optional[str]:
    conf_path = get_conf_path(module_name, module_type=module_type)
    if not conf_path:
        return None
    with open(conf_path) as f:
        return "\n".join(f.readlines())


def get_conf(module_name, module_type=None) -> Optional[dict]:
    from ..util.util import load_yml_conf

    p = get_conf_path(module_name, module_type=module_type)
    return load_yml_conf(p)


def get_readme_path(module_name, module_type=None) -> Optional[str]:
    from os.path import join
    from os.path import exists

    module_dir = get_module_dir(module_name, module_type=module_type)
    if module_dir:
        p = join(module_dir, module_name + ".md")
        if exists(p):
            return p
    return None


def get_readme(module_name, module_type=None) -> Optional[str]:
    p = get_readme_path(module_name, module_type=module_type)
    if not p:
        return None
    with open(p) as f:
        return "\n".join(f.readlines())


def get_module_size(module_name, module_type=None) -> Optional[int]:
    from ..util.util import get_directory_size

    d = get_module_dir(module_name, module_type=module_type)
    if d:
        return get_directory_size(d)


def get_data_size(module_name, module_type=None) -> Optional[int]:
    from ..util.util import get_directory_size
    from os.path import join
    from os.path import exists

    d = get_module_dir(module_name, module_type=module_type)
    if d:
        data_dir = join(d, "data")
        if exists(data_dir):
            return get_directory_size(data_dir)


def get_code_size(module_name, module_type=None) -> Optional[int]:
    module_size = get_module_size(module_name, module_type=module_type)
    data_size = get_data_size(module_name, module_type=module_type) or 0
    if module_size:
        return module_size - data_size
    return None


def get_module_name_and_module_dir(args) -> Tuple[str, str]:
    from os.path import exists
    from ..exceptions import ArgumentError
    from ..module.local import get_module_dir
    from ..exceptions import ModuleLoadingError
    from pathlib import Path

    module_name = args.get("module")
    if not module_name:
        raise ArgumentError(msg="argument module is missing")
    if exists(module_name):
        p = Path(module_name)
        module_dir = str(p.resolve())
        module_name = str(p.name)
    else:
        module_dir = get_module_dir(module_name)
    if not module_dir:
        raise ModuleLoadingError(module_name)
    return module_name, module_dir


def get_pack_dir_out_dir(kind: str, args: dict, module_dir: str) -> Tuple[str, str]:
    from os.path import exists
    from os.path import join

    outdir = args.get("outdir", ".")
    if not exists(outdir):
        from os import mkdir

        mkdir(outdir)
    if kind == "code":
        pack_dir = module_dir
    elif kind == "data":
        pack_dir = join(module_dir, "data")
    else:
        from ..exceptions import ArgumentError

        raise ArgumentError(msg=f"argument kind={kind} is wrong.")
    return pack_dir, outdir


def pack_module_zip(args: dict, kind: str):
    from os.path import join
    from zipfile import ZipFile
    from os import walk
    from os import sep
    from os.path import basename
    from os.path import exists
    from os import sep
    from ..util.util import quiet_print
    from ..module.local import get_module_code_version
    from split_file_reader.split_file_writer import SplitFileWriter
    from ..store.consts import ov_store_split_file_size
    from ..exceptions import ArgumentError

    module_name, module_dir = get_module_name_and_module_dir(args)
    if kind == "code":
        version = get_module_code_version(module_name, module_dir=module_dir)
    elif kind == "data":
        version = get_module_data_version(module_name, module_dir=module_dir)
    else:
        raise ArgumentError(msg=f"wrong module kind: {kind}")
    pack_dir, outdir = get_pack_dir_out_dir(kind, args, module_dir)
    if exists(pack_dir):
        pack_fn = f"{module_name}__{version}__{kind}.zip"
        pack_path = join(outdir, pack_fn)
        split = args.get("split")
        sfw = None
        z = None
        if split is not None:
            if len(split) == 0:
                split_size = ov_store_split_file_size
            else:
                split_size = split[0]
            sfw = SplitFileWriter(pack_path, split_size)
            z = ZipFile(file=sfw, mode="w")
        else:
            z = ZipFile(pack_path, "w")
        for root, _, files in walk(pack_dir):
            root_basename = basename(root)
            if root_basename.startswith(".") or root_basename.startswith("_"):
                continue
            if kind == "code" and root_basename == "data":
                continue
            for file in files:
                if (
                    file.startswith(".")
                    or file == "startofinstall"
                    or file == "endofinstall"
                ):
                    continue
                p = join(root, file)
                arcname = join(root, file)
                if pack_dir in arcname:
                    arcname = arcname[len(pack_dir) :].lstrip(sep)
                if kind == "code":
                    arcname = arcname  # join(module_name, arcname)
                elif kind == "data":
                    arcname = join("data", arcname)
                z.write(p, arcname=arcname)
        if z:
            z.close()
        if sfw:
            sfw.close()
            quiet_print(f"{pack_path}* files written", args=args)
        else:
            quiet_print(f"{pack_path} written", args=args)


def pack_module(args):
    from ..util.util import quiet_print

    pack_module_zip(args, "code")
    if not args.get("code_only"):
        pack_module_zip(args, "data")
    quiet_print(f"To register the packed module, use `ov store register`.", args=args)
    return True


def get_default_mapper_name() -> Optional[str]:
    from ..util.admin_util import get_user_conf

    conf = get_user_conf()
    if conf:
        default_assembly = conf.get("default_mapper", None)
        return default_assembly


def load_modules(annotators: list = [], mapper: Optional[str] = None, input_file=None):
    from .. import get_live_mapper
    from .. import get_live_annotator

    modules = {}
    if mapper:
        modules[mapper] = get_live_mapper(mapper, input_file=input_file)
    for module_name in annotators:
        modules[module_name] = get_live_annotator(module_name)
    return modules


