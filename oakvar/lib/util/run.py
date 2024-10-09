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
from typing import Dict
from typing import Any
from pathlib import Path
import logging


def update_status(status: str, logger=None, serveradmindb=None):
    if logger:
        logger.info(status)
    if serveradmindb:
        serveradmindb.update_job_info({"status": status})


def announce_module(module, logger=None, serveradmindb=None):
    update_status(
        f"running {module.name}",
        logger=logger,
        serveradmindb=serveradmindb,
    )


def log_variant_exception(
    lnum=0,
    line="",
    __input_data__=None,
    unique_excs=[],
    logger=None,
    error_logger=None,
    e=None,
):
    import traceback

    if logger:
        err_str = traceback.format_exc().rstrip()
        if err_str.endswith("None"):
            err_str_log = str(e)
        else:
            err_str_log = err_str
        if err_str_log not in unique_excs:
            unique_excs.append(err_str_log)
            logger.error(err_str_log)
    if error_logger:
        error_logger.error("\n[{:d}]{}\n({})\n#".format(lnum, line.rstrip(), str(e)))


# def print_log_handlers():
#    import logging
#
#    for k, v in logging.Logger.manager.loggerDict.items():
#        if "oakvar" in k:
#            print("+ [%s] {%s} " % (str.ljust(k, 20), str(v.__class__)[8:-2]))
#            if not isinstance(v, logging.PlaceHolder):
#                for h in v.handlers:
#                    print("     +++", str(h.__class__)[8:-2])
#                    for fld, val in h.__dict__.items():
#                        print("%s%s=%s" % ("   -", fld, val))


def get_y_or_n():
    from .util import is_in_jupyter_notebook

    while True:
        if is_in_jupyter_notebook():
            print(
                "Interactive mode is not available in Jupyter notebook. Proceeding..."
            )
            return True
        else:
            resp = input("Proceed? ([y]/n) > ")
        if resp == "y" or resp == "":
            return True
        if resp == "n":
            return False
        else:
            continue


def show_logo(outer=None):
    if not outer:
        return
    outer.write(
        r"""
==========================================================
 #######     ###    ##    ## ##     ##    ###    ########  
##     ##   ## ##   ##   ##  ##     ##   ## ##   ##     ## 
##     ##  ##   ##  ##  ##   ##     ##  ##   ##  ##     ## 
##     ## ##     ## #####    ##     ## ##     ## ########  
##     ## ######### ##  ##    ##   ##  ######### ##   ##   
##     ## ##     ## ##   ##    ## ##   ##     ## ##    ##  
 #######  ##     ## ##    ##    ###    ##     ## ##     ##
==========================================================
                                   Oak Bioinformatics, LLC
      Free with registration for personal and research use
            Commercial license required for commercial use
        Licensing and feedback: info@oakbioinformatics.com
                                        https://oakvar.com
""",
    )


def get_new_job_dir(jobs_dir: Path) -> Path:
    from datetime import datetime
    from pathlib import Path

    job_name = datetime.now().strftime(r"%y%m%d-%H%M%S")
    job_dir = Path(jobs_dir) / job_name
    if job_dir.exists():
        count = 1
        while True:
            job_name = datetime.now().strftime(r"%y%m%d-%H%M%S") + "_" + str(count)
            job_dir = Path(jobs_dir) / job_name
            if not job_dir.exists():
                break
            count += 1
    return job_dir


def get_new_job_name(jobs_dir: Path) -> str:
    from pathlib import Path

    job_dir = get_new_job_dir(jobs_dir)
    job_name = Path(job_dir).name
    return job_name


