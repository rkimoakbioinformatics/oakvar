from typing import Optional
from typing import List
from typing import Tuple
from typing import Any


def get_ov_store_cache_conn(conf=None):
    from sqlite3 import connect
    from .consts import ov_store_cache_fn
    from os.path import join
    from ..system import get_conf_dir

    conf_dir: Optional[str] = get_conf_dir(conf=conf)
    if conf_dir:
        ov_store_cache_path = join(conf_dir, ov_store_cache_fn)
        conn = connect(ov_store_cache_path)
        cursor = conn.cursor()
        return conn, cursor
    return None, None


def db_func(func):
    def encl_func(*args, conf=None, **kwargs):
        conn, cursor = get_ov_store_cache_conn(conf=conf)
        ret = func(*args, conn=conn, cursor=cursor, **kwargs)
        return ret

    return encl_func


@db_func
def find_name_store(
    module_name: str, conn=None, cursor=None
) -> Optional[Tuple[str, str]]:
    if not conn or not cursor:
        return None
    q = f"select name, store from summary where name=?"
    cursor.execute(q, (module_name,))
    ret = cursor.fetchall()
    name = None
    store = None
    for r in ret:
        if not name or r[1] == "ov":
            name = r[0]
            store = r[1]
    if name and store:
        return name, store
    else:
        return None


@db_func
def latest_module_version_size(
    module_name: str, conn=Any, cursor=Any
) -> Optional[dict]:
    from packaging.version import Version

    _ = conn
    q = f"select store, code_version, data_version, data_source, code_size, data_size from versions where name=?"
    cursor.execute(q, (module_name,))
    ret = cursor.fetchall()
    latest_code_version = ""
    latest_r = None
    for r in ret:
        if not latest_r:
            latest_r = r
            latest_code_version = r[1]
        elif Version(r[1]) > Version(latest_code_version):
            latest_r = r
            latest_code_version = r[1]
    if latest_r:
        return {
            "code_version": latest_r[1],
            "data_version": latest_r[2],
            "data_source": latest_r[3],
            "code_size": int(latest_r[4]),
            "data_size": int(latest_r[5]),
        }
    else:
        return None


@db_func
def module_code_versions(module_name, conn=None, cursor=None) -> Optional[List[str]]:
    if not conn or not cursor:
        return None
    r = find_name_store(module_name)
    if not r:
        return None
    name, store = r
    q = f"select code_version from versions where name=? and store=?"
    cursor.execute(q, (name, store))
    values = [r[0] for r in cursor.fetchall()]
    return values


@db_func
def module_data_versions(module_name, conn=None, cursor=None) -> Optional[List[str]]:
    if not conn or not cursor:
        return None
    r = find_name_store(module_name)
    if not r:
        return None
    name, store = r
    q = f"select data_version from versions where name=? and store=?"
    cursor.execute(q, (name, store))
    values = [r[0] for r in cursor.fetchall()]
    return values


@db_func
def module_data_sources(module_name, conn=Any, cursor=Any) -> Optional[List[str]]:
    _ = conn or cursor
    r = find_name_store(module_name)
    if not r:
        return None
    name, store = r
    q = f"select data_source from versions where name=? and store=?"
    cursor.execute(q, (name, store))
    values = [r[0] for r in cursor.fetchall()]
    return values


@db_func
def module_min_pkg_vers(module_name, conn=Any, cursor=Any) -> Optional[List[str]]:
    _ = conn or cursor
    r = find_name_store(module_name)
    if not r:
        return None
    name, store = r
    q = f"select min_pkg_ver from versions where name=? and store=?"
    cursor.execute(q, (name, store))
    values = [r[0] for r in cursor.fetchall()]
    return values


@db_func
def module_sizes(
    module_name: str, code_version: str, conn=None, cursor=None
) -> Optional[Tuple[int, int]]:
    if not conn or not cursor:
        return None
    r = find_name_store(module_name)
    if not r:
        return None
    name, store = r
    q = f"select code_size, data_size from versions where name=? and store=? and code_version=?"
    cursor.execute(q, (name, store, code_version))
    r = cursor.fetchone()
    if not r:
        return None
    code_size, data_size = r
    return int(code_size), int(data_size)


