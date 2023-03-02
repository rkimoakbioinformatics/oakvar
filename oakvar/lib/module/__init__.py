from typing import Optional
from typing import List
from pathlib import Path
from . import local
from . import remote

_ = local or remote


class InstallProgressHandler:
    def __init__(
        self,
        module_name: Optional[str] = None,
        module_version: Optional[str] = None,
        outer=None,
    ):
        self.module_name = module_name
        self.module_version = module_version
        self.display_name = None
        self.cur_stage = None
        self.outer = outer
        if module_name:
            self._make_display_name()

    def set_module(self, module_name: str = "", module_version: Optional[str] = None):
        self.module_name = module_name
        self.module_version = module_version
        if module_name:
            self._make_display_name()

    def _make_display_name(self):
        if not self.module_name:
            return
        ver_str = self.module_version if self.module_version is not None else ""
        self.display_name = ":".join([self.module_name, ver_str])

    def stage_start(self, __stage__):
        pass

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
            return f"[{get_current_time_str()}] finished installation of {self.display_name}"
        elif stage == "killed":
            return f"[{get_current_time_str()}] Aborted installation of {self.display_name}"
        elif stage == "Unqueued":
            return f"Unqueued {self.display_name} from installation"
        else:
            return f"[{get_current_time_str()}] {stage}"


def get_readme(module_name):
    from os.path import exists
    from ..store import remote_module_latest_version
    from ..store.db import get_latest_module_code_version
    from .local import module_exists_local
    from .cache import get_module_cache
    from .local import get_local_module_info
    from ..util.util import compare_version

    exists_local = module_exists_local(module_name)
    remote_ver = get_latest_module_code_version(module_name)
    if remote_ver:
        remote_readme = get_module_cache().get_remote_readme(
            module_name, version=remote_ver
        )
    else:
        remote_readme = ""
    if exists_local:
        local_info = get_local_module_info(module_name)
        if local_info and exists(local_info.readme_path):
            local_readme = open(local_info.readme_path, encoding="utf-8").read()
        else:
            local_readme = ""
        if local_info and remote_ver:
            remote_version = remote_module_latest_version(module_name)
            local_version = local_info.version
            if remote_version and local_version and compare_version(remote_version, local_version) > 0:
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


def install_pypi_dependency(pypi_dependency: Optional[List[str]] = None, outer=None):
    from subprocess import run

    if not pypi_dependency:
        return True
    if outer:
        outer.write(f"Installing required PyPI packages...")
    idx = 0
    while idx < len(pypi_dependency):
        dep = pypi_dependency[idx]
        r = run(["pip", "install", dep])
        if r.returncode == 0:
            pypi_dependency.remove(dep)
        else:
            idx += 1
    if len(pypi_dependency) > 0 and outer:
        outer.write(f"Following PyPI dependencies could not be installed.")
        for dep in pypi_dependency:
            outer.write(f"- {dep}")
    if pypi_dependency:
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


def update_available(module_name: str):
    from packaging.version import Version
    from .local import get_local_module_info
    from .remote import get_remote_module_info

    local_info = get_local_module_info(module_name)
    remote_info = get_remote_module_info(module_name)
    if (
        not local_info
        or not remote_info
        or not local_info.code_version
        or not remote_info.latest_code_version
    ):
        return False
    if Version(remote_info.latest_code_version) > Version(local_info.code_version):
        return True
    else:
        return False


def get_updatable(module_names: List[str] = []):
    from .local import get_local_module_info

    if not module_names:
        module_names = list_local()
    to_update = []
    for mn in module_names:
        local_info = get_local_module_info(mn)
        if not local_info:
            continue
        if update_available(mn):
            to_update.append(mn)
        requires = local_info.conf.get("requires")
        if not requires:
            continue
        for req_mn in requires:
            if req_mn in to_update:
                continue
            if update_available(req_mn):
                to_update.append(req_mn)
    return to_update


def make_install_temp_dir(
    module_name: Optional[str] = None,
    modules_dir: Optional[Path] = None,
    clean: bool = False,
) -> Optional[Path]:
    from ..system import get_modules_dir
    from ..consts import install_tempdir_name
    from shutil import rmtree
    from pathlib import Path

    if not modules_dir:
        modules_dir = get_modules_dir()
    if not modules_dir:
        raise Exception("modules root directory does not exist.")
    if not module_name:
        raise Exception("module_name was not given.")
    temp_dir = Path(modules_dir) / install_tempdir_name / module_name
    if clean:
        rmtree(str(temp_dir), ignore_errors=True)
    temp_dir.mkdir(parents=True, exist_ok=True)
    return temp_dir


