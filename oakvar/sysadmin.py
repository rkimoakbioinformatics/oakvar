from typing import Optional

custom_system_conf = None


def setup_system(args):
    from os.path import exists, join
    from shutil import copyfile
    from .sysadmin_const import root_dir_key
    from .sysadmin_const import conf_dir_key
    from .sysadmin_const import modules_dir_key
    from .sysadmin_const import jobs_dir_key
    from .sysadmin_const import log_dir_key
    from .sysadmin_const import main_conf_fname
    from .admin_util import get_packagedir
    from .util import quiet_print
    from .cli_module import module_installbase
    from os import environ
    from .sysadmin_const import sys_conf_path_key
    from .sysadmin import get_env_key

    # load sys conf.
    conf = None
    sys_conf_path = args.get("setup_file")
    if sys_conf_path:
        quiet_print(f"Loading system configuration from {sys_conf_path}...", args=args)
        conf = get_system_conf(sys_conf_path=sys_conf_path)
    else:
        quiet_print(f"Finding system configuration...", args=args)
        conf = get_system_conf()
    # save sys conf.
    save_system_conf(conf)
    quiet_print(f"System configuration is at {conf['conf_path']}.", args=args)
    # make system dirs if absent.
    quiet_print(f"Checking system directories...", args=args)
    create_dir_if_absent(conf[root_dir_key], args)
    create_dir_if_absent(conf[conf_dir_key], args)
    create_dir_if_absent(conf[modules_dir_key], args)
    create_dir_if_absent(conf[jobs_dir_key], args)
    create_dir_if_absent(conf[log_dir_key], args)
    # copy cravat conf file.
    quiet_print(f"Checking main configuration file...", args=args)
    main_conf_path = get_main_conf_path(conf=conf)
    if not exists(main_conf_path):
        copyfile(join(get_packagedir(), main_conf_fname), main_conf_path)
        quiet_print(f"Created main configuration file at {main_conf_path}.", args=args)
    # copy oc manifest
    quiet_print(f"Checking store manifest file...", args=args)
    fetch_and_save_oc_manifest(args=args)
    # install base modules.
    environ[get_env_key(sys_conf_path_key)] = conf[sys_conf_path_key]
    quiet_print(f"Checking system modules...", args=args)
    args.update({"conf": conf})
    module_installbase(args)
    quiet_print(f"Done setting up the system", args=args)


def get_root_dir(conf=None):
    from .sysadmin_const import root_dir_key

    return get_conf_dirvalue(root_dir_key, conf=conf)


def get_conf_dir(conf=None):
    from .sysadmin_const import conf_dir_key

    return get_conf_dirvalue(conf_dir_key, conf=conf)


def get_modules_dir(conf=None):
    from .sysadmin_const import modules_dir_key

    d = get_conf_dirvalue(modules_dir_key, conf=conf)
    return d


def get_jobs_dir(conf=None):
    from .sysadmin_const import jobs_dir_key

    return get_conf_dirvalue(jobs_dir_key, conf=conf)


def get_log_dir(conf=None):
    from .sysadmin_const import log_dir_key

    return get_conf_dirvalue(log_dir_key, conf=conf)


def get_conf_dirvalue(conf_key, conf=None):
    from os.path import abspath

    d = get_sys_conf_value(conf_key, conf=conf)
    if d:
        d = abspath(d)
    return d


def get_sys_conf_value(conf_key, sys_conf_path=None, conf=None):
    from os import environ
    from .admin_util import load_yml_conf
    from os.path import exists

    # custom conf
    if conf is not None and conf_key in conf:
        return conf[conf_key]
    # custom conf file
    if sys_conf_path is not None:
        custom_conf = load_yml_conf(sys_conf_path)
        if conf_key in custom_conf:
            return custom_conf[conf_key]
    # ENV
    env_key = get_env_key(conf_key)
    if env_key in environ:
        return environ.get(env_key)
    # from default system conf location
    sys_conf_path = get_system_conf_path()
    if sys_conf_path and exists(sys_conf_path):
        sys_conf = load_yml_conf(sys_conf_path)
        if conf_key in sys_conf:
            return sys_conf[conf_key]
    # from template
    template = get_system_conf_template()
    if conf_key in template:
        return template[conf_key]
    return None


