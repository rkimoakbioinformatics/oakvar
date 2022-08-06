custom_system_conf = None


def setup_system(args=None):
    from ..util.util import quiet_print
    from ..cli.module import installbase
    from os import environ
    from .consts import sys_conf_path_key
    from ..store.ov import setup_ov_store_cache
    from ..util.util import show_logo
    from ..exceptions import ArgumentError

    if not args:
        raise ArgumentError("necessary arguments were not provided.")
    show_logo()
    # set up a sys conf file.
    conf = setup_system_conf(args=args)
    add_system_dirs_to_system_conf(conf)
    save_system_conf(conf)
    quiet_print(f"System configuration file: {conf[sys_conf_path_key]}", args=args)
    setup_system_dirs(conf=conf, args=args)
    # set up a user conf file.
    setup_user_conf_file(args=args)
    # set up a store account.
    if not setup_store_account(args=args, conf=conf):
        return False
    # fetch ov store cache
    setup_ov_store_cache(conf=conf, args=args)
    # install base modules.
    environ[get_env_key(sys_conf_path_key)] = conf[sys_conf_path_key]
    args.update({"conf": conf})
    ret = installbase(args)
    if ret is None or ret == 0 or ret is True:  # 0 or None?
        quiet_print(f"Done setting up the system", args=args)
        return True
    else:  # return False is converted to 1 with @cli_func.
        quiet_print(f"Problem occurred while setting up the system. Return value is {ret}", args=args)
        return False


def setup_system_dirs(conf=None, args=None):
    from .consts import root_dir_key
    from .consts import conf_dir_key
    from .consts import modules_dir_key
    from .consts import jobs_dir_key
    from .consts import log_dir_key

    if conf:
        create_dir_if_absent(conf[root_dir_key], args)
        create_dir_if_absent(conf[conf_dir_key], args)
        create_dir_if_absent(conf[modules_dir_key], args)
        create_dir_if_absent(conf[jobs_dir_key], args)
        create_dir_if_absent(conf[log_dir_key], args)


def setup_system_conf(args={}) -> dict:
    from ..util.util import quiet_print
    from .consts import sys_conf_path_key
    from os.path import exists

    conf = None
    clean = args.get("clean")
    setup_file = args.get("setup_file")
    if setup_file:
        conf = get_system_conf(sys_conf_path=setup_file)
        quiet_print(f"Loaded system configuration from {setup_file}", args=args)
    else:
        conf = get_system_conf()
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
        quiet_print(f"Created {sys_conf_path}", args=args)
    return conf


