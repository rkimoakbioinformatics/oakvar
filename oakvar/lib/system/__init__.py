from typing import Optional
from typing import Union
from typing import Dict
from pathlib import Path

custom_system_conf = None


def setup_system(
    clean: bool = False,
    refresh_db: bool = False,
    clean_cache_files: bool = False,
    setup_file: Optional[Path] = None,
    email: Optional[str] = None,
    pw: Optional[str] = None,
    publish_time: str = "",
    custom_system_conf: Optional[Dict] = None,
    outer=None,
    system_worker_state=None,
    install_mode: str = "",
    ws_id: str = "",
):
    from os import environ
    from ...api.module import installbase
    from .consts import sys_conf_path_key
    from ..store.ov import setup_ov_store_cache
    from ..util.run import show_logo
    from ...gui.serveradmindb import setup_serveradmindb

    _ = ws_id
    show_logo(outer=outer)
    # set up a sys conf file.
    conf = setup_system_conf(
        clean=clean,
        setup_file=setup_file,
        custom_system_conf=custom_system_conf,
        outer=outer,
    )
    add_system_dirs_to_system_conf(conf)
    save_system_conf(conf)
    if outer:
        outer.write(f"System configuration file: {conf[sys_conf_path_key]}")
    setup_system_dirs(conf=conf, outer=outer)
    # set up a user conf file.
    setup_user_conf_file(clean=clean, outer=outer)
    # set up a store account.
    if outer:
        outer.write("Logging in...")
    ret = setup_store_account(conf=conf, email=email, pw=pw, install_mode=install_mode)
    if ret.get("success") != True:
        if outer:
            outer.write("Login failed")
        return False
    if outer:
        outer.write(f"Logged in as {ret['email']}")
    # fetch ov store cache
    if outer:
        outer.write("Setting up store cache...")
    setup_ov_store_cache(
        refresh_db=refresh_db,
        clean_cache_files=clean_cache_files,
        clean=clean,
        publish_time=publish_time,
        outer=outer,
    )
    # set up a multiuser database.
    if outer:
        outer.write("Setting up administrative database...")
    setup_serveradmindb(clean=clean)
    # install base modules.
    environ[get_env_key(sys_conf_path_key)] = conf[sys_conf_path_key]
    if outer:
        outer.write("Installing system modules...")
    modules_dir_op = conf.get("modules_dir")
    modules_dir = Path(modules_dir_op) if modules_dir_op else None
    ret = installbase(
        modules_dir=modules_dir,
        no_fetch=True,
        conf=conf,
        outer=outer,
        system_worker_state=system_worker_state,
    )
    if ret is None or ret == 0 or ret is True:  # 0 or None?
        if outer:
            outer.write(f"Done setting up the system.")
        return True
    else:  # return False is converted to 1 with @cli_func.
        if outer:
            outer.write(
                f"Problem occurred while installing system modules. Return value is {ret}.\nPlease run `ov system setup` again to install the missing modules.\n"
            )
        return False


def setup_system_dirs(conf=None, outer=None):
    from .consts import root_dir_key
    from .consts import conf_dir_key
    from .consts import modules_dir_key
    from .consts import jobs_dir_key
    from .consts import log_dir_key
    from .consts import LIFTOVER_DIR_KEY

    if conf:
        create_dir_if_absent(conf[root_dir_key], outer=outer)
        create_dir_if_absent(conf[conf_dir_key], outer=outer)
        create_dir_if_absent(conf[modules_dir_key], outer=outer)
        create_dir_if_absent(conf[jobs_dir_key], outer=outer)
        create_dir_if_absent(conf[log_dir_key], outer=outer)
        create_dir_if_absent(conf[LIFTOVER_DIR_KEY], outer=outer)