def set_stage_handler(module_name: str, stage_handler=None, version: str = ""):
    if stage_handler:
        stage_handler.set_module(module_name=module_name, module_version=version)
    else:
        stage_handler = InstallProgressHandler(module_name, version)
    return stage_handler


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


def check_install_kill(system_worker_state=None, module_name=None):
    from ..exceptions import KillInstallException
    from ...gui.consts import SYSTEM_STATE_INSTALL_KEY

    if not system_worker_state or not module_name:
        return
    if (
        system_worker_state[SYSTEM_STATE_INSTALL_KEY]
        .get(module_name, {})
        .get("kill_signal")
        == True
    ):
        raise KillInstallException


def get_download_zipfile_path(
    module_name: str, version: str, temp_dir: Path, kind: str
):
    zipfile_fname = f"{module_name}__{version}__{kind}.zip"
    zipfile_path = str(temp_dir / zipfile_fname)
    return zipfile_path


def download_code_or_data(
    urls: Optional[str] = None,
    module_name: Optional[str] = None,
    version: Optional[str] = None,
    kind: Optional[str] = None,
    temp_dir: Optional[Path] = None,
    outer=None,
    stage_handler=None,
    system_worker_state=None,
) -> Optional[str]:
    from pathlib import Path
    from os.path import getsize
    from os import remove
    from json import loads
    from ..util.download import download
    from ..store.consts import MODULE_PACK_SPLIT_FILE_SIZE

    check_install_kill(system_worker_state=system_worker_state, module_name=module_name)
    if not module_name or not version or not temp_dir:
        return
    if not kind or kind not in ["code", "data"]:
        return
    if stage_handler:
        stage_handler.stage_start(f"download_{kind}")
    zipfile_path = get_download_zipfile_path(module_name, version, temp_dir, kind)
    if not zipfile_path:
        return
    if urls is None:
        return
    one_url = ""
    url_list: List[str] = []
    if urls[0] == "[":  # a list of URLs
        url_list = loads(urls)
    else:
        one_url = urls
    if not one_url and not url_list:
        return
    if one_url:
        download(
            one_url,
            zipfile_path,
            system_worker_state=system_worker_state,
            check_install_kill=check_install_kill,
            module_name=module_name,
            kind=kind,
            outer=outer,
        )
    elif url_list:
        num_urls = len(url_list)
        download_from = 0
        total_size = num_urls * MODULE_PACK_SPLIT_FILE_SIZE
        if Path(zipfile_path).exists():
            zs = getsize(zipfile_path)
            if zs % MODULE_PACK_SPLIT_FILE_SIZE == 0:
                # partial download completed
                download_from = int(getsize(zipfile_path) / MODULE_PACK_SPLIT_FILE_SIZE)
            else:
                remove(zipfile_path)
        cur_size = download_from
        with open(zipfile_path, "ab") as wf:
            for i in range(num_urls):
                if i < download_from:
                    continue
                part_path = f"{zipfile_path}{i:03d}"
                if (
                    Path(part_path).exists()
                    and getsize(part_path) == MODULE_PACK_SPLIT_FILE_SIZE
                ):
                    continue
                download(
                    url_list[i],
                    part_path,
                    system_worker_state=system_worker_state,
                    check_install_kill=check_install_kill,
                    module_name=module_name,
                    total_size=total_size,
                    cur_size=cur_size,
                    outer=outer,
                )
                if i < num_urls - 1:
                    if getsize(part_path) != MODULE_PACK_SPLIT_FILE_SIZE:
                        if outer:
                            outer.write(f"corrupt download {part_path} at {url_list[i]}")
                        remove(part_path)
                        return
                with open(part_path, "rb") as f:
                    wf.write(f.read())
                remove(part_path)
    return zipfile_path


def extract_code_or_data(
    module_name: str = "",
    kind: str = "",
    zipfile_path: str = "",
    temp_dir: Optional[Path] = None,
    stage_handler=None,
    system_worker_state=None,
):
    import zipfile
    from os import remove

    check_install_kill(module_name=module_name, system_worker_state=system_worker_state)
    if not temp_dir or not module_name or not kind or not zipfile_path:
        return
    if not kind or kind not in ["code", "data"]:
        return
    if stage_handler:
        stage_handler.stage_start(f"extract_{kind}")
    zf = zipfile.ZipFile(zipfile_path)
    zf.extractall(temp_dir)
    zf.close()
    remove(zipfile_path)


