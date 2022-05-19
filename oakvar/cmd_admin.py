#!/usr/bin/env python3
import argparse
from .admin_util import InstallProgressHandler

class InstallProgressStdout(InstallProgressHandler):
    def __init__(self, module_name, module_version):
        super().__init__(module_name, module_version)

    def stage_start(self, stage):
        import sys
        self.cur_stage = stage
        sys.stdout.write(self._stage_msg(stage) + "\n")

    def stage_progress(self, cur_chunk, total_chunks, cur_size, total_size):
        import sys
        from .util import humanize_bytes
        rem_chunks = total_chunks - cur_chunk
        perc = cur_size / total_size * 100
        # trailing spaces needed to avoid leftover characters on resize
        out = (
            "\r[{cur_prog}{rem_prog}] {cur_size} / {total_size} ({perc:.0f}%)  ".format(
                cur_prog="*" * cur_chunk,
                rem_prog=" " * rem_chunks,
                cur_size=humanize_bytes(cur_size),
                total_size=humanize_bytes(total_size),
                perc=perc,
            )
        )
        sys.stdout.write(out)
        if cur_chunk == total_chunks:
            sys.stdout.write("\n")


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


def print_tabular_lines(l, *kwargs):
    for line in yield_tabular_lines(l, *kwargs):
        print(line)


def list_local_modules(
    pattern=r".*",
    types=[],
    include_hidden=False,
    tags=[],
    quiet=False,
    raw_bytes=False,
    fmt="tabular",
    **kwargs,
):
    from oyaml import dump
    from .admin_util import search_local, get_local_module_info
    from .util import humanize_bytes
    if quiet or fmt == "json" or fmt == "yaml":
        all_toks = []
    else:
        header = ["Name", "Title", "Type", "Version", "Data source ver", "Size"]
        all_toks = [header]
    for module_name in search_local(pattern):
        module_info = get_local_module_info(module_name)
        if len(types) > 0 and module_info.type not in types:
            continue
        if len(tags) > 0:
            if module_info.tags is None:
                continue
            if len(set(tags).intersection(module_info.tags)) == 0:
                continue
        if module_info.hidden and not include_hidden:
            continue
        if quiet:
            toks = [module_name]
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
            else:
                toks = [
                    module_name,
                    module_info.title,
                    module_info.type,
                    module_info.version,
                    module_info.datasource,
                ]
            if raw_bytes:
                if fmt in ["json", "yaml"]:
                    toks["size"] = size
                else:
                    toks.append(size)
            else:
                if fmt in ["json", "yaml"]:
                    toks["size"] = humanize_bytes(size)
                else:
                    toks.append(humanize_bytes(size))
        all_toks.append(toks)
    if fmt in ["tabular", "json"]:
        return all_toks
    elif fmt == "yaml":
        return dump(all_toks, default_flow_style=False)


def list_available_modules(**kwargs):
    from oyaml import dump
    from .admin_util import search_remote, get_local_module_info, get_remote_module_info
    from .util import humanize_bytes
    fmt = kwargs["fmt"]
    quiet = kwargs["quiet"]
    if fmt == "tabular":
        if quiet:
            all_toks = []
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
            all_toks = [header]
    elif fmt in ["json", "yaml"]:
        all_toks = []
    for module_name in search_remote(kwargs["pattern"]):
        remote_info = get_remote_module_info(module_name)
        if len(kwargs["types"]) > 0 and remote_info.type not in kwargs["types"]:
            continue
        if len(kwargs["tags"]) > 0:
            if remote_info.tags is None:
                continue
            if len(set(kwargs["tags"]).intersection(remote_info.tags)) == 0:
                continue
        if remote_info.hidden and not kwargs["include_hidden"]:
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
        if kwargs["raw_bytes"]:
            size = remote_info.size
        else:
            size = humanize_bytes(remote_info.size)
        if fmt == "tabular":
            if quiet:
                toks = [module_name]
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
                    size
                ]
        elif fmt in ["json", "yaml"]:
            toks = {"name": module_name,
                    "title": remote_info.title,
                    "type": remote_info.type,
                    "installed": installed,
                    "latest_version": remote_info.latest_version,
                    "datasource": remote_info.datasource,
                    "local_version": local_version,
                    "local_datasource": local_datasource,
                    "size": size}
        all_toks.append(toks)
    if fmt in ["tabular", "json"]:
        return all_toks
    elif fmt == "yaml":
        return dump(all_toks, default_flow_style=False)


