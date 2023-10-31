# OakVar Dual License
# 
# Copyright (c) 2023 Oak Bioinformatics, LLC
# 
# This program is dual licensed under the Affero GPL-3.0 or later for non-commercial, 
# open source use, and a commercial license, which is available for purchase, 
# for commercial use.
# 
# For commercial use, please contact Oak Bioinformatics, LLC for obtaining a
# commercial license. OakVar commercial license does not impose the Affero GPL
# open-source licensing terms, conditions, and limitations. To obtain a
# commercial-use license of OakVar, please visit our website at
# https://oakbioinformatics.com or contact us at info@oakbioinformatics.com for
# more information.
# 
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

servermode = None


def unpack_eud(eud={}):
    from ..lib.consts import VARIANT_LEVEL_PRIMARY_KEY

    email = eud.get("username")
    uid = eud.get(VARIANT_LEVEL_PRIMARY_KEY)
    dbpath = eud.get("dbpath")
    return email, uid, dbpath


def get_job_dir_from_eud(_, eud={}) -> Optional[str]:
    from pathlib import Path
    from .serveradmindb import ServerAdminDb
    from ..lib.consts import VARIANT_LEVEL_PRIMARY_KEY

    if eud.get("dbpath"):
        job_dir = Path(eud.get("dbpath")).parent
        if job_dir.exists():
            return str(job_dir)
        else:
            return None
    if eud.get("username") and eud.get(VARIANT_LEVEL_PRIMARY_KEY):
        serveradmindb = ServerAdminDb()
        job_dir = serveradmindb.get_job_dir_by_username_uid(eud=eud)
        return job_dir
    return None


def get_user_job_run_name(_, eud={}) -> Optional[str]:
    from pathlib import Path
    from .serveradmindb import get_serveradmindb

    username, uid, dbpath = unpack_eud(eud=eud)
    if dbpath:
        return Path(dbpath).stem
    if username and uid:
        serveradmindb = get_serveradmindb()
        run_name = serveradmindb.get_run_name(username=username, uid=uid)
        return run_name
    return None


def get_user_job_run_path(request, eud={}) -> Optional[str]:
    from pathlib import Path

    job_dir = get_job_dir_from_eud(request, eud=eud)
    if job_dir is None:
        return None
    run_name = get_user_job_run_name(request, eud=eud)
    if not run_name:
        return None
    run_path = Path(job_dir) / run_name
    return str(run_path)


def get_user_job_report_paths(request, report_type: str, eud={}) -> Optional[list]:
    from pathlib import Path
    from ..lib.module.local import get_local_module_info_by_name

    run_path = get_user_job_run_path(request, eud=eud)
    if not run_path:
        return None
    run_name = Path(run_path).name
    reporter = get_local_module_info_by_name(report_type + "reporter")
    if not reporter:
        return None
    output_filename_schema = reporter.conf.get("output_filename_schema")
    if not output_filename_schema:
        return None
    report_paths = []
    for pattern in output_filename_schema:
        report_paths.append(pattern.replace("{run_name}", run_name))
    return report_paths


def get_user_job_dbpath(request, eud={}) -> Optional[str]:
    from pathlib import Path
    from ..lib.consts import RESULT_DB_SUFFIX_DUCKDB
    from ..lib.consts import RESULT_DB_SUFFIX_SQLITE

    if eud.get("dbpath"):
        return eud.get("dbpath")
    run_path = get_user_job_run_path(request, eud=eud)
    if not run_path:
        return None
    dbpath = f"{run_path}{RESULT_DB_SUFFIX_DUCKDB}"
    if Path(dbpath).exists():
        return dbpath
    dbpath = f"{run_path}{RESULT_DB_SUFFIX_SQLITE}"
    return dbpath


def get_user_job_log_path(request, eud={}) -> Optional[str]:
    from ..lib.consts import LOG_SUFFIX

    run_path = get_user_job_run_path(request, eud=eud)
    if not run_path:
        return None
    log_path = run_path + LOG_SUFFIX
    return log_path


def get_user_jobs_dir_list() -> Optional[list]:
    from ..lib.system import get_jobs_dir

    user_jobs_dir_list = []
    root_jobs_dir = get_jobs_dir()
    if not root_jobs_dir:
        return user_jobs_dir_list
    for user_p in root_jobs_dir.glob("*"):
        if not user_p.is_dir():
            continue
        user_jobs_dir_list.append(str(user_p.resolve()))
    return user_jobs_dir_list


def get_log_path_in_job_dir(
    job_dir: Optional[str], run_name: Optional[str] = None
) -> Optional[str]:
    from pathlib import Path
    from ..lib.consts import LOG_SUFFIX

    if not job_dir:
        return None
    job_dir_p = Path(job_dir)
    if not job_dir_p.is_dir():
        return None
    if run_name:
        return str(job_dir_p / f"{run_name}{LOG_SUFFIX}")
    log_paths = [v for v in job_dir_p.glob("*.log")]
    return str(log_paths[0])


def get_job_runtime_in_job_dir(
    job_dir: Optional[str], run_name: Optional[str]
) -> Optional[float]:
    from pathlib import Path

    log_path = get_log_path_in_job_dir(job_dir, run_name=run_name)
    if not log_path:
        return None
    runtime = None
    if not Path(log_path).exists():
        return None
    with open(log_path) as f:
        for line in f:
            if "runtime:" in line:
                runtime = int(float(line.split("runtime:")[1].strip().rstrip("s")))
    return runtime