def get_system_conf(sys_conf_path=None, conf=None, no_default=False, no_custom=True):
    from os import environ
    from os.path import exists, dirname, abspath
    from .sysadmin_const import sys_conf_path_key
    from .sysadmin_const import root_dir_key
    from .sysadmin_const import modules_dir_key
    from .sysadmin_const import conf_dir_key
    from .sysadmin_const import jobs_dir_key
    from .sysadmin_const import log_dir_key
    from .sysadmin_const import package_dir_key
    from .admin_util import load_yml_conf

    # order is: given conf > custom conf path > env > sys conf > template
    # template
    final_conf = get_system_conf_template()
    # sys conf
    if sys_conf_path is None:
        sp = get_system_conf_path()
        if sp and exists(sp):
            sys_conf = load_yml_conf(sp)
            final_conf.update(sys_conf)
            final_conf[sys_conf_path_key] = sp
    # ENV
    for k in final_conf.keys():
        ek = get_env_key(k)
        if ek in environ:
            final_conf[k] = environ.get(ek)
    # custom sys conf path. update conf_path.
    if sys_conf_path is not None:
        custom_sys_conf = load_yml_conf(sys_conf_path)
        if custom_sys_conf is not None:
            final_conf.update(custom_sys_conf)
    # given conf
    if conf is not None:
        for k, v in conf.items():
            final_conf[k] = v
    # else use default sys conf if exists.
    if no_default:
        return final_conf
    # conf_path
    if sys_conf_path_key not in final_conf:
        final_conf[sys_conf_path_key] = get_system_conf_path(conf=final_conf)
    # root_dir
    if root_dir_key not in final_conf:
        final_conf[root_dir_key] = get_default_root_dir(conf=final_conf)
    # conf_dir
    if conf_dir_key not in final_conf:
        final_conf[conf_dir_key] = get_default_conf_dir(conf=final_conf)
    # modules_dir
    if modules_dir_key not in final_conf:
        final_conf[modules_dir_key] = get_default_modules_dir(conf=final_conf)
    # jobs_dir
    if jobs_dir_key not in final_conf:
        final_conf[jobs_dir_key] = get_default_jobs_dir(conf=final_conf)
    # log_dir
    if log_dir_key not in final_conf:
        final_conf[log_dir_key] = get_default_log_dir(conf=final_conf)
    # package_dir
    if package_dir_key not in final_conf:
        final_conf[package_dir_key] = dirname(abspath(__file__))
    if no_custom:
        return final_conf
    global custom_system_conf
    if custom_system_conf is not None:
        for k, v in custom_system_conf.items():
            final_conf[k] = v
    return final_conf


def show_system_conf(args):
    from oyaml import dump
    from os.path import exists
    from .util import quiet_print

    # args.setdefault("fmt", "json")
    # args.setdefault("to", "return")
    sys_conf_path = get_system_conf_path()
    if not sys_conf_path or not exists(sys_conf_path):
        return None
    conf = get_system_conf()
    if args.get("fmt") == "yaml":
        conf = dump(conf, default_flow_style=False)
    if args.get("to") == "stdout":
        quiet_print(conf, args=args)
    else:
        return conf


def update_system_conf_file(d):
    """
    Recursively update the system config and re-write to disk.
    """
    from .admin_util import recursive_update
    from .admin_util import update_mic

    sys_conf = get_system_conf(no_default=True)
    sys_conf = recursive_update(sys_conf, d)
    write_system_conf_file(sys_conf)
    update_mic()
    return True


def get_main_conf_path(conf=None):
    import os
    from .sysadmin_const import main_conf_fname

    conf_dir = get_conf_dir(conf=conf)
    if conf_dir is None:
        from .exceptions import SystemMissingException

        raise SystemMissingException(msg="conf_dir is missing")
    return os.path.join(conf_dir, main_conf_fname)


