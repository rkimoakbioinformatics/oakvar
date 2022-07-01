from typing import Optional
from typing import Tuple
from typing import List


def db_func(func):
    def encl_func(*args, **kwargs):
        conn, c = get_ov_store_cache_conn()
        ret = func(*args, conn=conn, c=c, **kwargs)
        return ret

    return encl_func


@db_func
def module_latest_version(module_name, conn=None, c=None):
    if not conn or not c:
        return None
    q = f"select code_version from modules where name=?"
    c.execute(q, (module_name,))
    ret = c.fetchone()
    if ret:
        return ret[0]
    else:
        return None


@db_func
def module_info_latest_version(module_name, conn=None, c=None):
    from distutils.version import LooseVersion
    from json import loads

    if not conn or not c:
        return None
    q = f"select info, code_version from modules where name=?"
    c.execute(q, (module_name,))
    ret = c.fetchall()
    latest_code_ver = None
    module_info = None
    for v in ret:
        info, code_ver = v
        if not latest_code_ver:
            latest_code_ver = LooseVersion(code_ver)
            module_info = info
        else:
            code_ver = LooseVersion(code_ver)
            if code_ver > latest_code_ver:
                latest_code_ver = code_ver
                module_info = info
    if module_info:
        module_info = loads(module_info)
    return module_info


@db_func
def module_config(module_name, version=None, conn=None, c=None) -> Optional[dict]:
    from json import loads
    from distutils.version import LooseVersion

    if not conn or not c:
        return None
    if version:
        q = f"select code_version, conf, store from modules where name=? and code_version=?"
        c.execute(q, (module_name, version))
    else:
        q = f"select code_version, conf, store from modules where name=?"
        c.execute(q, (module_name,))
    ret = c.fetchall()
    out = None
    latest = None
    if ret:
        for v in ret:
            code_ver, conf, store = v
            if not out or store == "ov":
                if not latest or LooseVersion(code_ver) > latest:
                    out = conf
                    latest = LooseVersion(code_ver)
    if out:
        return loads(out)
    else:
        return None


@db_func
def module_code_url(module_name: str, version=None, conn=None, c=None) -> Optional[str]:
    if not conn or not c:
        return None
    if not version:
        version = module_latest_version(module_name)
    q = f"select code_url from modules where name=? and code_version=?"
    c.execute(q, (module_name, version))
    ret = c.fetchone()
    if not ret:
        return None
    else:
        return ret[0]


@db_func
def module_data_url(module_name: str, version=None, conn=None, c=None) -> Optional[str]:
    if not conn or not c:
        return None
    if not version:
        version = module_latest_version(module_name)
    q = f"select data_url from modules where name=? and code_version=?"
    c.execute(q, (module_name, version))
    ret = c.fetchone()
    if not ret:
        return None
    else:
        return ret[0]


@db_func
def module_conf_url(module_name: str, version=None, conn=None, c=None) -> Optional[str]:
    if not conn or not c:
        return None
    if not version:
        version = module_latest_version(module_name)
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
    if not conn or not c:
        return None
    if version:
        q = f"select code_version, store from modules where name=? and code_version=?"
        c.execute(q, (module_name, version))
    else:
        q = f"select code_version, store from modules where name=?"
        c.execute(q, (module_name,))
    ret = c.fetchall()
    if len(ret) == 1:
        return ret[0][0]
    elif len(ret) > 1:
        for vs in ret:
            if vs[1] == channel:
                return vs[0]
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
    for table in ["modules", "info"]:
        if clean or table_exists(table):
            q = f"drop table if exists {table}"
            c.execute(q)
    conn.commit()


def create_ov_store_cache(conf=None, args={}):
    conn, c = get_ov_store_cache_conn(conf=conf)
    if not conn or not c:
        return False
    clean = args.get("clean")
    table = "modules"
    if clean or not table_exists(table):
        q = f"create table modules ( name text, type text, code_version text, data_version text, code_size int, data_size int, code_url text, data_url text, readme_url, logo_url text, conf_url text, description text, readme text, conf text, info text, store text, primary key ( name, code_version, store ) )"
        c.execute(q)
    table = "info"
    if clean or not table_exists(table):
        q = f"create table info ( key text primary key, value text )"
        c.execute(q)
    conn.commit()


@db_func
def fetch_ov_store_cache(
    email: Optional[str] = None,
    pw: Optional[str] = None,
    conn=None,
    c=None,
    args={},
):
    from ..consts import ov_store_email_key
    from ..consts import ov_store_pw_key
    from ..consts import ov_store_last_updated_col
    from ...system import get_sys_conf_value
    from ...system import get_user_conf
    from requests import Session
    from ...util.util import quiet_print
    from ...exceptions import StoreServerError
    from ...exceptions import AuthorizationError

    if not conn or not c:
        return False
    if not email and args:
        email = args.get("email")
        pw = args.get("pw")
    if not email:
        user_conf = get_user_conf()
        email = user_conf.get(ov_store_email_key)
        pw = user_conf.get(ov_store_pw_key)
    if not email or not pw:
        return False
    params = {"email": email, "pw": pw}
    s = Session()
    s.headers["User-Agent"] = "oakvar"
    store_url = get_sys_conf_value("store_url")
    if not store_url:
        return False
    server_last_updated, status_code = get_server_last_updated(email, pw)
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
    res = s.get(url, params=params)
    if res.status_code != 200:
        if res.status_code == 401:
            raise AuthorizationError()
        elif res.status_code == 500:
            raise StoreServerError()
        return False
    q = f"delete from modules"
    c.execute(q)
    conn.commit()
    res = res.json()
    cols = res["cols"]
    for row in res["data"]:
        q = f"insert into modules ( {', '.join(cols)} ) values ( {', '.join(['?'] * len(cols))} )"
        c.execute(q, row)
    q = f"insert or replace into info ( key, value ) values ( ?, ? )"
    c.execute(q, (ov_store_last_updated_col, str(server_last_updated)))
    conn.commit()
    quiet_print("OakVar store cache has been fetched.", args=args)


def get_server_last_updated(email: str, pw: str) -> Tuple[Optional[float], int]:
    from requests import Session
    from ...system import get_sys_conf_value

    s = Session()
    s.headers["User-Agent"] = "oakvar"
    store_url = get_sys_conf_value("store_url")
    if not store_url:
        return None, 0
    url = f"{store_url}/last_updated"
    params = {"email": email, "pw": pw}
    res = s.get(url, params=params)
    if res.status_code != 200:
        return None, res.status_code
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


@db_func
def get_manifest(conn=None, c=None) -> Optional[dict]:
    from json import loads

    if not conn or not c:
        return None
    q = "select name, info, logo_url, store from modules"
    c.execute(q)
    res = c.fetchall()
    mi = {}
    for r in res:
        name, info, logo_url, store = r
        if name not in mi or store == "ov":
            info = loads(info)
            info["logo_url"] = logo_url
            mi[name] = info
    return mi


@db_func
def get_readme(module_name: str, conn=None, c=None, version=None) -> Optional[str]:
    if not conn or not c:
        return None
    if not version:
        version = module_latest_version(module_name)
    q = "select readme, store from modules where name=? and code_version=?"
    c.execute(q, (module_name, version))
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

