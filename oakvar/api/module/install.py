from typing import List

def get_modules_to_install(module_names: List[str]=[], skip_dependencies: bool=False, outer=None) -> dict:
    from ...lib.util.download import is_url
    from ...lib.util.download import is_zip_path
    from ...lib.module.remote import get_install_deps
    from ...lib.store.db import get_latest_module_code_version
    from ...lib.store.db import module_code_version_is_not_compatible_with_pkg_version
    from ...lib.util.admin_util import oakvar_version

    mn_vs = collect_module_name_and_versions(module_names, outer=outer)
    module_versions = {}
    for module_name, version in mn_vs.items():
        if not version:
            version = get_latest_module_code_version(module_name)
        else:
            pkg_ver = oakvar_version()
            min_pkg_ver = module_code_version_is_not_compatible_with_pkg_version(module_name, version)
            if min_pkg_ver:
                if outer:
                    outer.write(f"{module_name}=={version} is not compatible with current OakVar version ({pkg_ver}). Please upgrade OakVar to at least {min_pkg_ver}.")
                continue
        module_versions[module_name] = version
    # dependency
    deps_install = {}
    if not skip_dependencies:
        for module_name, version in module_versions.items():
            if not is_url(module_name) and not is_zip_path(module_name):
                deps, _ = get_install_deps(module_name=module_name, version=version)
                deps_install.update(deps)
    to_install = module_versions
    to_install.update(deps_install)
    return to_install


def collect_module_name_and_versions(modules, outer=None):
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
            if outer:
                outer.write(f"Wrong module name==version format: {mv}")
    return mn_vs


def show_modules_to_install(to_install, outer):
    if not outer:
        return
    outer.write("The following modules will be installed:")
    for name, version in to_install.items():
        if version:
            outer.write(f"- {name}=={to_install[name]}")
        else:
            outer.write(f"- {name}")



