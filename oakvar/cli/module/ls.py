def list_modules(args):
    from oyaml import dump
    from ...lib.module.remote import search_remote
    from ...lib.module.local import search_local
    from ...lib.module.local import get_local_module_info
    from ...lib.module.remote import get_remote_module_info_ls
    from ...lib.util.util import humanize_bytes
    from ...lib.module.remote import RemoteModuleLs

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
                if not set(tags).intersection(module_info.tags):
                    continue
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
