def register(args, __name__="store register"):
    from ...lib.store.ov import register

    ret = register(args=args)
    return ret


def fetch(clean_cache_db: bool=False, clean_cache_files: bool=False, clean: bool=False, publish_time: str="", outer=None) -> bool:
    from ...lib.store.db import fetch_ov_store_cache

    ret = fetch_ov_store_cache(clean_cache_db=clean_cache_db, clean_cache_files=clean_cache_files, clean=clean, publish_time=publish_time, outer=outer)
    return ret


def url(args, __name__="store url"):
    from ...lib.store import url

    ret = url(args=args)
    return ret

