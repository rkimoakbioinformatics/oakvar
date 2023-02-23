from ...lib.module import InstallProgressHandler
from .. import cli_entry
from .. import cli_func


@cli_entry
def cli_module_pack(args):
    return pack(args)


@cli_func
def pack(args: dict, __name__="module pack"):
    from ...api.module import pack

    module_name = args.get("module_name", "")
    if "module_name" in args:
        del args["module_name"]
    pack(module_name, **args)
    print(f"To register the packed module, use `ov store register`.")


@cli_entry
def cli_module_ls(args):
    if not args.fmt:
        args.fmt = "tabular"
    return ls(args)


@cli_func
def ls(args, __name__="module ls"):
    from ...api.module import ls

    ls(**args)


@cli_entry
def cli_module_info(args):
    args.fmt = "yaml"
    return info(args)


@cli_func
def info(args, __name__="module info"):
    from ...api.module import info

    module_name = args.get("module_name")
    if not module_name:
        return None
    del args["module_name"]
    ret = info(module_name, **args)
    if not ret:
        print(f"Module not found")


@cli_entry
def cli_module_install(args):
    return install(args)


@cli_func
def install(args, __name__="module install"):
    from ...api.module import install as install_api
    from .install_defs import InstallProgressStdout

    stage_handler = InstallProgressStdout(outer=args.get("outer"))
    ret = install_api(stage_handler=stage_handler, **args)
    return ret


@cli_entry
def cli_module_update(args):
    return update(args)


@cli_func
def update(args, __name__="module update"):
    from ...api.module import update

    ret = update(**args)
    return ret


@cli_entry
def cli_module_uninstall(args):
    return uninstall(args)


@cli_func
def uninstall(args, __name__="module uninstall"):
    from ...api.module import uninstall

    args["module_names"] = args.get("module_name")
    del args["module_name"]
    return uninstall(**args)


@cli_entry
def cli_module_installbase(args):
    return installbase(args)


@cli_func
def installbase(args, no_fetch=False, __name__="module installbase"):
    from ...api.module import installbase

    ret = installbase(**args, no_fetch=no_fetch)
    return ret


class InstallProgressStdout(InstallProgressHandler):
    def __init__(self, module_name=None, module_version=None, quiet=True):
        super().__init__(module_name=module_name, module_version=module_version)
        self.quiet = quiet
        self.system_worker_state = None

    def stage_start(self, stage):
        self.cur_stage = stage
        if not self.quiet and self.outer:
            self.outer.write(self._stage_msg(stage))


def add_parser_fn_module_pack(subparsers):
    from ...lib.store.consts import MODULE_PACK_SPLIT_FILE_SIZE

    # pack
    parser_cli_module_pack = subparsers.add_parser(
        "pack", help="pack a module to register at OakVar store"
    )
    parser_cli_module_pack.add_argument(
        dest="module_name",
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
        action="store_true",
        help=f"split pack files into chunks of {MODULE_PACK_SPLIT_FILE_SIZE} bytes",
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
        "module_names",
        nargs="*",
        default=[],
        help="Modules to install. May be regular expressions.",
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
        default=False,
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
        "--skip-data", action="store_true", help="Skip installing data"
    )
    parser_ov_module_install.add_argument(
        "--no-fetch", action="store_true", help="Skip fetching the latest store"
    )
    parser_ov_module_install.add_argument(
        "--url", dest="urls", nargs="+", default=[], help="Install from URLs"
    )
    parser_ov_module_install.add_argument(
        "--quiet", action="store_true", default=None, help="suppress stdout output"
    )
    parser_ov_module_install.add_argument(
        "--clean",
        action="store_true",
        default=False,
        help="removes temporary installation directory",
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
    subparsers = parser_ov_module.add_subparsers()

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
        "module_name_patterns", nargs="*", help="Modules to update."
    )
    parser_ov_module_update.add_argument(
        "-y", "--yes", action="store_true", help="Proceed without prompt"
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
        "module_name",
        nargs="+",
        default=[],
        help="Modules to uninstall",
    )
    parser_ov_module_uninstall.add_argument(
        "-y", "--yes", action="store_true", help="Proceed without prompt"
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
    parser_ov_module_info.add_argument("module_name", help="Module to get info about")
    parser_ov_module_info.add_argument(
        "-l",
        "--local",
        dest="local",
        default=False,
        help="Include local info",
        action="store_true",
    )
    parser_ov_module_info.add_argument(
        "--fmt", default="json", help="format of module information data. json or yaml"
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
        "module_names",
        nargs="*",
        default=[".*"],
        help="Regular expression for module names",
    )
    parser_ov_module_ls.add_argument(
        "-a",
        "--search-store",
        action="store_true",
        default=False,
        help="Include available modules",
    )
    parser_ov_module_ls.add_argument(
        "-t",
        "--module-types",
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
        "--humanized-size",
        action="store_true",
        default=False,
        dest="raw_bytes",
        help="Machine readable data sizes",
    )
    parser_ov_module_ls.add_argument(
        "--fmt", default=None, help="Output format. tabular or json"
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