def update_new_system_conf_with_existing(conf):
    from ..util.util import load_yml_conf
    from os.path import exists
    from .consts import sys_conf_path_key

    oc_sys_conf_path = get_oc_system_conf_path()
    if exists(oc_sys_conf_path):
        old_conf = load_yml_conf(oc_sys_conf_path)
        for k, v in old_conf.items():
            # do not copy the old OC sys conf's conf_path.
            if k in [
                sys_conf_path_key,
                "conf_path",
                "publish_url",
                "store_url",
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
>
> Afterwards, press Enter to continue."""
    )


def setup_store_account(args={}, conf=None, email=None, pw=None) -> bool:
    from ..store.ov.account import total_login

    return total_login(email=email, pw=pw, args=args, conf=conf)


def setup_user_conf_file(args={}, conf=None):
    from os.path import exists
    from shutil import copyfile
    from ..util.util import quiet_print
    from os import mkdir

    clean = args.get("clean")
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
        quiet_print(f"Created: {user_conf_path}", args=args)
    # fill in missing fields, due to a newer version, with defaults.
    fill_user_conf_with_defaults_and_save()
    quiet_print(f"User configuration file: {user_conf_path}.", args=args)


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


def get_conf_dir(conf=None):
    from .consts import conf_dir_key

    return get_conf_dirvalue(conf_dir_key, conf=conf)


def get_modules_dir(conf=None):
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
    from os.path import abspath

    d = get_sys_conf_value(conf_key, conf=conf)
    if d:
        d = abspath(d)
    return d


def get_cache_dir(cache_key, conf=None):
    from os.path import join

    d = get_conf_dir(conf=conf)
    return join(d, cache_key)


def get_logo_path(module_name: str, store: str, conf=None) -> str:
    from os.path import join

    return join(get_cache_dir("logo", conf=conf), store, module_name + ".png")


def get_sys_conf_value(conf_key, sys_conf_path=None, conf=None):
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


def get_user_conf() -> dict:
    from ..util.util import load_yml_conf

    user_conf_path = get_user_conf_path()
    user_conf = load_yml_conf(user_conf_path)
    return user_conf


def get_user_conf_dir() -> str:
    from os.path import expanduser
    from os.path import join
    from .consts import user_dir_fname

    home_dir = expanduser("~")
    user_conf_dir = join(home_dir, user_dir_fname)
    return user_conf_dir


def get_user_conf_path() -> str:
    from os.path import join
    from .consts import user_conf_fname

    user_conf_dir = get_user_conf_dir()
    user_conf_path = join(user_conf_dir, user_conf_fname)
    return user_conf_path


def get_default_user_conf_path() -> str:
    from .consts import user_conf_fname
    from ..util.admin_util import get_packagedir
    from os.path import join

    default_user_conf_path = join(get_packagedir(), user_conf_fname)
    return default_user_conf_path


def get_default_user_conf() -> dict:
    from ..util.util import load_yml_conf

    default_user_conf_path = get_default_user_conf_path()
    default_user_conf = load_yml_conf(default_user_conf_path)
    return default_user_conf


def add_system_dirs_to_system_conf(system_conf: dict) -> dict:
    from .consts import root_dir_key
    from .consts import modules_dir_key
    from .consts import conf_dir_key
    from .consts import jobs_dir_key
    from .consts import log_dir_key
    from .consts import package_dir_key
    from .consts import sys_conf_path_key
    from ..util.admin_util import get_packagedir

    # conf_path
    if sys_conf_path_key not in system_conf:
        system_conf[sys_conf_path_key] = get_system_conf_path(conf=system_conf)
    # root_dir
    if root_dir_key not in system_conf:
        system_conf[root_dir_key] = get_default_root_dir(conf=system_conf)
    # conf_dir
    if conf_dir_key not in system_conf:
        system_conf[conf_dir_key] = get_default_conf_dir(conf=system_conf)
    # modules_dir
    if modules_dir_key not in system_conf:
        system_conf[modules_dir_key] = get_default_modules_dir(conf=system_conf)
    # jobs_dir
    if jobs_dir_key not in system_conf:
        system_conf[jobs_dir_key] = get_default_jobs_dir(conf=system_conf)
    # log_dir
    if log_dir_key not in system_conf:
        system_conf[log_dir_key] = get_default_log_dir(conf=system_conf)
    # package_dir
    if package_dir_key not in system_conf:
        system_conf[package_dir_key] = get_packagedir()
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
    from oyaml import dump
    from os.path import exists
    from ..util.util import quiet_print

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


def get_oc_cravat_conf_path(conf=None):
    import os
    from .consts import oc_cravat_conf_fname

    conf_dir = get_conf_dir(conf=conf)
    if conf_dir is None:
        from ..exceptions import SystemMissingException

        raise SystemMissingException(msg="conf_dir is missing")
    return os.path.join(conf_dir, oc_cravat_conf_fname)


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


def create_dir_if_absent(d, args=None):
    from os.path import exists
    from os import makedirs
    from ..util.util import quiet_print

    if d is not None:
        if not exists(d):
            makedirs(d)
            quiet_print(f"Created {d}", args=args)


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


def get_system_conf_path(conf=None):
    from os import environ
    from os.path import join
    from .consts import sys_conf_fname
    from .consts import sys_conf_path_key
    from .consts import root_dir_key
    from .consts import conf_dir_key
    from .consts import conf_dir_name

    # custom conf
    if conf:
        if sys_conf_path_key in conf:
            return conf.get(sys_conf_path_key)
        elif conf_dir_key in conf:
            return join(conf.get(conf_dir_key), sys_conf_fname)
        elif root_dir_key in conf:
            return join(conf.get(root_dir_key), conf_dir_name, sys_conf_fname)
    # ENV
    sys_conf_path_env_key = get_env_key(sys_conf_path_key)
    conf_dir_env_key = get_env_key(conf_dir_key)
    root_dir_env_key = get_env_key(root_dir_key)
    if sys_conf_path_env_key in environ:
        return environ.get(sys_conf_path_env_key)
    elif conf_dir_env_key in environ:
        return join(environ.get(conf_dir_env_key, ""), sys_conf_fname)
    elif root_dir_env_key in environ:
        return join(environ.get(root_dir_env_key, ""), conf_dir_name, sys_conf_fname)
    # default
    root_dir = get_default_conf_dir(conf=conf)
    return join(root_dir, sys_conf_fname)


def get_oc_system_conf_path(conf=None):
    from os import environ
    from os.path import join
    from .consts import oc_system_conf_fname
    from .consts import sys_conf_path_key

    # custom conf
    if conf is not None and sys_conf_path_key in conf:
        return conf.get(sys_conf_path_key)
    # ENV
    sys_conf_path = environ.get(get_env_key(sys_conf_path_key))
    if sys_conf_path is not None:
        return sys_conf_path
    # default
    root_dir = get_default_conf_dir(conf=conf)
    return join(root_dir, oc_system_conf_fname)


def get_default_conf_dir(conf=None):
    from os.path import join as pathjoin
    from .consts import conf_dir_name

    root_dir = get_default_root_dir(conf=conf)
    return pathjoin(root_dir, conf_dir_name)


def get_default_modules_dir(conf=None):
    from os.path import join as pathjoin
    from .consts import modules_dir_name

    root_dir = get_default_root_dir(conf=conf)
    return pathjoin(root_dir, modules_dir_name)


def get_default_jobs_dir(conf=None):
    from os.path import join as pathjoin
    from .consts import jobs_dir_name

    root_dir = get_default_root_dir(conf=conf)
    return pathjoin(root_dir, jobs_dir_name)


def get_default_log_dir(conf=None):
    from os.path import join as pathjoin
    from .consts import log_dir_name

    root_dir = get_default_root_dir(conf=conf)
    return pathjoin(root_dir, log_dir_name)


def get_default_root_dir(conf=None):
    from os.path import exists, join, expandvars
    from os import sep, environ
    from pathlib import Path
    from ..util.admin_util import get_packagedir
    from ..util.admin_util import get_platform
    from .consts import root_dir_key

    if conf and root_dir_key in conf:
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
    else:
        root_dir = "."
    return root_dir


def get_max_num_concurrent_annotators_per_job():
    from .consts import max_num_concurrent_annotators_per_job_key

    return get_system_conf().get(max_num_concurrent_annotators_per_job_key)


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


def save_system_conf(conf):
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
    wf = open(conf[sys_conf_path_key], "w")
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
    from os.path import join
    from .consts import sys_conf_fname
    from ..util.admin_util import get_packagedir

    return join(get_packagedir(), sys_conf_fname)


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


def check_system_yml(args={}) -> bool:
    from .consts import conf_dir_key
    from .consts import modules_dir_key
    from .consts import jobs_dir_key
    from .consts import log_dir_key
    from ..util.util import quiet_print

    system_conf = get_system_conf()
    if not system_conf:
        quiet_print("system configuration file is missing", args=args)
        return False
    system_conf_temp = get_system_conf_template()
    for k in system_conf_temp.keys():
        if k not in system_conf:
            quiet_print(f"system configuration file misses {k} field.", args=args)
            return False
    for k in [conf_dir_key, modules_dir_key, jobs_dir_key, log_dir_key]:
        if k not in system_conf:
            quiet_print(f"system configuration file misses {k} field.", args=args)
            return False
    return True


def check_oakvar_yml(args={}) -> bool:
    from ..util.util import quiet_print

    user_conf = get_user_conf()
    if not user_conf:
        quiet_print("user configuration file is missing", args=args)
        return False
    user_conf_temp = get_default_user_conf()
    for k in user_conf_temp.keys():
        if k not in user_conf:
            quiet_print(f"user configuration file misses {k} field.", args=args)
            return False
    return True


def check_system_directories(args={}) -> bool:
    from ..util.util import quiet_print
    from .consts import conf_dir_key
    from .consts import modules_dir_key
    from .consts import jobs_dir_key
    from .consts import log_dir_key
    from os.path import exists

    system_conf = get_system_conf(conf=None)
    for k in [conf_dir_key, modules_dir_key, jobs_dir_key, log_dir_key]:
        d = system_conf[k]
        if not exists(d):
            quiet_print(f"system directory {k} is missing.", args=args)
            return False
    return True


def check_account(args={}) -> bool:
    from ..util.util import quiet_print
    from ..store.ov.account import token_set_exists
    from ..store.ov.account import check

    if not token_set_exists():
        quiet_print(
            f"store account information does not exist. Use `ov store account login` to log in or `ov store account create` to create one.",
            args=args,
        )
        return False
    if not check(args={"quiet": True}):
        quiet_print(f"not logged in. Use `ov account login` to log in.", args=args)
        return False
    return True


def check_cache_files(args={}) -> bool:
    from os.path import join
    from os import listdir
    from ..util.util import quiet_print

    for k in ["readme", "logo", "conf"]:
        d = join(get_cache_dir(k), "oc")
        if len(listdir(d)) == 0:
            quiet_print(f"system directory {d} does not exist.", args=args)
            return False
    return True


def check(args) -> bool:
    from ..util.util import quiet_print
    from ..store.db import check_tables

    if not check_system_yml(args=args):
        return False
    if not check_oakvar_yml(args=args):
        return False
    if not check_system_directories(args=args):
        return False
    if not check_account(args=args):
        return False
    if not check_tables(args=args):
        return False
    if not check_cache_files(args=args):
        return False
    quiet_print(f"success", args=args)
    return True

