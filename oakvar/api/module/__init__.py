from typing import Optional
from typing import List
from ...lib.module import InstallProgressHandler


def pack(
    module_name: Optional[str] = None,
    outdir: str = ".",
    code_only: bool = False,
    split: bool = False,
    outer=None,
):
    from ...lib.module.local import pack_module

    if not module_name:
        return
    ret = pack_module(
        module_name=module_name,
        outdir=outdir,
        code_only=code_only,
        split=split,
        outer=outer,
    )
    return ret


def ls(
    patterns: List[str] = [".*"],
    available: bool = False,
    types: List[str] = [],
    tags: List[str] = [],
    nameonly: bool = False,
    raw_bytes: bool = False,
    **kwargs,
):
    from .ls_logic import list_modules

    _ = kwargs
    ret = list_modules(
        patterns=patterns,
        types=types,
        tags=tags,
        available=available,
        nameonly=nameonly,
        raw_bytes=raw_bytes,
    )
    return ret


def info(module_name: Optional[str] = None, local: bool = False, **kwargs):
    from ...lib.module.local import get_local_module_info
    from ...lib.module.remote import get_remote_module_info
    from ...lib.module.local import LocalModule
    from ...lib.module.remote import get_readme

    _ = kwargs
    ret = {}
    if not module_name:
        return None
    installed = False
    remote_available = False
    up_to_date = False
    local_info = None
    remote_info = None
    # Readm
    readme = get_readme(module_name)
    ret["readme"] = readme
    # Remote
    remote_info = get_remote_module_info(module_name)
    remote_available = remote_info != None
    # Local
    local_info = get_local_module_info(module_name)
    if local_info:
        installed = True
    else:
        installed = False
    if not remote_available and not installed:
        return None
    if remote_available and remote_info:
        ret.update(remote_info.to_info())
        ret["output_columns"] = []
        if remote_info.output_columns:
            for col in remote_info.output_columns:
                desc = ""
                if "desc" in col:
                    desc = col["desc"]
                ret["output_columns"].append(
                    {"name": col["name"], "title": col["title"], "desc": desc}
                )
    else:
        ret["store_availability"] = False
    ret["installed"] = installed
    if installed:
        if local and isinstance(local_info, LocalModule):
            ret["installed_version"] = local_info.code_version
            ret["location"] = local_info.directory
    else:
        pass
    if (
        installed
        and remote_available
        and local_info
        and local_info.code_version
        and remote_info
    ):
        if installed and local_info.code_version >= remote_info.latest_code_version:
            up_to_date = True
        else:
            up_to_date = False
        ret["latest_installed"] = up_to_date
        ret["latest_store_version"] = ret["latest_version"]
        del ret["latest_version"]
        ret["latest_version"] = max(
            local_info.code_version, remote_info.latest_code_version
        )
    return ret


def install(
    module_names: List[str] = [],
    modules_dir: Optional[str] = None,
    overwrite: bool = False,
    clean: bool = False,
    force_data: bool = False,
    yes: bool = False,
    skip_dependencies: bool = False,
    skip_data: bool = False,
    no_fetch: bool = False,
    outer=None,
    error=None,
    system_worker_state=None**kwargs,
):
    from .install import get_modules_to_install
    from .install import show_modules_to_install
    from ...lib.module import install_module
    from ...lib.module import install_module_from_url
    from ...lib.module import install_module_from_zip_path
    from ...lib.util.run import get_y_or_n
    from ...lib.util.download import is_url
    from ...lib.util.download import is_zip_path
    from ...lib.store.db import try_fetch_ov_store_cache
    from ...lib.exceptions import ModuleToSkipInstallation

    _ = kwargs
    if not no_fetch:
        try_fetch_ov_store_cache()
    to_install = get_modules_to_install(
        module_names, skip_dependencies=skip_dependencies, outer=outer
    )
    if len(to_install) == 0:
        if outer:
            outer.write("No module to install")
        return True
    show_modules_to_install(to_install, outer=outer)
    if not yes:
        if not get_y_or_n():
            return True
    problem_modules = []
    for module_name, module_version in sorted(to_install.items()):
        try:
            if is_url(module_name):
                if not install_module_from_url(
                    module_name,
                    modules_dir,
                    clean=clean,
                    overwrite=overwrite,
                    force_data=force_data,
                    skip_data=skip_data,
                    outer=outer,
                ):
                    problem_modules.append(module_name)
            elif is_zip_path(module_name):
                if not install_module_from_zip_path(
                    module_name, force_data=force_data, skip_data=skip_data, outer=outer
                ):
                    problem_modules.append(module_name)
            else:
                stage_handler = InstallProgressStdout(
                    module_name, module_version, outer=outer
                )
                ret = install_module(
                    module_name,
                    version=module_version,
                    force_data=force_data,
                    overwrite=overwrite,
                    stage_handler=stage_handler,
                    skip_data=skip_data,
                    outer=outer,
                    error=error,
                    system_worker_state=system_worker_state,
                )
                if not ret:
                    problem_modules.append(module_name)
        except Exception as e:
            if not isinstance(e, ModuleToSkipInstallation):
                if module_name not in problem_modules:
                    problem_modules.append(module_name)
            if hasattr(e, "traceback") and getattr(e, "traceback"):
                import traceback

                traceback.print_exc()
            if error:
                error.write(e)
    if problem_modules:
        if outer:
            outer.write(f"Following modules were not installed due to problems:")
        for mn in problem_modules:
            if outer:
                outer.write(f"- {mn}")
        return False
    else:
        return


