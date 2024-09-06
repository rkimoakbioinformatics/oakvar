# OakVar
#
# Copyright (c) 2024 Oak Bioinformatics, LLC
#
# All rights reserved.
#
# Do not distribute or use this software without obtaining
# a license from Oak Bioinformatics, LLC.
#
# Do not use this software to develop another software
# which competes with the products by Oak Bioinformatics, LLC,
# without obtaining a license for such use from Oak Bioinformatics, LLC.
#
# For personal use of non-commercial nature, you may use this software
# after registering with `ov store account create`.
#
# For research use of non-commercial nature, you may use this software
# after registering with `ov store account create`.
#
# For use by commercial entities, you must obtain a commercial license
# from Oak Bioinformatics, LLC. Please write to info@oakbioinformatics.com
# to obtain the commercial license.
# ================
# OpenCRAVAT
#
# MIT License
#
# Copyright (c) 2021 KarchinLab
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from typing import Optional
from typing import List


def get_modules_to_install(
    module_names: List[str] = [],
    urls: Optional[str] = None,
    skip_dependencies: bool = False,
    outer=None,
) -> dict:
    from ...lib.util.download import is_url
    from ...lib.util.download import is_zip_path
    from ...lib.module.remote import get_install_deps
    from ...lib.store.db import get_latest_module_code_version
    from ...lib.store.db import module_code_version_is_not_compatible_with_pkg_version
    from ...lib.util.admin_util import oakvar_version
    from ...lib.exceptions import ModuleInstallationError

    if urls:
        if len(module_names) != len(urls):
            raise ModuleInstallationError(
                "same number of arguments should be given to the module_name argument and --url option."
            )
    mn_vs = collect_module_name_and_versions(module_names, outer=outer)
    module_install_data = {}
    for i, data in enumerate(mn_vs):
        module_name = data.get("module_name")
        version = data.get("version")
        url = None
        if urls:
            ty = "url"
            url = urls[i]
        elif is_zip_path(module_name):
            ty = "zip"
        else:
            ty = "store"
        if not url:
            if not version:
                version = get_latest_module_code_version(module_name)
            else:
                pkg_ver = oakvar_version()
                min_pkg_ver = module_code_version_is_not_compatible_with_pkg_version(
                    module_name, version
                )
                if min_pkg_ver:
                    if outer:
                        outer.write(
                            f"{module_name}=={version} is not compatible with current OakVar version ({pkg_ver}). Please upgrade OakVar to at least {min_pkg_ver}."
                        )
                    continue
        module_install_data[module_name] = {"type": ty, "version": version, "url": url}
    # dependency
    deps_install = {}
    if not skip_dependencies:
        for module_name, install_data in module_install_data.items():
            if not is_url(module_name) and not is_zip_path(module_name):
                deps, _ = get_install_deps(
                    module_name=module_name, version=install_data.get("version")
                )
                deps_install.update(deps)
    to_install = module_install_data
    for module_name, version in deps_install.items():
        to_install[module_name] = {"type": "store", "version": version, "url": None}
    return to_install


def collect_module_name_and_versions(modules, outer=None) -> list:
    mn_vs = []
    if isinstance(modules, str):
        modules = [modules]
    for mv in modules:
        try:
            if "==" in mv:
                [module_name, version] = mv.split("==")
            else:
                module_name = mv
                version = None
            mn_vs.append({"module_name": module_name, "version": version})
        except Exception:
            if outer:
                outer.write(f"Wrong module name==version format: {mv}")
    return mn_vs


def show_modules_to_install(to_install, outer):
    if not outer:
        return
    outer.write("The following modules will be installed:")
    for name, data in to_install.items():
        version = data.get("version")
        if version:
            outer.write(f"- {name}=={version}")
        else:
            outer.write(f"- {name}")