def get_main_default_path():
    import os
    from .sysadmin_const import main_conf_fname
    from .admin_util import get_packagedir

    return os.path.join(get_packagedir(), main_conf_fname)


def get_local_oc_manifest() -> Optional[dict]:
    oc_manifest_path = get_oc_manifest_path()
    from os.path import exists

    if not exists(oc_manifest_path):
        return None
    from oyaml import safe_load

    with open(oc_manifest_path) as f:
        oc_manifest = safe_load(f)
        return oc_manifest


def get_oc_manifest_path() -> str:
    from os.path import join
    from .sysadmin_const import oc_manifest_fn

    conf_dir = get_conf_dir()
    oc_manifest_path = join(conf_dir, oc_manifest_fn)
    return oc_manifest_path


def get_remote_oc_manifest_timestamp() -> Optional[float]:
    from requests import head
    from dateutil.parser import parse
    from .constants import oc_manifest_url

    response = head(oc_manifest_url)
    if response.status_code == 200:
        ts = parse(response.headers["Last-Modified"]).timestamp()
        return float(ts)
    else:
        return None


def fetch_oc_manifest_response():
    from requests import get
    from .constants import oc_manifest_url

    response = get(oc_manifest_url)
    if response.status_code == 200:
        return response
    else:
        return None


def has_newer_remote_oc_manifest(path: Optional[str] = None) -> bool:
    if not path:
        path = get_oc_manifest_path()
    if not path:
        return False
    from os.path import exists

    if not exists(path):
        return True
    from os.path import getmtime

    local_oc_manifest_ts = getmtime(path)
    remote_oc_manifest_ts = get_remote_oc_manifest_timestamp()
    if not remote_oc_manifest_ts:
        return False
    if remote_oc_manifest_ts > local_oc_manifest_ts:
        return True
    else:
        return False


def fetch_and_save_oc_manifest(path: Optional[str] = None, args={}):
    from .util import quiet_print

    if not path:
        path = get_oc_manifest_path()
    if not path:
        return
    if has_newer_remote_oc_manifest(path=path):
        oc_manifest_response = fetch_oc_manifest_response()
        if oc_manifest_response:
            with open(path, "w") as wf:
                wf.write(oc_manifest_response.text)
                quiet_print(f"Saved {path}", args=args)


def set_modules_dir(path, __overwrite__=False):
    """
    Set the modules_dir to the directory in path.
    """
    import shutil
    import os
    from .sysadmin_const import modules_dir_key

    path = os.path.abspath(os.path.expanduser(path))
    if not (os.path.isdir(path)):
        os.makedirs(path)
    old_conf_path = get_main_conf_path()
    update_system_conf_file({modules_dir_key: path})
    if not (os.path.exists(get_main_conf_path())):
        if os.path.exists(old_conf_path):
            overwrite_conf_path = old_conf_path
        else:
            overwrite_conf_path = get_main_default_path()
        shutil.copy(overwrite_conf_path, get_main_conf_path())


def create_dir_if_absent(d, args=None):
    from os.path import exists
    from os import makedirs
    from .util import quiet_print

    if d is not None:
        if not exists(d):
            makedirs(d)
            quiet_print(f"Created {d}", args=args)


def is_root_user():
    from os import environ
    from .admin_util import get_platform

    pl = get_platform()
    if pl == "windows":
        return False
    elif pl == "linux":
        if environ.get("SUDO_USER") is not None:
            return True
        elif environ.get("HOME") == "/root":  # docker ubuntu
            return True
        else:
            return False
    elif pl == "macos":
        return False


def get_env_key(conf_key):
    from .sysadmin_const import env_key_prefix

    return env_key_prefix + conf_key.upper()