def update(module_name_patterns: List[str]=[], clean_cache_db: bool=False, clean_cache_files: bool=False, clean: bool=False, publish_time: str="", no_fetch: bool=False, conf: Optional[dict]=None, overwrite: bool=False, modules_dir: Optional[str]=None, outer=None, error=None, system_worker_state=None):
    from types import SimpleNamespace
    from ...lib.module.local import search_local
    from ...lib.module import get_updatable
    from ...lib.util.util import humanize_bytes
    from ...lib.util.util import quiet_print
    from ...lib.util.util import print_tabular_lines
    from ...lib.store.db import try_fetch_ov_store_cache

    if not no_fetch:
        try_fetch_ov_store_cache(clean_cache_db=clean_cache_db, clean_cache_files=clean_cache_files, clean=clean, publish_time=publish_time, outer=outer)
    requested_modules = search_local(*module_name_patterns)
    status_table = [["Name", "New Version", "Size"]]
    updates, _, reqs_failed = get_updatable(requested_modules=requested_modules)
    if reqs_failed:
        msg = f"Newer versions of ({}) are available, but would break dependencies. You may use --strategy=force to force installation.".format(
            ", ".join(reqs_failed.keys())
        )
        quiet_print(msg, args=args)
    if not updates:
        msg = "No module to update was found"
        quiet_print(msg, args=args)
        return True
    for mname, update_info in updates.items():
        version = update_info.version
        size = update_info.size
        status_table.append([mname, version, humanize_bytes(size)])
    print_tabular_lines(status_table, args=args)
    if not args["y"]:
        if not quiet:
            user_cont = input("Proceed to update? (y/n) > ")
            if user_cont.lower() not in ["y", "yes"]:
                return True
    for mname, update_info in updates.items():
        m_args = SimpleNamespace(
            modules=[mname],
            force_data=False,
            version=update_info.version,
            yes=True,
            private=False,
            skip_dependencies=False,
            force=False,
            skip_data=False,
            md=args.get("md", None),
            quiet=args.get("quiet"),
        )
        ret = install(module_names=base_modules, modules_dir=modules_dir, overwrite=False, clean=clean, force_data=False, yes=True, skip_dependencies=False, skip_data=False, no_fetch=no_fetch, outer=outer, error=error, system_worker_state=system_worker_state)
        if ret is not None:
            return False
    return True


def uninstall(args, __name__="module uninstall"):
    from ...lib.module.local import search_local
    from ...lib.module import uninstall_module
    from ...lib.util.util import quiet_print

    modules = args.get("modules")
    if not modules:
        from ...lib.exceptions import ArgumentError

        e = ArgumentError("no modules was given.")
        e.traceback = False
        raise e
    matching_names = search_local(*modules)
    if len(matching_names) > 0:
        quiet_print("Uninstalling: {:}".format(", ".join(matching_names)), args=args)
        if not (args["yes"]):
            while True:
                resp = input("Proceed? (y/n) > ")
                if resp == "y":
                    break
                elif resp == "n":
                    return False
                else:
                    quiet_print(
                        "Response '{:}' not one of (y/n).".format(resp), args=args
                    )
        for module_name in matching_names:
            uninstall_module(module_name)
            quiet_print("Uninstalled %s" % module_name, args=args)
    else:
        quiet_print("No modules to uninstall found", args=args)
    return True


def installbase(clean_cache_db: bool=False, clean_cache_files: bool=False, clean: bool=False, publish_time: str="", no_fetch: bool=False, conf: Optional[dict]=None, overwrite: bool=False, modules_dir: Optional[str]=None, outer=None, error=None, system_worker_state=None):
    from ...lib.system import get_system_conf
    from ...lib.system.consts import base_modules_key
    from ...lib.store.db import try_fetch_ov_store_cache

    if not no_fetch:
        try_fetch_ov_store_cache(clean_cache_db=clean_cache_db, clean_cache_files=clean_cache_files, clean=clean, publish_time=publish_time, outer=outer)
    sys_conf = get_system_conf(conf=conf)
    base_modules = sys_conf.get(base_modules_key, [])
    ret = install(module_names=base_modules, modules_dir=modules_dir, overwrite=overwrite, clean=clean, force_data=False, yes=True, skip_dependencies=False, skip_data=False, no_fetch=no_fetch, outer=outer, error=error, system_worker_state=system_worker_state)
    return ret


class InstallProgressStdout(InstallProgressHandler):
    def __init__(self, module_name: str, module_version: str, outer=None):
        super().__init__(module_name, module_version)
        self.outer = outer
        self.system_worker_state = None

    def stage_start(self, stage):
        self.cur_stage = stage
        if self.outer:
            self.outer.write(self._stage_msg(stage))
