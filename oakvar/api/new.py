from typing import Optional


def exampleinput(directory: Optional[str] = None):
    from ..lib.util.admin_util import fn_new_exampleinput

    if not directory:
        return
    return fn_new_exampleinput(directory)


def module(name: Optional[str] = None, type: Optional[str] = None):
    from ..lib.util.admin_util import create_new_module
    from ..lib.module.local import get_local_module_info

    if not name or not type:
        return None
    create_new_module(name, type)
    module_info = get_local_module_info(name)
    if module_info is not None:
        return module_info.directory
    else:
        return None
