from typing import Optional
from typing import Dict
from typing import Any
from pathlib import Path

custom_system_conf = None


def setup_system(clean: bool=False, refresh_db: bool=False, clean_cache_files: bool=False, setup_file: Optional[str]=None, email: Optional[str]=None, pw: Optional[str]=None, publish_time: str="", custom_system_conf: Optional[Dict]=None, outer=None, system_worker_state=None, install_mode: str="", ws_id: str=""):
    from os import environ
    from ...api.module import installbase
    from .consts import sys_conf_path_key
    from ..store.ov import setup_ov_store_cache
    from ..util.run import show_logo
    from ...gui.serveradmindb import setup_serveradmindb

    _ = ws_id
    show_logo(outer=outer)
    # set up a sys conf file.
    conf = setup_system_conf(clean=clean, setup_file=setup_file, custom_system_conf=custom_system_conf, outer=outer)
    add_system_dirs_to_system_conf(conf)
    save_system_conf(conf)
    if outer:
        outer.write(f"System configuration file: {conf[sys_conf_path_key]}")
    setup_system_dirs(conf=conf, outer=outer)
    # set up a user conf file.
    setup_user_conf_file(clean=clean, conf=conf, outer=outer)
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
    setup_ov_store_cache(refresh_db=refresh_db, clean_cache_files=clean_cache_files, clean=clean, publish_time=publish_time, outer=outer)
    # set up a multiuser database.
    if outer:
        outer.write("Setting up administrative database...")
    setup_serveradmindb(clean=clean)
    # install base modules.
    environ[get_env_key(sys_conf_path_key)] = conf[sys_conf_path_key]
    if outer:
        outer.write("Installing system modules...")
    ret = installbase(clean_cache_files=clean_cache_files, refresh_db=refresh_db, clean=clean, publish_time=publish_time, no_fetch=True, conf=conf, outer=outer, system_worker_state=system_worker_state)
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

    if conf:
        create_dir_if_absent(conf[root_dir_key], outer=outer)
        create_dir_if_absent(conf[conf_dir_key], outer=outer)
        create_dir_if_absent(conf[modules_dir_key], outer=outer)
        create_dir_if_absent(conf[jobs_dir_key], outer=outer)
        create_dir_if_absent(conf[log_dir_key], outer=outer)


def setup_system_conf(clean: bool=False, setup_file: Optional[str]=None, custom_system_conf: Optional[Dict]=None, outer=None) -> dict:
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
        # use the content of an old OC sys conf if present.
        conf = update_new_system_conf_with_existing(conf)
        # create the sys conf file.
        save_system_conf(conf)
        if outer:
            outer.write(f"Created {sys_conf_path}.")
    return conf


def update_new_system_conf_with_existing(conf):
    from os.path import exists
    from ..util.util import load_yml_conf
    from .consts import sys_conf_path_key
    from ..store.consts import store_url_key

    oc_sys_conf_path = get_oc_system_conf_path()
    if exists(oc_sys_conf_path):
        old_conf = load_yml_conf(oc_sys_conf_path)
        for k, v in old_conf.items():
            # do not copy the old OC sys conf's conf_path.
            if k in [
                sys_conf_path_key,
                "conf_path",
                "publish_url",
                store_url_key,
                "base_modules",
            ]:
                continue
            conf[k] = v
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


def show_invalid_account_prelude():
    print(
        f"""
########################################################################
#                                                                      #
# An OakVar account was found in the user configuration, but           #
# not in the server.                                                   #
#                                                                      #
# Please use `ov issue` to report if you believe that it is            #
# the server's issue.                                                  #
#                                                                      #
# Otherwise, please enter an email address and a password to register. #
#                                                                      #
# It's free, is securely stored, and will be used only for             #
# the operation and communication of OakVar.                           #
#                                                                      #
########################################################################
"""
    )


def show_email_verify_action_banner():
    print(
        """

> The email and password have not been verified yet.
>
> Please check your inbox for a verification email
> and click the verification link in the email.

"""
    )


def setup_store_account(conf=None, email=None, pw=None, install_mode: str="") -> dict:
    from ..store.ov.account import total_login

    return total_login(email=email, pw=pw, conf=conf, install_mode=install_mode)


