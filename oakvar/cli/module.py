from ..module import InstallProgressHandler
from ..decorators import cli_func
from ..decorators import cli_entry


@cli_entry
def cli_module_pack(args):
    return pack(args)


@cli_func
def pack(args, __name__="module pack"):
    from ..module.local import pack_module

    ret = pack_module(args)
    return ret


@cli_entry
def cli_module_ls(args):
    if not args.fmt:
        args.fmt = "tabular"
    return ls(args)


@cli_func
def ls(args, __name__="module ls"):
    if args.get("fmt") == None:
        args["fmt"] = "json"
    to = args.get("to", "return")
    fmt = args.get("fmt")
    ret = list_modules(args)
    if to == "stdout":
        if ret:
            if fmt == "tabular":
                print_tabular_lines(ret)
            else:
                print(ret)
    else:
        return ret


@cli_entry
def cli_module_info(args):
    args.fmt = "yaml"
    return info(args)


@cli_func
def info(args, __name__="module info"):
    from oyaml import dump
    from ..module.local import get_local_module_info
    from ..module.remote import get_remote_module_info
    from ..module.local import LocalModule

    ret = {}
    module_name = args.get("module", None)
    if not module_name:
        return ret
    installed = False
    remote_available = False
    up_to_date = False
    local_info = None
    remote_info = None
    fmt = args.get("fmt", "json")
    to = args.get("to", "return")
    # Remote
    remote_info = get_remote_module_info(module_name)
    remote_available = remote_info != None
    # Local
    local_info = get_local_module_info(module_name)
    if local_info:
        installed = True
    else:
        installed = False
    if remote_available and remote_info is not None:
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
        if not args.get("local") and isinstance(local_info, LocalModule):
            ret["installed_version"] = local_info.code_version
            ret["location"] = local_info.directory
    else:
        pass
    if (
        installed
        and remote_available
        and local_info is not None
        and local_info.code_version
        and remote_info is not None
    ):
        if installed and local_info.code_version >= remote_info.latest_code_version:
            up_to_date = True
        else:
            up_to_date = False
        ret["latest_installed"] = up_to_date
        ret["latest_store_version"] = ret["latest_version"]
        del ret["latest_version"]
        ret["latest_version"] = max(local_info.code_version, remote_info.latest_code_version)
    if fmt == "yaml":
        ret = dump(ret)
    if to == "stdout":
        print(ret)
    else:
        return ret


@cli_entry
def cli_module_install(args):
    return install(args)


def collect_module_name_and_versions(modules, args=None):
    from ..util.util import quiet_print

    mn_vs = {}
    if type(modules) == str:
        modules = [modules]
    for mv in modules:
        try:
            if "==" in mv:
                [module_name, version] = mv.split("==")
            else:
                module_name = mv
                version = None
            mn_vs[module_name] = version
        except:
            quiet_print(f"Wrong module name==version format: {mv}", args=args)
    return mn_vs

def get_modules_to_install(args={}) -> dict:
    from ..util.download import is_url
    from ..util.download import is_zip_path
    from ..module.remote import get_install_deps
    mn_vs = collect_module_name_and_versions(args.get("modules", []), args=args)
    module_versions = {}
    for module_name, version in mn_vs.items():
        module_versions[module_name] = version
    # dependency
    deps_install = {}
    if not args.get("skip_dependencies"):
        for module_name, version in module_versions.items():
            if not is_url(module_name) and not is_zip_path(module_name):
                deps, _ = get_install_deps(module_name=module_name, version=version)
                deps_install.update(deps)
    to_install = module_versions
    to_install.update(deps_install)
    return to_install

def show_modules_to_install(to_install, args={}):
    from ..util.util import quiet_print
    quiet_print("The following modules will be installed:", args=args)
    for name in sorted(list(to_install.keys())):
        version = to_install.get(name)
        if version:
            quiet_print(f"- {name}=={to_install[name]}", args=args)
        else:
            quiet_print(f"- {name}", args=args)

