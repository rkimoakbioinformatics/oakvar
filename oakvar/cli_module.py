from .decorators import cli_func
from .decorators import cli_entry


@cli_entry
def cli_ov_module_ls(args):
    args.fmt = "yaml"
    return ov_module_ls(args)

@cli_func
def ov_module_ls(args):
    from .util import quiet_print
    avail = args.get("available", False)
    to = args.get("to", "return")
    fmt = args.get("fmt", "json")
    if avail:
        ret = list_available_modules(args)
        if to == "stdout":
            if fmt == "tabular":
                print_tabular_lines(ret)
            else:
                quiet_print(ret, args=args)
        else:
            return ret
    else:
        ret = list_local_modules(args)
        if to == "stdout":
            if fmt == "tabular":
                print_tabular_lines(ret)
            else:
                print(ret)
        else:
            return ret


@cli_entry
def cli_ov_module_info(args):
    args.fmt = "yaml"
    return ov_module_info(args)


@cli_func
def ov_module_info(args):
    from oyaml import dump
    from .admin_util import (
        get_local_module_info,
        get_remote_module_info,
        get_remote_module_config,
    )
    ret = {}
    module_name = args.get("module", None)
    if module_name is None:
        return ret
    installed = False
    remote_available = False
    up_to_date = False
    local_info = None
    remote_info = None
    fmt = args.get("fmt", "json")
    to = args.get("to", "return")
    # Remote
    try:
        remote_info = get_remote_module_info(module_name)
        if remote_info != None:
            remote_available = True
    except LookupError:
        remote_available = False
    # Local
    release_note = {}
    try:
        local_info = get_local_module_info(module_name)
        if local_info != None:
            installed = True
            release_note = local_info.conf.get("release_note", {})
        else:
            installed = False
    except LookupError:
        installed = False
    if remote_available and remote_info is not None:
        versions = remote_info.versions
        data_sources = remote_info.data_sources
        new_versions = []
        for version in versions:
            data_source = data_sources.get(version, None)
            note = release_note.get(version, None)
            if data_source:
                version = version + " (data source " + data_source + ")"
            if note:
                version = version + " " + note
            new_versions.append(version)
        remote_info.versions = new_versions
        ret.update(remote_info.data)
        ret["output_columns"] = []
        conf = get_remote_module_config(module_name)
        if "output_columns" in conf:
            output_columns = conf["output_columns"]
            for col in output_columns:
                desc = ""
                if "desc" in col:
                    desc = col["desc"]
                ret["output_columns"].append({
                    "name": col["name"],
                    "title": col["title"],
                    "desc": desc
                })
    else:
        ret["store_availability"] = False
    ret["installed"] = installed
    if installed:
        from .admin_util import LocalInfoCache
        if args.get("local", None) and isinstance(local_info, LocalInfoCache):
            ret.update(local_info)
    else:
        pass
    if installed and remote_available and local_info is not None and remote_info is not None:
        if installed and local_info.version == remote_info.latest_version:
            up_to_date = True
        else:
            up_to_date = False
        ret["latest_installed"] = up_to_date
    if fmt == "yaml":
        ret = dump(ret)
    if to == "stdout":
        print(ret)
    else:
        return ret


@cli_entry
def cli_ov_module_install(args):
    return ov_module_install(args)


