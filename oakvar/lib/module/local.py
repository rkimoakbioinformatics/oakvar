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
from typing import Union
from typing import Tuple
from typing import List
from typing import Dict
from pathlib import Path


class LocalModule(object):
    def __init__(self, dir_path: Path, __module_type__=None, name=None):
        from ..util.util import load_yml_conf
        from ..store import get_developer_dict

        self.directory = Path(dir_path).absolute()
        if not name:
            self.name = self.directory.name
        else:
            self.name = name
        self.script_path = self.directory / (self.name + ".py")
        self.script_exists = self.script_path.exists()
        self.conf_path = self.directory / (self.name + ".yml")
        self.conf_exists = self.conf_path.exists()
        self.exists = self.conf_exists
        startofinstall_path = self.directory / "startofinstall"
        if startofinstall_path.exists():
            endofinstall_path = self.directory / "endofinstall"
            if endofinstall_path.exists():
                self.exists = True
            else:
                self.exists = False
        self.data_dir = dir_path / "data"
        self.test_dir = dir_path / "test"
        self.test_dir_exists = self.test_dir.is_dir()
        self.tests = self.get_tests()
        self.readme_path = self.directory / (self.name + ".md")
        self.readme_exists = self.readme_path.exists()
        if self.readme_exists:
            with open(self.readme_path, encoding="utf-8") as f:
                self.readme = f.read()
        else:
            self.readme = ""
        self.helphtml_path = self.directory / "help.html"
        self.helphtml_exists = self.helphtml_path.exists()
        self.conf: dict = {}
        if self.conf_exists:
            self.conf = load_yml_conf(self.conf_path)
        self.type = self.conf.get("type")
        self.code_version: Optional[str] = self.conf.get("code_version")
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
        self.tags: List[str] = self.conf.get("tags", [])
        self.data_source = str(self.conf.get("datasource", ""))
        self.groups = self.conf.get("groups", [])
        self.installed = True
        self.local_code_version = self.code_version
        self.local_data_source = self.data_source
        self.has_logo = (
            get_logo_path(self.name, self.type, module_dir=self.directory) is not None
        )

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
        Gets the module test input file(s) if the module has tests.
        A test is a input file / key file pair.
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
        d = {}
        for k, v in self.__dict__.items():
            if isinstance(v, Path):
                v = str(v)
            d[k] = v
        return d


def get_local_module_info(
    module_name: Union[str, Path], fresh=False
) -> Optional[LocalModule]:
    from .cache import get_module_cache

    if isinstance(module_name, str):
        p = Path(module_name)
    else:
        p = module_name
    if p.exists():
        module_info = LocalModule(p)
    else:
        module_info = None
        mc = get_module_cache(fresh=fresh)
        if fresh:
            module_path = get_module_dir(str(module_name))
            if module_path:
                module_info = LocalModule(module_path)
                if module_info:
                    mc.get_local()[module_name] = module_info
        else:
            module_info = mc.get_local().get(module_name)
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
        elif minfo.exists is False:
            continue
        else:
            return_infos.append(minfo)
    return return_infos


def get_local_module_infos_by_names(module_names: List[str]) -> Dict[str, LocalModule]:
    modules: Dict[str, LocalModule] = {}
    if not module_names:
        return modules
    for module_name in module_names:
        module = get_local_module_info(module_name)
        if module is not None:
            modules[module.name] = module
    return modules


def get_local_module_info_by_name(module_name) -> Optional[LocalModule]:
    return get_local_module_info(module_name)


def get_local_module_infos_of_type(t, update=False):
    from .cache import get_module_cache

    modules = {}
    if update:
        get_module_cache().update_local()
    for module_name in get_module_cache().get_local():
        if get_module_cache().get_local()[module_name].type == t:
            modules[module_name] = get_module_cache().get_local()[module_name]
    return modules


def get_module_code_version(
    module_name: str, module_dir: Optional[Path] = None
) -> Optional[str]:
    module_conf = get_module_conf(module_name, module_dir=module_dir)
    if not module_conf:
        return None
    version = module_conf.get("code_version", None)
    if not version:
        version = module_conf.get("version", None)
    return version


