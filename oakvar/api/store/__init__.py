from typing import Optional
from typing import List


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
    clean_cache_db: bool = False,
    clean_cache_files: bool = False,
    clean: bool = False,
    publish_time: str = "",
    outer=None,
) -> bool:
    from ...lib.store.db import fetch_ov_store_cache

    ret = fetch_ov_store_cache(
        clean_cache_db=clean_cache_db,
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


def delete():
    from ...lib.store.ov import delete
    from ...lib.store.db import fetch_ov_store_cache

    ret = delete()
    if ret == True:
        ret = fetch_ov_store_cache(refresh_db=True)
    return ret
