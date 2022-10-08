from typing import Optional

job_statuses = {}

def get_user_jobs_dir(request, email=None):
    from ...system import get_user_jobs_dir
    from .multiuser import get_email_from_request

    if not email:
        email = get_email_from_request(request)
    if not email:
        return None
    return get_user_jobs_dir(email)

async def get_user_job_dir(request, job_id_or_dbpath: Optional[str], given_username=None) -> Optional[str]:
    from pathlib import Path
    from .multiuser import get_username_str

    if not job_id_or_dbpath:
        return None
    job_id_or_dbpath_p = Path(job_id_or_dbpath)
    if job_id_or_dbpath_p.exists():
        return str(job_id_or_dbpath_p.absolute().parent)
    user_jobs_dir = get_user_jobs_dir(request)
    if not user_jobs_dir:
        return None
    if given_username is not None:
        username = given_username
    else:
        username = await get_username_str(request)
    if not username:
        return None
    job_dir = Path(user_jobs_dir) / username / job_id_or_dbpath
    return str(job_dir)

async def get_user_job_status_path_from_dbpath(dbpath):
    from ...consts import result_db_suffix
    from ...consts import status_suffix

    if not dbpath:
        return None
    if not dbpath.endswith(result_db_suffix):
        return None
    return dbpath[:-len(result_db_suffix)] + status_suffix

async def get_job_dir_from_job_id_or_dbpath(request, job_id_or_dbpath) -> Optional[str]:
    from pathlib import Path
    from ...consts import status_suffix
    if not job_id_or_dbpath:
        return None
    job_id_or_dbpath_p = Path(job_id_or_dbpath).absolute()
    if job_id_or_dbpath_p.exists():
        if job_id_or_dbpath.endswith(status_suffix):
            return str(job_id_or_dbpath_p.parent)
    if not request:
        return None
    return await get_user_job_dir(request, job_id_or_dbpath)

async def get_user_job_status_path(request, job_id_or_dbpath: Optional[str], job_dir: Optional[str]=None, run_name: Optional[str]=None) -> Optional[str]:
    from pathlib import Path
    from ...consts import status_suffix
    from ...system import get_status_path_in_job_dir

    # job_dir is given.
    if job_dir:
        return get_status_path_in_job_dir(job_dir)
    job_dir = await get_job_dir_from_job_id_or_dbpath(request, job_id_or_dbpath)
    if not job_dir or not job_id_or_dbpath:
        return None
    # sqlite file path is given.
    job_id_or_dbpath_p = Path(job_id_or_dbpath).absolute()
    if job_id_or_dbpath_p.exists():
        if job_id_or_dbpath_p.suffix != ".sqlite":
            return None
        run_name = job_id_or_dbpath_p.stem
        return f"{run_name}{status_suffix}"
    job_dir = await get_user_job_dir(request, job_id_or_dbpath)
    if not job_dir:
        return None
    job_dir_p = Path(job_dir)
    if run_name:
        return str(job_dir_p / f"{run_name}{status_suffix}")
    else:
        paths = list(job_dir_p.glob(f"*{status_suffix}"))
        if not paths:
            return None
        return str(paths[0].absolute())

async def get_user_job_status(request, job_id_or_dbpath, job_dir=None, new=False):
    from json import load
    from logging import getLogger
    status_json = None
    try:
        if not new and job_id_or_dbpath and job_id_or_dbpath in job_statuses:
            return job_statuses[job_id_or_dbpath]
        status_path = await get_user_job_status_path(request, job_id_or_dbpath, job_dir=job_dir)
        if not status_path:
            return None
        with open(status_path) as f:
            try:
                status_json = load(f)
            except:
                return None
        job_statuses[job_id_or_dbpath] = status_json
    except Exception as e:
        logger = getLogger()
        logger.exception(e)
        status_json = None
    finally:
        return status_json

async def get_user_job_run_name(request, job_id_or_dbpath):
    from os import listdir
    job_dir = await get_user_job_dir(request, job_id_or_dbpath)
    statusjson = await get_user_job_status(request, job_dir, job_id_or_dbpath)
    if not statusjson:
        return None
    run_name = statusjson.get("run_name")
    if not run_name:
        fns = listdir(job_dir)
        for fn in fns:
            if fn.endswith(".log"):
                run_name = fn[:-4]
                break
    return run_name

async def get_user_job_run_path(request, job_id_or_dbpath) -> Optional[str]:
    from pathlib import Path

    job_dir = await get_user_job_dir(request, job_id_or_dbpath)
    if job_dir is None:
        return None
    run_name = await get_user_job_run_name(request, job_id_or_dbpath)
    if not run_name:
        return None
    run_path = Path(job_dir) / run_name
    return str(run_path)

async def get_user_job_report_paths(request, job_id_or_dbpath: Optional[str], report_type: str) -> Optional[list]:
    from pathlib import Path
    from ...module.local import get_local_module_info_by_name

    run_path = await get_user_job_run_path(request, job_id_or_dbpath)
    if not run_path:
        return None
    run_name = Path(run_path).stem
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

async def get_user_job_dbpath(request, job_id_or_dbpath: Optional[str]) -> Optional[str]:
    from ...consts import result_db_suffix

    if not job_id_or_dbpath:
        return None
    run_path = await get_user_job_run_path(request, job_id_or_dbpath)
    if not run_path:
        return None
    dbpath = f"{run_path}{result_db_suffix}"
    return dbpath

async def get_user_job_log(request, job_id_or_dbpath: Optional[str]) -> Optional[str]:
    from pathlib import Path

    run_path = await get_user_job_run_path(request, job_id_or_dbpath)
    if not run_path:
        return None
    log_path = run_path + ".log"
    if not Path(log_path).exists():
        return None
    return str(log_path)

def get_user_jobs_dir_list() -> Optional[list]:
    from pathlib import Path
    from ...system import get_jobs_dir

    user_jobs_dir_list = []
    root_jobs_dir = get_jobs_dir()
    for user_p in Path(root_jobs_dir).glob("*"):
        if not user_p.is_dir():
            continue
        user_jobs_dir_list.append(str(user_p.absolute()))
    return user_jobs_dir_list

def get_log_path_in_job_dir(job_dir: Optional[str], run_name: Optional[str]=None) -> Optional[str]:
    from pathlib import Path
    from ...consts import log_suffix
    if not job_dir:
        return None
    job_dir_p = Path(job_dir)
    if not job_dir_p.is_dir():
        return None
    if run_name:
        return str(job_dir_p / f"{run_name}{log_suffix}")
    log_paths = [v for v in job_dir_p.glob("*.log")]
    return str(log_paths[0])

def get_job_runtime_in_job_dir(job_dir: Optional[str], run_name: Optional[str]) -> Optional[float]:
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