@cli_func
def ov_module_install(args):
    from .admin_util import (
        search_remote,
        get_local_module_info,
        get_remote_module_info,
        module_exists_remote,
        get_install_deps,
        install_module,
    )
    from distutils.version import LooseVersion
    from .util import quiet_print
    module_name_versions = {}
    modules = args.get("modules", [])
    if type(modules) == str:
        modules = [modules]
    quiet = args.get("quiet", True)
    if not modules: 
        from .exceptions import ArgumentError
        e = ArgumentError("no module was given")
        e.traceback = False
        raise e
    for mv in modules:
        try:
            if "==" in mv:
                [module_name, version] = mv.split("==")
            else:
                module_name = mv
                version = None
            module_name_versions[module_name] = version
        except:
            quiet_print(f"Wrong module name==version format: {mv}", args=args)
    module_names = list(module_name_versions.keys())
    # handles regex in module name.
    for module_name in module_names:
        version = module_name_versions[module_name]
        del module_name_versions[module_name]
        matching_names = search_remote(module_name)
        if len(matching_names) == 0:
            quiet_print(f"invalid module name: {module_name}", args=args)
            continue
        for mn in matching_names:
            module_name_versions[mn] = version
    # filters valid module name and version.
    selected_install = {}
    for module_name in module_name_versions.keys():
        local_info = get_local_module_info(module_name)
        remote_info = get_remote_module_info(module_name)
        version = module_name_versions[module_name]
        if version is None:
            if args.get("private", True):
                quiet_print(
                    f"{module_name}: a version should be given for a private module",
                    args=args)
                continue
            else:
                if remote_info is not None:
                    if local_info is not None:
                        #local_ver = local_info.version
                        #remote_ver = remote_info.latest_version
                        if not args["force"] and LooseVersion(
                                local_info.version) >= LooseVersion(
                                    remote_info.latest_version):
                            quiet_print(
                                f"{module_name}: latest version is already installed.",
                                args=args)
                            continue
                    selected_install[module_name] = remote_info.latest_version
        else:
            if not module_exists_remote(
                    module_name, version=version, private=args["private"]):
                from .exceptions import ModuleNotExist
                raise ModuleNotExist(module_name)
            else:
                if (not args["force"] and local_info is not None
                        and LooseVersion(
                            local_info.version) == LooseVersion(version)):
                    quiet_print(
                        f"{module_name}=={args['version']} is already installed. Use -f/--force to overwrite",
                        args=args)
                    continue
            selected_install[module_name] = version
    # Add dependencies of selected modules
    deps_install = {}
    deps_install_pypi = {}
    if not args["skip_dependencies"]:
        for module_name, version in selected_install.items():
            deps, deps_pypi = get_install_deps(module_name, version=version)
            deps_install.update(deps)
            deps_install_pypi.update(deps_pypi)
    # If overlap between selected modules and dependency modules, use the dependency version
    to_install = selected_install
    to_install.update(deps_install)
    if len(to_install) == 0:
        quiet_print("No module to install found", args=args)
    else:
        quiet_print("The following modules will be installed:", args=args)
        for name in sorted(list(to_install.keys())):
            quiet_print(f"- {name}=={to_install[name]}", args=args)
        if not (args["yes"]):
            while True:
                resp = input("Proceed? ([y]/n) > ")
                if resp == "y" or resp == "":
                    break
                if resp == "n":
                    return True
                else:
                    continue
        for module_name, module_version in sorted(to_install.items()):
            stage_handler = InstallProgressStdout(module_name,
                                                  module_version,
                                                  quiet=quiet)
            quiet_print(f"Installing {module_name}...", args=args)
            install_module(module_name,
                           version=module_version,
                           force_data=args["force_data"],
                           stage_handler=stage_handler,
                           force=args["force"],
                           skip_data=args["skip_data"],
                           quiet=quiet)
    return True


@cli_entry
def cli_ov_module_update(args):
    return ov_module_update(args)


@cli_func
def ov_module_update(args):
    from .admin_util import search_local, get_updatable
    from .util import humanize_bytes
    from .util import quiet_print
    from types import SimpleNamespace
    quiet = args.get("quiet", True)
    #ret = {"msg": []}
    modules = args.get("modules", [])
    if not modules:
        from .exceptions import ArgumentError
        e = ArgumentError("no modules was given.")
        e.traceback = False
        raise e
    requested_modules = search_local(*modules)
    update_strategy = args.get("strategy")
    status_table = [["Name", "New Version", "Size"]]
    updates, _, reqs_failed = get_updatable(requested_modules,
                                            strategy=update_strategy)
    if reqs_failed:
        msg = "Newer versions of ({}) are available, but would break dependencies. You may use --strategy=force to force installation.".format(
            ", ".join(reqs_failed.keys()))
        quiet_print(msg, args=args)
    if not updates:
        msg = "No module updates are needed"
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
        args = SimpleNamespace(
            modules=[mname],
            force_data=False,
            version=update_info.version,
            yes=True,
            private=False,
            skip_dependencies=False,
            force=False,
            skip_data=False,
            md=args.get("md", None),
        )
        if not ov_module_install(args):
            return False
    return True


@cli_entry
def cli_ov_module_uninstall(args):
    return ov_module_uninstall(args)