def set_logger_handler(
    logger,
    error_logger,
    output_dir: Optional[Path] = None,
    run_name: str = "",
    mode: str = "w",
    level: int = logging.INFO,
    logtofile: bool = False,
    clean: bool = False,
    newlog: bool = False,
):
    from os import remove
    from sys import stdout
    from sys import stderr
    from ..consts import LOG_SUFFIX

    # logging.basicConfig(level=logging.INFO, force=True)
    # logging.getLogger().propagate = False
    logging.getLogger().setLevel(logging.WARN)
    log_formatter = logging.Formatter(
        "%(asctime)s %(name)-20s %(message)s", "%Y/%m/%d %H:%M:%S"
    )
    err_formatter = logging.Formatter("%(name)s\t%(message)s")
    log_path: Optional[Path] = None
    error_log_path: Optional[Path] = None
    if logtofile and output_dir:
        log_path = Path(output_dir) / (run_name + LOG_SUFFIX)
        if (newlog or clean) and log_path.exists():
            remove(log_path)
        log_handler = logging.FileHandler(log_path, mode=mode)
    else:
        log_handler = logging.StreamHandler(stream=stdout)
    log_handler.setFormatter(log_formatter)
    if logtofile and output_dir:
        error_log_path = Path(output_dir) / (run_name + ".err")
        if error_log_path.exists():
            remove(error_log_path)
        error_log_handler = logging.FileHandler(error_log_path, mode=mode)
    else:
        error_log_handler = logging.StreamHandler(stream=stderr)
    error_log_handler.setFormatter(err_formatter)
    logger.setLevel(level)
    error_logger.setLevel(level)
    log_handler.setLevel(level)
    logger.addHandler(log_handler)
    error_log_handler.setLevel(level)
    error_logger.addHandler(error_log_handler)
    return log_path, error_log_path


def get_module_options(module_options_sl: Optional[List[str]], outer=None):
    module_options: Dict[str, Dict[str, Any]] = {}
    if not isinstance(module_options_sl, list):
        return module_options
    if not module_options_sl:
        return module_options
    for opt_str in module_options_sl:
        toks = opt_str.split("=")
        if len(toks) != 2:
            if outer:
                outer.write(
                    "Ignoring invalid module option {opt_str}. "
                    + "module-options should be module_name.key=value.\n",
                )
            continue
        k = toks[0]
        if k.count(".") != 1:
            if outer:
                outer.write(
                    "Ignoring invalid module option {opt_str}. "
                    + "module-options should be module_name.key=value.\n",
                )
            continue
        [module_name, key] = k.split(".")
        if module_name not in module_options:
            module_options[module_name] = {}
        v = toks[1]
        module_options[module_name][key] = v
    return module_options


def get_standardized_module_option(v: Any):
    import json

    if isinstance(v, str):
        if v.startswith("{"):  # dict
            v = v.replace("'", '"')
            v = json.loads(v)
        elif v.startswith("["):
            v = v.replace("'", '"')
            v = json.loads(v)
        elif ":" in v:
            v0 = {}
            for v1 in v.split("."):
                if ":" in v1:
                    v1toks = v1.split(":")
                    if len(v1toks) == 2:
                        level = v1toks[0]
                        v2s = v1toks[1].split(",")
                        v0[level] = v2s
            v = v0
        elif "," in v:
            v = [val for val in v.split(",") if val != ""]
    if v == "true":
        v = True
    elif v == "false":
        v = False
    return v


def get_spark_schema(module_names):
    from pyspark.sql.types import StructType  # type: ignore
    from ..module.local import get_module_conf
    from ... import get_mapper
    from ... import get_annotator

    modules = []
    for module_name in module_names:
        conf = get_module_conf(module_name)
        if conf.get("type") == "mapper":
            module = get_mapper(module_name)
        elif conf.get("type") == "annotator":
            module = get_annotator(module_name)
        else:
            raise ValueError(f"Module type {module_name} is not supported.")
        modules.append(module)
    schema = StructType()
    for module in modules:
        if module.conf.get("type", "annotator") == "mapper":
            add_spark_schema_field(schema, module, add_module_name=False)
        else:
            add_spark_schema_field(schema, module, add_module_name=True)
    return schema


def add_spark_schema_field(schema, module, add_module_name: bool = False):
    from pyspark.sql.types import StructField  # type: ignore
    from pyspark.sql.types import StringType  # type: ignore
    from pyspark.sql.types import IntegerType  # type: ignore
    from pyspark.sql.types import FloatType  # type: ignore

    module_name = module.module_name
    for v in module.conf.get("output_columns", []):
        ty = v["type"]
        if ty == "string":
            sty = StringType()
        elif ty == "int":
            sty = IntegerType()
        elif ty == "float":
            sty = FloatType()
        else:
            raise ValueError(f"Unknown type: {ty}")
        if not add_module_name:
            schema.add(StructField(v["name"], sty, True))
        else:
            schema.add(StructField(f"{module_name}__{v['name']}", sty, True))
