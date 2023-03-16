from typing import Dict
from pathlib import Path
from collections.abc import MutableMapping


class LocalModuleCache(MutableMapping):
    from .local import LocalModule

    def __init__(self, *args, **kwargs):
        from .local import LocalModule

        self.version = None
        self.store: Dict[str, LocalModule] = dict()
        self.update(dict(*args, **kwargs))  # use the free update to set keys

    def __getitem__(self, key: str) -> LocalModule:
        from .local import LocalModule

        if key not in self.store:
            raise KeyError(key)
        if not isinstance(self.store[key], LocalModule):
            self.store[key] = LocalModule(Path(key))
        return self.store[key]

    def __setitem__(self, key, value: LocalModule):
        from .local import LocalModule

        if not (isinstance(value, LocalModule) or Path(value).is_dir()):
            raise ValueError(value)
        self.store[key] = value

    def __delitem__(self, key):
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
                if module_name == "hgvs":  # deprecate hgvs
                    continue
                module_dir = mg_path / module_name
                yml_path = module_dir / (module_name + ".yml")
                if (
                    module_name.startswith(".") is False
                    and module_dir.is_dir()
                    and not module_name.startswith(".")
                    and not module_name.startswith("_")
                    and yml_path.exists()
                ):
                    self.local[path.name] = LocalModule(Path(module_dir))

    def get_remote_readme(self, module_name, version=None):
        from .remote import get_readme

        if module_name not in self.remote_readme:
            self.remote_readme[module_name] = {}
        if version in self.remote_readme[module_name]:
            return self.remote_readme[module_name][version]
        readme = get_readme(module_name)
        self.remote_readme[module_name][version] = readme
        return readme


def get_module_cache(fresh=False):
    global module_cache
    if not module_cache or fresh:
        module_cache = ModuleCache()
    return module_cache


module_cache = None