@cli_func
def ov_module_uninstall(args):
    from .admin_util import search_local, uninstall_module
    from .util import quiet_print
    modules = args.get("modules")
    if not modules:
        from .exceptions import ArgumentError
        e = ArgumentError("no modules was given.")
        e.traceback = False
        raise e
    matching_names = search_local(*modules)
    if len(matching_names) > 0:
        quiet_print("Uninstalling: {:}".format(", ".join(matching_names)),
                    args=args)
        if not (args["yes"]):
            while True:
                resp = input("Proceed? (y/n) > ")
                if resp == "y":
                    break
                elif resp == "n":
                    return False
                else:
                    quiet_print(
                        "Response '{:}' not one of (y/n).".format(resp),
                        args=args)
        for module_name in matching_names:
            uninstall_module(module_name)
            quiet_print("Uninstalled %s" % module_name, args=args)
    else:
        quiet_print("No modules to uninstall found", args=args)
    return True


@cli_entry
def cli_ov_module_installbase(args):
    return ov_module_installbase(args)


@cli_func
def ov_module_installbase(args):
    from .sysadmin import get_system_conf
    from .sysadmin_const import base_modules_key
    from types import SimpleNamespace
    sys_conf = get_system_conf(conf=args.get("conf"))
    base_modules = sys_conf.get(base_modules_key, [])
    args = SimpleNamespace(
        modules=base_modules,
        force_data=args.get("force_data", True),
        version=None,
        yes=True,
        private=False,
        skip_dependencies=False,
        force=args.get("force", False),
        skip_data=False,
        md=args.get("md", None),
        quiet=args.get("quiet", True),
    )
    ret = ov_module_install(args)
    return ret


def list_available_modules(args):
    from oyaml import dump
    from .admin_util import search_remote, get_local_module_info, get_remote_module_info
    from .util import humanize_bytes
    fmt = args.get("fmt", "return")
    nameonly = args.get("nameonly", False)
    all_toks_name = []
    all_toks_text = []
    all_toks_json = []
    if fmt == "tabular":
        if nameonly:
            all_toks_name = []
        else:
            header = [
                "Name",
                "Title",
                "Type",
                "Installed",
                "Store ver",
                "Store data ver",
                "Local ver",
                "Local data ver",
                "Size",
            ]
            all_toks_text = [header]
    elif fmt in ["json", "yaml"]:
        all_toks_json = []
    for module_name in search_remote(args.get("pattern")):
        remote_info = get_remote_module_info(module_name)
        if remote_info is not None:
            if len(args.get(
                    "types")) > 0 and remote_info.type not in args["types"]:
                continue
            if len(args.get("tags")) > 0:
                if remote_info.tags is None:
                    continue
                if len(set(args.get("tags")).intersection(
                        remote_info.tags)) == 0:
                    continue
            if remote_info.hidden and not args.get("include_hidden"):
                continue
            local_info = get_local_module_info(module_name)
            if local_info is not None:
                installed = "yes"
                local_version = local_info.version
                local_datasource = local_info.datasource
            else:
                installed = ""
                local_version = ""
                local_datasource = ""
            if args.get("raw_bytes"):
                size = remote_info.size
            else:
                size = humanize_bytes(remote_info.size)
            toks = []
            if fmt == "tabular":
                if args["nameonly"]:
                    toks = [module_name]
                    all_toks_name.append(toks)
                else:
                    toks = [
                        module_name,
                        remote_info.title,
                        remote_info.type,
                        installed,
                        remote_info.latest_version,
                        remote_info.datasource,
                        local_version,
                        local_datasource,
                        size,
                    ]
                    all_toks_text.append(toks)
            elif fmt in ["json", "yaml"]:
                toks = {
                    "name": module_name,
                    "title": remote_info.title,
                    "type": remote_info.type,
                    "installed": installed,
                    "latest_version": remote_info.latest_version,
                    "datasource": remote_info.datasource,
                    "local_version": local_version,
                    "local_datasource": local_datasource,
                    "size": size,
                }
                all_toks_json.append(toks)
    if fmt == "tabular":
        if nameonly:
            return all_toks_name
        else:
            return all_toks_text
    elif fmt == "json":
        return all_toks_json
    elif fmt == "yaml":
        return dump(all_toks_json, default_flow_style=False)
    else:
        return None


