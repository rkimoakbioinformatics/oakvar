from typing import Optional
from typing import List
from typing import Dict
from typing import Any
from typing import Union
from pathlib import Path
import logging
import sqlite3
import duckdb
import polars as pl


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


def get_log_formatter():
    import logging

    return logging.Formatter("%(asctime)s %(name)-20s %(message)s", "%Y/%m/%d %H:%M:%S")


def setup_ray_logger():
    import logging
    import sys

    # logging.getLogger().setLevel(logging.WARN)
    logger = logging.getLogger("ray")
    log_formatter = get_log_formatter()
    log_handler = logging.StreamHandler(stream=sys.stdout)
    log_handler.setFormatter(log_formatter)
    logger.addHandler(log_handler)


def set_logger_handler(
    logger,
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
    from ..consts import LOG_SUFFIX

    # logging.basicConfig(level=logging.INFO, force=True)
    # logging.getLogger().propagate = False
    # logging.getLogger().setLevel(logging.WARN)
    if logger:
        log_formatter = get_log_formatter()
        if logtofile and output_dir:
            log_path = Path(output_dir) / (run_name + LOG_SUFFIX)
            if (newlog or clean) and log_path.exists():
                remove(log_path)
            log_handler = logging.FileHandler(log_path, mode=mode)
        else:
            log_handler = logging.StreamHandler(stream=stdout)
        log_handler.setFormatter(log_formatter)
        logger.setLevel(level)
        log_handler.setLevel(level)
        logger.addHandler(log_handler)


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


def get_db_conn(
    dbpath: Union[str, Path]
) -> Union[sqlite3.Connection, duckdb.DuckDBPyConnection]:
    from ..consts import RESULT_DB_SUFFIX_DUCKDB

    if isinstance(dbpath, Path):
        dbpath = str(dbpath)
    if dbpath.endswith(RESULT_DB_SUFFIX_DUCKDB):
        conn = duckdb.connect(dbpath)
    else:
        conn = sqlite3.connect(dbpath)
    return conn


def open_result_database(dbpath: Path, use_duckdb: bool, clean: bool = False):
    import sqlite3
    import duckdb
    from os import remove

    if clean and dbpath.exists():
        remove(dbpath)
    if use_duckdb:
        conn = duckdb.connect(str(dbpath))
    else:
        conn = sqlite3.connect(dbpath)
        conn.execute('pragma journal_mode="wal"')
        conn.execute("pragma synchronous=0;")
        conn.execute("pragma journal_mode=off;")
        conn.execute("pragma cache_size=1000000;")
        conn.execute("pragma locking_mode=EXCLUSIVE;")
        conn.execute("pragma temp_store=MEMORY;")
    return conn


def initialize_err_series_data():
    err_series_data: Dict[str, List[Any]] = {}
    err_series_data["fileno"] = []
    err_series_data["lineno"] = []
    err_series_data["uid"] = []
    err_series_data["err"] = []
    return err_series_data


def add_to_err_series(
    err_series: Dict[str, List[Any]],
    fileno: Optional[int] = None,
    lineno: Optional[int] = None,
    uid: Optional[int] = None,
    errno: Optional[int] = None,
    err: Optional[str] = None,
):
    from ..consts import FILENO_KEY
    from ..consts import LINENO_KEY
    from ..consts import VARIANT_LEVEL_PRIMARY_KEY
    from ..consts import ERRNO_KEY
    from ..consts import ERR_KEY

    err_series[FILENO_KEY].append(fileno)
    err_series[LINENO_KEY].append(lineno)
    err_series[VARIANT_LEVEL_PRIMARY_KEY].append(uid)
    err_series[ERRNO_KEY].append(errno)
    err_series[ERR_KEY].append(err)


def get_pl_dtype(col: Dict[str, Any]) -> pl.PolarsDataType:
    ty: str = col.get("type", "")
    dtype: pl.PolarsDataType
    if ty in ["str", "string"]:
        dtype = pl.Utf8
    elif ty == "int":
        dtype = pl.Int32
    elif ty == "int64":
        dtype = pl.Int64
    elif ty == "float":
        dtype = pl.Float32
    elif ty == "bool":
        dtype = pl.Boolean
    elif "string[]" in ty:
        dtype = pl.List(pl.Utf8)
    elif "int[]" in ty:
        dtype = pl.List(pl.Int32)
    elif "int64[]" in ty:
        dtype = pl.List(pl.Int64)
    elif "float[]" in ty:
        dtype = pl.List(pl.Float32)
    else:
        dtype = pl.Utf8
    return dtype


def get_df_headers(
    output: Dict[str, Dict[str, Any]]
) -> Dict[str, Dict[str, pl.PolarsDataType]]:
    import polars as pl
    from ..consts import OUTPUT_COLS_KEY

    df_headers: Dict[str, Dict[str, pl.PolarsDataType]] = {}
    for table_name, table_output in output.items():
        df_headers[table_name] = {}
        coldefs = table_output.get(OUTPUT_COLS_KEY, [])
        for col in coldefs:
            ty = get_pl_dtype(col)
            df_headers[table_name][col.get("name")] = ty
    return df_headers