def get_module_data_version(
    module_name: str, module_dir: Optional[Path] = None
) -> Optional[str]:
    module_conf = get_module_conf(module_name, module_dir=module_dir)
    if not module_conf:
        return None
    version = module_conf.get("data_version", None)
    return version


def get_new_module_dir(
    module_name: str, module_type: str, modules_dir: Optional[Path] = None
):
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


def get_module_dir(module_name: str, module_type: str = "") -> Optional[Path]:
    from ..system import get_modules_dir

    if Path(module_name).exists():
        return Path(module_name)
    modules_dir = get_modules_dir()
    assert modules_dir is not None
    if module_type:  # module name and type are given.
        p = modules_dir / (module_type + "s") / module_name
        if p.exists():
            return p
    else:  # module folder should be searched.
        type_fns = list(modules_dir.iterdir())
        for type_fn in type_fns:
            if type_fn.name in ["temp"]:
                continue
            if type_fn.is_dir() is False:
                continue
            module_fns = list(type_fn.iterdir())
            for module_fn in module_fns:
                if module_fn.name == module_name:
                    return module_fn
    return None


def get_module_conf(
    module_name, module_type: str = "", module_dir: Optional[Path] = None
) -> Dict[str, Any]:
    from pathlib import Path
    from ..util.util import load_yml_conf

    if module_dir:
        p = Path(module_dir)
        conf_path = p / (p.stem + ".yml")
    else:
        conf_path = get_module_conf_path(module_name, module_type=module_type)
    if conf_path is None:
        return {}
    if conf_path.exists():
        return load_yml_conf(conf_path)
    else:
        return {}


def get_module_conf_path(module_name: str, module_type: str = ""):
    from pathlib import Path

    p = Path(module_name)
    if p.exists():
        return p / (p.stem + ".yml")
    module_dir = get_module_dir(module_name, module_type=module_type)
    if not module_dir:
        return None
    # module_name can be a folder path.
    yml_fn = module_name + ".yml"
    return module_dir / yml_fn


def search_local(*patterns):
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
    module_names = list_local()
    for module_name in module_names:
        for pattern in patterns:
            try:
                ret = fullmatch(pattern, module_name)
                if ret:
                    matching_names.append(module_name)
                    break
            except Exception:
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


def get_logo_b64_path(
    module_name: str, module_type: str = "", module_dir=None
) -> Optional[str]:
    from os.path import join
    from os.path import exists

    if not module_dir:
        module_dir = get_module_dir(module_name, module_type=module_type)
    if module_dir:
        p = join(module_dir, "logo.png.b64")
        if exists(p):
            return p
    return ""


def get_logo_path(
    module_name: str, module_type: str = "", module_dir=None
) -> Optional[str]:
    from os.path import join
    from os.path import exists

    if not module_dir:
        module_dir = get_module_dir(module_name, module_type=module_type)
    if module_dir:
        p = join(module_dir, "logo.png")
        if exists(p):
            return p
    return None


def get_logo_b64(module_name: str, module_type: str = "") -> Optional[str]:
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


def get_remote_manifest_from_local(module_name: str, outer=None):
    from os.path import exists
    from datetime import datetime
    from ..util.admin_util import oakvar_version
    from ..consts import publish_time_fmt

    module_info = get_local_module_info(module_name)
    if not module_info:
        return None
    module_conf = module_info.conf
    rmi = {}
    rmi["name"] = module_name
    rmi["commercial_warning"] = module_conf.get("commercial_warning", "")
    if exists(module_info.data_dir) is False:
        rmi["data_size"] = 0
    else:
        rmi["data_size"] = module_info.get_data_size()
    rmi["code_size"] = module_info.get_code_size()
    rmi["description"] = module_conf.get("description", "")
    rmi["developer"] = module_conf.get("developer", {})
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
        if outer:
            outer.error(f"code_version should be defined in {module_name}.yml\n")
        return None
    rmi["data_version"] = module_conf.get("data_version", "")
    rmi["data_source"] = module_info.latest_data_source
    rmi["no_data"] = module_conf.get("no_data", False)
    rmi["readme"] = module_info.readme
    rmi["conf"] = module_conf
    rmi["logo"] = get_logo_b64(module_name)
    rmi["min_pkg_ver"] = module_conf.get("requires_oakvar", oakvar_version())
    return rmi