@db_func
def module_data_source(
    module_name: str, code_version: str, conn=None, cursor=None
) -> Optional[str]:
    if not conn or not cursor:
        return None
    r = find_name_store(module_name)
    if not r:
        return None
    name, store = r
    q = f"select data_source from versions where name=? and store=? and code_version=?"
    cursor.execute(q, (name, store, code_version))
    r = cursor.fetchone()
    if not r:
        return None
    return r[0]


@db_func
def remote_module_data_version(
    module_name: str, code_version: str, conn=None, cursor=None
) -> Optional[str]:
    if not conn or not cursor:
        return None
    r = find_name_store(module_name)
    if not r:
        return None
    name, store = r
    q = f"select data_version from versions where name=? and store=? and code_version=?"
    cursor.execute(q, (name, store, code_version))
    r = cursor.fetchone()
    if not r:
        return None
    return r[0]


@db_func
def get_latest_module_code_version(module_name, conn=None, cursor=None):
    from ..util.util import get_latest_version
    from ..util.admin_util import oakvar_version
    from packaging.version import Version

    if not conn or not cursor:
        return None
    r = find_name_store(module_name)
    if not r:
        return None
    pkg_ver = Version(oakvar_version())
    name, store = r
    q = f"select code_version, min_pkg_ver from versions where name=? and store=?"
    cursor.execute(q, (name, store))
    code_versions = []
    for row in cursor.fetchall():
        [code_version, min_pkg_ver] = row
        if min_pkg_ver.startswith(">="):
            min_pkg_ver = min_pkg_ver[2:]
        if pkg_ver >= Version(min_pkg_ver):
            code_versions.append(code_version)
    latest_code_version = get_latest_version(code_versions)
    return latest_code_version


@db_func
def module_code_version_is_not_compatible_with_pkg_version(module_name: str, code_version: str, conn=Any, cursor=Any) -> Optional[str]:
    from packaging.version import Version
    from ..util.admin_util import oakvar_version

    _ = conn
    pkg_ver = Version(oakvar_version())
    q = f"select min_pkg_ver from versions where name=? and code_version=?"
    cursor.execute(q, (module_name, code_version))
    min_pkg_ver = None
    for row in cursor.fetchall():
        version = row[0]
        if Version(version) <= pkg_ver:
            return None
        else:
            if min_pkg_ver is None or Version(version) < Version(min_pkg_ver):
                min_pkg_ver = version
    if min_pkg_ver is None:
        min_pkg_ver = "?"
    return min_pkg_ver

@db_func
def module_info_ls(module_name, conn=None, cursor=None):
    import sqlite3
    from .consts import summary_table_cols
    from ..module.remote import RemoteModuleLs

    if not conn or not cursor:
        return None
    cursor.row_factory = sqlite3.Row
    q = f"select { ', '.join(summary_table_cols) } from summary where name=?"
    cursor.execute(q, (module_name,))
    ret = cursor.fetchall()
    module_info = None
    for r in ret:
        info = {}
        for col in summary_table_cols:
            info[col] = r[col]
        if not module_info or info["store"] == "ov":
            module_info = RemoteModuleLs("", **info)
    return module_info


@db_func
def module_info(module_name, conn=None, cursor=None):
    import sqlite3
    from .consts import summary_table_cols
    from ..module.remote import RemoteModule

    if not conn or not cursor:
        return None
    cursor.row_factory = sqlite3.Row
    q = f"select { ', '.join(summary_table_cols) } from summary where name=?"
    cursor.execute(q, (module_name,))
    ret = cursor.fetchall()
    module_info = None
    for r in ret:
        info = {}
        for col in summary_table_cols:
            info[col] = r[col]
        if not module_info or info["store"] == "ov":
            module_info = RemoteModule("", **info)
    return module_info


