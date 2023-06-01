from typing import Optional
from pathlib import Path


def exampleinput(directory: Optional[str] = ".", outer=None) -> Optional[Path]:
    """exampleinput.

    Args:
        directory (Optional[str]): Directory to create the example input file in
        outer:

    Returns:
        `None` if the given directory does not exist. Path to the created example input file if successful.
    """
    from ..lib.util.admin_util import fn_new_exampleinput

    if not directory:
        return None
    ret = fn_new_exampleinput(directory)
    if outer:
        outer.write(ret)
    return ret


def module(module_name: str, module_type: str, outer=None) -> Optional[Path]:
    """module.

    Args:
        module_name (str): Module name
        module_type (str): Module type

    Returns:
        `None` if not successful. Directory of the created module if successful.
    """
    from ..lib.util.admin_util import create_new_module
    from ..lib.module.local import get_local_module_info
    from ..lib.exceptions import ArgumentError

    if not module_name:
        e = ArgumentError("module_name should not be empty.")
        e.traceback = False
        raise e
    if not module_type:
        e = ArgumentError("module_type should not be empty.")
        e.traceback = False
        raise e
    ret = create_new_module(module_name, module_type, outer=outer)
    if not ret:
        return
    module_info = get_local_module_info(module_name)
    if module_info is not None:
        return module_info.directory
    else:
        return None