@cli_func
def install(args, __name__="module install"):
    from ..module import install_module
    from ..module import install_module_from_url
    from ..module import install_module_from_zip_path
    from ..util.util import quiet_print
    from ..util.util import wait_for_y
    from ..util.download import is_url
    from ..util.download import is_zip_path
    from ..store.db import try_fetch_ov_store_cache

    try_fetch_ov_store_cache(args=args)
    to_install = get_modules_to_install(args=args)
    if len(to_install) == 0:
        quiet_print("No module to install", args=args)
        return True
    show_modules_to_install(to_install, args=args)
    if not (args["yes"]):
        wait_for_y()
    problem_modules = []
    for module_name, module_version in sorted(to_install.items()):
        try:
            if is_url(module_name):
                if not install_module_from_url(module_name, args=args):
                    problem_modules.append(module_name)
            elif is_zip_path(module_name):
                if not install_module_from_zip_path(module_name, args=args):
                    problem_modules.append(module_name)
            else:
                stage_handler = InstallProgressStdout(
                    module_name, module_version, quiet=args.get("quiet")
                )
                ret = install_module(
                    module_name,
                    version=module_version,
                    force_data=args["force_data"],
                    stage_handler=stage_handler,
                    skip_data=args["skip_data"],
                    quiet=args.get("quiet"),
                    args=args,
                )
                if not ret:
                    problem_modules.append(module_name)
        except Exception as e:
            if module_name not in problem_modules:
                problem_modules.append(module_name)
            quiet_print(e, args=args)
    if problem_modules:
        quiet_print(
            f"following modules were not installed due to problems:", args=args
        )
        for mn in problem_modules:
            quiet_print(f"- {mn}", args=args)
        return False
    else:
        return


@cli_entry
def cli_module_update(args):
    return update(args)


@cli_func
def update(args, __name__="module update"):
    from ..module.local import search_local
    from ..module import get_updatable
    from ..util.util import humanize_bytes
    from ..util.util import quiet_print
    from ..store.db import try_fetch_ov_store_cache
    from types import SimpleNamespace

    try_fetch_ov_store_cache(args=args)
    quiet = args.get("quiet", True)
    modules = args.get("modules", [])
    requested_modules = search_local(*modules)
    update_strategy = args.get("strategy")
    status_table = [["Name", "New Version", "Size"]]
    updates, _, reqs_failed = get_updatable(
        modules=modules, requested_modules=requested_modules, strategy=update_strategy
    )
    if reqs_failed:
        msg = "Newer versions of ({}) are available, but would break dependencies. You may use --strategy=force to force installation.".format(
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
            quiet=args.get("quiet")
        )
        ret = install(m_args)
        if ret is not None:
            return False
    return True


@cli_entry
def cli_module_uninstall(args):
    return uninstall(args)


@cli_func
def uninstall(args, __name__="module uninstall"):
    from ..module.local import search_local
    from ..module import uninstall_module
    from ..util.util import quiet_print

    modules = args.get("modules")
    if not modules:
        from ..exceptions import ArgumentError

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


@cli_entry
def cli_module_installbase(args):
    return installbase(args)