@db_func
def summary_col_value(module_name: str, colname: str, conn=None, cursor=None):
    from json import loads

    if not conn or not cursor:
        return None
    q = f"select {colname}, store from summary where name=?"
    cursor.execute(q, (module_name,))
    ret = cursor.fetchall()
    out = None
    if ret:
        for r in ret:
            v, store = r
            if not out or store == "ov":
                out = v
    if out:
        if out[0] in ["[", "{"]:
            return loads(out)
        else:
            return out
    else:
        return None


@db_func
def module_list(module_type=None, conn=None, cursor=None) -> List[str]:
    if not conn or not cursor:
        return []
    if module_type:
        q = f"select distinct(name) from summary where type=?"
        cursor.execute(q, (module_type,))
    else:
        q = f"select distinct(name) from summary"
        cursor.execute(q)
    ret = cursor.fetchall()
    l = set()
    for v in ret:
        l.add(v[0])
    return list(l)


@db_func
def table_exists(table: str, conf=None, conn=None, cursor=None) -> bool:
    if not conn or not cursor:
        return False
    if conf:
        pass
    q = f"select name from sqlite_master where type='table' and name=?"
    cursor.execute(q, (table,))
    ret = cursor.fetchone()
    if not ret:
        return False
    else:
        return True


@db_func
def is_store_db_schema_changed(conn=Any, cursor=Any) -> bool:
    from .consts import summary_table_cols
    from .consts import versions_table_cols

    _ = conn
    q = f'pragma table_info("summary")'
    cursor.execute(q)
    cols = [row[1] for row in cursor.fetchall()]
    if len(cols) > 0 and cols != summary_table_cols:
        return True
    q = f'pragma table_info("versions")'
    cursor.execute(q)
    cols = [row[1] for row in cursor.fetchall()]
    if len(cols) > 0 and cols != versions_table_cols:
        return True
    return False

@db_func
def drop_ov_store_cache(conf=None, conn=None, cursor=None, args={}):
    from os.path import exists
    from ..system import get_cache_dir
    from ..system.consts import cache_dirs
    from shutil import rmtree

    if not conn or not cursor:
        return
    if conf:
        pass
    if args.get("clean_cache_db"):
        for table in ["summary", "versions", "info"]:
            if table_exists(table):
                q = f"drop table if exists {table}"
                cursor.execute(q)
                conn.commit()
    if args.get("clean_cache_files"):
        for cache_key in cache_dirs:
            fp = get_cache_dir(cache_key)
            if exists(fp):
                rmtree(fp)


@db_func
def create_ov_store_cache(conf=None, args={}, conn=None, cursor=None):
    from .consts import summary_table_cols
    from .consts import versions_table_cols
    from ..system.consts import cache_dirs
    from ..system import get_cache_dir
    from os.path import exists
    from os.path import join
    from os import mkdir

    if not conn or not cursor:
        return False
    if conf:
        pass
    clean_cache_db = args.get("clean_cache_db")
    if clean_cache_db or not table_exists("summary"):
        q = f"create table summary ( { ', '.join([col + ' text' for col in summary_table_cols]) }, primary key ( name, store ) )"
        cursor.execute(q)
    if clean_cache_db or not table_exists("versions"):
        q = f"create table versions ( { ', '.join([col + ' text' for col in versions_table_cols]) }, primary key ( name, store, code_version ) )"
        cursor.execute(q)
    if clean_cache_db or not table_exists("info"):
        q = f"create table info ( key text primary key, value text )"
        cursor.execute(q)
    conn.commit()
    for cache_key in cache_dirs:
        fp = get_cache_dir(cache_key)
        if not exists(fp):
            mkdir(fp)
            mkdir(join(fp, "ov"))
            mkdir(join(fp, "oc"))


def try_fetch_ov_store_cache(args={}):
    from ..util.util import quiet_print

    try:
        return fetch_ov_store_cache(args=args)
    except Exception as e:
        quiet_print(
            f"Fetching store update failed:\n\n>>{e}.\n\nContinuing with the current store cache...\n",
            args=args,
        )