def get_conf_path(module_name, module_type: str = "") -> Optional[Path]:
    module_dir = get_module_dir(module_name, module_type=module_type)
    if module_dir:
        conf_path = module_dir / (module_name + ".yml")
        if conf_path.exists():
            return conf_path
    return None


def get_conf(module_name, module_type: str = "") -> Optional[dict]:
    from pathlib import Path
    from ..util.util import load_yml_conf

    p = get_conf_path(module_name, module_type=module_type)
    if p and Path(p).exists():
        return load_yml_conf(p)


def get_cache_conf(module_name, module_type: str = "") -> Optional[dict]:
    conf = get_conf(module_name, module_type=module_type)
    if not conf:
        return None
    cache_conf = conf.get("cache", None)
    return cache_conf


def get_readme_path(module_name, module_type: str = "") -> Optional[str]:
    module_dir = get_module_dir(module_name, module_type=module_type)
    if module_dir:
        p = module_dir / (module_name + ".md")
        if p.exists():
            return p
    return None


def get_readme(module_name, module_type: str = "") -> Optional[str]:
    p = get_readme_path(module_name, module_type=module_type)
    if not p:
        return None
    with open(p) as f:
        return "\n".join(f.readlines())


def get_module_size(module_name, module_type: str = "") -> int:
    from ..util.util import get_directory_size

    d = get_module_dir(module_name, module_type=module_type)
    if d:
        return get_directory_size(d)
    else:
        return 0


def get_data_size(
    module_name, data_version: str = "", module_type: str = ""
) -> Optional[int]:
    from ..util.util import get_directory_size
    from ..store.db import get_module_data_version_size_from_store

    d = get_module_dir(module_name, module_type=module_type)
    if d:
        data_dir = d / "data"
        if data_dir.exists():
            return get_directory_size(data_dir)
    else:
        return get_module_data_version_size_from_store(module_name, data_version)


def get_code_size(module_name, module_type: str = "") -> Optional[int]:
    module_size = get_module_size(module_name, module_type=module_type)
    data_size = get_data_size(module_name, module_type=module_type) or 0
    if module_size > data_size:
        return module_size - data_size
    else:
        return None


def get_module_name_and_module_dir(module_name: str) -> Tuple[str, Path]:
    from os.path import exists
    from ..exceptions import ArgumentError
    from ..module.local import get_module_dir
    from ..exceptions import ModuleLoadingError
    from pathlib import Path

    if not module_name:
        raise ArgumentError(msg="argument module is missing")
    if exists(module_name):
        p = Path(module_name)
        module_dir = p.resolve()
        module_name = str(p.name)
    else:
        module_dir = get_module_dir(module_name)
    if not module_dir:
        raise ModuleLoadingError(module_name=module_name)
    return module_name, module_dir


def get_pack_dir_out_dir(
    kind: str, outdir: Path, module_dir: Path
) -> Tuple[Path, Path]:
    from os import mkdir

    if not outdir.exists():
        mkdir(outdir)
    if kind == "code":
        pack_dir = module_dir
    elif kind == "data":
        pack_dir = module_dir / "data"
    else:
        from ..exceptions import ArgumentError

        raise ArgumentError(msg=f"argument kind={kind} is wrong.")
    return pack_dir, outdir


