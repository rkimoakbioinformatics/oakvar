def get_modules_to_install(args={}) -> dict:
    from ...util.download import is_url
    from ...util.download import is_zip_path
    from ...util.util import quiet_print
    from ...module.remote import get_install_deps
    from ...store.db import get_latest_module_code_version
    from ...store.db import module_code_version_is_not_compatible_with_pkg_version
    from ...util.admin_util import oakvar_version

    mn_vs = collect_module_name_and_versions(args.get("modules", []), args=args)
    module_versions = {}
    for module_name, version in mn_vs.items():
        if not version:
            version = get_latest_module_code_version(module_name)
        else:
            pkg_ver = oakvar_version()
            min_pkg_ver = module_code_version_is_not_compatible_with_pkg_version(module_name, version)
            if min_pkg_ver:
                quiet_print(f"{module_name}=={version} is not compatible with current OakVar version ({pkg_ver}). Please upgrade OakVar to at least {min_pkg_ver}.", args=args)
                continue
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


def collect_module_name_and_versions(modules, args=None):
    from ...util.util import quiet_print

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


def show_modules_to_install(to_install, args={}):
    from ...util.util import quiet_print

    quiet_print("The following modules will be installed:", args=args)
    for name, version in to_install.items():
        if version:
            quiet_print(f"- {name}=={to_install[name]}", args=args)
        else:
            quiet_print(f"- {name}", args=args)