def get_system_conf_path(conf=None):
    from os import environ
    from os.path import join
    from .sysadmin_const import system_conf_fname
    from .sysadmin_const import sys_conf_path_key

    # custom conf
    if conf is not None and sys_conf_path_key in conf:
        return conf.get(sys_conf_path_key)
    # ENV
    sys_conf_path = environ.get(get_env_key(sys_conf_path_key))
    if sys_conf_path is not None:
        return sys_conf_path
    # default
    root_dir = get_default_conf_dir(conf=conf)
    if root_dir:
        return join(root_dir, system_conf_fname)
    else:
        return None


def get_default_conf_dir(conf=None):
    from os.path import join as pathjoin
    from .sysadmin_const import conf_dir_name

    root_dir = get_default_root_dir(conf=conf)
    if root_dir:
        return pathjoin(root_dir, conf_dir_name)
    else:
        return None


def get_default_modules_dir(conf=None):
    from os.path import join as pathjoin
    from .sysadmin_const import modules_dir_name

    root_dir = get_default_root_dir(conf=conf)
    if root_dir:
        return pathjoin(root_dir, modules_dir_name)
    else:
        return None


def get_default_jobs_dir(conf=None):
    from os.path import join as pathjoin
    from .sysadmin_const import jobs_dir_name

    root_dir = get_default_root_dir(conf=conf)
    if root_dir:
        return pathjoin(root_dir, jobs_dir_name)
    else:
        return None


def get_default_log_dir(conf=None):
    from os.path import join as pathjoin
    from .sysadmin_const import log_dir_name

    root_dir = get_default_root_dir(conf=conf)
    if root_dir:
        return pathjoin(root_dir, log_dir_name)
    else:
        return None


def get_default_root_dir(conf=None):
    from os.path import exists, join, expandvars
    from os import sep, environ
    from pathlib import Path
    from .admin_util import get_packagedir
    from .admin_util import get_platform
    from .sysadmin_const import root_dir_key

    if conf is not None and root_dir_key in conf:
        return conf.get(root_dir_key)
    pl = get_platform()
    root_dir = None
    if pl == "windows":
        root_dir = join(expandvars("%systemdrive%"), sep, "open-cravat")
        if exists(root_dir) == False:  # OakVar first installation
            root_dir = join(expandvars("%systemdrive%"), sep, "oakvar")
    elif pl == "linux":
        path = ".oakvar"
        root_dir = get_packagedir()
        if (
            exists(join(root_dir, "conf")) == False
        ):  # packagedir/conf is the old conf dir of OpenCRAVAT.
            if is_root_user():
                sudo_user = environ.get("SUDO_USER")
                home = environ.get("HOME")
                if sudo_user is not None:
                    root_dir = join("/home", sudo_user, path)
                elif home is not None and home == "/root":  # Ubuntu in docker
                    root_dir = join(home, ".oakvar")
                else:
                    root_dir = join(str(Path.home()), path)
            else:
                user = environ.get("USER")
                if user is not None:
                    root_dir = join("/home", user, path)
                else:
                    root_dir = join(str(Path.home()), path)
    elif pl == "macos":
        root_dir = "/Users/Shared/open-cravat"
        if exists(root_dir) == False:  # OakVar first installation
            root_dir = "/Users/Shared/oakvar"
    return root_dir


def get_max_num_concurrent_annotators_per_job():
    from .sysadmin_const import max_num_concurrent_annotators_per_job_key

    return get_system_conf().get(max_num_concurrent_annotators_per_job_key)


def get_system_conf_dir():
    from os.path import dirname
    from .sysadmin import get_system_conf_path

    path = get_system_conf_path()
    if path:
        return dirname(path)
    else:
        return None


def copy_system_conf_template_if_absent(
    sys_conf_path=None, sys_conf_template_path=None, quiet=False
):
    from os.path import exists, join, dirname
    from os import makedirs
    from shutil import copy
    from .sysadmin_const import system_conf_template_fname
    from .sysadmin import get_system_conf_path
    from .admin_util import get_packagedir
    from .util import quiet_print

    if sys_conf_path is None:
        sys_conf_path = get_system_conf_path()
    if sys_conf_path and not exists(sys_conf_path):
        sys_conf_dir = dirname(sys_conf_path)
        if not exists(sys_conf_dir):
            makedirs(sys_conf_dir)
        sys_conf_template_path = join(get_packagedir(), system_conf_template_fname)
        copy(sys_conf_template_path, sys_conf_path)
        quiet_print(f"Created {sys_conf_path}", args={"quiet": quiet})


