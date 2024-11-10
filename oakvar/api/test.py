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

from typing import List


def get_time_str() -> str:
    from datetime import datetime

    time_format = "[steel_blue]\\[%Y/%m/%d %H:%M:%S][white]"
    return datetime.now().strftime(time_format)


def test(modules: List[str] = [], output_dir: str="oakvar_module_test", clean: bool=False, **kwargs):
    from ..lib.module.local import get_local_module_info
    from ..lib.util.util import load_module
    from rich.console import Console
    import os
    import shutil

    from pathlib import Path
    console = Console()
    module_names = modules
    if not module_names:
        print("No modules specified")
        return {"passed": True, "details": {}, "num_passed": 0, "num_failed": 0}
    module_names.sort()
    result = {}
    cur_dir = os.getcwd()
    output_dir_p = Path(output_dir).resolve()
    if not output_dir_p.exists():
        os.mkdir(output_dir_p)
    for module_name in module_names:
        os.chdir(output_dir_p)
        test_dir = (output_dir_p / module_name).resolve()
        if clean and test_dir.exists():
            shutil.rmtree(test_dir)
        if not test_dir.exists():
            os.mkdir(test_dir)
        os.chdir(test_dir)
        console.print(f"{get_time_str()} {module_name}: testing... ")
        module_info = get_local_module_info(module_name)
        if not module_info:
            console.print(f"{get_time_str()}[yellow] {module_name}: not installed. Skipping.")
            result[module_name] = {"passed": True, "msg": "not installed"}
            continue
        m = load_module(module_info.script_path)
        if not m:
            console.print(f"{get_time_str()}[red] {module_name}: could not be loaded. Skipping.")
            result[module_name] = {"passed": False, "msg": "could not be loaded"}
            continue
        if "test" not in dir(m):
            console.print(f"{get_time_str()}[yellow] {module_name}: no test function. Skipping.")
            result[module_name] = {"passed": True, "msg": "no test function"}
            continue
        try:
            (success, msg) = m.test(**kwargs)
            msg = msg.rstrip()
            if success:
                console.print(f"{get_time_str()}[green] {module_name}: ok")
            else:
                console.print(f"{get_time_str()}[red] {module_name}: failed")
                console.print(f"[dark_goldenrod]{msg}")
        except NotImplementedError:
            console.print(f"{get_time_str()}[yellow]{module_name}: test function not implemented. Skipping.")
            result[module_name] = {"passed": True, "msg": "test function not implemented"}
            continue
        except Exception:
            import traceback
            msg = traceback.format_exc().rstrip()
            console.print(msg)
            result[module_name] = {"passed": False, "msg": msg}
            continue
        if success:
            result[module_name] = {"passed": True, "msg": msg}
        else:
            result[module_name] = {"passed": False, "msg": msg}
    os.chdir(cur_dir)
    passed = [v for v in result.keys() if result[v]["passed"]]
    failed = [v for v in result.keys() if not result[v]["passed"]]
    console.print(f"{get_time_str()} passed {len(passed)} failed {len(failed)}")
    for module_name in failed:
        console.print(f"{get_time_str()}[red] failed module: {module_name}")
    return {"passed": len(failed) == 0, "details": result, "num_passed": len(passed), "num_failed": len(failed)}
