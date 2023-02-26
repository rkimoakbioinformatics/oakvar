from typing import Optional
from typing import List
from pathlib import Path
from packaging.version import Version

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


def get_current_package_version() -> str:
    from pkg_resources import get_distribution

    version = get_distribution("oakvar").version
    return version


def get_package_versions() -> Optional[List[str]]:
    """
    Return available oakvar versions from pypi, sorted asc
    """
    import json
    from requests import get
    from requests.exceptions import ConnectionError
    from ..exceptions import InternetConnectionError

    try:
        r = get("https://pypi.org/pypi/oakvar/json", timeout=(3, None))
    except ConnectionError:
        raise InternetConnectionError()
    if r.status_code == 200:
        d = json.loads(r.text)
        all_vers: List[str] = list(d["releases"].keys())
        all_vers.sort(key=Version)
        return all_vers
    else:
        return None


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


def fn_new_exampleinput(d: str) -> Path:
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


def oakvar_version():
    global pkg_version
    if not pkg_version:
        pkg_version = get_current_package_version()
    return pkg_version


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


def get_max_version_supported_for_migration():
    return Version("1.7.0")


def get_latest_package_version() -> Optional[Version]:
    vers = get_package_versions()
    if vers:
        latest_ver = max([Version(v) for v in vers])
    else:
        latest_ver = None
    return latest_ver