def list_local_modules(args):
    from oyaml import dump
    from .admin_util import search_local, get_local_module_info
    from .util import humanize_bytes
    pattern = args.get("pattern", r".*")
    types = args.get("types", [])
    include_hidden = args.get("include_hidden", False)
    tags = args.get("tags", [])
    raw_bytes = args.get("raw_bytes", False)
    fmt = args.get("fmt", "json")
    nameonly = args.get("nameonly", False)
    all_toks_nameonly = []
    all_toks_text = []
    all_toks_json = []
    if fmt == "tabular" and not nameonly:
        header = [
            "Name", "Title", "Type", "Version", "Data source ver", "Size"
        ]
        all_toks_text = [header]
    for module_name in search_local(pattern):
        module_info = get_local_module_info(module_name)
        if module_info is not None:
            if len(types) > 0 and module_info.type not in types:
                continue
            if len(tags) > 0:
                if module_info.tags is None:
                    continue
                if len(set(tags).intersection(module_info.tags)) == 0:
                    continue
            if module_info.hidden and not include_hidden:
                continue
            if nameonly:
                toks = [module_name]
                all_toks_nameonly.append(toks)
            else:
                size = module_info.get_size()
                if fmt in ["json", "yaml"]:
                    toks = {
                        "name": module_name,
                        "title": module_info.title,
                        "type": module_info.type,
                        "version": module_info.version,
                        "datasource": module_info.datasource,
                    }
                    if raw_bytes:
                        toks["size"] = size
                    else:
                        toks["size"] = humanize_bytes(size)
                    all_toks_json.append(toks)
                else:
                    toks = [
                        module_name,
                        module_info.title,
                        module_info.type,
                        module_info.version,
                        module_info.datasource,
                    ]
                    if raw_bytes:
                        toks.append(size)
                    else:
                        toks.append(humanize_bytes(size))
                    all_toks_text.append(toks)
    if fmt == "tabular":
        if nameonly:
            return all_toks_nameonly
        else:
            return all_toks_text
    elif fmt == "json":
        return all_toks_json
    elif fmt == "yaml":
        return dump(all_toks_json, default_flow_style=False)


def print_tabular_lines(l, args=None):
    from .util import quiet_print
    for line in yield_tabular_lines(l):
        if args:
            quiet_print(line, args=args)
        else:
            print(line)


def yield_tabular_lines(l, col_spacing=2, indent=0):
    if not l:
        return
    sl = []
    n_toks = len(l[0])
    max_lens = [0] * n_toks
    for toks in l:
        if len(toks) != n_toks:
            raise RuntimeError("Inconsistent sub-list length")
        stoks = [str(x) for x in toks]
        sl.append(stoks)
        stoks_len = [len(x) for x in stoks]
        max_lens = [max(x) for x in zip(stoks_len, max_lens)]
    for stoks in sl:
        jline = " " * indent
        for i, stok in enumerate(stoks):
            jline += stok + " " * (max_lens[i] + col_spacing - len(stok))
        yield jline


from .admin_util import InstallProgressHandler
class InstallProgressStdout(InstallProgressHandler):

    def __init__(self, module_name, module_version, quiet=True):
        super().__init__(module_name, module_version)
        self.quiet = quiet

    def stage_start(self, stage):
        from .util import quiet_print
        self.cur_stage = stage
        quiet_print(self._stage_msg(stage), args={"quiet": self.quiet})

    def stage_progress(self, cur_chunk, total_chunks, cur_size, total_size):
        from .util import humanize_bytes
        from .util import quiet_print
        from .util import get_current_time_str
        rem_chunks = total_chunks - cur_chunk
        perc = cur_size / total_size * 100
        # trailing spaces needed to avoid leftover characters on resize
        out = f"\033[F\033[K[{get_current_time_str()}] Downloading {humanize_bytes(cur_size)} / {humanize_bytes(total_size)} ({perc:.0f}%)"
        quiet_print(out, args={"quiet": self.quiet})