@db_func
def fetch_ov_store_cache(
    conn=None,
    cursor=None,
    args={},
):
    from .consts import ov_store_last_updated_col
    from ..util.util import quiet_print
    from ..exceptions import StoreServerError
    from ..exceptions import AuthorizationError
    from .ov.account import login_with_token_set
    from .ov import get_server_last_updated
    from ..module.remote import make_remote_manifest
    from ..gui.webstore.webstore import save_remote_manifest_cache

    if not conn or not cursor:
        return False
    if not login_with_token_set():
        quiet_print(f"not logged in", args=args)
        return False
    if is_new_store_db_setup():
        args["clean_cache_db"] = True
        args["clean_cache_files"] = True
        args["clean"] = True
        local_last_updated = None
    else:
        local_last_updated = get_local_last_updated()
    if is_store_db_schema_changed():
        quiet_print(f"Need to fetch store cache due to schema change", args=args)
        args["clean_cache_db"] = True
    clean_cache_files = args.get("clean_cache_files")
    clean_cache_db = args.get("clean_cache_db")
    server_last_updated, status_code = get_server_last_updated()
    if not server_last_updated:
        if status_code == 401:
            raise AuthorizationError()
        elif status_code == 500:
            raise StoreServerError()
        return False
    if (
        not clean_cache_db
        and not clean_cache_files
        and local_last_updated
        and local_last_updated >= server_last_updated
    ):
        quiet_print("No store update to fetch", args=args)
        return True
    args["publish_time"] = local_last_updated
    drop_ov_store_cache(args=args)
    create_ov_store_cache(args=args)
    fetch_summary_cache(args=args)
    fetch_versions_cache(args=args)
    if args.get("clean_cache_files") or args.get("clean"):
        args["publish_time"] = ""
    else:
        args["publish_time"] = local_last_updated
    fetch_readme_cache(args=args)
    fetch_logo_cache(args=args)
    fetch_conf_cache(args=args)
    q = f"insert or replace into info ( key, value ) values ( ?, ? )"
    cursor.execute(q, (ov_store_last_updated_col, str(server_last_updated)))
    conn.commit()
    content = make_remote_manifest()
    save_remote_manifest_cache(content)
    quiet_print("OakVar store cache has been fetched.", args=args)
    return True


@db_func
def is_new_store_db_setup(conn=Any, cursor=Any):
    _ = conn
    q = "pragma table_info('info')"
    cursor.execute(q)
    ret = cursor.fetchall()
    if len(ret) > 0:
        return False
    else:
        return True

@db_func
def get_summary_module_store_list(args={}, conn=None, cursor=None):
    if not conn or not cursor:
        return
    q = "select name, store from summary where publish_time >= ?"
    cursor.execute(q, (args.get("publish_time"),))
    ret = cursor.fetchall()
    out = []
    for r in ret:
        out.append({"name": r[0], "store": r[1]})
    return out


@db_func
def fetch_conf_cache(args={}, conn=None, cursor=None, conf={}):
    from requests import Session
    from .ov.account import get_current_id_token
    from ..system import get_cache_dir
    from .ov import get_store_url
    from os.path import join
    from ..util.util import quiet_print

    if not conn or not cursor:
        return
    module_stores = get_summary_module_store_list(args=args)
    if not module_stores:
        return
    id_token = get_current_id_token(args=args)
    params = {"idToken": id_token, "publish_time": args.get("publish_time")}
    s = Session()
    s.headers["User-Agent"] = "oakvar"
    quiet_print(f"fetching store cache 5/5...", args=args)
    for module_store in module_stores:
        name = module_store["name"]
        store = module_store["store"]
        fpath = join(get_cache_dir("conf", conf=conf), store, name + ".json")
        url = f"{get_store_url()}/fetch_conf/{store}/{name}"
        res = s.post(url, data=params)
        content = b"{}"
        if res.status_code == 200:
            content = res.content
        elif res.status_code == 404:
            content = b"{}"
        else:
            continue
        with open(fpath, "wb") as wf:
            wf.write(content)


