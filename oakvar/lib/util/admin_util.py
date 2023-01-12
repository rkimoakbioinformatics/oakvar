from typing import Optional

pkg_version: Optional[str] = None


def get_user_conf():
    from ..system import get_user_conf_path
    from ..util.util import load_yml_conf
    from os.path import exists

    conf_path = get_user_conf_path()
    if exists(conf_path):
        ret = load_yml_conf(conf_path)
        ret["conf_path"] = conf_path
        return ret
    else:
        return None


def get_current_package_version():
    from pkg_resources import get_distribution

    version = get_distribution("oakvar").version
    return version


def get_default_assembly():
    conf = get_user_conf()
    if conf:
        default_assembly = conf.get("default_assembly", None)
        return default_assembly


def get_last_assembly():
    conf = get_user_conf()
    if conf:
        last_assembly = conf.get("last_assembly")
        return last_assembly


def get_latest_package_version():
    """
    Return latest oakvar version on pypi
    """
    all_vers = get_package_versions()
    if all_vers:
        return all_vers[-1]
    else:
        return None


def get_package_versions():
    """
    Return available oakvar versions from pypi, sorted asc
    """
    import json
    from requests import get
    from requests.exceptions import ConnectionError
    from packaging.version import Version
    from ..exceptions import InternetConnectionError

    try:
        r = get("https://pypi.org/pypi/oakvar/json", timeout=(3, None))
    except ConnectionError:
        raise InternetConnectionError()
    if r.status_code == 200:
        d = json.loads(r.text)
        all_vers = list(d["releases"].keys())
        all_vers.sort(key=Version)
        return all_vers
    else:
        return None


def get_widgets_for_annotator(annotator_name, skip_installed=False):
    from ..module.local import module_exists_local
    from ..module.remote import get_remote_module_info
    from ..module import list_remote
    from ..module.cache import get_module_cache

    linked_widgets = []
    l = list_remote()
    if not l:
        return None
    for widget_name in l:
        widget_info = get_remote_module_info(widget_name)
        if widget_info is not None and widget_info.type == "webviewerwidget":
            widget_config = get_module_cache().get_remote_module_piece_url(
                widget_name, "config"
            )
            if widget_config:
                linked_annotator = widget_config.get("required_annotator")
            else:
                linked_annotator = None
            if linked_annotator == annotator_name:
                if skip_installed and module_exists_local(widget_name):
                    continue
                else:
                    linked_widgets.append(widget_info)
    return linked_widgets


def input_formats():
    import os
    from ..system import get_modules_dir

    modules_dir = get_modules_dir()
    assert modules_dir is not None
    formats = set()
    d = os.path.join(modules_dir, "converters")
    if os.path.exists(d):
        fns = os.listdir(d)
        for fn in fns:
            if fn.endswith("-converter"):
                formats.add(fn.split("-")[0])
    return formats


def install_widgets_for_module(module_name):
    from ..module import install_module

    widget_name = "wg" + module_name
    install_module(widget_name)


def fn_new_exampleinput(d: str):
    from pathlib import Path
    import shutil

    fn = "exampleinput"
    ifn = Path(get_packagedir()) / "lib" / "assets" / fn
    ofn = Path(d) / fn
    shutil.copyfile(ifn, ofn)
    return ofn


def create_new_module(name: Optional[str] = None, type: Optional[str] = None):
    from shutil import copytree
    from pathlib import Path
    from ..system import get_modules_dir
    from ..module.cache import get_module_cache

    modules_dir = get_modules_dir()
    assert modules_dir is not None
    assert name is not None and type is not None
    module_dir = Path(modules_dir) / type / name
    template_dir = Path(get_packagedir()) / "lib" / "assets" / "module_templates" / type
    copytree(template_dir, module_dir)
    for fn in module_dir.iterdir():
        new_fn = str(fn).replace("template", name)
        fn.rename(new_fn)
    get_module_cache().update_local()


def recursive_update(d1, d2):
    """
    Recursively merge two dictionaries and return a copy.
    d1 is merged into d2. Keys in d1 that are not present in d2 are preserved
    at all levels. The default Dict.update() only preserved keys at the top
    level.
    """
    import copy

    d3 = copy.deepcopy(d1)  # Copy perhaps not needed. Test.
    for k, v in d2.items():
        if k in d3:
            orig_v = d3[k]
            if isinstance(v, dict):
                if isinstance(orig_v, dict) == False:
                    d3[k] = v
                else:
                    t = recursive_update(d3.get(k, {}), v)
                    d3[k] = t
            else:
                d3[k] = d2[k]
        else:
            d3[k] = v
    return d3


def report_issue():
    import webbrowser

    webbrowser.open("http://github.com/rkimoakbioinformatics/oakvar/issues")


def set_user_conf_prop(key, val):
    import oyaml as yaml
    from ..system import get_user_conf_path

    conf = get_user_conf()
    if conf:
        conf[key] = val
        wf = open(get_user_conf_path(), "w")
        yaml.dump(conf, wf, default_flow_style=False)
        wf.close()


def set_jobs_dir(d):
    from ..system import update_system_conf_file

    update_system_conf_file({"jobs_dir": d})


def oakvar_version():
    global pkg_version
    if not pkg_version:
        pkg_version = get_current_package_version()
    return pkg_version


def write_user_conf(user_conf):
    import oyaml as yaml
    from ..system import get_user_conf_path

    confpath = get_user_conf_path()
    wf = open(confpath, "w")
    yaml.dump(user_conf, wf, default_flow_style=False)
    wf.close()


def get_liftover_chain_paths():
    from os.path import join

    liftover_chains_dir = get_liftover_chains_dir()
    liftover_chain_paths = {
        "hg19": join(liftover_chains_dir, "hg19ToHg38.over.chain"),
        "hg18": join(liftover_chains_dir, "hg18ToHg38.over.chain"),
    }
    return liftover_chain_paths


def get_packagedir():
    from pathlib import Path

    return Path(__file__).parent.parent.parent.absolute()


def get_platform():
    from platform import platform

    pl = platform()
    if pl.startswith("Windows"):
        pl = "windows"
    elif pl.startswith("Darwin") or pl.startswith("macOS"):
        pl = "macos"
    elif pl.startswith("Linux"):
        pl = "linux"
    else:
        pl = "linux"
    return pl


def get_liftover_chains_dir():
    from pathlib import Path
    from os.path import join as pathjoin

    d_new = pathjoin(get_packagedir(), "lib", "liftover")
    d_old = pathjoin(get_packagedir(), "liftover")
    if Path(d_new).exists():
        return d_new
    elif Path(d_old).exists():
        return d_old
    else:
        return None


def get_max_version_supported_for_migration():
    from packaging.version import Version

    return Version("1.7.0")