def pack_module_zip(
    module_name: str,
    kind: str,
    outdir: Path = Path(".").absolute(),
    split: bool = False,
    outer=None,
) -> Optional[Path]:
    from zipfile import ZipFile
    from os import walk
    from os import sep
    from pathlib import Path
    from split_file_reader.split_file_writer import SplitFileWriter
    from ..module.local import get_module_code_version
    from ..store.consts import MODULE_PACK_SPLIT_FILE_SIZE
    from ..exceptions import ArgumentError
    from ..exceptions import ModuleLoadingError

    try:
        module_name, module_dir = get_module_name_and_module_dir(module_name)
    except ModuleLoadingError:
        if outer:
            outer.error(f"Module {module_name} not found.")
        return None
    if kind == "code":
        version = get_module_code_version(module_name, module_dir=module_dir)
    elif kind == "data":
        version = get_module_data_version(module_name, module_dir=module_dir)
    else:
        raise ArgumentError(msg=f"wrong module kind: {kind}")
    if kind == "data" and version is None:
        e = ArgumentError(
            msg="data_version: <version> or no_data: true should be "
            + "defined in the module yml file."
        )
        e.traceback = False
        raise e
    pack_dir, outdir = get_pack_dir_out_dir(kind, outdir, module_dir)
    outdir_p = Path(outdir)
    if Path(pack_dir).exists():
        pack_fn = f"{module_name}__{version}__{kind}.zip"
        pack_path = outdir_p / pack_fn
        sfw = None
        z = None
        if split:
            sfw = SplitFileWriter(pack_path, MODULE_PACK_SPLIT_FILE_SIZE)
            z = ZipFile(file=sfw, mode="w")
        else:
            z = ZipFile(pack_path, "w")
        for root, _, files in walk(pack_dir):
            root_p = Path(root)
            if root_p.name.startswith(".") or root_p.name.startswith("_"):
                continue
            if root_p.name in ["config", "cache"]:
                continue
            if kind == "code" and root_p.name == "data":
                continue
            for file in files:
                if (
                    file.startswith(".")
                    or file == "startofinstall"
                    or file == "endofinstall"
                ):
                    continue
                p = root_p / file
                arcname = root_p / file
                if str(arcname).startswith(str(pack_dir)):
                    arcname = str(arcname)[len(str(pack_dir)) :].lstrip(sep)
                if kind == "code":
                    arcname = arcname  # join(module_name, arcname)
                elif kind == "data":
                    arcname = Path("data") / arcname
                z.write(p, arcname=arcname)
        if z:
            z.close()
        if sfw:
            sfw.close()
            if outer:
                outer.write(f"{pack_path}* files written")
            return pack_path
        else:
            if outer:
                outer.write(f"{pack_path} written")
            return pack_path


def pack_module(
    module_name: str, outdir: Path, code_only: bool, split: bool, outer=None
) -> Optional[Dict[str, Optional[Path]]]:
    conf = get_module_conf(module_name)
    code_zip_path = pack_module_zip(
        module_name, "code", outdir=outdir, split=split, outer=outer
    )
    if code_zip_path is None:
        return None
    if not code_only and not (conf and conf.get("no_data")):
        data_zip_path = pack_module_zip(
            module_name, "data", outdir=outdir, split=split, outer=outer
        )
        if data_zip_path is None:
            return None
    else:
        data_zip_path = None
    return {"code": code_zip_path, "data": data_zip_path}


def load_modules(annotators: list = [], mapper: Optional[str] = None, input_file=None):
    from ... import get_mapper
    from ... import get_annotator

    modules = {}
    if mapper:
        modules[mapper] = get_mapper(mapper, input_file=input_file)
    for module_name in annotators:
        modules[module_name] = get_annotator(module_name)
    return modules


def remove_code_part_of_module(module_name: str, module_dir=None):
    from pathlib import Path
    from os import listdir
    from os import remove
    from shutil import rmtree

    if not module_dir:
        module_dir = get_module_dir(module_name)
    if not module_dir:
        return
    for item in listdir(module_dir):
        item_path = Path(module_dir) / item
        if item != "data" and item_path.exists():
            if item_path.is_dir():
                rmtree(item_path, ignore_errors=True)
            else:
                remove(item_path)


