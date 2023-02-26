from typing import Optional
from typing import Union
from typing import Dict
from pathlib import Path


def setup(
    clean: bool = False,
    refresh_db: bool = False,
    clean_cache_files: bool = False,
    setup_file: Optional[Union[Path, str]] = None,
    email: Optional[str] = None,
    pw: Optional[str] = None,
    custom_system_conf: Optional[Dict] = None,
    publish_time: str = "",
    outer=None,
    system_worker_state=None,
):
    """setup.

    Args:
        clean (bool): Perform clean installation. Installed modules and analysis results are not erased.
        refresh_db (bool): Refreshes store server data.
        clean_cache_files (bool): Cleans store cache files.
        setup_file (Optional[Union[Path, str]]): Path to a custom system configuration file. If given, the system configuraton from this file will be used instead of default system configuratoin values.
        email (Optional[str]): OakVar store account Email
        pw (Optional[str]): OakVar store account password
        custom_system_conf (Optional[Dict]): Custom system configuration as a Dict
        publish_time (str): publish_time
        system_worker_state:
        outer:
    """
    from ..lib.system import setup_system

    if isinstance(setup_file, str):
        setup_file = Path(setup_file)
    return setup_system(
        clean=clean,
        refresh_db=refresh_db,
        clean_cache_files=clean_cache_files,
        setup_file=setup_file,
        email=email,
        pw=pw,
        publish_time=publish_time,
        custom_system_conf=custom_system_conf,
        outer=outer,
        system_worker_state=system_worker_state,
    )


def md(directory: Optional[Union[Path, str]] = None) -> Optional[Path]:
    """Gets or sets OakVar modules directory.

    Args:
        directory (Optional[Union[Path, str]]): Path to a new OakVar modules directory. If given, OakVar modules directory will be set to this value.

    Returns:
        Path of the new or existing OakVar modules directory. `None` if `directory` is not given and an OakVar modules directory is not defined in the system configuration.
    """
    from ..lib.system import set_modules_dir, get_modules_dir

    if directory:
        set_modules_dir(directory)
        return Path(directory)
    else:
        d = get_modules_dir()
        return d


def check(outer=None) -> bool:
    """Performs OakVar system checkup.

    Args:
        outer:

    Returns:
        True if all tests passed. False if not.
    """
    from ..lib.system import check

    ret = check(outer=outer)
    return ret