def fn_module_ls(*args, **kwargs):
    from .util import get_args
    from inspect import currentframe
    fnname = currentframe().f_code.co_name
    parser = globals()["parser_" + fnname]
    args = get_args(parser, args, kwargs)
    if args["available"]:
        ret = list_available_modules(**args)
        if args["to"] == "stdout":
            if args["fmt"] == "tabular":
                print_tabular_lines(ret)
            else:
                print(ret)
        else:
            return ret
    else:
        ret = list_local_modules(**args)
        if args["to"] == "stdout":
            if args["fmt"] == "tabular":
                print_tabular_lines(ret)
            else:
                print(ret)
        else:
            return ret


def yaml_string(x):
    from oyaml import dump
    from re import sub
    s = dump(x, default_flow_style=False)
    s = sub("!!.*", "", s)
    s = s.strip("\r\n")
    return s


def fn_module_info(args):
    from oyaml import dump
    from .admin_util import get_local_module_info, get_remote_module_info
    from .util import get_dict_from_namespace
    from .constants import custom_modules_dir
    args = get_dict_from_namespace(args)
    ret = {}
    md = args.get("md", None)
    module_name = args.get("module", None)
    if md is not None:
        custom_modules_dir = md
    if module_name is None:
        return ret
    installed = False
    remote_available = False
    up_to_date = False
    local_info = None
    remote_info = None
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
    if remote_available:
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
        # del remote_info.data_sources
        # dump = yaml_string(remote_info)
        # print(dump)
        ret.update(remote_info.data)
        # output columns
        # print('output columns:')
        ret["output_columns"] = []
        conf = get_remote_module_config(module_name)
        if "output_columns" in conf:
            output_columns = conf["output_columns"]
            for col in output_columns:
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
        if args.get("local", None):
            ret.update(local_info)
    else:
        pass
    if installed and remote_available:
        if installed and local_info.version == remote_info.latest_version:
            up_to_date = True
        else:
            up_to_date = False
        ret["latest_installed"] = up_to_date
    if args["to"] == "stdout":
        print(dump(ret))
    else:
        return ret


def fn_config_md(args):
    from .admin_util import set_modules_dir, get_modules_dir
    from .util import get_dict_from_namespace
    args = get_dict_from_namespace(args)
    if args["directory"]:
        set_modules_dir(args["directory"])
    print(get_modules_dir())


def fn_module_install(*args, **kwargs):
    from .admin_util import search_remote, get_local_module_info, get_remote_module_info, module_exists_remote, get_install_deps, install_module
    from .util import get_args
    from .constants import custom_modules_dir
    from distutils.version import LooseVersion
    args = get_args(parser_fn_module_install, args, kwargs)
    if args["md"] is not None:
        custom_modules_dir = args["md"]
    # split module name and version
    module_name_versions = {}
    for mv in args["modules"]:
        try:
            if "==" in mv:
                [module_name, version] = mv.split("==")
            else:
                module_name = mv
                version = None
            module_name_versions[module_name] = version
        except:
            print(f"Wrong module name==version format: {mv}")
    module_names = list(module_name_versions.keys())
    # handles regex in module name.
    for module_name in module_names:
        version = module_name_versions[module_name]
        del module_name_versions[module_name]
        matching_names = search_remote(module_name)
        if len(matching_names) == 0:
            print(f"invalid module name: {module_name}")
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
            if args["private"]:
                print(
                    f"{module_name}: a version should be given for a private module", flush=True)
                continue
            else:
                if local_info is not None:
                    local_ver = local_info.version
                    remote_ver = remote_info.latest_version
                    if not args["force"] and LooseVersion(local_info.version) >= LooseVersion(remote_info.latest_version):
                        print(f"{module_name}: latest version is already installed.", flush=True)
                        continue
                selected_install[module_name] = remote_info.latest_version
        else:
            if not module_exists_remote(module_name, version=version, private=args["private"]):
                print(f"{module_name}=={version} does not exist.", flush=True)
                continue
            else:
                if (
                    not args["force"]
                    and local_info is not None
                    and LooseVersion(local_info.version) == LooseVersion(version)
                ):
                    print(
                        f"{module_name}=={args['version']} is already installed. Use -f/--force to overwrite",
                        flush=True,
                    )
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
        print("No module to install found", flush=True)
    else:
        print("The following modules will be installed:", flush=True)
        for name in sorted(list(to_install.keys())):
            print(f"- {name}=={to_install[name]}", flush=True)
        if not (args["yes"]):
            while True:
                resp = input("Proceed? ([y]/n) > ")
                if resp == "y" or resp == "":
                    break
                if resp == "n":
                    return False
                else:
                    continue
        for module_name, module_version in sorted(to_install.items()):
            stage_handler = InstallProgressStdout(module_name, module_version)
            install_module(
                module_name,
                version=module_version,
                force_data=args["force_data"],
                stage_handler=stage_handler,
                force=args["force"],
                skip_data=args["skip_data"],
            )