def setup_system_conf(
    clean: bool = False,
    setup_file: Optional[Path] = None,
    custom_system_conf: Optional[Dict] = None,
    outer=None,
) -> dict:
    from .consts import sys_conf_path_key
    from os.path import exists

    conf = None
    if setup_file:
        conf = get_system_conf(sys_conf_path=setup_file, conf=custom_system_conf)
        if outer:
            outer.write(f"Loaded system configuration from {setup_file}.")
    else:
        conf = get_system_conf(conf=custom_system_conf)
    # set system conf path if absent in sys conf.
    sys_conf_path = conf.get(sys_conf_path_key)
    if not sys_conf_path:
        sys_conf_path = get_system_conf_path(conf=conf)
        conf[sys_conf_path_key] = sys_conf_path
    # if sys conf file does not exist,
    # this is the first time installing OakVar.
    if not sys_conf_path or not exists(sys_conf_path) or clean:
        # create the sys conf file.
        save_system_conf(conf)
        if outer:
            outer.write(f"Created {sys_conf_path}.")
    return conf


def show_no_user_account_prelude():
    print(
        f"""
###############################################################
#                                                             #
# Welcome to OakVar.                                          #
#                                                             #
# An OakVar Store account is needed for its proper operation. #
# of OakVar.                                                  #
#                                                             #
# It's free, is securely stored, and will be used only for    #
# the operation of and communication with OakVar.             #
#                                                             #
###############################################################
"""
    )


def show_email_verify_action_banner(email: str):
    print(
        f"""
> {email} has not been verified yet.
>
> Please check your inbox for a verification email
> and click the verification link in the email.
"""
    )


def setup_store_account(conf=None, email=None, pw=None, install_mode: str = "") -> dict:
    from ..store.ov.account import total_login

    return total_login(email=email, pw=pw, conf=conf, install_mode=install_mode)


def setup_user_conf_file(clean: bool = False, outer=None):
    from os.path import exists
    from shutil import copyfile
    from os import mkdir

    user_conf_dir = get_user_conf_dir()
    if not exists(user_conf_dir):
        mkdir(user_conf_dir)
    user_conf_path = get_user_conf_path()
    if not exists(user_conf_path) or clean:
        copyfile(get_default_user_conf_path(), user_conf_path)
        if outer:
            outer.write(f"Created: {user_conf_path}")
    # fill in missing fields, due to a newer version, with defaults.
    fill_user_conf_with_defaults_and_save()
    if outer:
        outer.write(f"User configuration file: {user_conf_path}.")


def fill_user_conf_with_defaults_and_save():
    user_conf = get_user_conf()
    default_user_conf = get_default_user_conf()
    for k, v in default_user_conf.items():
        if k not in user_conf:
            user_conf[k] = v
    user_conf_path = get_user_conf_path()
    with open(user_conf_path, "w") as wf:
        from oyaml import dump

        dump(user_conf, wf, default_flow_style=False)


def get_root_dir(conf=None):
    from .consts import root_dir_key

    return get_conf_dirvalue(root_dir_key, conf=conf)


def get_conf_dir(conf=None) -> Optional[Path]:
    from .consts import conf_dir_key

    return get_conf_dirvalue(conf_dir_key, conf=conf)


def get_modules_dir(conf=None) -> Optional[Path]:
    from .consts import modules_dir_key

    d = get_conf_dirvalue(modules_dir_key, conf=conf)
    return d


def get_jobs_dir(conf=None):
    from .consts import jobs_dir_key

    return get_conf_dirvalue(jobs_dir_key, conf=conf)


def get_log_dir(conf=None):
    from .consts import log_dir_key

    return get_conf_dirvalue(log_dir_key, conf=conf)


def get_conf_dirvalue(conf_key, conf=None) -> Optional[Path]:
    from pathlib import Path

    d: Optional[str] = get_sys_conf_str_value(conf_key, conf=conf)
    if d:
        return Path(d).absolute()
    else:
        return None


def get_cache_dir(cache_key, conf=None) -> Optional[Path]:
    d = get_conf_dir(conf=conf)
    if d:
        return d / cache_key
    return None


def get_default_logo_path() -> str:
    from pathlib import Path

    path = (
        Path(__file__).parent.parent.parent
        / "gui"
        / "webstore"
        / "images"
        / "no_logo_module.svg"
    )
    return str(path)


