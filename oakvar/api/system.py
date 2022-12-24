from typing import Optional


def setup():
    from ..lib.system import setup_system

    return setup_system()


def md(directory: Optional[str] = None):
    from ..lib.system import set_modules_dir, get_modules_dir

    if directory:
        set_modules_dir(directory)
    d = get_modules_dir()
    return d


def check(outer=None):
    from ..lib.system import check

    ret = check(outer=outer)
    return ret