def is_same_class_val(a_val, b_val):
    from types import FunctionType
    from inspect import getsource

    a_ty = type(a_val)
    b_ty = type(b_val)
    if a_ty != b_ty:
        return False
    else:
        if a_ty == FunctionType:
            a_code = getsource(a_val)
            b_code = getsource(b_val)
            if a_code != b_code:
                return False
            else:
                return True
        else:
            if a_val != b_val:
                return False
            else:
                return True


def get_code_for_class_val(key, val, cls) -> str:
    import types
    from inspect import getsourcelines

    ty = type(val)
    if isinstance(ty, types.FunctionType):
        lines = getsourcelines(val)[0]
        if not str(val).startswith(f"<function {cls.__name__}"):
            lines = ["    " + line for line in lines]
        return "".join(lines)
    else:
        if isinstance(val, str):
            return f'    {key} = "{val}"'
        else:
            return f"    {key} = {val}"


def get_class_code(cls) -> List[str]:
    from types import FunctionType

    code = []
    base_cls = cls.__mro__[1]
    code.append(f"class {cls.__name__}({base_cls.__name__}):\n")
    keys_to_write_non_fn = []
    keys_to_write_fn = []
    for key in dir(cls):
        if key.startswith("__"):
            continue
        a_val = getattr(cls, key)
        a_type = type(a_val)
        if key not in dir(base_cls):
            if a_type == FunctionType:
                keys_to_write_fn.append(key)
            else:
                keys_to_write_non_fn.append(key)
            continue
        ba_val = getattr(base_cls, key)
        if not is_same_class_val(a_val, ba_val):
            if a_type == FunctionType:
                keys_to_write_fn.append(key)
            else:
                keys_to_write_non_fn.append(key)
            continue
    for key in keys_to_write_non_fn:
        val = getattr(cls, key)
        code.append(get_code_for_class_val(key, val, cls))
    if keys_to_write_non_fn:
        code.append("")
    for key in keys_to_write_fn:
        val = getattr(cls, key)
        code.append(get_code_for_class_val(key, val, cls))
    return code


