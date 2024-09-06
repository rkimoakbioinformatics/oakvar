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

from typing import Any
from typing import List
from typing import Dict


def list_modules(
    module_names: List[str] = [],
    module_types: List[str] = [],
    tags: List[str] = [],
    search_store: bool = False,
    nameonly: bool = False,
    humanized_size: bool = False,
) -> List[Dict[str, Any]]:
    import re
    from ...lib.module.remote import search_remote
    from ...lib.module.local import search_local
    from ...lib.module.local import get_local_module_info
    from ...lib.module.remote import get_remote_module_info_ls
    from ...lib.util.util import humanize_bytes
    from ...lib.module.remote import RemoteModuleLs

    all_toks_json = []
    if search_store:
        if module_types:
            module_names_to_search = []
            for mt in module_types:
                module_names_to_search.extend(
                    search_remote(*module_names, module_type=mt)
                )
        else:
            module_names_to_search = search_remote(*module_names)
    else:
        module_names_to_search = search_local(*module_names)
    if not module_names_to_search:
        return all_toks_json
    for module_name in module_names_to_search:
        if search_store:
            module_info = get_remote_module_info_ls(module_name)
            if module_info:
                add_local_module_info_to_remote_module_info(module_info)
        else:
            module_info = get_local_module_info(module_name)
        if not module_info:
            continue
        if module_types and module_info.type not in module_types:
            continue
        if tags and module_info.tags:
            if not module_info.tags:
                continue
            matched = False
            for pattern in tags:
                for tag in module_info.tags:
                    if re.match(pattern, tag):
                        matched = True
                        break
                if matched:
                    break
            if not matched:
                continue
        if isinstance(module_info, RemoteModuleLs):
            size = module_info.size
        else:
            size = module_info.get_size()
        if humanized_size:
            size = humanize_bytes(size)
        toks = {"name": module_name}
        if not nameonly:
            if search_store:
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
    return all_toks_json


def add_local_module_info_to_remote_module_info(remote_info):
    from ...lib.module.local import get_local_module_info

    local_info = get_local_module_info(remote_info.name)
    if local_info:
        remote_info.installed = "yes"
        remote_info.local_code_version = local_info.latest_code_version
        remote_info.local_data_source = local_info.latest_data_source
    else:
        remote_info.installed = ""
        remote_info.local_code_version = ""
        remote_info.local_data_source = ""
