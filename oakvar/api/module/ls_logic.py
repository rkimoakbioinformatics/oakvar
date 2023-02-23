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
            l = []
            for mt in module_types:
                l.extend(search_remote(*module_names, module_type=mt))
        else:
            l = search_remote(*module_names)
    else:
        l = search_local(*module_names)
    if not l:
        return all_toks_json
    for module_name in l:
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
