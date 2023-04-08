from typing import Optional
from typing import Any
from typing import List
from typing import Dict
from . import account as account


def register(
    module_name: str,
    url_file: Optional[str] = None,
    code_url: List[str] = [],
    data_url: List[str] = [],
    overwrite: bool = False,
    outer=None,
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
    )
    return ret


def fetch(
    refresh_db: bool = False,
    clean_cache_files: bool = False,
    clean: bool = False,
    publish_time: str = "",
    outer=None,
) -> bool:
    """Fetches OakVar store cache.

    Args:
        refresh_db (bool): `True` will fetch a clean copy of OakVar store database.
        clean_cache_files (bool): `True` will fetch a clean copy of OakVar store cache files.
        clean (bool): `True` will install OakVar store cache from scratch.
        publish_time (str): `YYYY-MM-DDTHH:MM:SS` format datetime string. Fetch will be done for new entries newer than this datetime.
        outer:

    Returns:
        `True` if successful. `False` if not.
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


def url(url: str = "", outer=None) -> str:
    """Gets or sets the URL of the OakVar store.

    Args:
        url (str): OakVar Store URL to use
        outer:

    Returns:
        str of the OakVar Store URL
    """
    from ...lib.store import url as url_fn

    ret = url_fn(url=url, outer=outer)
    return ret


def delete(
    module_name: str,
    code_version: Optional[str] = None,
    all: bool = False,
    keep_only_latest: bool = False,
    outer=None,
) -> bool:
    """Deletes a module from the OakVar store and fetches the OakVar store.

    Args:
        module_name (str): Module name
        code_version (Optional[str]): Version number of the module
        all (bool): `True` will delete all versions of the module.
        keep_only_latest (bool): `True` will delete all but the latest version of the module.
        outer:

    Returns:
        `True` if successful. `False` if not.
    """
    from ...lib.store.ov import delete
    from ...lib.store.db import fetch_ov_store_cache

    ret = delete(
        module_name,
        code_version=code_version,
        all=all,
        keep_only_latest=keep_only_latest,
        outer=outer,
    )
    if ret is True:
        ret = fetch_ov_store_cache(refresh_db=True)
    return ret


def login(
    email: Optional[str] = None,
    pw: Optional[str] = None,
    interactive: bool = False,
    relogin: bool = False,
    outer=None,
) -> Dict[str, Any]:
    """Logs in to the OakVar store.

    Args:
        email (Optional[str]): Email of an OakVar store account
        pw (Optional[str]): Password of an OakVar store account
        interactive (bool): If `True` and `email` or `pw` is not given, missing fields will be interactvely received with prompts.
        relogin (bool): If `True`, fresh login will be performed.
        outer:

    Returns:
        Result of login as a dict, with the fields `success`, `status_code`, `msg`, and `email`.
    """
    from ...lib.store.ov.account import login

    ret = login(
        email=email, pw=pw, interactive=interactive, relogin=relogin, outer=outer
    )
    return ret


def logout(outer=None) -> bool:
    """Logs out from the OakVar store.

    Args:
        outer:

    Returns:
        `True` if successful. `False` if not.
    """
    from ...lib.store.ov.account import logout

    ret = logout(outer=outer)
    return ret
