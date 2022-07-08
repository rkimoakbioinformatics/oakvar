from typing import Optional
from typing import Tuple
from typing import List
from ...module.remote import RemoteModuleInfo


def db_func(func):
    def encl_func(*args, **kwargs):
        conn, c = get_ov_store_cache_conn()
        ret = func(*args, conn=conn, c=c, **kwargs)
        return ret

    return encl_func


@db_func
def module_latest_code_version(module_name, conn=None, c=None):
    from ...util.util import get_latest_version
    from json import loads

    if not conn or not c:
        return None
    q = f"select code_versions, store from summary where name=?"
    c.execute(q, (module_name,))
    ret = c.fetchall()
    out = None
    for r in ret:
        if not out or r[1] == "ov":
            out = loads(r[0])
    if out:
        out = get_latest_version(out)
    return out


@db_func
def module_info(module_name, conn=None, c=None) -> Optional[RemoteModuleInfo]:
    import sqlite3
    from ..consts import summary_table_cols
    from ...module.remote import RemoteModuleInfo

    if not conn or not c:
        return None
    c.row_factory = sqlite3.Row
    q = f"select { ', '.join(summary_table_cols) } from summary where name=?"
    c.execute(q, (module_name,))
    ret = c.fetchall()
    module_info = None
    for r in ret:
        info = {}
        for col in summary_table_cols:
            info[col] = r[col]
        mi = RemoteModuleInfo("", **info)
        if not module_info or info["store"] == "ov":
            module_info = mi
    return module_info


@db_func
def summary_col_value(
    module_name: str, colname: str, conn=None, c=None
) -> Optional[dict]:
    from json import loads

    if not conn or not c:
        return None
    q = f"select {colname}, store from summary where name=?"
    c.execute(q, (module_name,))
    ret = c.fetchall()
    out = None
    if ret:
        for r in ret:
            v, store = r
            if not v or store == "ov":
                out = v
    if out:
        return loads(out)
    else:
        return None


def module_code_url(module_name: str, version=None, conn=None, c=None) -> Optional[str]:
    from requests import Session
    from .account import get_current_id_token
    from ...exceptions import AuthorizationError
    from ...exceptions import StoreServerError

    id_token = get_current_id_token(args={"quiet": True})
    s = Session()
    s.headers["User-Agent"] = "oakvar"
    url = get_store_url() + f"/moduleurls/{module_name}/{version}/code"
    params = {"idToken": id_token}
    res = s.post(url, data=params)
    if res.status_code == 200:
        code_url = res.text
        return code_url
    elif res.status_code == 401:
        raise AuthorizationError()
    elif res.status_code == 500:
        raise StoreServerError()
    else:
        return None


def module_data_url(module_name: str, version=None, conn=None, c=None) -> Optional[str]:
    from requests import Session
    from .account import get_current_id_token
    from ...exceptions import AuthorizationError
    from ...exceptions import StoreServerError

    id_token = get_current_id_token(args={"quiet": True})
    s = Session()
    s.headers["User-Agent"] = "oakvar"
    url = get_store_url() + f"/moduleurls/{module_name}/{version}/data"
    params = {"idToken": id_token}
    res = s.post(url, data=params)
    if res.status_code == 200:
        data_url = res.text
        return data_url
    elif res.status_code == 401:
        raise AuthorizationError()
    elif res.status_code == 500:
        raise StoreServerError()
    else:
        return None


@db_func
def module_conf_url(module_name: str, version=None, conn=None, c=None) -> Optional[str]:
    if not conn or not c:
        return None
    if not version:
        version = module_latest_code_version(module_name)
    q = f"select conf_url from modules where name=? and code_version=?"
    c.execute(q, (module_name, version))
    ret = c.fetchone()
    if not ret:
        return None
    else:
        return ret[0]


@db_func
def module_list(conn=None, c=None) -> List[str]:
    if not conn or not c:
        return []
    q = f"select name from modules"
    c.execute(q)
    ret = c.fetchall()
    l = set()
    for v in ret:
        l.add(v[0])
    return list(l)