def fn_module_update(args):
    from .admin_util import search_local, get_updatable
    from .util import get_dict_from_namespace, humanize_bytes
    from .constants import custom_modules_dir
    args = get_dict_from_namespace(args)
    if args["md"] is not None:
        custom_modules_dir = args["md"]
    if len(args["modules"]) > 0:
        requested_modules = search_local(*args["modules"])
    else:
        requested_modules = []
    update_strategy = args["strategy"]
    status_table = [["Name", "New Version", "Size"]]
    updates, _, reqs_failed = get_updatable(
        requested_modules, strategy=update_strategy
    )
    if reqs_failed:
        print(
            "Newer versions of ({}) are available, but would break dependencies. You may use --strategy=force to force installation.".format(
                ", ".join(reqs_failed.keys())
            )
        )
    if not updates:
        print("No module updates are needed")
        exit()
    for mname, update_info in updates.items():
        version = update_info.version
        size = update_info.size
        status_table.append([mname, version, humanize_bytes(size)])
    print_tabular_lines(status_table)
    if not args["y"]:
        user_cont = input("Update the above modules? (y/n) > ")
        if user_cont.lower() not in ["y", "yes"]:
            exit()
    for mname, update_info in updates.items():
        args["modules"] = [mname]
        args["force_data"] = False
        args["version"] = update_info.version
        args["yes"] = True
        args["private"] = False
        args["skip_dependencies"] = False
        args["force"] = False
        args["skip_data"] = False
        fn_module_install(args)


def fn_module_uninstall(args):
    from .admin_util import search_local, uninstall_module
    from .util import get_dict_from_namespace
    from .constants import custom_modules_dir
    args = get_dict_from_namespace(args)
    if args["md"] is not None:
        custom_modules_dir = args["md"]
    matching_names = search_local(*args["modules"])
    if len(matching_names) > 0:
        print("Uninstalling: {:}".format(", ".join(matching_names)))
        if not (args["yes"]):
            while True:
                resp = input("Proceed? (y/n) > ")
                if resp == "y":
                    break
                elif resp == "n":
                    exit()
                else:
                    print("Response '{:}' not one of (y/n).".format(resp))
        for module_name in matching_names:
            uninstall_module(module_name)
            print("Uninstalled %s" % module_name)
    else:
        print("No modules to uninstall found")


def fn_store_publish(args):
    from .admin_util import get_system_conf, publish_module
    from .util import get_dict_from_namespace
    from .constants import custom_modules_dir
    from getpass import getpass
    args = get_dict_from_namespace(args)
    if args["md"] is not None:
        custom_modules_dir = args["md"]
    sys_conf = get_system_conf()
    if args["user"] is None:
        if "publish_username" in sys_conf:
            args["user"] = sys_conf["publish_username"]
        else:
            args["user"] = input("Username: ")
    if args["password"] is None:
        if "publish_password" in sys_conf:
            args["password"] = sys_conf["publish_password"]
        else:
            args["password"] = getpass()
    publish_module(
        args["module"],
        args["user"],
        args["password"],
        overwrite=args["overwrite"],
        include_data=args["data"],
    )


def fn_module_installbase(args):
    from .admin_util import get_system_conf
    from .util import get_dict_from_namespace
    from .constants import base_modules_key
    from types import SimpleNamespace
    args = get_dict_from_namespace(args)
    sys_conf = get_system_conf()
    base_modules = sys_conf.get(base_modules_key, [])
    args = SimpleNamespace(
        modules=base_modules,
        force_data=args["force_data"],
        version=None,
        yes=True,
        private=False,
        skip_dependencies=False,
        force=args["force"],
        skip_data=False,
        md=args["md"],
    )
    fn_module_install(args)


