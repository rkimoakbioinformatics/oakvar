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
            local_readme = open(local_info.readme_path, encoding='utf-8').read()
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


def install_pypi_dependency(args={}):
    from subprocess import run
    from ..util.util import quiet_print

    pypi_dependency = args.get("pypi_dependency")
    idx = 0
    if pypi_dependency:
        quiet_print(
            f"Following PyPI dependencies should be met before installing {args.get('module_name')}.",
            args=args,
        )
        for dep in pypi_dependency:
            quiet_print(f"- {dep}", args=args)
        quiet_print(f"Installing required PyPI packages...", args=args)
        idx = 0
        while idx < len(pypi_dependency):
            dep = pypi_dependency[idx]
            r = run(["pip", "install", dep])
            if r.returncode == 0:
                pypi_dependency.remove(dep)
            else:
                idx += 1
        if len(pypi_dependency) > 0:
            quiet_print(
                f"Following PyPI dependencies could not be installed.",
                args=args,
            )
            for dep in pypi_dependency:
                quiet_print(f"- {dep}", args=args)
    if pypi_dependency:
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


def get_updatable(modules=[], requested_modules=[], strategy="consensus"):
    from packaging.version import Version
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
    else:
        modules = requested_modules
    reqs_by_dep = defaultdict(dict)
    all_versions = {}
    for mname in list_local():
        local_info = get_local_module_info(mname, force=True)
        remote_info = get_remote_module_info(mname)
        if remote_info:
            all_versions[mname] = sorted(remote_info.versions, key=Version)
        if local_info:
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
            and Version(selected_version) <= Version(local_info.version)
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
            and Version(selected_version) > Version(local_info.version)
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
    from ..consts import install_tempdir_name
    from shutil import rmtree
    from pathlib import Path

    if not args.get("module_dir"):
        args["modules_dir"] = get_modules_dir()
    temp_dir = Path(args.get("modules_dir")) / install_tempdir_name / args.get("module_name")
    if args.get("clean"):
        rmtree(str(temp_dir), ignore_errors=True)
    temp_dir.mkdir(parents=True, exist_ok=True)
    args["temp_dir"] = str(temp_dir)
    return temp_dir


def set_stage_handler(args={}):
    if args:
        pass
    if not args.get("stage_handler"):
        args["stage_handler"] = InstallProgressHandler(
            args.get("module_name"), args.get("version")
        )
        args["stage_handler"].set_module_version(args.get("version"))
    if hasattr(args.get("stage_handler"), "install_state") == True:
        args["install_state"] = args.get("stage_handler").install_state  # type: ignore
    else:
        args["install_state"] = None


def get_pypi_dependency_from_conf(conf={}):
    if not conf:
        return []
    pypi_dependency = []
    for key in ["pypi_dependency", "pypi_dependencies", "requires_pypi"]:
        vals = conf.get(key) or []
        for v in vals:
            if v not in pypi_dependency:
                pypi_dependency.append(v)
    return pypi_dependency


def check_install_kill(args={}):
    from ..exceptions import KillInstallException

    install_state = args.get("install_state")
    if install_state:
        if (
            install_state["module_name"] == args.get("module_name")
            and install_state["kill_signal"] == True
        ):
            raise KillInstallException


def download_code_or_data(kind=None, args={}):
    from ..util.download import download
    from os.path import join
    from os.path import exists
    from os.path import getsize
    from os import remove
    from ..store.consts import ov_store_split_file_size
    from ..util.util import quiet_print
    from json import loads

    check_install_kill(args=args)
    if not kind or kind not in ["code", "data"]:
        return
    if args.get("stage_handler"):
        args.get("stage_handler").stage_start(f"download_{kind}")
    zipfile_fname = (
        args.get("module_name") + "__" + args.get(f"version") + f"__{kind}.zip"
    )
    zipfile_path = join(args.get("temp_dir"), zipfile_fname)
    urls = args.get(f"{kind}_url")
    if urls[0] == "[": # a list of URLs
        urls = loads(urls)
    urls_ty = type(urls)
    if urls_ty == str:
        download(args.get(f"{kind}_url"), zipfile_path)
    elif urls_ty == list:
        download_from = 0
        if exists(zipfile_path):
            zs = getsize(zipfile_path)
            if zs % ov_store_split_file_size == 0:
                # partial download completed
                download_from = int(getsize(zipfile_path) / ov_store_split_file_size)
            else:
                remove(zipfile_path)
        with open(zipfile_path, "ab") as wf:
            urls_len = len(urls)
            for i in range(urls_len):
                if i < download_from:
                    continue
                part_path = f"{zipfile_path}{i:03d}"
                if exists(part_path) and getsize(part_path) == ov_store_split_file_size:
                    continue
                download(urls[i], part_path)
                if i < urls_len - 1:
                    if getsize(part_path) != ov_store_split_file_size:
                        quiet_print(f"corrupt download {part_path} at {urls[i]}", args=args)
                        remove(part_path)
                        return False
                with open(part_path, "rb") as f:
                    wf.write(f.read())
                remove(part_path)
    args[f"{kind}_zipfile_path"] = zipfile_path
    return True


