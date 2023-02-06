from typing import Optional
from typing import List
from . import account as account


def register(
    module_name: str,
    url_file: Optional[str] = None,
    code_url: List[str] = [],
    data_url: List[str] = [],
    overwrite: bool = False,
    outer=None,
    error=None,
):
    from ...lib.store.ov import register

    ret = register(
        module_name,
        url_file=url_file,
        code_url=code_url,
        data_url=data_url,
        overwrite=overwrite,
        outer=outer,
        error=error,
    )
    return ret


def fetch(
    refresh_db: bool = False,
    clean_cache_files: bool = False,
    clean: bool = False,
    publish_time: str = "",
    outer=None,
) -> bool:
    from ...lib.store.db import fetch_ov_store_cache

    ret = fetch_ov_store_cache(
        refresh_db=refresh_db,
        clean_cache_files=clean_cache_files,
        clean=clean,
        publish_time=publish_time,
        outer=outer,
    )
    return ret


def url(outer=None):
    from ...lib.store import url

    ret = url(outer=outer)
    return ret


def delete(
    module_name: str,
    code_version: Optional[str] = None,
    all: bool = False,
    keep_only_latest: bool = False,
    outer=None,
    error=None,
):
    from ...lib.store.ov import delete
    from ...lib.store.db import fetch_ov_store_cache

    ret = delete(
        module_name,
        code_version=code_version,
        all=all,
        keep_only_latest=keep_only_latest,
        outer=outer,
        error=error,
    )
    if ret == True:
        ret = fetch_ov_store_cache(refresh_db=True)
    return ret


def login(
    email: Optional[str] = None,
    pw: Optional[str] = None,
    interactive: bool = False,
    relogin: bool = False,
    outer=None,
):
    from ...lib.store.ov.account import login

    ret = login(
        email=email, pw=pw, interactive=interactive, relogin=relogin, outer=outer
    )
    return ret


def logout(outer=None):
    from ...lib.store.ov.account import logout

    ret = logout(outer=outer)
    return ret
