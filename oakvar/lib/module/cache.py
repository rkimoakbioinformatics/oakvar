# OakVar Dual License
# 
# Copyright (c) 2023 Oak Bioinformatics, LLC
# 
# This program is dual licensed under the Affero GPL-3.0 or later for non-commercial, 
# open source use, and a commercial license, which is available for purchase, 
# for commercial use.
# 
# For commercial use, please contact Oak Bioinformatics, LLC for obtaining a
# commercial license. OakVar commercial license does not impose the Affero GPL
# open-source licensing terms, conditions, and limitations. To obtain a
# commercial-use license of OakVar, please visit our website at
# https://oakbioinformatics.com or contact us at info@oakbioinformatics.com for
# more information.
# 
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


class LocalModuleCache(MutableMapping):
    from .local import LocalModule

    def __init__(self, *args, **kwargs):
        from .local import LocalModule

        self.version = None
        self.store: Dict[str, LocalModule] = dict()
        self.update(dict(*args, **kwargs))  # use the free update to set keys

    def __getitem__(self, key: Union[str, Path]) -> LocalModule:
        if isinstance(key, Path):
            key = str(key)
        if key not in self.store:
            raise KeyError(key)
        return self.store[key]

    def __setitem__(self, key, value: LocalModule):
        from pathlib import Path
        from .local import LocalModule

        if not (isinstance(value, LocalModule) or Path(value).is_dir()):
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

    def __len__(self) -> int:
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
        from .local import LocalModule

        # from .local import get_local_module_info
        mdir = get_module_dir(module_name)
        if not mdir:
            return
        # module = get_local_module_info(module_name)
        self.local[module_name] = LocalModule(mdir)
        return mdir

    def remove_local(self, module_name):
        if module_name in self.local:
            del self.local[module_name]

    def update_local(self):
        from ..consts import install_tempdir_name
        from ..system import get_modules_dir
        from ..exceptions import SystemMissingException
        from .local import LocalModule

        self.local = LocalModuleCache()
        self._modules_dir = get_modules_dir()
        if self._modules_dir is None:
            raise SystemMissingException(msg="Modules directory is not set")
        if not self._modules_dir.exists():
            return None
        for mg in self._modules_dir.iterdir():
            try:
                basename = mg.name
                if basename == install_tempdir_name:
                    continue
                mg_path = self._modules_dir / mg
                if (
                    not mg_path.is_dir()
                    or basename.startswith(".")
                    or basename.startswith("_")
                ):
                    continue
                for path in mg_path.iterdir():
                    module_name = path.name
                    module_dir = mg_path / module_name
                    yml_path = module_dir / (module_name + ".yml")
                    if (
                        module_name.startswith(".") is False
                        and module_dir.is_dir()
                        and not module_name.startswith(".")
                        and not module_name.startswith("_")
                        and yml_path.exists()
                    ):
                        try:
                            self.local[path.name] = LocalModule(Path(module_dir))
                        except Exception:
                            import traceback

                            traceback.print_exc()
                            continue
            except Exception:
                import traceback

                traceback.print_exc()
                continue

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