def setup_user_conf_file(clean: bool=False, conf: Optional[Dict]=None, outer=None):
    from os.path import exists
    from shutil import copyfile
    from os import mkdir

    user_conf_dir = get_user_conf_dir()
    if not exists(user_conf_dir):
        mkdir(user_conf_dir)
    user_conf_path = get_user_conf_path()
    if not exists(user_conf_path) or clean:
        oc_cravat_conf_path = get_oc_cravat_conf_path(conf=conf)
        if exists(oc_cravat_conf_path):
            # copy cravat.yml as oakvar.yml.
            copyfile(oc_cravat_conf_path, user_conf_path)
        else:
            # create oakvar.yml
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


def get_conf_dirvalue(conf_key, conf=None):
    from pathlib import Path

    d: Optional[str] = get_sys_conf_value(conf_key, conf=conf)
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
        Path(__file__).parent.parent
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


def get_sys_conf_value(conf_key, sys_conf_path=None, conf=None) -> Optional[Any]:
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


def get_system_conf(sys_conf_path=None, conf=None):
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
    conf_template = get_system_conf_template()
    final_conf = get_system_conf_template()
    # sys conf
    if not sys_conf_path:
        sp = get_system_conf_path()
        if sp and exists(sp):
            sys_conf = load_yml_conf(sp)
            final_conf.update(sys_conf)
            final_conf[sys_conf_path_key] = sp
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
            if k in dir_keys and final_conf.get(root_dir_key):
                continue
            final_conf[k] = v
    global custom_system_conf
    if custom_system_conf:
        for k, v in custom_system_conf.items():
            if k in dir_keys and final_conf.get(k):
                continue
            final_conf[k] = v
    augment_with_sys_conf_temp(final_conf, conf_template)
    return final_conf


def show_system_conf(args):
    from os.path import exists
    from rich.console import Console
    from rich.table import Table
    from rich.box import SQUARE
    from ..util.util import quiet_print

    # args.setdefault("fmt", "json")
    # args.setdefault("to", "return")
    sys_conf_path = get_system_conf_path()
    if not sys_conf_path or not exists(sys_conf_path):
        return None
    conf = get_system_conf()
    if args.get("to") == "stdout":
        if args.get("fmt") == "json":
            quiet_print(conf, args=args)
        else:
            console = Console()
            table = Table(title=conf.get("sys_conf_path"), box=SQUARE)
            table.add_column("Key")
            table.add_column("Value")
            for k, v in conf.items():
                table.add_row(k, str(v))
            console.print(table)
    else:
        return conf


def update_system_conf_file(d):
    from ..util.admin_util import recursive_update

    sys_conf = get_system_conf()
    sys_conf = recursive_update(sys_conf, d)
    write_system_conf_file(sys_conf)
    return True


def get_oc_cravat_conf(conf=None) -> dict:
    from ..util.util import load_yml_conf

    oc_cravat_conf_path = get_oc_cravat_conf_path(conf=conf)
    oc_cravat_conf = load_yml_conf(oc_cravat_conf_path)
    return oc_cravat_conf


def get_oc_cravat_conf_path(conf=None) -> Path:
    from .consts import oc_cravat_conf_fname
    from ..exceptions import SystemMissingException

    conf_dir = get_conf_dir(conf=conf)
    if conf_dir is None:
        raise SystemMissingException(msg="conf_dir is missing")
    return conf_dir / oc_cravat_conf_fname


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


def get_oc_system_conf_path(conf=None) -> Path:
    from os import environ
    from .consts import oc_system_conf_fname
    from .consts import sys_conf_path_key

    # custom conf
    if conf is not None and sys_conf_path_key in conf:
        return Path(conf[sys_conf_path_key])
    # ENV
    sys_conf_path = environ.get(get_env_key(sys_conf_path_key))
    if sys_conf_path is not None:
        return Path(sys_conf_path)
    # default
    root_dir = get_default_conf_dir(conf=conf)
    return root_dir / oc_system_conf_fname


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
    from ..util.admin_util import get_packagedir
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
        root_dir = get_packagedir()
        if not (root_dir / "conf").exists(): # packagedir/conf is the old conf dir of OpenCRAVAT.
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
        root_dir = Path("/Users/Shared/open-cravat")
        if not root_dir.exists(): # OakVar first installation
            root_dir = Path("/Users/Shared/oakvar")
    else:
        root_dir = Path(".")
    return root_dir


def get_max_num_concurrent_modules_per_job():
    from .consts import max_num_concurrent_modules_per_job_key
    from .consts import max_num_concurrent_annotators_per_job_key # TODO: backward-compatibility. remove after some time.

    value = get_system_conf().get(max_num_concurrent_modules_per_job_key)
    if not value:
        value = get_system_conf().get(max_num_concurrent_annotators_per_job_key)
    return value