def save_system_conf(conf):
    from .sysadmin_const import sys_conf_path_key
    from oyaml import dump
    from os import makedirs
    from os.path import dirname, exists

    sys_conf_path = conf.get(sys_conf_path_key)
    if sys_conf_path is None or sys_conf_path == "":
        from .exceptions import SystemMissingException

        raise SystemMissingException(msg="System conf file path is null")
    sys_conf_dir = dirname(sys_conf_path)
    if not exists(sys_conf_dir):
        makedirs(sys_conf_dir)
    wf = open(conf[sys_conf_path_key], "w")
    dump(conf, wf, default_flow_style=False)
    wf.close()


def get_system_conf_template_path():
    from os.path import join
    from .sysadmin_const import system_conf_template_fname
    from .admin_util import get_packagedir

    return join(get_packagedir(), system_conf_template_fname)


def get_system_conf_template():
    from oyaml import safe_load

    with open(get_system_conf_template_path()) as f:
        d = safe_load(f)
        return d


def write_system_conf_file(d):
    from oyaml import dump

    path = get_system_conf_path()
    if path:
        with open(path, "w") as wf:
            wf.write(dump(d, default_flow_style=False))


def get_system_conf_info(conf=None, json=False):
    from oyaml import dump

    conf = get_system_conf(conf=conf)
    if json:
        content = conf
    else:
        content = dump(conf, default_flow_style=False)
    return content


def get_ov_store_cache_conn(conf=None):
    from sqlite3 import connect
    from .sysadmin_const import ov_store_cache_fn
    from os.path import join

    conf_dir: Optional[str] = get_conf_dir(conf=conf)
    if conf_dir:
        ov_store_cache_path = join(conf_dir, ov_store_cache_fn)
        conn = connect(ov_store_cache_path)
        cursor = conn.cursor()
        return conn, cursor
    return None, None


def drop_ov_store_cache(conf=None):
    conn, c = get_ov_store_cache_conn(conf=conf)
    if not conn or not c:
        return False
    q = f"drop table if exists modules"
    c.execute(q)
    conn.commit()


def create_ov_store_cache(conf=None):
    conn, c = get_ov_store_cache_conn(conf=conf)
    if not conn or not c:
        return False
    q = f"create table modules ( name text, type text, code_version text, data_version text, code_size int, data_size int, code_url text, data_url text, readme_url, conf_url text, description text, readme text, conf text, json text, store text )"
    c.execute(q)
    conn.commit()


def fetch_ov_store_cache(
    conf: Optional[dict] = None, email: Optional[str] = None, pw: Optional[str] = None
):
    from .sysadmin_const import ov_store_email_key
    from .sysadmin_const import ov_store_pw_key
    from requests import Session

    s = Session()
    if not email:
        email = get_sys_conf_value(ov_store_email_key)
    if not pw:
        pw = get_sys_conf_value(ov_store_pw_key)
    if not email or not pw:
        return False
    s.headers["User-Agent"] = "oakvar"
    store_url = get_sys_conf_value("store_url")
    if not store_url:
        return False
    url = f"{store_url}/fetchstore?email={email}&pw={pw}"
    res = s.get(url)
    if res.status_code != 200:
        return False
    conn, c = get_ov_store_cache_conn()
    if not conn or not c:
        return False
    q = f"delete from modules"
    c.execute(q)
    conn.commit()
    data = res.json()
    columns = data["columns"]
    for row in data["data"]:
        q = f"insert into modules ( name, type, code_version, data_version, code_size, data_size, code_url, data_url, readme_url, conf_url, description, conf, store ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        c.execute(q, row)
    conn.commit()