def fn_store_newaccount(args):
    from .admin_util import create_account
    from .util import get_dict_from_namespace
    args = get_dict_from_namespace(args)
    ret = create_account(args["username"], args["password"])
    return ret


def fn_store_changepassword(args):
    from .admin_util import change_password
    from .util import get_dict_from_namespace
    args = get_dict_from_namespace(args)
    ret = change_password(args["username"], args["current_password"], args["new_password"])
    return ret


def fn_store_resetpassword(args):
    from .admin_util import send_reset_email
    from .util import get_dict_from_namespace
    args = get_dict_from_namespace(args)
    ret = send_reset_email(args["username"])
    return ret


def fn_store_verifyemail(args):
    from .admin_util import send_verify_email
    from .util import get_dict_from_namespace
    args = get_dict_from_namespace(args)
    ret = send_verify_email(args["username"])
    return ret


def fn_store_checklogin(args):
    from .admin_util import check_login
    from .util import get_dict_from_namespace
    args = get_dict_from_namespace(args)
    ret = check_login(args.username, args["password"])
    return ret


def fn_new_exampleinput(args):
    from .admin_util import fn_new_exampleinput
    from .util import get_dict_from_namespace
    args = get_dict_from_namespace(args)
    fn_new_exampleinput(args["directory"])


def fn_new_annotator(args):
    from .admin_util import new_annotator, get_local_module_info
    from .util import get_dict_from_namespace
    from .constants import custom_modules_dir
    args = get_dict_from_namespace(args)
    if args["md"] is not None:
        custom_modules_dir = args["md"]
    new_annotator(args["annotator_name"])
    module_info = get_local_module_info(args["annotator_name"])
    print(f"created {module_info.directory}")
    return module_info.directory


def fn_feedback(args):
    from .admin_util import report_issue
    report_issue()


def fn_config_system(args):
    from .admin_util import show_system_conf
    from .util import get_dict_from_namespace
    args = get_dict_from_namespace(args)
    ret = show_system_conf(**args)
    return ret


def fn_config_oakvar(args):
    from .admin_util import show_oakvar_conf
    from .util import get_dict_from_namespace
    args = get_dict_from_namespace(args)
    ret = show_oakvar_conf(**args)
    return ret


def fn_version(args):
    from .admin_util import oakvar_version
    from .util import get_dict_from_namespace
    args = get_dict_from_namespace(args)
    ret = oakvar_version()
    if args["to"] == "stdout":
        print(ret)
    else:
        return ret


###########################################################################
# PARSERS START HERE
###########################################################################
parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
subparsers = parser.add_subparsers(title="Commands")

# md
parser_fn_config_md = subparsers.add_parser(
    "md",
    help="displays or changes OakVar modules directory.",
    description="displays or changes OakVar modules directory.",
    formatter_class=argparse.RawDescriptionHelpFormatter,
)
parser_fn_config_md.add_argument("directory", nargs="?", help="sets modules directory.")
parser_fn_config_md.set_defaults(func=fn_config_md)

# install-base
parser_fn_module_installbase = subparsers.add_parser(
    "installbase", help="installs base modules.", description="installs base modules."
)
parser_fn_module_installbase.add_argument(
    "-f",
    "--force",
    action="store_true",
    help="Overwrite existing modules",
)
parser_fn_module_installbase.add_argument(
    "-d",
    "--force-data",
    action="store_true",
    help="Download data even if latest data is already installed",
)
parser_fn_module_installbase.add_argument(
    "--md", default=None, help="Specify the root directory of OakVar modules"
)
parser_fn_module_installbase.set_defaults(func=fn_module_installbase)

# install
parser_fn_module_install = subparsers.add_parser(
    "install", help="installs OakVar modules.", description="Installs OakVar modules."
)
parser_fn_module_install.add_argument(
    "modules", nargs="+", help="Modules to install. May be regular expressions."
)
parser_fn_module_install.add_argument(
    "-f",
    "--force",
    action="store_true",
    help="Install module even if latest version is already installed",
)
parser_fn_module_install.add_argument(
    "-d",
    "--force-data",
    action="store_true",
    help="Download data even if latest data is already installed",
)
parser_fn_module_install.add_argument(
    "-y", "--yes", action="store_true", help="Proceed without prompt"
)
parser_fn_module_install.add_argument(
    "--skip-dependencies", action="store_true", help="Skip installing dependencies"
)
parser_fn_module_install.add_argument(
    "-p", "--private", action="store_true", help="Install a private module"
)
parser_fn_module_install.add_argument(
    "--skip-data", action="store_true", help="Skip installing data"
)
parser_fn_module_install.add_argument(
    "--md", default=None, help="Specify the root directory of OakVar modules"
)
parser_fn_module_install.set_defaults(func=fn_module_install)