def cleanup_install(
    module_name: str,
    module_dir: str,
    temp_dir: Path,
    installation_finished: bool,
    code_installed: bool,
    data_installed: bool,
):
    from pathlib import Path
    from shutil import rmtree
    from shutil import move
    from os import listdir
    from pathlib import Path
    from .local import remove_code_part_of_module

    if not module_dir:
        return
    # Unsuccessful installation
    if not installation_finished:
        return
    # New installation
    if not Path(module_dir).exists():
        move(str(temp_dir), module_dir)
        return
    # Update
    if data_installed:
        rmtree(module_dir)
        move(str(temp_dir), module_dir)
    elif code_installed:
        remove_code_part_of_module(module_name)
        for item in listdir(temp_dir):
            old_path = Path(temp_dir) / item
            new_path = Path(module_dir) / item
            if item != "data":
                move(str(old_path), new_path)
        rmtree(temp_dir)


def write_install_marks(module_dir: str):
    from os.path import join

    wf = open(join(module_dir, "startofinstall"), "w")
    wf.close()
    wf = open(join(module_dir, "endofinstall"), "w")
    wf.close()


def install_module_from_url(
    module_name: str,
    url: str,
    modules_dir: Optional[Path] = None,
    clean: bool = False,
    overwrite=False,
    force_data=False,
    skip_data=False,
    skip_dependencies=False,
    outer=None,
    stage_handler: Optional[InstallProgressHandler] = None,
):
    from shutil import move
    from shutil import rmtree
    from zipfile import ZipFile
    from urllib.parse import urlparse
    from os import remove
    from pathlib import Path
    from ..util.download import download
    from ..util.util import load_yml_conf
    from .remote import get_install_deps
    from ..util.download import is_url
    from ..exceptions import ModuleToSkipInstallation
    from ..system import get_modules_dir

    if not is_url(url):
        raise ModuleToSkipInstallation("", msg=f"{url} is not a valid URL")
    temp_dir = make_install_temp_dir(
        module_name=module_name, modules_dir=modules_dir, clean=clean
    )
    if not temp_dir:
        raise
    fname = Path(urlparse(url).path).name
    if Path(fname).suffix == ".zip":
        fpath = temp_dir / fname
        download(url=url, fpath=fpath, directory=temp_dir, module_name=module_name)
        with ZipFile(fpath) as f:
            f.extractall(path=temp_dir)
        remove(fpath)
    else:
        download(url=url, directory=temp_dir, module_name=module_name, outer=outer)
    if not module_name:
        raise ModuleToSkipInstallation("", msg=f"No module was found in the URL")
    yml_conf_path = temp_dir / (module_name + ".yml")
    if not yml_conf_path.exists():
        if outer:
            outer.write(
                f"{url} is not a valid OakVar module. {module_name}.yml should exist."
            )
        return False
    conf = load_yml_conf(yml_conf_path)
    ty = conf.get("type") or ""
    if not ty:
        if outer:
            outer.write(
                f"{url} is not a valid OakVar module. {module_name}.yml does not have 'type' field."
            )
        return False
    if not skip_dependencies:
        deps, pypi_dependency = get_install_deps(conf_path=yml_conf_path)
        if not install_pypi_dependency(pypi_dependency=pypi_dependency, outer=outer):
            if outer:
                outer.write(
                    f"Skipping installation of {module_name} due to some PyPI dependency was not installed."
                )
            return False
        for deps_mn, deps_ver in deps.items():
            install_module(
                deps_mn,
                version=deps_ver,
                stage_handler=stage_handler,
                force_data=force_data,
                skip_data=skip_data,
                outer=outer,
            )
    if not modules_dir:
        modules_dir = get_modules_dir()
    if not modules_dir:
        raise ModuleToSkipInstallation("", msg="modules root directory does not exist.")
    module_type_dir: Path = Path(modules_dir) / (ty + "s")
    if not module_type_dir.exists():
        module_type_dir.mkdir()
    module_dir = module_type_dir / module_name
    if module_dir.exists():
        if overwrite:
            rmtree(str(module_dir))
        else:
            if outer:
                outer.write(f"{module_dir} already exists.")
            return False
    move(str(temp_dir), str(module_type_dir))
    return True