def get_logo_path(module_name: str, store: str, conf=None) -> Optional[Path]:
    from os.path import getsize

    fname = module_name + ".png"
    logo_dir = get_cache_dir("logo", conf=conf)
    if logo_dir:
        path = logo_dir / store / fname
        if (not path.exists() or getsize(path) == 0) and store == "ov":
            path = logo_dir / "oc" / fname
        return path
    else:
        return None


def get_sys_conf_str_value(conf_key: str, sys_conf_path: Optional[Path]=None, conf: Optional[dict]=None) -> Optional[str]:
    v = get_sys_conf_value(conf_key, sys_conf_path=sys_conf_path, conf=conf)
    if v is None:
        return None
    elif isinstance(v, str):
        return v
    else:
        return str(v)


def get_sys_conf_int_value(conf_key: str, sys_conf_path: Optional[Path]=None, conf: Optional[dict]=None) -> Optional[int]:
    v = get_sys_conf_value(conf_key, sys_conf_path=sys_conf_path, conf=conf)
    if isinstance(v, int):
        return v
    elif isinstance(v, str):
        return int(v)
    else:
        return None


def get_sys_conf_value(conf_key: str, sys_conf_path=None, conf=None) -> Optional[Union[str, int, float, dict]]:
    from os import environ
    from ..util.util import load_yml_conf
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


def set_sys_conf_value(key: str, in_value: str, ty: str, sys_conf_path=None, conf=None):
    sys_conf = get_system_conf(sys_conf_path=sys_conf_path, conf=conf)
    if ty == "int":
        value = int(in_value)
    elif ty == "float":
        value = float(in_value)
    else:
        value = in_value
    sys_conf[key] = value
    save_system_conf(sys_conf)


def get_user_conf() -> dict:
    from ..util.util import load_yml_conf

    user_conf_path = get_user_conf_path()
    user_conf = load_yml_conf(user_conf_path)
    return user_conf


def get_user_conf_dir() -> Path:
    from .consts import user_dir_fname

    home_dir = Path().home()
    user_conf_dir = home_dir / user_dir_fname
    return user_conf_dir


def get_user_conf_path() -> Path:
    from .consts import user_conf_fname

    user_conf_dir = get_user_conf_dir()
    user_conf_path = user_conf_dir / user_conf_fname
    return user_conf_path


def get_default_user_conf_path() -> Path:
    from .consts import user_conf_fname
    from ..util.admin_util import get_packagedir

    default_user_conf_path = get_packagedir() / "lib" / "assets" / user_conf_fname
    return default_user_conf_path


def get_default_user_conf() -> dict:
    from ..util.util import load_yml_conf

    default_user_conf_path = get_default_user_conf_path()
    default_user_conf = load_yml_conf(default_user_conf_path)
    return default_user_conf