def extract_code_or_data(kind=None, args={}):
    import zipfile
    from os import remove

    check_install_kill(args=args)
    if not kind or kind not in ["code", "data"]:
        return
    if args.get("stage_handler"):
        args.get("stage_handler").stage_start(f"extract_{kind}")
    zf = zipfile.ZipFile(args.get(f"{kind}_zipfile_path"))
    zf.extractall(args.get("temp_dir"))
    zf.close()
    remove(args.get(f"{kind}_zipfile_path"))


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


def install_module_dependency(conf={}, args={}):
    from ..cli.module import collect_module_name_and_versions
    requires = conf.get("requires", [])
    if not requires:
        return
    mn_vs = collect_module_name_and_versions(requires, args=args)
    for module_name, version in mn_vs.items():
        install_module(module_name, version=version, args=args)

def install_module_from_url(url, args={}):
    from pathlib import Path
    from ..system import get_modules_dir
    from ..util.download import download
    from ..util.util import load_yml_conf
    from ..util.util import quiet_print
    from .remote import get_install_deps
    from shutil import move
    from shutil import rmtree

    module_name = Path(url).name
    args["module_name"] = module_name
    temp_dir = make_install_temp_dir(args=args)
    download(url, temp_dir.parent)
    yml_conf_path = temp_dir / (args["module_name"] + ".yml")
    if not yml_conf_path.exists():
        quiet_print(f"{url} is not a valid OakVar module. {module_name}.yml should exist.", args=args)
        return False
    conf = load_yml_conf(yml_conf_path)
    args["conf"] = conf
    deps, deps_pypi = get_install_deps(conf_path=str(yml_conf_path))
    args["pypi_dependency"] = deps_pypi
    if not install_pypi_dependency(args=args):
        quiet_print(f"failed in installing pypi package dependence", args=args)
        return False
    for deps_mn, deps_ver in deps.items():
        install_module(deps_mn, version=deps_ver, force_data=args["force_data"], skip_data=args["skip_data"], quiet=args["quiet"], args=args)
    ty = conf.get("type") or ""
    if not ty:
        quiet_print(f"{url} is not a valid OakVar module. {module_name}.yml does not have 'type' field.", args=args)
        return False
    modules_dir = Path(get_modules_dir())
    module_type_dir = modules_dir / (ty + "s")
    if not module_type_dir.exists():
        module_type_dir.mkdir()
    module_dir = module_type_dir / module_name
    if module_dir.exists():
        if args.get("force"):
            rmtree(str(module_dir))
        else:
            quiet_print(f"{module_dir} already exists.", args=args)
            return False
    move(str(temp_dir), str(module_type_dir))
    return True


