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
    while True:
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
              Licensed under AGPL-3 and commercial license
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

def get_module_options(module_options_sl: Optional[List[str]], outer=None):
    module_options: Dict[str, Dict[str, Any]] = {}
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
        if v.startswith("{"): # dict
            v = v.replace("'", "\"")
            v = json.loads(v)
        elif v.startswith("["):
            v = v.replace("'", "\"")
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