def add_system_dirs_to_system_conf(system_conf: dict) -> dict:
    from pathlib import Path
    from .consts import root_dir_key
    from .consts import modules_dir_key
    from .consts import conf_dir_key
    from .consts import jobs_dir_key
    from .consts import log_dir_key
    from .consts import package_dir_key
    from .consts import sys_conf_path_key
    from .consts import LIFTOVER_DIR_KEY
    from .consts import LIFTOVER_DIR_NAME
    from ..util.admin_util import get_packagedir

    # conf_path
    if sys_conf_path_key in system_conf:
        sys_conf_path: Path = Path(system_conf[sys_conf_path_key])
    else:
        sys_conf_path = get_system_conf_path(conf=system_conf)
    system_conf[sys_conf_path_key] = str(sys_conf_path.expanduser())
    # root_dir
    if root_dir_key in system_conf:
        root_dir: Path = Path(system_conf[root_dir_key])
    else:
        root_dir = get_default_root_dir(conf=system_conf)
    system_conf[root_dir_key] = str(root_dir.expanduser())
    # conf_dir
    if conf_dir_key in system_conf:
        conf_dir: Path = Path(system_conf[conf_dir_key])
    else:
        conf_dir: Path = get_default_conf_dir(conf=system_conf)
    system_conf[conf_dir_key] = str(conf_dir.expanduser())
    # liftover dir
    liftover_dir = conf_dir / LIFTOVER_DIR_NAME
    system_conf[LIFTOVER_DIR_KEY] = str(liftover_dir)
    # modules_dir
    if modules_dir_key in system_conf:
        modules_dir = Path(system_conf[modules_dir_key])
    else:
        modules_dir = get_default_modules_dir(conf=system_conf)
    system_conf[modules_dir_key] = str(modules_dir.expanduser())
    # jobs_dir
    if jobs_dir_key in system_conf:
        jobs_dir = Path(system_conf[jobs_dir_key])
    else:
        jobs_dir = get_default_jobs_dir(conf=system_conf)
    system_conf[jobs_dir_key] = str(jobs_dir.expanduser())
    # log_dir
    if log_dir_key in system_conf:
        log_dir = Path(system_conf[log_dir_key])
    else:
        log_dir = get_default_log_dir(conf=system_conf)
    system_conf[log_dir_key] = str(log_dir.expanduser())
    # package_dir
    if package_dir_key in system_conf:
        package_dir = Path(system_conf[package_dir_key])
    else:
        package_dir = get_packagedir()
    system_conf[package_dir_key] = str(package_dir.expanduser())
    return system_conf


def augment_with_sys_conf_temp(conf: dict, conf_template: dict):
    for k_t, v_t in conf_template.items():
        if k_t not in conf:
            conf[k_t] = v_t
        else:
            ty_t = type(v_t)
            if ty_t == list:
                for v in v_t:
                    if v not in conf[k_t]:
                        conf[k_t].append(v)
            elif ty_t == dict:
                for kk_t, vv_t in conf[k_t].items():
                    if kk_t not in conf[k_t]:
                        conf[k_t][kk_t] = vv_t


def get_system_conf(sys_conf_path=None, conf=None) -> dict:
    from os import environ
    from os.path import exists
    from .consts import sys_conf_path_key
    from .consts import root_dir_key
    from .consts import modules_dir_key
    from .consts import log_dir_key
    from .consts import conf_dir_key
    from .consts import jobs_dir_key
    from ..util.util import load_yml_conf

    dir_keys = [modules_dir_key, log_dir_key, conf_dir_key, jobs_dir_key]
    # order is: given conf > custom conf path > env > sys conf > template
    # template
    final_conf = get_system_conf_template()
    # sys conf
    if not sys_conf_path:
        sp = get_system_conf_path()
        if sp and exists(sp):
            sys_conf = load_yml_conf(sp)
            final_conf.update(sys_conf)
            final_conf[sys_conf_path_key] = str(sp)
    # ENV
    for k in final_conf.keys():
        if k in dir_keys and final_conf.get(root_dir_key):
            continue
        ek = get_env_key(k)
        if ek in environ:
            final_conf[k] = environ.get(ek)
    for k in [root_dir_key, modules_dir_key, log_dir_key, conf_dir_key, jobs_dir_key]:
        env_key = get_env_key(k)
        if environ.get(env_key):
            final_conf[k] = environ.get(env_key)
    # custom sys conf path. update conf_path.
    if sys_conf_path:
        custom_sys_conf = load_yml_conf(sys_conf_path)
        if custom_sys_conf:
            for k, v in custom_sys_conf.items():
                if k in dir_keys and final_conf.get(root_dir_key):
                    continue
                final_conf[k] = v
            # final_conf.update(custom_sys_conf)
    # given conf
    if conf is not None:
        for k, v in conf.items():
            final_conf[k] = v
    conf_template = get_system_conf_template()
    augment_with_sys_conf_temp(final_conf, conf_template)
    return final_conf


def update_system_conf_file(d):
    from ..util.admin_util import recursive_update

    sys_conf = get_system_conf()
    sys_conf = recursive_update(sys_conf, d)
    write_system_conf_file(sys_conf)
    return True