def get_parser_fn_module():
    from argparse import ArgumentParser, RawDescriptionHelpFormatter
    parser_fn_module = ArgumentParser(
        formatter_class=RawDescriptionHelpFormatter)
    _subparsers = parser_fn_module.add_subparsers(title="Commands",
                                                  dest="command")

    # installbase
    parser_ov_module_installbase = _subparsers.add_parser(
        "installbase",
        help="installs base modules.",
        description="installs base modules.")
    parser_ov_module_installbase.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Overwrite existing modules",
    )
    parser_ov_module_installbase.add_argument(
        "-d",
        "--force-data",
        action="store_true",
        help="Download data even if latest data is already installed",
    )
    parser_ov_module_installbase.add_argument(
        "--md",
        default=None,
        help="Specify the root directory of OakVar modules")
    parser_ov_module_installbase.add_argument("--quiet",
                                               default=True,
                                               action="store_true",
                                               help="suppress stdout output")
    parser_ov_module_installbase.set_defaults(func=cli_ov_module_installbase)
    parser_ov_module_installbase.r_return = "A boolean. TRUE if successful, FALSE if not"  # type: ignore
    parser_ov_module_installbase.r_examples = [  # type: ignore
        "# Install OakVar system modules", "ov.module.installbase()"
    ]

    # install
    parser_ov_module_install = _subparsers.add_parser(
        "install",
        help="installs OakVar modules.",
        description="Installs OakVar modules.")
    parser_ov_module_install.add_argument(
        "modules",
        nargs="+",
        help="Modules to install. May be regular expressions.")
    parser_ov_module_install.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Install module even if latest version is already installed",
    )
    parser_ov_module_install.add_argument(
        "-d",
        "--force-data",
        action="store_true",
        help="Download data even if latest data is already installed",
    )
    parser_ov_module_install.add_argument("-y",
                                           "--yes",
                                           action="store_true",
                                           help="Proceed without prompt")
    parser_ov_module_install.add_argument("--skip-dependencies",
                                           action="store_true",
                                           help="Skip installing dependencies")
    parser_ov_module_install.add_argument("-p",
                                           "--private",
                                           action="store_true",
                                           help="Install a private module")
    parser_ov_module_install.add_argument("--skip-data",
                                           action="store_true",
                                           help="Skip installing data")
    parser_ov_module_install.add_argument(
        "--md",
        default=None,
        help="Specify the root directory of OakVar modules")
    parser_ov_module_install.add_argument(
        "--to", default="return", help="'stdout' to print. 'return' to return")
    parser_ov_module_install.add_argument("--quiet",
                                           default=True,
                                           action="store_true",
                                           help="suppress stdout output")
    parser_ov_module_install.set_defaults(func=cli_ov_module_install)
    parser_ov_module_install.r_return = "A boolean. TRUE if successful, FALSE if not"  # type: ignore
    parser_ov_module_install.r_examples = [  # type: ignore
        "# Install the ClinVar module",
        "ov.module.install(modules=\"clinvar\")",
        "# Install the ClinVar and the COSMIC modules",
        "ov.module.install(modules=list(\"clinvar\", \"cosmic\")",
        "# Re-install the ClinVar module overwriting the already installed copy",
        "ov.module.install(modules=\"clinvar\", force=TRUE)"
    ]

    # update
    parser_ov_module_update = _subparsers.add_parser(
        "update",
        help="updates modules.",
        description="updates modules.",
        formatter_class=RawDescriptionHelpFormatter,
    )
    parser_ov_module_update.add_argument("modules",
                                          nargs="*",
                                          help="Modules to update.")
    parser_ov_module_update.add_argument("-y",
                                          action="store_true",
                                          help="Proceed without prompt")
    parser_ov_module_update.add_argument(
        "--strategy",
        help=
        'Dependency resolution strategy. "consensus" will attempt to resolve dependencies. "force" will install the highest available version. "skip" will skip modules with constraints.',
        default="consensus",
        type=str,
        choices=("consensus", "force", "skip"),
    )
    parser_ov_module_update.add_argument(
        "--md",
        default=None,
        help="Specify the root directory of OakVar modules")
    parser_ov_module_update.add_argument("--quiet",
                                          default=True,
                                          action="store_true",
                                          help="suppress stodout output")
    parser_ov_module_update.set_defaults(func=cli_ov_module_update)
    parser_ov_module_update.r_return = "A boolean. TRUE if successful, FALSE if not"  # type: ignore
    parser_ov_module_update.r_examples = [  # type: ignore
        "# Update the ClinVar module", "ov.module.update(modules=\"clinvar\")",
        "# Update all the installed modules", "ov.module.update()"
    ]

    # uninstall
    parser_ov_module_uninstall = _subparsers.add_parser(
        "uninstall", help="uninstalls modules.")
    parser_ov_module_uninstall.add_argument("modules",
                                             nargs="+",
                                             help="Modules to uninstall")
    parser_ov_module_uninstall.add_argument("-y",
                                             "--yes",
                                             action="store_true",
                                             help="Proceed without prompt")
    parser_ov_module_uninstall.add_argument(
        "--md",
        default=None,
        help="Specify the root directory of OakVar modules")
    parser_ov_module_uninstall.add_argument("--quiet",
                                             default=True,
                                             help="Run quietly")
    parser_ov_module_uninstall.set_defaults(func=cli_ov_module_uninstall)
    parser_ov_module_uninstall.r_return = "A boolean. TRUE if successful, FALSE if not"  # type: ignore
    parser_ov_module_uninstall.r_examples = [  # type: ignore
        "# Uninstall the ClinVar module",
        "ov.module.uninstall(modules=\"clinvar\")"
        "# Uninstall the ClinVar and the COSMIC modules",
        "ov.module.uninstall(modules=(\"clinvar\", \"cosmic\")"
    ]

    # info
    parser_ov_module_info = _subparsers.add_parser(
        "info",
        epilog="returns information of the queried module",
        help="shows module information.")
    parser_ov_module_info.add_argument("module",
                                        help="Module to get info about")
    parser_ov_module_info.add_argument("-l",
                                        "--local",
                                        dest="local",
                                        help="Include local info",
                                        action="store_true")
    parser_ov_module_info.add_argument(
        "--md",
        default=None,
        help="Specify the root directory of OakVar modules")
    parser_ov_module_info.add_argument(
        "--fmt",
        default="json",
        help="format of module information data. json or yaml")
    parser_ov_module_info.add_argument(
        "--to",
        default="return",
        help='"stdout" to stdout / "return" to return')
    parser_ov_module_info.add_argument("--quiet",
                                        default=True,
                                        help="Run quietly")
    parser_ov_module_info.set_defaults(func=cli_ov_module_info)
    parser_ov_module_info.r_return = "A named list. Information of the queried module"  # type: ignore
    parser_ov_module_info.r_examples = [  # type: ignore
        "# Get the information of the ClinVar module",
        "ov.module.info(module=\"clinvar\")"
    ]

    # ls
    parser_ov_module_ls = _subparsers.add_parser(
        "ls",
        help="lists modules.",
        description="lists modules.",
        formatter_class=RawDescriptionHelpFormatter,
    )
    parser_ov_module_ls.add_argument(
        "pattern",
        nargs="?",
        default=r".*",
        help="Regular expression for module names")
    parser_ov_module_ls.add_argument("-a",
                                      "--available",
                                      action="store_true",
                                      default=False,
                                      help="Include available modules")
    parser_ov_module_ls.add_argument(
        "-t",
        "--types",
        nargs="+",
        default=[],
        help="Only list modules of certain types")
    parser_ov_module_ls.add_argument("-i",
                                      "--include-hidden",
                                      action="store_true",
                                      default=False,
                                      help="Include hidden modules")
    parser_ov_module_ls.add_argument("--tags",
                                      nargs="+",
                                      default=[],
                                      help="Only list modules of given tag(s)")
    parser_ov_module_ls.add_argument("--nameonly",
                                      action="store_true",
                                      default=False,
                                      help="Only list module names")
    parser_ov_module_ls.add_argument("--bytes",
                                      action="store_true",
                                      default=False,
                                      dest="raw_bytes",
                                      help="Machine readable data sizes")
    parser_ov_module_ls.add_argument(
        "--md",
        default=None,
        help="Specify the root directory of OakVar modules")
    parser_ov_module_ls.add_argument("--fmt",
                                      default="json",
                                      help="Output format. tabular or json")
    parser_ov_module_ls.add_argument(
        "--to", default="return", help="stdout to print / return to return")
    parser_ov_module_ls.add_argument("--quiet",
                                      default=True,
                                      help="Run quietly")
    parser_ov_module_ls.set_defaults(func=cli_ov_module_ls)
    parser_ov_module_ls.r_return = "A named list. List of modules"  # type: ignore
    parser_ov_module_ls.r_examples = [  # type: ignore
        "# Get the list of all installed modules", "ov.module.ls()",
        "# Get the list of all available modules",
        "ov.module.ls(available=TRUE)",
        "# Get the list of all available modules of the type \"converter\"",
        "ov.module.ls(available=TRUE, types=\"converter\")"
    ]
    return parser_fn_module