@db_func
def fetch_logo_cache(args={}, conn=None, cursor=None, conf={}):
    from requests import Session
    from .ov.account import get_current_id_token
    from ..system import get_cache_dir
    from .ov import get_store_url
    from os.path import join
    from ..util.util import quiet_print

    if not conn or not cursor:
        return
    module_stores = get_summary_module_store_list(args=args)
    if not module_stores:
        return
    id_token = get_current_id_token(args=args)
    params = {"idToken": id_token, "publish_time": args.get("publish_time")}
    s = Session()
    s.headers["User-Agent"] = "oakvar"
    quiet_print(f"fetching store cache 4/5...", args=args)
    for module_store in module_stores:
        name = module_store["name"]
        store = module_store["store"]
        fpath = join(get_cache_dir("logo", conf=conf), store, name + ".png")
        url = f"{get_store_url()}/fetch_logo/{store}/{name}"
        res = s.post(url, data=params)
        content = b""
        if res.status_code == 200:
            content = res.content
        elif res.status_code == 404:
            content = b""
        else:
            continue
        with open(fpath, "wb") as wf:
            wf.write(content)


@db_func
def fetch_readme_cache(args={}, conn=None, cursor=None, conf={}):
    from requests import Session
    from .ov.account import get_current_id_token
    from ..system import get_cache_dir
    from .ov import get_store_url
    from os.path import join
    from ..util.util import quiet_print

    if not conn or not cursor:
        return
    module_stores = get_summary_module_store_list(args=args)
    if not module_stores:
        return
    id_token = get_current_id_token(args=args)
    params = {"idToken": id_token, "publish_time": args.get("publish_time")}
    s = Session()
    s.headers["User-Agent"] = "oakvar"
    quiet_print(f"fetching store cache 3/5...", args=args)
    for module_store in module_stores:
        name = module_store["name"]
        store = module_store["store"]
        fpath = join(get_cache_dir("readme", conf=conf), store, name)
        url = f"{get_store_url()}/fetch_readme/{store}/{name}"
        res = s.post(url, data=params)
        content = b""
        if res.status_code == 200:
            content = res.content
        elif res.status_code == 404:
            content = b""
        else:
            continue
        with open(fpath, "wb") as wf:
            wf.write(content)


@db_func
def fetch_summary_cache(args={}, conn=Any, cursor=Any):
    from requests import Session
    from .ov.account import get_current_id_token
    from ..exceptions import StoreServerError
    from ..exceptions import AuthorizationError
    from .ov import get_store_url
    from ..util.util import quiet_print

    _ = conn
    url = f"{get_store_url()}/fetch_summary"
    id_token = get_current_id_token(args=args)
    params = {"idToken": id_token, "publish_time": args.get("publish_time")}
    s = Session()
    s.headers["User-Agent"] = "oakvar"
    quiet_print(f"fetching store cache 1/5...", args=args)
    res = s.post(url, data=params)
    if res.status_code != 200:
        if res.status_code == 401:
            raise AuthorizationError()
        elif res.status_code == 500:
            raise StoreServerError()
        return False
    if args.get("clean_cache_db"):
        q = f"delete from summary"
        cursor.execute(q)
        conn.commit()
    res = res.json()
    cols = res["cols"]
    for row in res["data"]:
        q = f"insert or replace into summary ( {', '.join(cols)} ) values ( {', '.join(['?'] * len(cols))} )"
        cursor.execute(q, row)
    conn.commit()