def get_main_default_path():
    import os
    from .consts import user_conf_fname
    from ..util.admin_util import get_packagedir

    return os.path.join(get_packagedir(), user_conf_fname)


def set_modules_dir(path, __overwrite__=False):
    """
    Set the modules_dir to the directory in path.
    """
    import shutil
    import os
    from .consts import modules_dir_key

    path = os.path.abspath(os.path.expanduser(path))
    if not (os.path.isdir(path)):
        os.makedirs(path)
    old_conf_path = get_user_conf_path()
    update_system_conf_file({modules_dir_key: path})
    if not (os.path.exists(get_user_conf_path())):
        if os.path.exists(old_conf_path):
            overwrite_conf_path = old_conf_path
        else:
            overwrite_conf_path = get_main_default_path()
        shutil.copy(overwrite_conf_path, get_user_conf_path())


def create_dir_if_absent(d, outer=None):
    from os.path import exists
    from os import makedirs

    if d is not None:
        if not exists(d):
            makedirs(d)
            if outer:
                outer.write(f"Created {d}.")


def is_root_user():
    from os import environ
    from ..util.admin_util import get_platform

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
    from .consts import env_key_prefix

    return env_key_prefix + conf_key.upper()


def get_system_conf_path(conf=None) -> Path:
    from os import environ
    from pathlib import Path
    from .consts import sys_conf_fname
    from .consts import sys_conf_path_key
    from .consts import root_dir_key
    from .consts import conf_dir_key
    from .consts import conf_dir_name

    # custom conf
    if conf:
        if sys_conf_path_key in conf:
            return Path(conf.get(sys_conf_path_key))
        elif conf_dir_key in conf:
            return Path(conf.get(conf_dir_key)) / sys_conf_fname
        elif root_dir_key in conf:
            return Path(conf.get(root_dir_key)) / conf_dir_name / sys_conf_fname
    # ENV
    sys_conf_path_env_key = get_env_key(sys_conf_path_key)
    conf_dir_env_key = get_env_key(conf_dir_key)
    root_dir_env_key = get_env_key(root_dir_key)
    if sys_conf_path_env_key in environ:
        return Path(environ[sys_conf_path_env_key])
    elif conf_dir_env_key in environ:
        return Path(environ[conf_dir_env_key]) / sys_conf_fname
    elif root_dir_env_key in environ:
        return Path(environ[root_dir_env_key]) / conf_dir_name / sys_conf_fname
    # default
    root_dir = get_default_conf_dir(conf=conf)
    return Path(root_dir) / sys_conf_fname


def get_default_conf_dir(conf=None) -> Path:
    from .consts import conf_dir_name

    root_dir = get_default_root_dir(conf=conf)
    return root_dir / conf_dir_name


def get_default_modules_dir(conf=None) -> Path:
    from .consts import modules_dir_name

    root_dir = get_default_root_dir(conf=conf)
    return root_dir / modules_dir_name


def get_default_jobs_dir(conf=None) -> Path:
    from .consts import jobs_dir_name

    root_dir = get_default_root_dir(conf=conf)
    return root_dir / jobs_dir_name


def get_default_log_dir(conf=None):
    from .consts import log_dir_name

    root_dir = get_default_root_dir(conf=conf)
    return root_dir / log_dir_name


