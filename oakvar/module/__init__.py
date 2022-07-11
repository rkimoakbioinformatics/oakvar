class InstallProgressHandler(object):
    def __init__(self, module_name, module_version):
        self.module_name = module_name
        self.module_version = module_version
        self.display_name = None
        self._make_display_name()
        self.cur_stage = None

    def _make_display_name(self):
        ver_str = self.module_version if self.module_version is not None else ""
        self.display_name = ":".join([self.module_name, ver_str])

    def stage_start(self, __stage__):
        pass

    def stage_progress(
        self, __cur_chunk__, __total_chunks__, __cur_size__, __total_size__
    ):
        pass

    def set_module_version(self, module_version):
        self.module_version = module_version
        self._make_display_name()

    def set_module_name(self, module_name):
        self.module_name = module_name
        self._make_display_name()

    def _stage_msg(self, stage):
        from ..util.util import get_current_time_str

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


def get_readme(module_name):
    from os.path import exists
    from ..store import remote_module_latest_version
    from ..store.db import module_latest_code_version
    from .local import module_exists_local
    from .cache import get_module_cache
    from .local import get_local_module_info
    from ..util.util import compare_version

    exists_local = module_exists_local(module_name)
    remote_ver = module_latest_code_version(module_name)
    if remote_ver:
        remote_readme = get_module_cache().get_remote_readme(
            module_name, version=remote_ver
        )
    else:
        remote_readme = ""
    if exists_local:
        local_info = get_local_module_info(module_name)
        if local_info and exists(local_info.readme_path):
            local_readme = open(local_info.readme_path).read()
        else:
            local_readme = ""
        if local_info and remote_ver:
            remote_version = remote_module_latest_version(module_name)
            local_version = local_info.version
            if compare_version(remote_version, local_version) > 0:
                return remote_readme
            else:
                return local_readme
        else:
            return local_readme
    else:
        local_readme = ""
        if remote_ver:
            return remote_readme
        else:
            return local_readme


def install_pypi_dependencies(module_name: str, pypi_deps, args={}):
    from subprocess import run
    from ..util.util import quiet_print

    idx = 0
    if pypi_deps:
        quiet_print(
            f"Following PyPI dependencies should be met before installing {module_name}.",
            args=args,
        )
        for dep in pypi_deps:
            quiet_print(f"- {dep}", args=args)
        quiet_print(f"Installing required PyPI packages...", args=args)
        idx = 0
        while idx < len(pypi_deps):
            dep = pypi_deps[idx]
            r = run(["pip", "install", dep])
            if r.returncode == 0:
                pypi_deps.remove(dep)
            else:
                idx += 1
        if len(pypi_deps) > 0:
            quiet_print(
                f"Following PyPI dependencies could not be installed.",
                args=args,
            )
            for dep in pypi_deps:
                quiet_print(f"- {dep}", args=args)
    if pypi_deps:
        quiet_print(
            f"Skipping installation of {module_name} due to unmet requirement for PyPI packages",
            args=args,
        )
        return False
    else:
        return True


def list_local():
    from ..system import get_modules_dir
    from .cache import get_module_cache

    modules_dir = get_modules_dir()
    module_cache = get_module_cache()
    if module_cache._modules_dir != modules_dir:
        module_cache._modules_dir = modules_dir
        module_cache.update_local()
    return sorted(list(get_module_cache().get_local().keys()))


def list_remote():
    from ..store.db import module_list

    return module_list()


def get_updatable(modules=[], strategy="consensus"):
    from distutils.version import LooseVersion
    from pkg_resources import Requirement
    from collections import defaultdict
    from types import SimpleNamespace
    from .local import get_local_module_info
    from .remote import get_remote_module_info
    from ..store.db import module_data_version

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
        if local_info is not None:
            req_strings = local_info.conf.get("requires", [])
            reqs = [Requirement.parse(s) for s in req_strings]
            for req in reqs:
                dep = req.unsafe_name
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
            and local_info
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
                    for _, requirement in reqs.items():
                        version_passes = version in requirement
                        if not version_passes:
                            break
                    if version_passes:
                        passing_versions.append(version)
                selected_version = passing_versions[-1] if passing_versions else None
        if (
            selected_version
            and remote_info
            and local_info
            and local_info.version
            and LooseVersion(selected_version) > LooseVersion(local_info.version)
        ):
            update_data_version = module_data_version(mname, selected_version)
            installed_data_version = module_data_version(mname, local_info.version)
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


