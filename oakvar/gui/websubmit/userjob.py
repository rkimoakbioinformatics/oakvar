from typing import Optional

job_statuses = {}


def unpack_eud(eud={}):
    email = eud.get("username")
    uid = eud.get("uid")
    dbpath = eud.get("dbpath")
    return email, uid, dbpath


def get_user_jobs_dir(request, email=None):
    from ...system import get_user_jobs_dir
    from .multiuser import get_email_from_request

    if not email:
        email = get_email_from_request(request)
    if not email:
        return None
    return get_user_jobs_dir(email)


async def get_job_dir_from_eud(_, eud={}) -> Optional[str]:
    from pathlib import Path
    from .serveradmindb import ServerAdminDb

    if eud.get("dbpath"):
        job_dir = Path(eud.get("dbpath")).parent
        if job_dir.exists():
            return str(job_dir)
        else:
            return None
    if eud.get("username") and eud.get("uid"):
        serveradmindb = ServerAdminDb()
        job_dir = await serveradmindb.get_job_dir_by_username_uid(eud=eud)
        return job_dir
    return None


async def get_user_job_run_name(_, eud={}) -> Optional[str]:
    from pathlib import Path
    from .multiuser import get_serveradmindb

    username, uid, dbpath = unpack_eud(eud=eud)
    if dbpath:
        return Path(dbpath).stem
    if username and uid:
        serveradmindb = await get_serveradmindb()
        run_name = await serveradmindb.get_run_name(username=username, uid=uid)
        return run_name
    return None


async def get_user_job_run_path(request, eud={}) -> Optional[str]:
    from pathlib import Path

    job_dir = await get_job_dir_from_eud(request, eud=eud)
    if job_dir is None:
        return None
    run_name = await get_user_job_run_name(request, eud=eud)
    if not run_name:
        return None
    run_path = Path(job_dir) / run_name
    return str(run_path)


async def get_user_job_report_paths(
    request, report_type: str, eud={}
) -> Optional[list]:
    from pathlib import Path
    from ...module.local import get_local_module_info_by_name

    run_path = await get_user_job_run_path(request, eud=eud)
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


async def get_user_job_dbpath(request, eud={}) -> Optional[str]:
    from ...consts import result_db_suffix

    if eud.get("dbpath"):
        return eud.get("dbpath")
    run_path = await get_user_job_run_path(request, eud=eud)
    if not run_path:
        return None
    dbpath = f"{run_path}{result_db_suffix}"
    return dbpath


async def get_user_job_log_path(request, eud={}) -> Optional[str]:
    from ...consts import LOG_SUFFIX

    run_path = await get_user_job_run_path(request, eud=eud)
    if not run_path:
        return None
    log_path = run_path + LOG_SUFFIX
    return log_path


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


def get_log_path_in_job_dir(
    job_dir: Optional[str], run_name: Optional[str] = None
) -> Optional[str]:
    from pathlib import Path
    from ...consts import LOG_SUFFIX

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