def get_default_root_dir(conf=None) -> Path:
    from os.path import expandvars
    from os import environ
    from pathlib import Path
    from ..util.admin_util import get_platform
    from .consts import root_dir_key

    if conf and root_dir_key in conf:
        d: str = conf.get(root_dir_key)
        return Path(d)
    pl = get_platform()
    root_dir = None
    if pl == "windows":
        root_dir = Path(expandvars("%systemdrive%")) / "open-cravat"
        if not root_dir.exists():
            root_dir = Path(expandvars("%systemdrive%")) / "oakvar"
    elif pl == "linux":
        path = ".oakvar"
        if is_root_user():
            sudo_user = environ.get("SUDO_USER")
            home = environ.get("HOME")
            if sudo_user is not None:
                root_dir = Path("/home") / sudo_user / path
            elif home is not None and home == "/root":  # Ubuntu in docker
                root_dir = Path(home) / ".oakvar"
            else:
                root_dir = Path.home() / path
        else:
            user = environ.get("USER")
            if user is not None:
                root_dir = Path("/home") / user / path
            else:
                root_dir = Path.home() / path
    elif pl == "macos":
        root_dir = Path("/Users/Shared/oakvar")
    else:
        root_dir = Path(".")
    return root_dir


def get_max_num_concurrent_modules_per_job() -> int:
    from .consts import max_num_concurrent_modules_per_job_key
    from .consts import (
        max_num_concurrent_annotators_per_job_key,
    )  # TODO: backward-compatibility. remove after some time.
    from .consts import DEFAULT_MAX_NUM_CONCURRENT_JOBS

    value = get_sys_conf_int_value(max_num_concurrent_modules_per_job_key)
    if not value:
        value = get_sys_conf_int_value(max_num_concurrent_annotators_per_job_key)
    if not value:
        value = DEFAULT_MAX_NUM_CONCURRENT_JOBS
    return value


def save_system_conf(conf: Dict):
    from .consts import sys_conf_path_key
    from oyaml import dump
    from os import makedirs
    from ..exceptions import SystemMissingException

    sys_conf_path: Optional[str] = conf.get(sys_conf_path_key)
    if sys_conf_path is None or sys_conf_path == "":
        raise SystemMissingException(msg="System conf file path is null")
    sys_conf_dir = Path(sys_conf_path).parent
    if not sys_conf_dir.exists():
        makedirs(sys_conf_dir)
    wf = open(sys_conf_path, "w")
    dump(conf, wf, default_flow_style=False)
    wf.close()


def get_system_conf_template_path():
    from .consts import sys_conf_fname
    from ..util.admin_util import get_packagedir

    return get_packagedir() / "lib" / "assets" / sys_conf_fname


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


def check_system_yml(outer=None) -> bool:
    from .consts import conf_dir_key
    from .consts import modules_dir_key
    from .consts import jobs_dir_key
    from .consts import log_dir_key

    if outer:
        outer.write("Checking system configuration file...")
    system_conf = get_system_conf()
    if not system_conf:
        if outer:
            outer.error("  System configuration file is missing.")
        return False
    system_conf_temp = get_system_conf_template()
    for k in system_conf_temp.keys():
        if k not in system_conf:
            if outer:
                outer.error(f"  System configuration file misses {k} field.")
            return False
    for k in [conf_dir_key, modules_dir_key, jobs_dir_key, log_dir_key]:
        if k not in system_conf:
            if outer:
                outer.error(f"  System configuration file misses {k} field.")
            return False
    return True


def check_user_yml(outer=None) -> bool:
    from pathlib import Path
    from ..util.util import load_yml_conf

    if outer:
        outer.write("Checking user configuration file...")
    user_conf_path = get_user_conf_path()
    if not Path(user_conf_path).exists():
        if outer:
            outer.error("User configuration file is missing.")
        return False
    user_conf = load_yml_conf(user_conf_path)
    default_user_conf = get_default_user_conf()
    for k in default_user_conf.keys():
        if k not in user_conf:
            if outer:
                outer.error(f"User configuration file misses {k} field.")
            return False
    return True


def check_system_directories(outer=None) -> bool:
    from .consts import conf_dir_key
    from .consts import modules_dir_key
    from .consts import jobs_dir_key
    from .consts import log_dir_key
    from os.path import exists

    if outer:
        outer.write("Checking system directories...")
    system_conf = get_system_conf(conf=None)
    if not system_conf:
        if outer:
            outer.error(f"System configuration file is missing.")
        return False
    for k in [conf_dir_key, modules_dir_key, jobs_dir_key, log_dir_key]:
        d = system_conf.get(k)
        if not d or not exists(d):
            if outer:
                outer.error(f"System directory {k} is missing.")
            return False
    return True