def get_system_conf_dir():
    from os.path import dirname

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
    from .consts import sys_conf_fname
    from ..util.admin_util import get_packagedir
    from ..util.util import quiet_print

    if sys_conf_path is None:
        sys_conf_path = get_system_conf_path()
    if sys_conf_path and not exists(sys_conf_path):
        sys_conf_dir = dirname(sys_conf_path)
        if not exists(sys_conf_dir):
            makedirs(sys_conf_dir)
        sys_conf_template_path = join(get_packagedir(), sys_conf_fname)
        copy(sys_conf_template_path, sys_conf_path)
        quiet_print(f"Created {sys_conf_path}", args={"quiet": quiet})


def save_system_conf(conf: Dict):
    from .consts import sys_conf_path_key
    from oyaml import dump
    from os import makedirs
    from os.path import dirname, exists
    from ..exceptions import SystemMissingException

    sys_conf_path = conf.get(sys_conf_path_key)
    if sys_conf_path is None or sys_conf_path == "":
        raise SystemMissingException(msg="System conf file path is null")
    sys_conf_dir = dirname(sys_conf_path)
    if not exists(sys_conf_dir):
        makedirs(sys_conf_dir)
    wf = open(sys_conf_path, "w")
    dump(conf, wf, default_flow_style=False)
    wf.close()


def save_user_conf(user_conf):
    from oyaml import dump
    from os import makedirs
    from os.path import exists

    user_conf_dir = get_user_conf_dir()
    user_conf_path = get_user_conf_path()
    if not exists(user_conf_dir):
        makedirs(user_conf_dir)
    with open(user_conf_path, "w") as wf:
        dump(user_conf, wf, default_flow_style=False)


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


def get_system_conf_info(conf=None, json=False):
    from oyaml import dump

    conf = get_system_conf(conf=conf)
    if json:
        content = conf
    else:
        content = dump(conf, default_flow_style=False)
    return content


def check_system_yml(outer=None) -> bool:
    from .consts import conf_dir_key
    from .consts import modules_dir_key
    from .consts import jobs_dir_key
    from .consts import log_dir_key

    system_conf = get_system_conf()
    if not system_conf:
        if outer:
            outer.write("System configuration file is missing.")
        return False
    system_conf_temp = get_system_conf_template()
    for k in system_conf_temp.keys():
        if k not in system_conf:
            if outer:
                outer.write(f"System configuration file misses {k} field.")
            return False
    for k in [conf_dir_key, modules_dir_key, jobs_dir_key, log_dir_key]:
        if k not in system_conf:
            if outer:
                outer.write(f"System configuration file misses {k} field.")
            return False
    return True


def check_oakvar_yml(outer=None) -> bool:
    from pathlib import Path
    from ..util.util import load_yml_conf
    user_conf_path = get_user_conf_path()
    if not Path(user_conf_path).exists():
        if outer:
            outer.write("User configuration file is missing.")
        return False
    user_conf = load_yml_conf(user_conf_path)
    default_user_conf = get_default_user_conf()
    for k in default_user_conf.keys():
        if k not in user_conf:
            if outer:
                outer.write(f"User configuration file misses {k} field.")
            return False
    return True


def check_system_directories(outer=None) -> bool:
    from .consts import conf_dir_key
    from .consts import modules_dir_key
    from .consts import jobs_dir_key
    from .consts import log_dir_key
    from os.path import exists

    system_conf = get_system_conf(conf=None)
    for k in [conf_dir_key, modules_dir_key, jobs_dir_key, log_dir_key]:
        d = system_conf[k]
        if not exists(d):
            if outer:
                outer.write(f"System directory {k} is missing.")
            return False
    return True


def check_account(outer=None) -> bool:
    from ..store.ov.account import token_set_exists
    from ..store.ov.account import check_logged_in_with_token

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


def check(outer=None) -> bool:
    from ..store.db import check_tables

    if not check_system_yml(outer=outer):
        return False
    if not check_oakvar_yml(outer=outer):
        return False
    if not check_system_directories(outer=outer):
        return False
    if not check_account(outer=outer):
        return False
    if not check_tables(outer=outer):
        return False
    if not check_cache_files(outer=outer):
        return False
    if outer:
        outer.write(f"Success")
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