def install_module(
    module_name,
    version=None,
    force_data=False,
    skip_data=False,
    stage_handler=None,
    quiet=True,
    args={},
):
    import zipfile
    import shutil
    import os
    from ..consts import install_tempdir_name
    from ..store import download
    from ..exceptions import KillInstallException
    from ..system import get_modules_dir
    from ..store import get_module_urls
    from ..store import remote_module_latest_version
    from ..store.db import module_data_version
    from .local import get_local_module_info
    from .remote import get_remote_module_info
    from .cache import get_module_cache
    from ..exceptions import ModuleLoadingError
    from ..util.util import quiet_print
    from .remote import get_conf

    quiet_args = {"quiet": quiet}
    modules_dir = get_modules_dir()
    temp_dir = os.path.join(modules_dir, install_tempdir_name, module_name)
    shutil.rmtree(temp_dir, ignore_errors=True)
    os.makedirs(temp_dir)
    # Ctrl-c in this func must be caught to delete temp_dir
    # def raise_kbi(__a__, __b__):
    #    raise KeyboardInterrupt
    # original_sigint = signal.signal(signal.SIGINT, raise_kbi)
    try:
        if stage_handler is None:
            stage_handler = InstallProgressHandler(module_name, version)
        if version is None:
            version = remote_module_latest_version(module_name)
            stage_handler.set_module_version(version)
        if not version:
            quiet_print(f"version could not be found.", args=args)
            return
        if hasattr(stage_handler, "install_state") == True:
            install_state = stage_handler.install_state  # type: ignore
        else:
            install_state = None
        stage_handler.stage_start("start")
        # Checks and installs pip packages.
        conf = get_conf(module_name) or {}
        pypi_dependencies = conf.get("pypi_dependencies") or []
        if pypi_dependencies:
            pypi_dependencies.extend(conf.get("requires_pypi", []))
        else:
            pypi_dependencies = conf.get("requires_pypi") or []
        if not install_pypi_dependencies(module_name, pypi_dependencies, quiet_args):
            return False
        remote_data_version = module_data_version(module_name, version)
        if module_name in list_local():
            local_info = get_local_module_info(module_name)
            if local_info and local_info.has_data and local_info.version:
                local_data_version = module_data_version(
                    module_name, local_info.version
                )
            else:
                local_data_version = None
        else:
            local_data_version = None
        r = get_module_urls(module_name, code_version=version)
        if not r:
            return False
        code_url = r.get("code_url")
        data_url = r.get("data_url")
        zipfile_fname = module_name + ".zip"
        remote_info = get_remote_module_info(module_name)
        if remote_info is not None:
            module_type = remote_info.type
        else:
            # Private module. Fallback to remote config.
            module_type = conf.get("type")
        if not module_type:
            raise ModuleLoadingError(module_name)
        if install_state:
            if (
                install_state["module_name"] == module_name
                and install_state["kill_signal"] == True
            ):
                raise KillInstallException
        zipfile_path = os.path.join(temp_dir, zipfile_fname)
        stage_handler.stage_start("download_code")
        download(
            code_url,
            zipfile_path,
        )
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
        # code_manifest_url = store_path_builder.module_code_manifest(
        #    module_name, version
        # )
        # code_manifest = yaml.safe_load(get_file_to_string(code_manifest_url))
        # verify_against_manifest(temp_dir, code_manifest)
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
            data_fname = ".".join([module_name, "data", "zip"])
            data_path = os.path.join(temp_dir, data_fname)
            stage_handler.stage_start("download_data")
            download(
                data_url,
                data_path,
            )
            if install_state:
                if (
                    install_state["module_name"] == module_name
                    and install_state["kill_signal"] == True
                ):
                    raise KillInstallException
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
            # data_manifest_url = store_path_builder.module_data_manifest(
            #    module_name, remote_data_version
            # )
            # data_manifest = yaml.safe_load(get_file_to_string(data_manifest_url))
            # verify_against_manifest(temp_dir, data_manifest)
            os.remove(data_path)
            if install_state:
                if (
                    install_state["module_name"] == module_name
                    and install_state["kill_signal"] == True
                ):
                    raise KillInstallException
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
        get_module_cache().update_local()
        stage_handler.stage_start("finish")
    # except (Exception, KeyboardInterrupt, SystemExit) as e:
    except Exception as e:
        shutil.rmtree(temp_dir, ignore_errors=True)
        if type(e) == KillInstallException:
            if stage_handler:
                stage_handler.stage_start("killed")
        elif isinstance(e, KeyboardInterrupt):
            # signal.signal(signal.SIGINT, original_sigint)
            raise e
        elif isinstance(e, SystemExit):
            pass
        else:
            # signal.signal(signal.SIGINT, original_sigint)
            raise e
    # finally:
    #    signal.signal(signal.SIGINT, original_sigint)


def uninstall_module(module_name):
    """
    Uninstalls a module.
    """
    import shutil
    from .local import get_local_module_info
    from .cache import get_module_cache

    uninstalled_modules = False
    if module_name in list_local():
        local_info = get_local_module_info(module_name)
        if local_info:
            shutil.rmtree(local_info.directory)
            uninstalled_modules = True
    if uninstalled_modules:
        get_module_cache().update_local()