def create_module_files(instance, overwrite: bool = False, interactive: bool = False):
    from pathlib import Path
    from os import makedirs
    from os import getcwd
    from shutil import copytree
    from shutil import ignore_patterns
    from oyaml import dump
    from ..exceptions import IncompleteModuleError
    from ..exceptions import SystemMissingException
    from ..system import get_modules_dir
    from ..util.util import is_in_jupyter_notebook

    cls = instance.__class__
    if not cls:
        raise Exception("Only an OakVar class can be saved into module files.")
    modules_dir = get_modules_dir()
    if not modules_dir:
        raise SystemMissingException(
            msg="Modules root directory does not exist. Consider running "
            + "'ov system setup'."
        )
    module_conf = getattr(instance, "conf", {})
    module_name: Optional[str] = getattr(
        instance, "module_name", module_conf.get("name")
    )
    module_type: Optional[str] = getattr(
        instance, "module_type", module_conf.get("type")
    )
    module_version: Optional[str] = getattr(
        instance, "code_version", module_conf.get("code_version")
    )
    module_title: Optional[str] = getattr(instance, "title", module_conf.get("title"))
    module_level: Optional[str] = getattr(instance, "level", module_conf.get("level"))
    output_columns: Optional[List[Dict[str, Any]]] = getattr(
        instance, "output_columns", module_conf.get("output_columns", [])
    )
    if not module_name:
        if interactive:
            if is_in_jupyter_notebook():
                print(
                    "Interactive mode is not available in Jupyter notebook. Please provide module name in the instance argument."
                )
            else:
                module_name = input("Module name:")
    if not module_name:
        raise IncompleteModuleError(
            msg="name property does not exist in the module. Consider "
            + "giving 'name' argument at initializing the module."
        )
    if not module_version:
        if interactive:
            if is_in_jupyter_notebook():
                print(
                    "Interactive mode is not available in Jupyter notebook. Please provide module version in the instance argument."
                )
            else:
                module_version = input("Module version:")
    if not module_version:
        raise IncompleteModuleError(
            msg="code_version property does not exist in the module. Consider "
            + "giving 'code_version' argument at initializing the module."
        )
    if not module_title:
        if interactive:
            if is_in_jupyter_notebook():
                print(
                    "Interactive mode is not available in Jupyter notebook. Please provide module title in the instance argument."
                )
            else:
                module_title = input("Module title:")
    if not module_title:
        raise IncompleteModuleError(
            msg="title property does not exist in the module. Consider giving "
            + "'title' argument at initializing the module."
        )
    if not module_type:
        if is_in_jupyter_notebook():
            print(
                "Interactive mode is not available in Jupyter notebook. Please provide module type in the instance argument."
            )
        else:
            module_type = input("Module type:")
    if not module_type:
        raise IncompleteModuleError(
            msg="module_type property does not exist in the module."
        )
    module_dir = modules_dir / (module_type + "s") / module_name
    if module_type in ["annotator", "postaggregator"]:
        if not module_level:
            if is_in_jupyter_notebook():
                print(
                    "Interactive mode is not available in Jupyter notebook. Please provide module level in the instance argument."
                )
            else:
                module_level = input("Module level:")
        if not module_level:
            raise IncompleteModuleError(
                msg="title property does not exist in the module. Consider giving "
                + "'level' argument at initializing the module."
            )
        if not output_columns:
            raise IncompleteModuleError(
                msg="output_columns property does not exist in the module. "
                + "Consider giving 'output_columns' argument at initializing the module."
            )
    if module_dir.exists() and not overwrite:
        raise Exception(f"{module_dir} already exists.")
    makedirs(module_dir, exist_ok=True)
    makedirs(module_dir / "data", exist_ok=True)
    makedirs(module_dir / "test", exist_ok=True)
    makedirs(module_dir / "cache", exist_ok=True)
    md_path = module_dir / (module_name + ".md")
    py_path = module_dir / (module_name + ".py")
    yml_path = module_dir / (module_name + ".yml")
    template_md_path = (
        Path(__file__).parent.parent
        / "assets"
        / "module_templates"
        / module_type
        / "template.md"
    )
    with open(md_path, "w") as wf, open(template_md_path) as f:
        lines = f.readlines()
        for line in lines:
            wf.write(line.replace("MODULE_TITLE", module_title))
    with open(py_path, "w") as wf:
        base_cls = cls.__mro__[1]
        wf.write(f"from oakvar import {base_cls.__name__}\n")
        wf.write("\n")
        wf.write("\n".join(get_class_code(cls)))
    with open(yml_path, "w") as wf:
        wf.write(f"name: {module_name}\n")
        wf.write(f"title: {module_title}\n")
        wf.write(f"code_version: {module_version}\n")
        wf.write(f"type: {module_type}\n")
        if module_level:
            wf.write(f"level: {module_level}\n")
        yml = module_conf.copy()
        if "name" in yml:
            del yml["name"]
        if "title" in yml:
            del yml["title"]
        if "code_version" in yml:
            del yml["code_version"]
        if "type" in yml:
            del yml["type"]
        if "level" in yml:
            del yml["level"]
        if "output_columns" not in yml and output_columns:
            yml["output_columns"] = output_columns
        if "output_columns" in yml:
            del_idx = None
            for i, col in enumerate(yml["output_columns"]):
                if module_level == "variant" and col.get("name") == "uid":
                    del_idx = i
                    break
                elif module_level == "gene" and col.get("name") == "hugo":
                    del_idx = i
                    break
            if del_idx is not None:
                del yml["output_columns"][del_idx]
        if "output_columns" in yml and not yml["output_columns"]:
            del yml["output_columns"]
        if yml:
            dump(yml, wf)
    cwd = Path(getcwd())
    data_dir = cwd / "data"
    if data_dir.exists():
        copytree(
            data_dir,
            module_dir / "data",
            ignore=ignore_patterns(".ipynb_checkpoints"),
            dirs_exist_ok=True,
        )