def install_module_from_zip_path(path: str, args: dict={}):
    from pathlib import Path
    from ..util.util import load_yml_conf
    from ..util.util import quiet_print
    from ..util.util import get_random_string
    from ..util.util import load_yml_conf
    from ..exceptions import ExpectedException
    from .local import get_new_module_dir
    from .remote import get_install_deps
    from shutil import copytree
    from shutil import rmtree
    from zipfile import ZipFile

    f = ZipFile(path)
    temp_dir = "oakvar_temp_dir__" + get_random_string(k=16)
    try:
        while Path(temp_dir).exists():
            temp_dir = "oakvar_temp_dir__" + get_random_string(k=16)
        f.extractall(path=temp_dir)
        children = [v for v in Path(temp_dir).iterdir()]
        if len(children) > 1:
            raise ExpectedException(msg=f"Only 1 module folder should exist in {path}.")
        temp_module_path = children[0]
        if not temp_module_path.is_dir():
            raise ExpectedException(msg=f"1 module folder should exist in {path}.")
        yml_paths = [v for v in temp_module_path.glob("*.yml")]
        if len(yml_paths) > 1:
            raise ExpectedException(msg=f"Only 1 module config file should exist in {str(temp_module_path)}.")
        yml_path = yml_paths[0]
        module_name = yml_path.stem
        args["module_name"] = module_name
        f = open(str(yml_path))
        conf = load_yml_conf(str(yml_path))
        module_type = conf.get("type")
        if not module_type:
            raise ExpectedException(msg=f"Module type should be defined in {module_name}.yml.")
        module_dir = get_new_module_dir(module_name, module_type)
        if not module_dir:
            raise ExpectedException(msg=f"{module_dir} could not be created.")
        # dependencies
        deps, deps_pypi = get_install_deps(conf_path=str(yml_path))
        args["pypi_dependency"] = deps_pypi
        if not install_pypi_dependency(args=args):
            raise ExpectedException("failed in installing pypi package dependence")
        for deps_mn, deps_ver in deps.items():
            install_module(deps_mn, version=deps_ver, force_data=args["force_data"], skip_data=args["skip_data"], quiet=args["quiet"], args=args)
        # move module
        copytree(str(temp_module_path), module_dir, dirs_exist_ok=True)
        quiet_print(f"{module_name} installed at {module_dir}", args=args)
        rmtree(temp_dir)
        return True
    except Exception as e:
        rmtree(temp_dir)
        raise e

def get_module_install_version(module_name, version=None, args={}) -> str:
    from packaging.version import Version
    from ..module.local import get_local_module_info
    from ..module.remote import get_remote_module_info
    from ..exceptions import ModuleNotExist
    from ..exceptions import ModuleVersionError
    from ..exceptions import DuplicateModuleToInstall
    local_info = get_local_module_info(module_name)
    remote_info = get_remote_module_info(module_name)
    if not remote_info:
        raise ModuleNotExist(module_name)
    if not version and remote_info:
        version = remote_info.latest_code_version
    if not version:
        raise ModuleNotExist(module_name)
    if not remote_info:
        raise ModuleVersionError(module_name, version)
    if (not args.get("overwrite") and local_info and Version(local_info.code_version or "") == Version(version)):
        raise DuplicateModuleToInstall(module_name, version)
    return version

def install_module(
    module_name,
    version=None,
    force_data=False,
    skip_data=False,
    stage_handler=None,
    quiet=True,
    conf_path=None,
    args={},
):
    from os.path import join
    from ..exceptions import KillInstallException
    from ..store import get_module_urls
    from ..store.db import remote_module_data_version
    from ..store.db import summary_col_value
    from .cache import get_module_cache
    from .remote import get_conf
    from .local import get_module_data_version as local_module_data_version
    from ..util.util import quiet_print

    version = get_module_install_version(module_name, version=version, args=args)
    args["quiet"] = quiet
    args["module_name"] = module_name
    args["version"] = version
    args["stage_handler"] = stage_handler
    quiet_print(f"installing {module_name}...", args=args)
    args["code_version"] = version
    make_install_temp_dir(args=args)
    # Ctrl-c in this func must be caught to delete temp_dir
    # def raise_kbi(__a__, __b__):
    #    raise KeyboardInterrupt
    # original_sigint = signal.signal(signal.SIGINT, raise_kbi)
    try:
        set_stage_handler(args=args)
        args.get("stage_handler").stage_start("start")
        args["conf"] = get_conf(module_name=module_name, conf_path=conf_path) or {}
        args["pypi_dependency"] = get_pypi_dependency_from_conf(conf=args.get("conf"))
        # Checks and installs pip packages.
        if not install_pypi_dependency(args=args):
            quiet_print(f"failed in installing pypi package dependence", args=args)
            return False
        args["remote_data_version"] = remote_module_data_version(
                args.get("module_name"), args.get("code_version")
                )
        args["local_data_version"] = local_module_data_version(args.get("module_name"))
        r = get_module_urls(module_name, code_version=version)
        if not r:
            quiet_print(f"failed in getting module URLs", args=args)
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
        if not download_code_or_data(kind="code", args=args):
            quiet_print(f"code download failed", args=args)
            return False
        extract_code_or_data(kind="code", args=args)
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
            if not download_code_or_data(kind="data", args=args):
                quiet_print(f"data download failed", args=args)
                return False
            extract_code_or_data(kind="data", args=args)
        cleanup_install(args=args)
        write_install_marks(args=args)
        get_module_cache().update_local()
        args.get("stage_handler").stage_start("finish")
        return True
    # except (Exception, KeyboardInterrupt, SystemExit) as e:
    except Exception as e:
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
