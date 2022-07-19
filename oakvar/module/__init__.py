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


def install_pypi_dependencies(args={}):
    from subprocess import run
    from ..util.util import quiet_print

    pypi_dependencies = args.get("pypi_dependencies")
    idx = 0
    if pypi_dependencies:
        quiet_print(
            f"Following PyPI dependencies should be met before installing {args.get('module_name')}.",
            args=args,
        )
        for dep in pypi_dependencies:
            quiet_print(f"- {dep}", args=args)
        quiet_print(f"Installing required PyPI packages...", args=args)
        idx = 0
        while idx < len(pypi_dependencies):
            dep = pypi_dependencies[idx]
            r = run(["pip", "install", dep])
            if r.returncode == 0:
                pypi_dependencies.remove(dep)
            else:
                idx += 1
        if len(pypi_dependencies) > 0:
            quiet_print(
                f"Following PyPI dependencies could not be installed.",
                args=args,
            )
            for dep in pypi_dependencies:
                quiet_print(f"- {dep}", args=args)
    if pypi_dependencies:
        quiet_print(
            f"Skipping installation of {args.get('module_name')} due to unmet requirement for PyPI packages",
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


def list_remote(module_type=None):
    from ..store.db import module_list

    return module_list(module_type=module_type)


def get_updatable(modules=[], strategy="consensus"):
    from distutils.version import LooseVersion
    from pkg_resources import Requirement
    from collections import defaultdict
    from types import SimpleNamespace
    from .local import get_local_module_info
    from .remote import get_remote_module_info
    from ..store.db import remote_module_data_version

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
            update_data_version = remote_module_data_version(mname, selected_version)
            installed_data_version = remote_module_data_version(
                mname, local_info.version
            )
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


def make_install_temp_dir(args={}):
    from ..system import get_modules_dir
    from os.path import join
    from os import makedirs
    from ..consts import install_tempdir_name
    from shutil import rmtree

    args["modules_dir"] = get_modules_dir()
    temp_dir = join(
        args.get("modules_dir"), install_tempdir_name, args.get("module_name")
    )
    rmtree(temp_dir, ignore_errors=True)
    makedirs(temp_dir)
    args["temp_dir"] = temp_dir


def set_stage_handler(args={}):
    if args:
        pass
    if not args.get("stage_handler"):
        args["stage_handler"] = InstallProgressHandler(
            args.get("module_name"), args.get("version")
        )
        args["stage_handler"].set_module_version(args.get("version"))
    if hasattr(args.get("stage_handler"), "install_state") == True:
        args["install_state"] = stage_handler.install_state  # type: ignore
    else:
        args["install_state"] = None


def get_pypi_dependencies(args={}):
    pypi_dependencies = args.get("conf").get("pypi_dependencies") or []
    if pypi_dependencies:
        pypi_dependencies.extend(args.get("conf").get("requires_pypi", []))
    else:
        pypi_dependencies = args.get("conf").get("requires_pypi") or []
    args["pypi_dependencies"] = pypi_dependencies


def check_install_kill(args={}):
    from ..exceptions import KillInstallException

    install_state = args.get("install_state")
    if install_state:
        if (
            install_state["module_name"] == args.get("module_name")
            and install_state["kill_signal"] == True
        ):
            raise KillInstallException


def download_code(args={}):
    from ..store import download
    from os.path import join

    check_install_kill(args=args)
    args.get("stage_handler").stage_start("download_code")
    zipfile_fname = (
        args.get("module_name") + "__" + args.get("code_version") + "__code.zip"
    )
    zipfile_path = join(args.get("temp_dir"), zipfile_fname)
    download(args.get("code_url"), zipfile_path)
    args["code_zipfile_path"] = zipfile_path


def extract_code(args={}):
    import zipfile
    from os import remove

    check_install_kill(args=args)
    args.get("stage_handler").stage_start("extract_code")
    zf = zipfile.ZipFile(args.get("code_zipfile_path"))
    zf.extractall(args.get("temp_dir"))
    zf.close()
    remove(args.get("code_zipfile_path"))


def download_data(args={}):
    from ..store import download
    from os.path import join

    check_install_kill(args=args)
    args.get("stage_handler").stage_start("download_data")
    zipfile_fname = (
        args.get("module_name") + "__" + args.get("remote_data_version") + "__data.zip"
    )
    zipfile_path = join(args.get("temp_dir"), zipfile_fname)
    download(args.get("data_url"), zipfile_path)
    args["data_zipfile_path"] = zipfile_path


def extract_data(args={}):
    import zipfile
    from os import remove

    check_install_kill(args=args)
    args.get("stage_handler").stage_start("extract_code")
    zf = zipfile.ZipFile(args.get("data_zipfile_path"))
    zf.extractall(args.get("temp_dir"))
    zf.close()
    remove(args.get("data_zipfile_path"))


def cleanup_install(args={}):
    from os.path import isdir
    from shutil import rmtree
    from shutil import move
    from os import listdir
    from os import remove
    from os.path import join

    module_dir = args.get("module_dir")
    temp_dir = args.get("temp_dir")
    if isdir(args.get("module_dir")):
        # Module being updated
        if args.get("data_installed"):
            # Overwrite the whole module
            rmtree(module_dir)
            move(temp_dir, module_dir)
        else:
            # Remove all code items
            for item in listdir(module_dir):
                item_path = join(module_dir, item)
                if item != "data":
                    if isdir(item_path):
                        rmtree(item_path)
                    else:
                        remove(item_path)
            # Copy in new code items
            for item in listdir(temp_dir):
                old_path = join(temp_dir, item)
                new_path = join(module_dir, item)
                if item != "data":
                    move(old_path, new_path)
            rmtree(temp_dir)
    else:
        # Move the module to the right place
        move(temp_dir, module_dir)


def write_install_marks(args={}):
    from os.path import join

    module_dir = args.get("module_dir")
    wf = open(join(module_dir, "startofinstall"), "w")
    wf.close()
    wf = open(join(module_dir, "endofinstall"), "w")
    wf.close()


def install_module(
    module_name,
    version=None,
    force_data=False,
    skip_data=False,
    stage_handler=None,
    quiet=True,
    args={},
):
    from shutil import rmtree
    from os.path import join
    from ..exceptions import KillInstallException
    from ..store import get_module_urls
    from ..store.db import remote_module_data_version
    from ..store.db import summary_col_value
    from .cache import get_module_cache
    from .remote import get_conf
    from .local import module_data_version as local_module_data_version
    from ..store import remote_module_latest_version
    from ..util.util import quiet_print

    args["quiet"] = quiet
    args["module_name"] = module_name
    args["version"] = version
    args["stage_handler"] = stage_handler
    if not args.get("version"):
        args["version"] = remote_module_latest_version(module_name)
        if not args.get("version"):
            quiet_print(f"version could not be found.", args=args)
            return False
    args["code_version"] = args.get("version")
    make_install_temp_dir(args=args)
    # Ctrl-c in this func must be caught to delete temp_dir
    # def raise_kbi(__a__, __b__):
    #    raise KeyboardInterrupt
    # original_sigint = signal.signal(signal.SIGINT, raise_kbi)
    try:
        set_stage_handler(args=args)
        args.get("stage_handler").stage_start("start")
        args["conf"] = get_conf(module_name) or {}
        get_pypi_dependencies(args=args)
        # Checks and installs pip packages.
        if not install_pypi_dependencies(args=args):
            quiet_print(f"failed in installing pypi package dependence", args=args)
            return False
        args["remote_data_version"] = remote_module_data_version(
            args.get("module_name"), args.get("code_version")
        )
        args["local_data_version"] = local_module_data_version(args.get("module_name"))
        r = get_module_urls(module_name, code_version=version)
        if not r:
            quiet_print(f"failed in getting module versions", args=args)
            return False
        args["code_url"], args["data_url"] = r.get("code_url"), r.get("data_url")
        args["module_type"] = summary_col_value(args.get("module_name"), "type")
        if not args.get("module_type"):
            # Private module. Fallback to remote config.
            args["module_type"] = args.get("conf").get("type")
        if not args.get("module_type"):
            quiet_print(f"module type not found", args=args)
            return False
        args["module_dir"] = join(
            args.get("modules_dir"),
            args.get("module_type") + "s",
            args.get("module_name"),
        )
        download_code(args=args)
        extract_code(args=args)
        args["data_installed"] = False
        if (
            not skip_data
            and args.get("remote_data_version")
            and (
                args.get("remote_data_version") != args.get("local_data_version")
                or force_data
            )
        ):
            args["data_installed"] = True
            download_data(args=args)
            extract_data(args=args)
        cleanup_install(args=args)
        write_install_marks(args=args)
        get_module_cache().update_local()
        args.get("stage_handler").stage_start("finish")
        return True
    # except (Exception, KeyboardInterrupt, SystemExit) as e:
    except Exception as e:
        rmtree(args.get("temp_dir"), ignore_errors=True)
        if type(e) == KillInstallException:
            if stage_handler:
                stage_handler.stage_start("killed")
        elif isinstance(e, KeyboardInterrupt):
            # signal.signal(signal.SIGINT, original_sigint)
            raise e
        elif isinstance(e, SystemExit):
            return False
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
