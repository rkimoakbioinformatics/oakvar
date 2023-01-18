from typing import Optional
from typing import Dict


def setup(
    clean: bool = False,
    refresh_db: bool = False,
    clean_cache_files: bool = False,
    setup_file: Optional[str] = None,
    email: Optional[str] = None,
    pw: Optional[str] = None,
    publish_time: str = "",
    custom_system_conf: Optional[Dict] = None,
    outer=None,
    system_worker_state=None,
):
    from ..lib.system import setup_system

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


def md(directory: Optional[str] = None):
    from ..lib.system import set_modules_dir, get_modules_dir

    if directory:
        set_modules_dir(directory)
    else:
        d = get_modules_dir()
        return d


def check(outer=None):
    from ..lib.system import check

    ret = check(outer=outer)
    return ret