@db_func
def code_version(
    module_name, version=None, conn=None, c=None, channel="ov"
) -> Optional[str]:
    from ...util.util import get_latest_version
    from json import loads

    if version:
        return version
    if not conn or not c:
        return None
    q = f"select code_versions, store from summary where name=?"
    c.execute(q, (module_name,))
    ret = c.fetchall()
    if len(ret) == 1:
        return get_latest_version(loads(ret[0][0]))
    elif len(ret) > 1:
        for vs in ret:
            if vs[1] == channel:
                return get_latest_version(loads(vs[0]))
    return None


@db_func
def data_version(
    module_name, version=None, conn=None, c=None, channel="ov"
) -> Optional[Tuple[str, str]]:
    if not conn or not c:
        return None
    if version:
        q = f"select data_version, store from modules where name=? and code_version=?"
        c.execute(q, (module_name, version))
    else:
        q = f"select data_version, store from modules where name=?"
        c.execute(q, (module_name,))
    ret = c.fetchall()
    if len(ret) == 1:
        return ret[0][0]
    elif len(ret) > 1:
        for vs in ret:
            if vs[2] == channel:
                return vs[0]
    return None


def get_ov_store_cache_conn(conf=None):
    from sqlite3 import connect
    from ..consts import ov_store_cache_fn
    from os.path import join
    from ...system import get_conf_dir

    conf_dir: Optional[str] = get_conf_dir(conf=conf)
    if conf_dir:
        ov_store_cache_path = join(conf_dir, ov_store_cache_fn)
        conn = connect(ov_store_cache_path)
        cursor = conn.cursor()
        return conn, cursor
    return None, None


def setup_ov_store_cache(conf=None, args=None):
    drop_ov_store_cache(conf=conf, args=args)
    create_ov_store_cache(conf=conf, args=args)
    fetch_ov_store_cache(args=args)


def table_exists(table: str, conf=None) -> bool:
    conn, c = get_ov_store_cache_conn(conf=conf)
    if not conn or not c:
        return False
    q = f"select name from sqlite_master where type='table' and name=?"
    c.execute(q, (table,))
    ret = c.fetchone()
    if not ret:
        return False
    else:
        return True


def drop_ov_store_cache(conf=None, args={}):
    conn, c = get_ov_store_cache_conn(conf=conf)
    if not conn or not c:
        return False
    clean = args.get("clean")
    for table in ["summary", "info"]:
        if clean or table_exists(table):
            q = f"drop table if exists {table}"
            c.execute(q)
    conn.commit()


def create_ov_store_cache(conf=None, args={}):
    from ..consts import summary_table_cols

    conn, c = get_ov_store_cache_conn(conf=conf)
    if not conn or not c:
        return False
    clean = args.get("clean")
    table = "summary"
    if clean or not table_exists(table):
        q = f"create table summary ( { ', '.join([col + ' text' for col in summary_table_cols]) }, primary key ( name, store ) )"
        c.execute(q)
    table = "info"
    if clean or not table_exists(table):
        q = f"create table info ( key text primary key, value text )"
        c.execute(q)
    conn.commit()


def url_is_valid(url: str) -> bool:
    from requests import head

    res = head(url)
    if res.status_code == 200:
        return True
    else:
        return False


def get_register_args_of_module(module_name: str, args={}) -> Optional[dict]:
    from ...module.local import get_remote_manifest_from_local
    from ...exceptions import ArgumentError
    from re import fullmatch

    rmi = get_remote_manifest_from_local(module_name)
    if not rmi or not args:
        return None
    rmi["code_url"] = args.get("code_url")
    rmi["data_url"] = args.get("data_url")
    rmi["logo_url"] = args.get("logo_url")
    rmi["module_name"] = module_name
    for v in ["code", "data", "logo"]:
        k = f"{v}_url"
        if v == "logo" and rmi[k] == "":
            continue
        if not fullmatch(
            r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)",
            rmi[k],
        ) or not url_is_valid(rmi[k]):
            raise ArgumentError(f"invalid {k}")
    return rmi