def install_module_from_zip_path(
    path: str, force_data: bool = False, skip_data: bool = False, outer=None
):
    from pathlib import Path
    from ..util.util import load_yml_conf
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
            raise ExpectedException(
                msg=f"Only 1 module config file should exist in {str(temp_module_path)}."
            )
        yml_path = yml_paths[0]
        module_name = yml_path.stem
        f = open(yml_path)
        conf = load_yml_conf(yml_path)
        module_type = conf.get("type")
        if not module_type:
            raise ExpectedException(
                msg=f"Module type should be defined in {module_name}.yml."
            )
        module_dir = get_new_module_dir(module_name, module_type)
        if not module_dir:
            raise ExpectedException(msg=f"{module_dir} could not be created.")
        # dependencies
        deps, pypi_dependency = get_install_deps(conf_path=yml_path)
        if not install_pypi_dependency(pypi_dependency=pypi_dependency, outer=outer):
            raise ExpectedException("failed in installing pypi package dependence")
        for deps_mn, deps_ver in deps.items():
            install_module(
                deps_mn,
                version=deps_ver,
                force_data=force_data,
                skip_data=skip_data,
            )
        # move module
        copytree(str(temp_module_path), module_dir, dirs_exist_ok=True)
        if outer:
            outer.write(f"{module_name} installed at {module_dir}")
        rmtree(temp_dir)
        return True
    except Exception as e:
        rmtree(temp_dir)
        raise e


def get_module_install_version(
    module_name, version=None, fresh=False, overwrite=False
) -> str:
    from packaging.version import Version
    from ..module.local import get_local_module_info
    from ..module.remote import get_remote_module_info
    from ..exceptions import ModuleNotExist
    from ..exceptions import ModuleVersionError
    from ..exceptions import ModuleToSkipInstallation

    local_info = get_local_module_info(module_name, fresh=fresh)
    remote_info = get_remote_module_info(module_name)
    if not remote_info:
        raise ModuleNotExist(module_name)
    if not version and remote_info:
        version = remote_info.latest_code_version
    if not version:
        raise ModuleNotExist(module_name)
    if not remote_info:
        raise ModuleVersionError(module_name, version)
    if (
        not overwrite
        and local_info
        and Version(local_info.code_version or "") == Version(version)
    ):
        raise ModuleToSkipInstallation(
            module_name,
            msg=f"{module_name}=={version} already exists.",
        )
    if (
        not overwrite
        and local_info
        and local_info.code_version
        and Version(local_info.code_version or "") >= Version(version)
    ):
        raise ModuleToSkipInstallation(
            module_name,
            msg=f"{module_name}: Local version ({local_info.code_version}) is higher than the latest store version ({version}). Use --overwrite to overwrite.",
        )
    else:
        return version