# update
parser_fn_module_update = subparsers.add_parser(
    "update",
    help="updates modules.",
    description="updates modules.",
    formatter_class=argparse.RawDescriptionHelpFormatter,
)
parser_fn_module_update.add_argument("modules", nargs="*", help="Modules to update.")
parser_fn_module_update.add_argument("-y", action="store_true", help="Proceed without prompt")
parser_fn_module_update.add_argument(
    "--strategy",
    help='Dependency resolution strategy. "consensus" will attempt to resolve dependencies. "force" will install the highest available version. "skip" will skip modules with constraints.',
    default="consensus",
    type=str,
    choices=("consensus", "force", "skip"),
)
parser_fn_module_update.add_argument(
    "--md", default=None, help="Specify the root directory of OakVar modules"
)
parser_fn_module_update.set_defaults(func=fn_module_update)

# uninstall
parser_fn_module_uninstall = subparsers.add_parser("uninstall", help="uninstalls modules.")
parser_fn_module_uninstall.add_argument("modules", nargs="+", help="Modules to uninstall")
parser_fn_module_uninstall.add_argument(
    "-y", "--yes", action="store_true", help="Proceed without prompt"
)
parser_fn_module_uninstall.add_argument(
    "--md", default=None, help="Specify the root directory of OakVar modules"
)
parser_fn_module_uninstall.set_defaults(func=fn_module_uninstall)

# info
parser_fn_module_info = subparsers.add_parser("info", help="shows module information.")
parser_fn_module_info.add_argument("module", help="Module to get info about")
parser_fn_module_info.add_argument(
    "-l", "--local", dest="local", help="Include local info", action="store_true"
)
parser_fn_module_info.add_argument(
    "--md", default=None, help="Specify the root directory of OakVar modules"
)
parser_fn_module_info.add_argument("--to", default="stdout", help="\"print\" to stdout / \"return\" to return")
parser_fn_module_info.set_defaults(func=fn_module_info)

# ls
parser_fn_module_ls = subparsers.add_parser(
    "ls",
    help="lists modules.",
    description="lists modules.",
    formatter_class=argparse.RawDescriptionHelpFormatter,
)
parser_fn_module_ls.add_argument(
    "pattern", nargs="?", default=r".*", help="Regular expression for module names"
)
parser_fn_module_ls.add_argument(
    "-a", "--available", action="store_true", help="Include available modules"
)
parser_fn_module_ls.add_argument(
    "-t", "--types", nargs="+", default=[], help="Only list modules of certain types"
)
parser_fn_module_ls.add_argument(
    "-i", "--include-hidden", action="store_true", help="Include hidden modules"
)
parser_fn_module_ls.add_argument(
    "--tags", nargs="+", default=[], help="Only list modules of given tag(s)"
)
parser_fn_module_ls.add_argument(
    "-q", "--quiet", action="store_true", help="Only list module names"
)
parser_fn_module_ls.add_argument(
    "--bytes", action="store_true", dest="raw_bytes", help="Machine readable data sizes"
)
parser_fn_module_ls.add_argument(
    "--md", default=None, help="Specify the root directory of OakVar modules"
)
parser_fn_module_ls.add_argument(
    "--fmt", default="tabular", help="Output format. tabular or json"
)
parser_fn_module_ls.add_argument("--to", default="stdout", help="stdout to print / return to return")
parser_fn_module_ls.set_defaults(func=fn_module_ls)

# publish
parser_fn_store_publish = subparsers.add_parser("publish", help="publishes a module.")
parser_fn_store_publish.add_argument("module", help="module to publish")
data_group = parser_fn_store_publish.add_mutually_exclusive_group(required=True)
data_group.add_argument(
    "-d",
    "--data",
    action="store_true",
    default=False,
    help="publishes module with data.",
)
data_group.add_argument(
    "-c", "--code", action="store_true", help="publishes module without data."
)
parser_fn_store_publish.add_argument(
    "-u", "--user", default=None, help="user to publish as. Typically your email."
)
parser_fn_store_publish.add_argument(
    "-p",
    "--password",
    default=None,
    help="password for the user. Enter at prompt if missing.",
)
parser_fn_store_publish.add_argument(
    "--force-yes",
    default=False,
    action="store_true",
    help="overrides yes to overwrite question",
)
parser_fn_store_publish.add_argument(
    "--overwrite",
    default=False,
    action="store_true",
    help="overwrites a published module/version",
)
parser_fn_store_publish.add_argument(
    "--md", default=None, help="Specify the root directory of OakVar modules"
)
parser_fn_store_publish.set_defaults(func=fn_store_publish)