def make_remote_module_info_from_local(module_name: str) -> Optional[dict]:
    from ...module.local import get_local_module_info
    from time import time

    mi = get_local_module_info(module_name)
    if not mi:
        return None
    versions = {}
    latest_version = ""
    ty = mi.type
    title = mi.title
    description = mi.description
    size = mi.size
    code_size = 0
    data_size = 0
    datasource = mi.datasource
    hidden = mi.conf.get("hidden", False)
    developer = mi.developer
    data_versions = {}
    data_sources = {}
    tags = mi.tags
    publish_time = str(time())
    rmi = {
        "versions": versions,
        "latest_version": latest_version,
        "type": ty,
        "title": title,
        "description": description,
        "size": size,
        "code_size": code_size,
        "data_size": data_size,
        "datasource": datasource,
        "hidden": hidden,
        "developer": developer,
        "data_versions": data_versions,
        "data_sources": data_sources,
        "tags": tags,
        "publish_time": publish_time,
    }
    return rmi


@db_func
def register(conn=None, c=None, args={}) -> bool:
    from requests import post
    from .account import get_current_id_token
    from ...util.util import quiet_print

    if not conn or not c:
        return False
    id_token = get_current_id_token()
    module_name = args.get("module_name")
    url = get_store_url() + "/register_module"
    try:
        params = get_register_args_of_module(module_name, args=args)
        if not params:
            return False
        params["idToken"] = id_token
        res = post(url, data=params)
        if res.status_code == 200:
            quiet_print(f"success", args=args)
            return True
        else:
            quiet_print(f"{res.text}", args=args)
            return False
    except Exception as e:
        quiet_print(f"{str(e)}", args=args)
        return False


@db_func
def fetch_ov_store_cache(
    conn=None,
    c=None,
    args={},
):
    from ..consts import ov_store_last_updated_col
    from requests import Session
    from ...util.util import quiet_print
    from ...exceptions import StoreServerError
    from ...exceptions import AuthorizationError
    from .account import get_current_id_token

    if not conn or not c:
        return False
    s = Session()
    s.headers["User-Agent"] = "oakvar"
    store_url = get_store_url()
    if not store_url:
        return False
    id_token = get_current_id_token(args=args)
    if not id_token:
        quiet_print(f"not logged in", args=args)
        return False
    server_last_updated, status_code = get_server_last_updated()
    local_last_updated = get_local_last_updated()
    clean = args.get("clean")
    if not server_last_updated:
        if status_code == 401:
            raise AuthorizationError()
        elif status_code == 500:
            raise StoreServerError()
        return False
    if not clean and local_last_updated and local_last_updated >= server_last_updated:
        quiet_print("No store update to fetch", args=args)
        return True
    url = f"{store_url}/fetch"
    params = {"idToken": id_token}
    res = s.post(url, data=params)
    if res.status_code != 200:
        if res.status_code == 401:
            raise AuthorizationError()
        elif res.status_code == 500:
            raise StoreServerError()
        return False
    q = f"delete from summary"
    c.execute(q)
    conn.commit()
    res = res.json()
    cols = res["cols"]
    for row in res["data"]:
        q = f"insert into summary ( {', '.join(cols)} ) values ( {', '.join(['?'] * len(cols))} )"
        c.execute(q, row)
    q = f"insert or replace into info ( key, value ) values ( ?, ? )"
    c.execute(q, (ov_store_last_updated_col, str(server_last_updated)))
    conn.commit()
    quiet_print("OakVar store cache has been fetched.", args=args)


def get_server_last_updated(args={}):
    from requests import Session
    from .account import get_current_id_token

    id_token = get_current_id_token(args=args)
    s = Session()
    s.headers["User-Agent"] = "oakvar"
    url = get_store_url() + "/last_updated"
    params = {"idToken": id_token}
    res = s.post(url, data=params)
    if res.status_code != 200:
        return 0, res.status_code
    server_last_updated = float(res.json())
    return server_last_updated, res.status_code