@db_func
def fetch_versions_cache(args={}, conn=None, cursor=None):
    from requests import Session
    from json import dumps
    from .ov.account import get_current_id_token
    from ..exceptions import StoreServerError
    from ..exceptions import AuthorizationError
    from .ov import get_store_url
    from ..util.util import quiet_print
    from .consts import versions_table_cols

    if not conn or not cursor:
        return
    url = f"{get_store_url()}/fetch_versions"
    id_token = get_current_id_token(args=args)
    cols = dumps(versions_table_cols)
    params = {"idToken": id_token, "publish_time": args.get("publish_time"), "cols": cols}
    s = Session()
    s.headers["User-Agent"] = "oakvar"
    quiet_print(f"fetching store cache 2/5...", args=args)
    res = s.post(url, data=params)
    if res.status_code != 200:
        if res.status_code == 401:
            raise AuthorizationError()
        elif res.status_code == 500:
            raise StoreServerError(text=res.text)
        return False
    if args.get("clean_cache_db"):
        q = f"delete from versions"
        cursor.execute(q)
        conn.commit()
    res = res.json()
    cols = res["cols"]
    for row in res["data"]:
        q = f"insert or replace into versions ( {', '.join(cols)} ) values ( {', '.join(['?'] * len(cols))} )"
        cursor.execute(q, row)
    conn.commit()


@db_func
def get_local_last_updated(conn=None, cursor=None) -> str:
    from .consts import ov_store_last_updated_col

    if not conn or not cursor:
        return ""
    q = "select value from info where key=?"
    cursor.execute(q, (ov_store_last_updated_col,))
    res = cursor.fetchone()
    if not res:
        return ""
    last_updated = res[0]
    return last_updated


@db_func
def get_manifest(conn=None, cursor=None) -> Optional[dict]:
    import sqlite3

    if not conn or not cursor:
        return None
    cursor.row_factory = sqlite3.Row
    q = f"select distinct(name) from summary"
    cursor.execute(q)
    res = cursor.fetchall()
    mi = {}
    for r in res:
        name = r[0]
        m = module_info(name)
        if m:
            mi[name] = m.to_dict()
    return mi


@db_func
def get_urls(module_name: str, code_version: str, args={}, conn=None, cursor=None):
    from requests import Session
    from .ov.account import get_current_id_token
    from ..exceptions import StoreServerError
    from ..exceptions import AuthorizationError
    from .ov import get_store_url

    if not conn or not cursor:
        return
    q = f"select store from versions where name=? and code_version=?"
    cursor.execute(q, (module_name, code_version))
    ret = cursor.fetchall()
    store = None
    for r in ret:
        if not store or r[0] == "ov":
            store = r[0]
    if not store:
        return None
    url = f"{get_store_url()}/urls/{module_name}/{code_version}"
    id_token = get_current_id_token(args=args)
    params = {"idToken": id_token}
    s = Session()
    s.headers["User-Agent"] = "oakvar"
    res = s.post(url, data=params)
    if res.status_code == 200:
        return res.json()
    else:
        if res.status_code == 401:
            raise AuthorizationError()
        elif res.status_code == 500:
            raise StoreServerError()
        return


@db_func
def set_server_last_updated(args={}, conn=None, cursor=None):
    from .consts import ov_store_last_updated_col
    from ..consts import publish_time_fmt
    from datetime import datetime

    if not conn or not cursor:
        return
    if args:
        pass
    dt = datetime.now().strftime(publish_time_fmt)
    q = f"insert or replace into info ( key, value ) values ( ?, ? )"
    cursor.execute(q, (ov_store_last_updated_col, dt))
    conn.commit()


@db_func
def table_has_entry(table: str, conn=Any, cursor=Any) -> bool:
    _ = conn or cursor
    q = f"select count(*) from {table}"
    cursor.execute(q)
    v = cursor.fetchone()[0]
    return v > 0


@db_func
def check_tables(args={}, conn=Any, cursor=Any) -> bool:
    from ..util.util import quiet_print

    _ = conn or cursor
    for table in ["summary", "versions", "info"]:
        if not table_exists(table) or not table_has_entry(table):
            quiet_print(f"store cache table {table} does not exist.", args=args)
            return False
    return True


@db_func
def module_is_in_store(module_name: str, conn=Any, cursor=Any) -> bool:
    _ = conn
    q = f"select name from summary where name=?"
    cursor.execute(q, (module_name,))
    ret = cursor.fetchone()
    if ret:
        return True
    else:
        return False
