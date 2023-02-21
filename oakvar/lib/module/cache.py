from collections.abc import MutableMapping


class LocalModuleCache(MutableMapping):
    def __init__(self, *args, **kwargs):
        self.version = None
        self.store = dict()
        self.update(dict(*args, **kwargs))  # use the free update to set keys

    def __getitem__(self, key):
        from pathlib import Path
        from .local import LocalModule

        if key not in self.store:
            raise KeyError(key)
        if not isinstance(self.store[key], LocalModule):
            self.store[key] = LocalModule(Path(self.store[key]))
        return self.store[key]

    def __setitem__(self, key, value):
        from os.path import isdir
        from .local import LocalModule

        if not (isinstance(value, LocalModule) or isdir(value)):
            raise ValueError(value)
        self.store[key] = value

    def __delitem__(self, key):
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

        # from .local import get_local_module_info
        mdir = get_module_dir(module_name)
        if not mdir:
            return
        # module = get_local_module_info(module_name)
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
                    module_dir.startswith(".") == False
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


def get_module_cache(fresh=False):
    global module_cache
    if not module_cache or fresh:
        module_cache = ModuleCache()
    return module_cache


module_cache = None
