# OakVar Dual License
# 
# Copyright (c) 2023 Oak Bioinformatics, LLC
# 
# This program is dual licensed under the Affero GPL-3.0 or later for non-commercial, 
# open source use, and a commercial license, which is available for purchase, 
# for commercial use.
# 
# For commercial use, please contact Oak Bioinformatics, LLC for obtaining a
# commercial license. OakVar commercial license does not impose the Affero GPL
# open-source licensing terms, conditions, and limitations. To obtain a
# commercial-use license of OakVar, please visit our website at
# https://oakbioinformatics.com or contact us at info@oakbioinformatics.com for
# more information.
# 
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
from typing import Any
from typing import List
from typing import Dict


def get_modules_to_install(
    module_names: List[str] = [],
    urls: Optional[str] = None,
    skip_dependencies: bool = False,
    outer=None,
) -> Dict[str, Dict[str, Any]]:
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
    module_install_data: Dict[str, Dict[str, Any]] = {}
    for i, data in enumerate(mn_vs):
        module_name = data.get("module_name")
        if module_name is None:
            continue
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
        module_install_data[module_name] = {
            "type": ty,
            "version": version,
            "url": url,
            "size": data.get("size"),
        }
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


def collect_module_name_and_versions(
    modules: List[str], outer=None
) -> List[Dict[str, Any]]:
    from ...lib.module.remote import get_remote_module_info_ls

    mn_vs: List[Dict[str, Any]] = []
    if isinstance(modules, str):
        modules = [modules]
    for mv in modules:
        try:
            if "==" in mv:
                [module_name, version] = mv.split("==")
            else:
                module_name = mv
                version = None
            info_ls = get_remote_module_info_ls(module_name, version)
            if info_ls is None:
                if outer:
                    outer.write(f"Module does not exist: {module_name}")
                continue
            mn_vs.append(
                {"module_name": module_name, "version": version, "size": info_ls.size}
            )
        except Exception:
            if outer:
                outer.write(f"Wrong module_name==version format: {mv}")
    return mn_vs


def show_modules_to_install(to_install: Dict[str, Dict[str, Any]], outer):
    from ...lib.util.util import humanize_bytes

    if not outer:
        return
    outer.write("The following modules will be installed:")
    for name, data in to_install.items():
        version = data.get("version")
        sz = humanize_bytes(int(data.get("size") or "0"))
        if version:
            outer.write(f"- {name}=={version} (size: {sz} bytes)")
        else:
            outer.write(f"- {name} (size: {sz} bytes)")
