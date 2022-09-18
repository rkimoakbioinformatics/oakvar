job_statuses = {}

async def get_user_jobs_dir(request):
    from ...system import get_jobs_dir
    from .multiuser import get_email_from_request
    from os.path import join
    from os.path import exists
    from os import mkdir

    root_jobs_dir = get_jobs_dir()
    email = get_email_from_request(request)
    if not email:
        return
    jobs_dir = join(root_jobs_dir, email)
    if exists(jobs_dir) == False:
        mkdir(jobs_dir)
    return jobs_dir

async def get_user_job_dir(request, job_id_or_dbpath, given_username=None):
    from os.path import exists
    from os.path import dirname
    from os.path import abspath
    from .multiuser import get_username
    if exists(job_id_or_dbpath):
        return dirname(abspath(job_id_or_dbpath))
    user_jobs_dir = await get_user_jobs_dir(request)
    if not user_jobs_dir:
        return None
    if given_username is not None:
        username = given_username
    else:
        username = await get_username(request, return_str=True)
    if not username:
        return None
    job_dir = os.path.join(os.path.dirname(user_jobs_dir), username, job_id_or_dbpath) # type: ignore
    return job_dir

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

async def get_user_job_status(_, job_dir, job_id_or_dbpath, new=False):
    from os.path import exists
    from os.path import join
    from os.path import abspath
    from os import listdir
    from json import load
    from json import JSONDecodeError
    from logging import getLogger
    from oakvar.consts import status_prefix
    try:
        if not new:
            if job_id_or_dbpath in job_statuses:
                return job_statuses[job_id_or_dbpath]
        statusjson = None
        status_fn = None
        if exists(job_id_or_dbpath):
            job_id_or_dbpath = abspath(job_id_or_dbpath)
            if not job_id_or_dbpath.endswith(".sqlite"):
                return None, None
            run_name = job_id_or_dbpath[:-7]
            status_fn = run_name + status_prefix
        else:
            fns = listdir(job_dir)
            for fn in fns:
                if fn.endswith(".status.json"):
                    status_fn = join(job_dir, fn)
                    break
        if not status_fn:
            return None, None
        with open(status_fn) as f:
            try:
                statusjson = load(f)
            except JSONDecodeError:
                statusjson = job_statuses.get(job_id_or_dbpath)
        job_statuses[job_id_or_dbpath] = statusjson
    except Exception as e:
        logger = getLogger()
        logger.exception(e)
        statusjson = None
    return statusjson


async def job_run_path(request, job_id_or_dbpath):
    job_dir = await get_user_job_dir(request, job_id_or_dbpath)
    if job_dir is None:
        run_path = None
    else:
        run_name = await job_run_name(request, job_id_or_dbpath)
        if run_name is not None:
            run_path = os.path.join(job_dir, run_name)
        else:
            run_path = None
    return run_path