def install_module(
    module_name: str,
    version=None,
    overwrite=False,
    force_data=False,
    skip_data=False,
    modules_dir: Optional[Path] = None,
    stage_handler: Optional[InstallProgressHandler] = None,
    conf_path=None,
    fresh=False,
    clean=False,
    outer=None,
    error=None,
    system_worker_state=None,
):
    import traceback
    from os.path import join
    from ..exceptions import KillInstallException
    from ..exceptions import ModuleToSkipInstallation
    from ..exceptions import ModuleInstallationError
    from ..store import get_module_urls
    from ..store.db import remote_module_data_version
    from ..store.db import summary_col_value
    from .cache import get_module_cache
    from .remote import get_conf
    from .local import get_module_data_version as local_module_data_version
    from ..system import get_modules_dir

    temp_dir = make_install_temp_dir(module_name=module_name, clean=clean)
    if not temp_dir:
        raise ModuleInstallationError("cannot make a temp module directory.")
    module_dir: str = ""
    installation_finished: bool = False
    code_installed: bool = False
    data_installed: bool = False
    try:
        version = get_module_install_version(
            module_name, version=version, fresh=fresh, overwrite=overwrite
        )
        code_version = version
        stage_handler = set_stage_handler(
            module_name, stage_handler=stage_handler, version=version
        )
        if stage_handler:
            stage_handler.stage_start("start")
        conf = get_conf(module_name=module_name, conf_path=conf_path) or {}
        pypi_dependency = get_pypi_dependency_from_conf(conf=conf)
        # Checks and installs pip packages.
        if not install_pypi_dependency(pypi_dependency=pypi_dependency, outer=outer):
            if outer:
                outer.error(f"Failed in installing pypi package dependence")
            raise ModuleInstallationError(module_name)
        remote_data_version = remote_module_data_version(module_name, code_version)
        local_data_version = local_module_data_version(module_name)
        r = get_module_urls(module_name, code_version=version)
        if not r:
            if outer:
                outer.error(f"failed in getting module URLs")
            raise ModuleInstallationError(module_name)
        code_url: Optional[str] = r.get("code_url")
        data_url: Optional[str] = r.get("data_url")
        module_type = summary_col_value(module_name, "type")
        if not module_type:
            # Private module. Fallback to remote config.
            module_type = conf.get("type")
        if not module_type:
            if outer:
                outer.error(f"module type not found")
            raise ModuleInstallationError(module_name)
        if not modules_dir:
            modules_dir = get_modules_dir()
        if not modules_dir:
            raise ModuleInstallationError("modules root directory does not exist.")
        module_dir = join(
            modules_dir,
            module_type + "s",
            module_name,
        )
        zipfile_path = download_code_or_data(
            urls=code_url,
            module_name=module_name,
            version=code_version,
            kind="code",
            temp_dir=temp_dir,
            outer=outer,
            stage_handler=stage_handler,
            system_worker_state=system_worker_state,
        )
        if not zipfile_path:
            if outer:
                outer.error(f"code download failed")
            raise ModuleInstallationError(module_name)
        extract_code_or_data(
            module_name=module_name,
            kind="code",
            zipfile_path=zipfile_path,
            temp_dir=temp_dir,
            stage_handler=stage_handler,
            system_worker_state=system_worker_state,
        )
        code_installed = True
        if (
            not skip_data
            and remote_data_version
            and (remote_data_version != local_data_version or force_data)
        ):
            if not data_url:
                if outer:
                    outer.error(f"data_url is empty.")
                raise ModuleInstallationError(module_name)
            data_zipfile_path: Optional[str] = download_code_or_data(
                urls=data_url,
                module_name=module_name,
                version=remote_data_version,
                kind="data",
                temp_dir=temp_dir,
                outer=outer,
                stage_handler=stage_handler,
                system_worker_state=system_worker_state,
            )
            if not data_zipfile_path:
                if error:
                    error.write(f"Data download failed")
                raise ModuleInstallationError(module_name)
            extract_code_or_data(
                module_name=module_name,
                kind="data",
                zipfile_path=data_zipfile_path,
                temp_dir=temp_dir,
                stage_handler=stage_handler,
                system_worker_state=system_worker_state,
            )
            data_installed = True
        installation_finished = True
        cleanup_install(
            module_name,
            module_dir,
            temp_dir,
            installation_finished,
            code_installed,
            data_installed,
        )
        write_install_marks(module_dir)
        get_module_cache().update_local()
        if stage_handler:
            stage_handler.stage_start("finish")
        if outer:
            outer.write(f"Installed {module_name}.")
        return True
    # except (Exception, KeyboardInterrupt, SystemExit) as e:
    except Exception as e:
        if isinstance(e, ModuleToSkipInstallation):
            if outer:
                outer.write(str(e))
            return True
        elif isinstance(e, ModuleInstallationError):
            traceback.print_exc()
            if outer:
                outer.error(e)
            cleanup_install(
                module_name,
                module_dir,
                temp_dir,
                installation_finished,
                code_installed,
                data_installed,
            )
        elif isinstance(e, KillInstallException):
            if stage_handler:
                stage_handler.stage_start("killed")
            cleanup_install(
                module_name,
                module_dir,
                temp_dir,
                installation_finished,
                code_installed,
                data_installed,
            )
            return False
        elif isinstance(e, KeyboardInterrupt):
            # signal.signal(signal.SIGINT, original_sigint)
            raise e
        elif isinstance(e, SystemExit):
            return False
        else:
            cleanup_install(
                module_name,
                module_dir,
                temp_dir,
                installation_finished,
                code_installed,
                data_installed,
            )
            # signal.signal(signal.SIGINT, original_sigint)
            raise e
    # finally:
    #    signal.signal(signal.SIGINT, original_sigint)


def uninstall_module(module_name, outer=None):
    import shutil
    from .local import get_local_module_info
    from .cache import get_module_cache

    if not module_name in list_local():
        if outer:
            outer.write(f"{module_name} does not exist.")
        return False
    local_info = get_local_module_info(module_name)
    if not local_info:
        if outer:
            outer.write(f"{module_name} does not exist.")
        return False
    shutil.rmtree(local_info.directory)
    mc = get_module_cache()
    mc.remove_local(module_name)