@db_func
def get_local_last_updated(conn=None, c=None) -> Optional[float]:
    from ..consts import ov_store_last_updated_col

    if not conn or not c:
        return None
    q = "select value from info where key=?"
    c.execute(q, (ov_store_last_updated_col,))
    res = c.fetchone()
    if not res:
        return None
    last_updated = float(res[0])
    return last_updated


def make_module_info_from_table_row(row: dict) -> dict:
    d = {
        "name": row["name"],
        "type": row["type"],
        "code_version": row["code_version"],
        "data_version": row["data_version"],
        "tags": row["tags"],
        "code_size": row["code_size"],
        "data_size": row["data_size"],
        "logo_url": row["logo_url"],
        "description": row["description"],
        "readme": row["readme"],
        "logo": row["logo"],
        "conf": row["conf"],
        "store": row["store"],
    }
    return d


@db_func
def get_manifest(conn=None, c=None) -> Optional[dict]:
    import sqlite3

    if not conn or not c:
        return None
    c.row_factory = sqlite3.Row
    q = f"select distinct(name) from summary"
    c.execute(q)
    res = c.fetchall()
    mi = {}
    for r in res:
        name = r[0]
        m = module_info(name)
        if m:
            mi[name] = m.to_dict()
    return mi


@db_func
def get_readme(module_name: str, conn=None, c=None, version=None) -> Optional[str]:
    if not conn or not c:
        return None
    if not version:
        version = module_latest_code_version(module_name)
    q = "select readme, store from summary where name=?"
    c.execute(q, (module_name,))
    res = c.fetchall()
    out = None
    for r in res:
        readme, store = r
        if not out or store == "ov":
            out = readme
    return out


def get_store_url() -> str:
    from ...system import get_system_conf

    sys_conf = get_system_conf()
    store_url = sys_conf["store_url"]
    return store_url


# @db_func
# def fetch_ov_store_cache(
#    email: Optional[str] = None,
#    pw: Optional[str] = None,
#    conn=None,
#    c=None,
#    args={},
# ):
#    from ..consts import ov_store_email_key
#    from ..consts import ov_store_pw_key
#    from ..consts import ov_store_last_updated_col
#    from ...system import get_sys_conf_value
#    from ...system import get_user_conf
#    from requests import Session
#    from ...util.util import quiet_print
#    from ...exceptions import StoreServerError
#    from ...exceptions import AuthorizationError
#
#    if not conn or not c:
#        return False
#    if not email and args:
#        email = args.get("email")
#        pw = args.get("pw")
#    if not email:
#        user_conf = get_user_conf()
#        email = user_conf.get(ov_store_email_key)
#        pw = user_conf.get(ov_store_pw_key)
#    if not email or not pw:
#        return False
#    params = {"email": email, "pw": pw}
#    s = Session()
#    s.headers["User-Agent"] = "oakvar"
#    store_url = get_sys_conf_value("store_url")
#    if not store_url:
#        return False
#    server_last_updated, status_code = get_server_last_updated(email, pw)
#    local_last_updated = get_local_last_updated()
#    clean = args.get("clean")
#    if not server_last_updated:
#        if status_code == 401:
#            raise AuthorizationError()
#        elif status_code == 500:
#            raise StoreServerError()
#        return False
#    if not clean and local_last_updated and local_last_updated >= server_last_updated:
#        quiet_print("No store update to fetch", args=args)
#        return True
#    url = f"{store_url}/fetch"
#    res = s.get(url, params=params)
#    if res.status_code != 200:
#        if res.status_code == 401:
#            raise AuthorizationError()
#        elif res.status_code == 500:
#            raise StoreServerError()
#        return False
#    q = f"delete from modules"
#    c.execute(q)
#    conn.commit()
#    res = res.json()
#    cols = res["cols"]
#    for row in res["data"]:
#        q = f"insert into modules ( {', '.join(cols)} ) values ( {', '.join(['?'] * len(cols))} )"
#        c.execute(q, row)
#    q = f"insert or replace into info ( key, value ) values ( ?, ? )"
#    c.execute(q, (ov_store_last_updated_col, str(server_last_updated)))
#    conn.commit()
#    quiet_print("OakVar store cache has been fetched.", args=args)
