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
) -> bool:
    """Register a module in the OakVar store.

    Args:
        module_name (str): Module name
        code_url (List[str]): URLs of code zip files
        data_url (List[str]): URLs of data zip files
        url_file (Optional[str]): Path to a yaml file which contains the URLs of code and data zip files.
        overwrite (bool): overwrite
        outer:
        error:

    Returns:
        `True` if successful. `False` if not.

    Examples:
        Pack `custommodule` module to produce `custommodule__1.0.0__code.zip` and `custommodule__1.0.0__data.zip`.

        >>> oakvar.api.module.pack("custommodule")

        Upload the two files to `https://module.storage.com/annotators/custommodule__1.0.0__code.zip` and `https://module.storage.com/annotators/custommodule__1.0.0__data.zip`.

        Then, register the module.

        >>> oakvar.api.store.register("custommodule",\\
            code_url=\\
                ["https://module.storage.com/annotators/custommodule__1.0.0__code.zip"],\\
            data_url=\\
                ["https://module.storage.com/annotators/custommodule__1.0.0__data.zip"])

        `url_file.yml` for this registration can be made:

            - code:
              - https://module.storage.com/annotators/custommodule__1.0.0__code.zip
            - data:
              - https://module.storage.com/annotators/custommodule__1.0.0__data.zip

        and used:

        >>> oakvar.api.store.register("custommodule", url_file="url_file.yml")
    """
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
    """fetch.

    Args:
        refresh_db (bool): refresh_db
        clean_cache_files (bool): clean_cache_files
        clean (bool): clean
        publish_time (str): publish_time
        outer:

    Returns:
        bool:
    """
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
    """url.

    Args:
        outer:
    """
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
    """delete.

    Args:
        module_name (str): module_name
        code_version (Optional[str]): code_version
        all (bool): all
        keep_only_latest (bool): keep_only_latest
        outer:
        error:
    """
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
    """login.

    Args:
        email (Optional[str]): email
        pw (Optional[str]): pw
        interactive (bool): interactive
        relogin (bool): relogin
        outer:
    """
    from ...lib.store.ov.account import login

    ret = login(
        email=email, pw=pw, interactive=interactive, relogin=relogin, outer=outer
    )
    return ret


def logout(outer=None):
    """logout.

    Args:
        outer:
    """
    from ...lib.store.ov.account import logout

    ret = logout(outer=outer)
    return ret