# create-account
parser_fn_store_newaccount = subparsers.add_parser(
    "createaccount", help="creates a OakVar store developer account."
)
parser_fn_store_newaccount.add_argument("username", help="use your email as your username.")
parser_fn_store_newaccount.add_argument("password", help="this is your password.")
parser_fn_store_newaccount.set_defaults(func=fn_store_newaccount)

# change-password
parser_fn_store_changepassword = subparsers.add_parser(
    "changepassword", help="changes OakVar store account password."
)
parser_fn_store_changepassword.add_argument("username", help="username")
parser_fn_store_changepassword.add_argument("current_password", help="current password")
parser_fn_store_changepassword.add_argument("new_password", help="new password")
parser_fn_store_changepassword.set_defaults(func=fn_store_changepassword)

# reset-password
parser_fn_store_resetpassword = subparsers.add_parser(
    "resetpassword", help="resets OakVar store account password."
)
parser_fn_store_resetpassword.add_argument("username", help="username")
parser_fn_store_resetpassword.set_defaults(func=fn_store_resetpassword)

# verify-email
parser_fn_store_verifyemail = subparsers.add_parser(
    "verifyemail", help="sends a verification email."
)
parser_fn_store_verifyemail.add_argument("username", help="username")
parser_fn_store_verifyemail.set_defaults(func=fn_store_verifyemail)

# check-login
parser_fn_store_checklogin = subparsers.add_parser(
    "checklogin", help="checks username and password."
)
parser_fn_store_checklogin.add_argument("username", help="username")
parser_fn_store_checklogin.add_argument("password", help="password")
parser_fn_store_checklogin.set_defaults(func=fn_store_checklogin)

# test input file
parser_fn_new_exampleinput = subparsers.add_parser(
    "new-exampleinput", help="makes a file with example input variants."
)
parser_fn_new_exampleinput.add_argument(
    "-d",
    dest="directory",
    default=".",
    help="Directory to make the example input file in",
)
parser_fn_new_exampleinput.set_defaults(func=fn_new_exampleinput)

# new-annotator
parser_fn_new_annotator = subparsers.add_parser(
    "new-annotator", help="creates a new annotator"
)
parser_fn_new_annotator.add_argument("-n", dest="annotator_name", default="annotator", help="Annotator name")
parser_fn_new_annotator.add_argument(
    "--md", default=None, help="Specify the root directory of OakVar modules"
)
parser_fn_new_annotator.set_defaults(func=fn_new_annotator)

# opens issue report
parser_fn_feedback = subparsers.add_parser(
    "report-issue", help="opens a browser window to report issues"
)
parser_fn_feedback.set_defaults(func=fn_feedback)

# shows system conf content.
parser_fn_config_system = subparsers.add_parser(
    "show-system-conf", help="shows system configuration."
)
parser_fn_config_system.add_argument("--fmt", default="yaml", help="Format of output. json or yaml.")
parser_fn_config_system.add_argument("--to", default="stdout", help="\"stdout\" to print. \"return\" to return")
parser_fn_config_system.set_defaults(func=fn_config_system)

# shows oakvar conf content.
parser_fn_config_oakvar = subparsers.add_parser(
    "ov config system", help="shows oakvar configuration."
)
parser_fn_config_oakvar.add_argument("--fmt", default="yaml", help="Format of output. json or yaml.")
parser_fn_config_oakvar.add_argument("--to", default="stdout", help="\"stdout\" to print. \"return\" to return")
parser_fn_config_oakvar.set_defaults(func=fn_config_oakvar)

# shows version
parser_fn_version = subparsers.add_parser("version", help="shows oakvar version")
parser_fn_version.add_argument("--to", default="stdout", help="\"stdout\" to print. \"return\" to return")
parser_fn_version.set_defaults(func=fn_version)


def main():
    import sys
    # Print usage if no args
    if len(sys.argv) == 1:
        sys.argv.append("-h")
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