def check_account(outer=None) -> bool:
    from ..store.ov.account import token_set_exists
    from ..store.ov.account import check_logged_in_with_token

    if outer:
        outer.write("Checking OakVar account...")
    if not token_set_exists():
        if outer:
            outer.write(
                f"Store account information does not exist. Use `ov store account login` to log in or `ov store account create` to create one.\n"
            )
        return False
    if not check_logged_in_with_token(outer=outer):
        if outer:
            outer.write(f"Not logged in. Use `ov account login` to log in.")
        return False
    return True


def check_cache_files(outer=None) -> bool:
    from os import listdir

    if outer:
        outer.write("Checking OakVar store cache files...")
    for k in ["readme", "logo", "conf"]:
        d = get_cache_dir(k)
        if d:
            ov_dir = d / "ov"
            oc_dir = d / "oc"
            if len(listdir(ov_dir)) == 0 and len(listdir(oc_dir)) == 0:
                if outer:
                    outer.write(f"System directory {d} does not exist.")
                return False
    return True


def check_module_version_requirement(outer=None) -> bool:
    from ..util.admin_util import get_packagedir
    from ..util.util import compare_version
    from ..module.local import get_local_module_info

    if outer:
        outer.write("Checking module version requirements...")
    pkg_dir = get_packagedir()
    p = pkg_dir / "module_requirement.txt"
    if not p.exists():
        return True
    invalid_modules = []
    for line in open(p):
        [module_name, required_version] = line.strip().split()
        mi = get_local_module_info(module_name)
        if not mi:
            continue
        if not mi.code_version:
            continue
        if compare_version(required_version, mi.code_version) > 0:
            invalid_modules.append([module_name, required_version])
    if not invalid_modules:
        return True
    if outer:
        for module_name, required_version in invalid_modules:
            outer.write(f"Module version requirement not met for this version of OakVar: {module_name}>={required_version}")
    return False


def check(outer=None) -> bool:
    from rich.console import Console
    from rich.table import Table
    from rich.text import Text
    from rich import box
    from ..store.db import check_tables

    success = True
    ok = Text()
    ok.append("Ok", style="green")
    err = Text()
    err.append("Error", style="red")
    if check_system_yml(outer=outer) == True:
        if outer:
            outer.write("System configuration file Ok")
        status_system_yml = ok
    else:
        if outer:
            outer.error("System configuration file Error")
        status_system_yml = err
        success = False
    if check_user_yml(outer=outer):
        status_user_yml = ok
        if outer:
            outer.write("User configuration file Ok")
    else:
        status_user_yml = err
        if outer:
            outer.error("User configuration file Error")
        success = False
    if check_system_directories(outer=outer):
        status_system_directories = ok
        if outer:
            outer.write("System directories Ok")
    else:
        status_system_directories = err
        if outer:
            outer.error("System directories Error")
        success = False
    if check_account(outer=outer):
        if outer:
            outer.write("OakVar store account Ok")
        status_account = ok
    else:
        status_account = err
        if outer:
            outer.error("OakVar store account Error")
        success = False
    if check_tables(outer=outer):
        status_tables = ok
        if outer:
            outer.write("OakVar store database Ok")
    else:
        status_tables = err
        if outer:
            outer.error("OakVar store database Error")
        success = False
    if check_cache_files(outer=outer):
        status_cache_files = ok
        if outer:
            outer.write("OakVar store cache files Ok")
    else:
        status_cache_files = err
        if outer:
            outer.error("OakVar store cache files Error")
        success = False
    if check_module_version_requirement(outer=outer):
        status_module_version_requirement = ok
        if outer:
            outer.write("Module version requirement Ok")
    else:
        status_module_version_requirement = err
        if outer:
            outer.error("Module version requirement Error")
        success = False
    if outer:
        if success:
            outer.write(ok)
        else:
            outer.write(err)
        console = Console()
        table = Table(title="System Check Result", title_style="bold", box=box.SQUARE)
        table.add_column("Item")
        table.add_column("Status")
        table.add_row("System configuration file", status_system_yml)
        table.add_row("User configuration file", status_user_yml)
        table.add_row("System directories", status_system_directories)
        table.add_row("Store account", status_account)
        table.add_row("Store database", status_tables)
        table.add_row("Store cache files", status_cache_files)
        table.add_row("Module version requirements", status_module_version_requirement)
        console.print(table)
    return True


