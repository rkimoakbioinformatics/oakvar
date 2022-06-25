from collections.abc import MutableMapping


class LocalModuleCache(MutableMapping):
    def __init__(self, *args, **kwargs):
        self.version = None
        self.store = dict()
        self.update(dict(*args, **kwargs))  # use the free update to set keys

    def __getitem__(self, key):
        from .local import LocalModuleInfo

        if key not in self.store:
            raise KeyError(key)
        if not isinstance(self.store[key], LocalModuleInfo):
            self.store[key] = LocalModuleInfo(self.store[key])
        return self.store[key]

    def __setitem__(self, key, value):
        from os.path import isdir
        from .local import LocalModuleInfo

        if not (isinstance(value, LocalModuleInfo) or isdir(value)):
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
        self.remote_readme = {}
        self.remote_config = {}
        self.download_counts = {}
        self.remote_module_piece = {}
        self.update_local()

    def get_local(self):
        return self.local

    def update_download_counts(self, force=False):
        import oyaml as yaml
        from ..store import fetch_file_content_to_string

        if force or not self.download_counts:
            from ..store.oc import oc_module_download_counts_url

            counts_url = oc_module_download_counts_url()
            counts_str = fetch_file_content_to_string(counts_url)
            if counts_str != "" and type(counts_str) != str:
                self.download_counts = yaml.safe_load(counts_str).get("modules", {})

    def update_local(self):
        import os
        from ..consts import install_tempdir_name
        from ..system import get_modules_dir

        self.local = LocalModuleCache()
        self._modules_dir = get_modules_dir()
        if self._modules_dir is None:
            from ..exceptions import SystemMissingException

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
        from ..store import fetch_file_content_to_string
        from ..store import get_module_piece_url

        readme_url = get_module_piece_url(module_name, "readme", version=version)
        readme = fetch_file_content_to_string(readme_url)
        # add to cache
        if module_name not in self.remote_readme:
            self.remote_readme[module_name] = {}
        self.remote_readme[module_name][version] = readme
        return readme

    def get_remote_config(self, module_name, version=None):
        import oyaml as yaml
        from ..store import fetch_file_content_to_string
        from ..store import get_module_piece_url

        conf_url = get_module_piece_url(module_name, "config", version=version)
        config = yaml.safe_load(fetch_file_content_to_string(conf_url))
        # add to cache
        if module_name not in self.remote_config:
            self.remote_config[module_name] = {}
        self.remote_config[module_name][version] = config
        return config

    def get_remote_module_piece_content(self, module_name, kind, version=None):
        import oyaml as yaml
        from ..store import fetch_file_content_to_string
        from ..store import get_module_piece_url

        if (
            kind in self.remote_module_piece
            and module_name in self.remote_module_piece[kind]
        ):
            return self.remote_module_piece[kind][module_name]
        conf_url = get_module_piece_url(module_name, kind, version=version)
        if not conf_url:
            return None
        content = yaml.safe_load(fetch_file_content_to_string(conf_url))
        if kind not in self.remote_module_piece:
            self.remote_module_piece[kind] = {}
        if module_name not in self.remote_module_piece[kind]:
            self.remote_module_piece[kind][module_name] = content
        return content


def update_mic():
    global module_cache
    global custom_system_conf

    module_cache = ModuleCache()


def get_module_cache():
    global module_cache
    if not module_cache:
        module_cache = ModuleCache()
    return module_cache


module_cache = None
