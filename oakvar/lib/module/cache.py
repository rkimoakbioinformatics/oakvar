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

from typing import Dict
from typing import Union
from pathlib import Path
from collections.abc import MutableMapping
from .local import LocalModule


class LocalModuleCache(MutableMapping):
    def __init__(self, *args, **kwargs):
        self.version = None
        self.store: Dict[str, LocalModule] = dict()
        self.update(dict(*args, **kwargs))  # use the free update to set keys

    def __getitem__(self, key: Union[str, Path]):
        if isinstance(key, Path):
            key = str(key)
        if key not in self.store:
            raise KeyError(key)
        return self.store[key]

    def __setitem__(self, key: Union[str, Path], value: Union[str, Path, LocalModule]):
        from os.path import isdir
        from pathlib import Path
        from .local import LocalModule

        if not (isinstance(value, LocalModule) or isdir(value)):
            raise ValueError(value)
        if isinstance(key, Path):
            key = str(key)
        if isinstance(value, str):
            value = LocalModule(Path(value))
        elif isinstance(value, Path):
            value = LocalModule(value)
        self.store[key] = value

    def __delitem__(self, key: str):
        del self.store[key]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)


class ModuleCache(object):
    def __init__(self):
        from ..system import get_modules_dir

        self._modules_dir = get_modules_dir()
        self.local = LocalModuleCache()
        self.remote = {}
        self.remote_ls = {}
        self.remote_readme = {}
        self.update_local()

    def get_local(self):
        return self.local

    def add_local(self, module_name):
        from .local import get_module_dir

        mdir = get_module_dir(module_name)
        if not mdir:
            return
        self.local[module_name] = mdir
        return mdir

    def remove_local(self, module_name):
        if module_name in self.local:
            del self.local[module_name]

    def update_local(self):
        import os
        from ..consts import install_tempdir_name
        from ..system import get_modules_dir
        from ..exceptions import SystemMissingException

        self.local = LocalModuleCache()
        self._modules_dir = get_modules_dir()
        if self._modules_dir is None:
            raise SystemMissingException(msg="Modules directory is not set")
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
                    module_dir.startswith(".") is False
                    and os.path.isdir(module_dir)
                    and not module_name.startswith(".")
                    and not module_name.startswith("_")
                    and os.path.exists(os.path.join(module_dir, module_name + ".yml"))
                ):
                    self.local[module_name] = module_dir

    def get_remote_readme(self, module_name, version=None):
        from .remote import get_readme

        if module_name not in self.remote_readme:
            self.remote_readme[module_name] = {}
        if version in self.remote_readme[module_name]:
            return self.remote_readme[module_name][version]
        readme = get_readme(module_name)
        self.remote_readme[module_name][version] = readme
        return readme


def get_module_cache(fresh=False) -> ModuleCache:
    global module_cache
    if not module_cache or fresh:
        module_cache = ModuleCache()
    return module_cache


module_cache = None