@cli_func
def installbase(args, __name__="module installbase"):
    from ..system import get_system_conf
    from ..system.consts import base_modules_key
    from types import SimpleNamespace
    from ..store.db import try_fetch_ov_store_cache

    try_fetch_ov_store_cache(args=args)
    sys_conf = get_system_conf(conf=args.get("conf"))
    base_modules = sys_conf.get(base_modules_key, [])
    m_args = SimpleNamespace(
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
    ret = install(m_args)
    return ret


def add_local_module_info_to_remote_module_info(remote_info):
    from ..module.local import get_local_module_info

    local_info = get_local_module_info(remote_info.name)
    if local_info:
        remote_info.installed = "yes"
        remote_info.local_code_version = local_info.latest_code_version
        remote_info.local_data_source = local_info.latest_data_source
    else:
        remote_info.installed = ""
        remote_info.local_code_version = ""
        remote_info.local_data_source = ""


def list_modules(args):
    from oyaml import dump
    from ..module.remote import search_remote
    from ..module.local import search_local
    from ..module.local import get_local_module_info
    from ..module.remote import get_remote_module_info_ls
    from ..util.util import humanize_bytes
    from ..module.remote import RemoteModuleLs

    fmt = args.get("fmt", "return")
    nameonly = args.get("nameonly", False)
    available = args.get("available", False)
    types = args.get("types")
    tags = args.get("tags")
    all_toks = []
    all_toks_json = []
    if fmt == "tabular":
        if nameonly:
            all_toks = []
        else:
            if available:
                header = [
                    "Name",
                    "Title",
                    "Type",
                    "Size",
                    "Store version",
                    "Store data source",
                    "Installed",
                    "Local version",
                    "Local data source",
                ]
            else:
                header = [
                    "Name",
                    "Title",
                    "Type",
                    "Size",
                    "Version",
                    "Data source",
                ]
            all_toks = [header]
    elif fmt in ["json", "yaml"]:
        all_toks_json = []
    if available:
        if types:
            l = []
            for mt in types:
                l.extend(search_remote(args.get("pattern"), module_type=mt))
        else:
            l = search_remote(args.get("pattern"))
    else:
        l = search_local(args.get("pattern"))
    if l:
        for module_name in l:
            if available:
                module_info = get_remote_module_info_ls(module_name)
                if module_info:
                    add_local_module_info_to_remote_module_info(module_info)
            else:
                module_info = get_local_module_info(module_name)
            if not module_info:
                continue
            if types and module_info.type not in types:
                continue
            if tags:
                if not module_info.tags:
                    continue
                if not set(types).intersection(module_info.tags):
                    continue
            #if module_info.hidden and not args.get("include_hidden"):
            #    continue
            if isinstance(module_info, RemoteModuleLs):
                size = module_info.size
            else:
                size = module_info.get_size()
            if not args.get("raw_bytes"):
                size = humanize_bytes(size)
            toks = []
            if fmt == "tabular":
                toks = [module_name]
                if not nameonly:
                    if available:
                        toks.extend(
                            [
                                module_info.title,
                                module_info.type,
                                size,
                                module_info.latest_code_version,
                                module_info.latest_data_source,
                                module_info.installed,
                                module_info.local_code_version,
                                module_info.local_data_source,
                            ]
                        )
                    else:
                        toks.extend(
                            [
                                module_info.title,
                                module_info.type,
                                size,
                                module_info.latest_code_version,
                                module_info.latest_data_source,
                            ]
                        )
                all_toks.append(toks)
            elif fmt in ["json", "yaml"]:
                toks = {"name": module_name}
                if not nameonly:
                    if available:
                        toks.update(
                            {
                                "title": module_info.title,
                                "type": module_info.type,
                                "size": size,
                                "version": module_info.latest_code_version,
                                "data_source": module_info.latest_data_source,
                                "installed": module_info.installed,
                                "local_code_version": module_info.local_code_version,
                                "local_data_source": module_info.local_data_source,
                            }
                        )
                    else:
                        toks.update(
                            {
                                "title": module_info.title,
                                "type": module_info.type,
                                "size": size,
                                "version": module_info.latest_code_version,
                                "data_source": module_info.latest_data_source,
                            }
                        )
                all_toks_json.append(toks)
    if fmt == "tabular":
        return all_toks
    elif fmt == "json":
        return all_toks_json
    elif fmt == "yaml":
        if all_toks_json:
            return dump(all_toks_json, default_flow_style=False)
        else:
            return ""
    else:
        return None


def print_tabular_lines(l, args=None):
    from ..util.util import quiet_print

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


class InstallProgressStdout(InstallProgressHandler):
    def __init__(self, module_name, module_version, quiet=True):
        super().__init__(module_name, module_version)
        self.quiet = quiet

    def stage_start(self, stage):
        from ..util.util import quiet_print

        self.cur_stage = stage
        quiet_print(self._stage_msg(stage), args={"quiet": self.quiet})

    def stage_progress(self, __cur_chunk__, __total_chunks__, cur_size, total_size):
        from ..util.util import humanize_bytes
        from ..util.util import quiet_print
        from ..util.util import get_current_time_str

        # perc = cur_size / total_size * 100
        # trailing spaces needed to avoid leftover characters on resize
        out = f"\033[F\033[K[{get_current_time_str()}] Downloading {humanize_bytes(cur_size)} / {humanize_bytes(total_size)}"
        quiet_print(out, args={"quiet": self.quiet})


def add_parser_fn_module_pack(subparsers):
    # pack
    parser_cli_module_pack = subparsers.add_parser(
        "pack", help="pack a module to register at OakVar store"
    )
    parser_cli_module_pack.add_argument(
        dest="module",
        default=None,
        help="Name of or path to the module to pack",
    )
    parser_cli_module_pack.add_argument(
        "-d",
        "--outdir",
        default=".",
        help="Directory to make code and data zip files in",
    )
    parser_cli_module_pack.add_argument(
        "--code-only",
        action="store_true",
        help="pack code only",
    )
    parser_cli_module_pack.add_argument(
        "--split",
        type=int,
        default=None,
        nargs="*",
        help="split pack files into chunks of the given size",
    )
    parser_cli_module_pack.add_argument(
        "--quiet", action="store_true", default=None, help="run quietly"
    )
    parser_cli_module_pack.set_defaults(func=cli_module_pack)
    parser_cli_module_pack.r_return = "A boolean. A boolean. TRUE if successful, FALSE if not"  # type: ignore
    parser_cli_module_pack.r_examples = [  # type: ignore
        '# Pack a module "mymodule" into one zip file for its code and another zip file for its data.',
        '#roakvar::store.pack(module="mymodule")',
    ]


def add_parser_ov_module_installbase(subparsers):
    parser_ov_module_installbase = subparsers.add_parser(
        "installbase",
        help="installs base modules.",
        description="installs base modules.",
    )
    parser_ov_module_installbase.add_argument(
        "-f",
        "--force",
        default=None,
        help="Overwrite existing modules",
    )
    parser_ov_module_installbase.add_argument(
        "-d",
        "--force-data",
        action="store_true",
        help="Download data even if latest data is already installed",
    )
    parser_ov_module_installbase.add_argument(
        "--md", default=None, help="Specify the root directory of OakVar modules"
    )
    parser_ov_module_installbase.add_argument(
        "--quiet", action="store_true", default=None, help="suppress stdout output"
    )
    parser_ov_module_installbase.set_defaults(func=cli_module_installbase)
    parser_ov_module_installbase.r_return = "A boolean. TRUE if successful, FALSE if not"  # type: ignore
    parser_ov_module_installbase.r_examples = [  # type: ignore
        "# Install OakVar system modules",
        "#roakvar::module.installbase()",
    ]


def add_parser_ov_module_install(subparsers):
    parser_ov_module_install = subparsers.add_parser(
        "install",
        help="installs OakVar modules.",
        description="Installs OakVar modules.",
    )
    parser_ov_module_install.add_argument(
        "modules", nargs="+", help="Modules to install. May be regular expressions."
    )
    parser_ov_module_install.add_argument(
        "-f",
        "--force",
        dest="overwrite",
        action="store_true",
        help="Install module even if latest version is already installed",
    )
    parser_ov_module_install.add_argument(
        "--overwrite",
        action="store_true",
        help="Install module even if latest version is already installed",
    )
    parser_ov_module_install.add_argument(
        "-d",
        "--force-data",
        action="store_true",
        help="Download data even if latest data is already installed",
    )
    parser_ov_module_install.add_argument(
        "-y", "--yes", action="store_true", help="Proceed without prompt"
    )
    parser_ov_module_install.add_argument(
        "--skip-dependencies", action="store_true", help="Skip installing dependencies"
    )
    parser_ov_module_install.add_argument(
        "-p", "--private", action="store_true", help="Install a private module"
    )
    parser_ov_module_install.add_argument(
        "--skip-data", action="store_true", help="Skip installing data"
    )
    parser_ov_module_install.add_argument(
        "--md", default=None, help="Specify the root directory of OakVar modules"
    )
    parser_ov_module_install.add_argument(
        "--to", default="return", help="'stdout' to print. 'return' to return"
    )
    parser_ov_module_install.add_argument(
        "--quiet", action="store_true", default=None, help="suppress stdout output"
    )
    parser_ov_module_install.add_argument(
        "--clean", action="store_true", default=False, help="removes temporary installation directory",
    )
    parser_ov_module_install.set_defaults(func=cli_module_install)
    parser_ov_module_install.r_return = "A boolean. TRUE if successful, FALSE if not"  # type: ignore
    parser_ov_module_install.r_examples = [  # type: ignore
        "# Install the ClinVar module without confirmation",
        '#roakvar::module.install(modules="clinvar", force=True)',
    ]


def add_parser_ov_module(subparsers):
    parser_ov_module = subparsers.add_parser(
        "module",
        description="Manages OakVar modules",
        help="Manages OakVar modules",
    )
    subparsers = parser_ov_module.add_subparsers(title="Commands", dest="command")

    # installbase
    add_parser_ov_module_installbase(subparsers)
    # install
    add_parser_ov_module_install(subparsers)
    # pack
    add_parser_fn_module_pack(subparsers)
    # update
    parser_ov_module_update = subparsers.add_parser(
        "update",
        help="updates modules.",
        description="updates modules.",
    )
    parser_ov_module_update.add_argument(
        "modules", nargs="*", help="Modules to update."
    )
    parser_ov_module_update.add_argument(
        "-y", action="store_true", help="Proceed without prompt"
    )
    parser_ov_module_update.add_argument(
        "--strategy",
        help='Dependency resolution strategy. "consensus" will attempt to resolve dependencies. "force" will install the highest available version. "skip" will skip modules with constraints.',
        default="consensus",
        type=str,
        choices=("consensus", "force", "skip"),
    )
    parser_ov_module_update.add_argument(
        "--md", default=None, help="Specify the root directory of OakVar modules"
    )
    parser_ov_module_update.add_argument(
        "--quiet", action="store_true", default=None, help="suppress stodout output"
    )
    parser_ov_module_update.set_defaults(func=cli_module_update)
    parser_ov_module_update.r_return = "A boolean. TRUE if successful, FALSE if not"  # type: ignore
    parser_ov_module_update.r_examples = [  # type: ignore
        "# Update the ClinVar module without confirmation",
        '#roakvar::module.update(modules="clinvar", force=True)',
    ]

    # uninstall
    parser_ov_module_uninstall = subparsers.add_parser(
        "uninstall", help="uninstalls modules."
    )
    parser_ov_module_uninstall.add_argument(
        "modules", nargs="+", help="Modules to uninstall"
    )
    parser_ov_module_uninstall.add_argument(
        "-y", "--yes", action="store_true", help="Proceed without prompt"
    )
    parser_ov_module_uninstall.add_argument(
        "--md", default=None, help="Specify the root directory of OakVar modules"
    )
    parser_ov_module_uninstall.add_argument(
        "--quiet", action="store_true", default=None, help="run quietly"
    )
    parser_ov_module_uninstall.set_defaults(func=cli_module_uninstall)
    parser_ov_module_uninstall.r_return = "A boolean. TRUE if successful, FALSE if not"  # type: ignore
    parser_ov_module_uninstall.r_examples = [  # type: ignore
        "# Uninstall the ClinVar module without confirmation",
        '#roakvar::module.uninstall(modules="clinvar", force=True)',
    ]

    # info
    parser_ov_module_info = subparsers.add_parser(
        "info",
        epilog="returns information of the queried module",
        help="shows module information.",
    )
    parser_ov_module_info.add_argument("module", help="Module to get info about")
    parser_ov_module_info.add_argument(
        "-l", "--local", dest="local", help="Include local info", action="store_true"
    )
    parser_ov_module_info.add_argument(
        "--md", default=None, help="Specify the root directory of OakVar modules"
    )
    parser_ov_module_info.add_argument(
        "--fmt", default="json", help="format of module information data. json or yaml"
    )
    parser_ov_module_info.add_argument(
        "--to", default="return", help='"stdout" to stdout / "return" to return'
    )
    parser_ov_module_info.add_argument(
        "--quiet", action="store_true", default=None, help="run quietly"
    )
    parser_ov_module_info.set_defaults(func=cli_module_info)
    parser_ov_module_info.r_return = "A named list. Information of the queried module"  # type: ignore
    parser_ov_module_info.r_examples = [  # type: ignore
        "# Get the information of the ClinVar module",
        '#roakvar::module.info(module="clinvar")',
    ]

    # ls
    parser_ov_module_ls = subparsers.add_parser(
        "ls",
        help="lists modules.",
        description="lists modules.",
    )
    parser_ov_module_ls.add_argument(
        "pattern", nargs="?", default=r".*", help="Regular expression for module names"
    )
    parser_ov_module_ls.add_argument(
        "-a",
        "--available",
        action="store_true",
        default=False,
        help="Include available modules",
    )
    parser_ov_module_ls.add_argument(
        "-t",
        "--types",
        nargs="+",
        default=[],
        help="Only list modules of certain types",
    )
    parser_ov_module_ls.add_argument(
        "-i",
        "--include-hidden",
        action="store_true",
        default=False,
        help="Include hidden modules",
    )
    parser_ov_module_ls.add_argument(
        "--tags", nargs="+", default=[], help="Only list modules of given tag(s)"
    )
    parser_ov_module_ls.add_argument(
        "--nameonly", action="store_true", default=False, help="Only list module names"
    )
    parser_ov_module_ls.add_argument(
        "--bytes",
        action="store_true",
        default=False,
        dest="raw_bytes",
        help="Machine readable data sizes",
    )
    parser_ov_module_ls.add_argument(
        "--md", default=None, help="Specify the root directory of OakVar modules"
    )
    parser_ov_module_ls.add_argument(
        "--fmt", default=None, help="Output format. tabular or json"
    )
    parser_ov_module_ls.add_argument(
        "--to", default="return", help="stdout to print / return to return"
    )
    parser_ov_module_ls.add_argument(
        "--quiet", action="store_true", default=None, help="run quietly"
    )
    parser_ov_module_ls.set_defaults(func=cli_module_ls)
    parser_ov_module_ls.r_return = "A named list. List of modules"  # type: ignore
    parser_ov_module_ls.r_examples = [  # type: ignore
        "# Get the list of all installed modules",
        "#roakvar::module.ls()",
        "# Get the list of all available modules",
        "#roakvar::module.ls(available=TRUE)",
        '# Get the list of all available modules of the type "converter"',
        '#roakvar::module.ls(available=TRUE, types="converter")',
    ]