def get_user_jobs_dir(email=None) -> Optional[Path]:
    root_jobs_dir = get_jobs_dir()
    if not email:
        return None
    jobs_dir = root_jobs_dir / email
    return jobs_dir


def get_legacy_status_json_path_in_job_dir(
    job_dir: Optional[str], run_name=None
) -> Optional[str]:
    from pathlib import Path

    legacy_status_suffix = ".status.json"
    if not job_dir:
        return None
    job_dir_p = Path(job_dir).absolute()
    if run_name:
        legacy_status_json_path = job_dir_p / (run_name + legacy_status_suffix)
        return str(legacy_status_json_path)
    legacy_status_json_paths = list(job_dir_p.glob("*" + legacy_status_suffix))
    if not legacy_status_json_paths:
        return None
    return str(legacy_status_json_paths[0])


def get_legacy_status_json(job_dir: Optional[str]) -> Optional[dict]:
    from json import load
    from logging import getLogger

    try:
        legacy_status_path = get_legacy_status_json_path_in_job_dir(job_dir)
        if not legacy_status_path:
            return None
        with open(legacy_status_path) as f:
            try:
                legacy_status_json = load(f)
            except:
                return None
        return legacy_status_json
    except Exception as e:
        logger = getLogger()
        logger.exception(e)
        return None


def get_liftover_dir() -> Union[Path, None]:
    from .consts import LIFTOVER_DIR_NAME

    conf_dir = get_conf_dir()
    if not conf_dir:
        return None
    liftover_dir = conf_dir / LIFTOVER_DIR_NAME
    return liftover_dir


def get_license_dir() -> Path:
    from ..util.admin_util import get_packagedir

    return get_packagedir() / "lib" / "assets" / "license"

def show_license(outer=None):
    from rich.console import Console
    if not outer:
        outer = Console()
    show_oakvar_license(outer=outer)
    show_liftover_license(outer=outer)

def show_oakvar_license(outer=None):
    from ..util.inout import get_file_content_as_table

    if not outer:
        return
    fpath = get_license_dir() / "LICENSE"
    get_file_content_as_table(fpath, "OakVar License", outer=outer)

def show_liftover_license(outer=None):
    from ..util.inout import get_file_content_as_table

    if not outer:
        return
    fpath = get_license_dir() / "liftover.txt"
    get_file_content_as_table(fpath, "LiftOver License", outer=outer)

def update(outer=None):
    from subprocess import run
    from packaging.version import Version
    from ..util.admin_util import get_current_package_version
    from ..util.admin_util import get_latest_package_version

    if outer:
        outer.write("Updating OakVar PyPI package...")
    cur_ver = Version(get_current_package_version())
    pypi_ver = get_latest_package_version()
    if not pypi_ver or cur_ver > pypi_ver:
        if outer:
            outer.error(f"Installed OakVer version ({str(cur_ver)}) is higher than the latest version at PyPI ({str(pypi_ver)}). Aborting.")
        return True
    cmd = ["pip", "install", "-U", "oakvar"]
    cp = run(cmd)
    if cp.returncode != 0:
        if outer:
            outer.error(str(cp.stderr))
            outer.error("Updating OakVar PyPI package failed.")
        return False
    if outer:
        outer.write("Package updated successfully.")
        outer.write("Setting up system...")
    ret = setup_system(outer=outer)
    if ret == True:
        if outer:
            outer.write("System setup successful.")
    else:
        if outer:
            outer.error("System setup failed.")
    return ret

