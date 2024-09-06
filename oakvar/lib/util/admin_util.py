# OakVar
#
# Copyright (c) 2024 Oak Bioinformatics, LLC
#
# All rights reserved.
#
# Do not distribute or use this software without obtaining
# a license from Oak Bioinformatics, LLC.
#
# Do not use this software to develop another software
# which competes with the products by Oak Bioinformatics, LLC,
# without obtaining a license for such use from Oak Bioinformatics, LLC.
#
# For personal use of non-commercial nature, you may use this software
# after registering with `ov store account create`.
#
# For research use of non-commercial nature, you may use this software
# after registering with `ov store account create`.
#
# For use by commercial entities, you must obtain a commercial license
# from Oak Bioinformatics, LLC. Please write to info@oakbioinformatics.com
# to obtain the commercial license.
# ================
# OpenCRAVAT
#
# MIT License
#
# Copyright (c) 2021 KarchinLab
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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
        ret["conf_path"] = str(conf_path)
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

    fn = "oakvar_example.vcf"
    ifn = Path(get_packagedir()) / "lib" / "assets" / fn
    ofn = Path(d) / fn
    shutil.copyfile(ifn, ofn)
    return ofn


def create_new_module(module_name: str, module_type: str, outer=None) -> bool:
    from shutil import copytree
    from pathlib import Path
    from ..system import get_modules_dir
    from ..module.cache import get_module_cache

    modules_dir = get_modules_dir()
    if not modules_dir:
        if outer:
            outer.error("modules_dir does not exist. Run `ov system setup`?")
        return False
    module_dir = Path(modules_dir) / (module_type + "s") / module_name
    template_dir = (
        Path(get_packagedir()) / "lib" / "assets" / "module_templates" / module_type
    )
    if not template_dir.exists():
        e = ValueError(
            f"{template_dir} does not exist. Maybe a wrong module_type {module_type}?"
        )
        if outer:
            outer.error(e)
        raise e
    copytree(template_dir, module_dir)
    for fn in module_dir.iterdir():
        new_fn = str(fn).replace("template", module_name)
        fn.rename(new_fn)
    customize_module_template(module_name, module_dir / f"{module_name}.md")
    customize_module_template(module_name, module_dir / f"{module_name}.yml")
    get_module_cache().update_local()
    return True


def customize_module_template(module_name: str, fpath: Path):
    with open(fpath) as f:
        lines = f.readlines()
    with open(fpath, "w") as wf:
        for line in lines:
            new_line = line.replace("MODULE_TITLE", module_name)
            wf.write(new_line)


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
                if isinstance(orig_v, dict) is False:
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
    from pathlib import Path
    from ..system import get_user_conf_path

    if isinstance(val, Path):
        val = str(val)
    user_conf = get_user_conf()
    if not user_conf:
        user_conf = {key: val}
    else:
        user_conf[key] = val
    user_conf_path = get_user_conf_path()
    wf = open(user_conf_path, "w")
    yaml.dump(user_conf, wf, default_flow_style=False)
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
