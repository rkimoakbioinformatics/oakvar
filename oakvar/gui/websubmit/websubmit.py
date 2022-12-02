from typing import Optional
from typing import Tuple
from multiprocessing import Queue

REPORT_RUNNING = 1
REPORT_FINISHED = 2
REPORT_ERROR = 3
manager = None
job_queue = Queue()
info_of_running_jobs = None
report_generation_ps = None
valid_report_types = None
servermode = False
VIEW_PROCESS = None
live_modules = {}
include_live_modules = None
exclude_live_modules = None
live_mapper = None
count_single_api_access = 0
time_of_log_single_api_access = None
interval_log_single_api_access = 60
job_worker = None
logger = None
mu = None
job_statuses = {}
FINISHED = "Finished"
ABORTED = "Aborted"
ERROR = "Error"

def get_info_of_running_jobs():
    from multiprocessing import Manager
    global manager
    global info_of_running_jobs
    if not manager:
        manager = Manager()
    if info_of_running_jobs is None:
        info_of_running_jobs = manager.list()
    return info_of_running_jobs

def get_report_generation_ps():
    from multiprocessing import Manager
    global manager
    global report_generation_ps
    if not manager:
        manager = Manager()
    if report_generation_ps is None:
        report_generation_ps = manager.list()
        report_generation_ps.append("initial")
    return report_generation_ps

def get_report_generation_key_str(key, report_type):
    return f"{key}__{report_type}"

def add_to_report_generation_ps(key, report_type):
    report_generation_ps = get_report_generation_ps()
    d = report_generation_ps
    d.append(f"{key}__{report_type}==={REPORT_RUNNING}")
    report_generation_ps = d

def remove_from_report_generation_ps(key, report_type):
    report_generation_ps = get_report_generation_ps()
    del_num = None
    key_str = get_report_generation_key_str(key, report_type) + "==="
    for i, v in enumerate(report_generation_ps):
        if v.startswith(key_str):
            del_num = i
            break
    if del_num is not None:
        del report_generation_ps[del_num]

def get_report_generation_ps_value(key, report_type):
    report_generation_ps = get_report_generation_ps()
    key_str = get_report_generation_key_str(key, report_type) + "==="
    for v in report_generation_ps:
        if v.startswith(key_str):
            return int(v.split("===")[1])

class Job(object):
    def __init__(self, job_dir):
        self.info = {}
        self.info["dir"] = job_dir
        self.info["orig_input_fname"] = ""
        self.info["assembly"] = ""
        self.info["note"] = ""
        self.info["db_path"] = ""
        self.info["viewable"] = False
        self.info["reports"] = []
        self.info["annotators"] = []
        self.info["annotator_version"] = ""
        self.info["package_version"] = None
        self.info["num_input_var"] = ""
        self.info["submission_time"] = ""
        self.info["reports_being_generated"] = []
        self.job_dir = job_dir
        self.info["info_json"] = None

    def save_job_options(self, job_options: dict):
        self.set_values(**job_options)

    def set_info_values(self, **kwargs):
        self.set_values(**kwargs)

    def get_info_dict(self):
        return self.info

    def set_values(self, **kwargs):
        self.info.update(kwargs)


async def resubmit(request):
    from .userjob import get_user_jobs_dir

    jobs_dir = get_user_jobs_dir(request)
    ret = await pre_submit_check(request, jobs_dir)
    if ret:
        return ret


def check_submit_input_size(request):
    from aiohttp.web import HTTPLengthRequired
    from aiohttp.web import HTTPRequestEntityTooLarge
    from json import dumps
    from ...system import get_system_conf

    sysconf = get_system_conf()
    size_cutoff = sysconf["gui_input_size_limit"]
    if request.content_length is None:
        return HTTPLengthRequired(
            text=dumps({"status": "fail", "msg": "Content-Length header required"})
        )
    size_cutoff_mb = size_cutoff * 1024 * 1024
    if request.content_length > size_cutoff_mb:
        return HTTPRequestEntityTooLarge(
            max_size=size_cutoff,
            actual_size=request.content_length,
            text=dumps(
                {
                    "status": "fail",
                    "msg": f"Input is too big. Limit is {size_cutoff}MB.",
                }
            ),
        )


async def pre_submit_check(request, jobs_dir: Optional[str]):
    from aiohttp.web import Response
    from aiohttp.web import json_response

    ret = check_submit_input_size(request)
    if ret:
        return ret
    if mu and not await mu.is_loggedin(request):
        return Response(status=401)
    if not job_queue:
        return json_response({"status": "server error. Job queue is not running."})
    if not mu:
        return json_response({"status": "server error. User control is not running."})
    if not jobs_dir:
        return Response(status=404)


def create_new_job_dir(jobs_dir: str) -> str:
    from os import makedirs
    from ...util.run import get_new_job_dir

    job_dir = get_new_job_dir(jobs_dir)
    makedirs(job_dir, exist_ok=True)
    return job_dir


def add_module_option(job_options: dict, module_name, option_name, option_value):
    from ...consts import MODULE_OPTIONS_KEY

    if not MODULE_OPTIONS_KEY in job_options:
        job_options[MODULE_OPTIONS_KEY] = {}
    if not module_name in job_options[MODULE_OPTIONS_KEY]:
        job_options[MODULE_OPTIONS_KEY][module_name] = {}
    job_options[MODULE_OPTIONS_KEY][module_name][option_name] = option_value

def update_job_options(job_options: dict, data: dict):
    from ...consts import MODULE_OPTIONS_KEY

    for k, v in data.items():
        if k == MODULE_OPTIONS_KEY:
            if not MODULE_OPTIONS_KEY in job_options:
                job_options[MODULE_OPTIONS_KEY] = {}
            for module_name, option_dict in v.items():
                if not module_name in job_options[MODULE_OPTIONS_KEY]:
                    job_options[MODULE_OPTIONS_KEY][module_name] = {}
                for option_name, option_value in option_dict.items():
                    job_options[MODULE_OPTIONS_KEY][module_name][option_name] = option_value
        else:
            job_options[k] = v
    return job_options

async def save_job_input_files(request, job_dir: str) -> dict:
    from pathlib import Path
    from ...util.util import get_unique_path

    submit_options = {}
    job_options = {}
    input_files = []
    job_options = {}
    reader = await request.multipart()
    while True:
        part = await reader.next()
        if not part:
            break
        if part.name.startswith("file_"):
            input_files.append(part)
            path = Path(job_dir) / part.filename
            with open(path, "wb") as wf:
                chunk = await part.read_chunk()
                while chunk:
                    wf.write(chunk)
                    chunk = await part.read_chunk()
        elif part.name == "options":
            job_options = update_job_options(job_options, await part.json())
        elif part.name.startswith("module_option_file__"):
            [_, module_name, option_name] = part.name.split("__")
            fname = f"{module_name}__{option_name}"
            path = get_unique_path(str((Path(job_dir) / fname).absolute()))
            with open(path, "wb") as wf:
                wf.write(await part.read())
            add_module_option(job_options, module_name, option_name, path)
    submit_options["job_options"] = job_options
    submit_options["input_files"] = input_files
    return submit_options


def process_job_options(submit_options: dict):
    from pathlib import Path

    job_options = submit_options.get("job_options", {})
    input_files = submit_options.get("input_files", [])
    if "inputServerFiles" in job_options and len(job_options["inputServerFiles"]) > 0:
        input_files = job_options["inputServerFiles"]
        input_fnames = [str(Path(fn).name) for fn in input_files]
        submit_options["use_server_input_files"] = True
    else:
        input_fnames = [fp.filename for fp in input_files]
        submit_options["use_server_input_files"] = False
    run_name = input_fnames[0]
    if len(input_fnames) > 1:
        run_name += "_etc"
    submit_options["input_fnames"] = input_fnames
    submit_options["run_name"] = run_name
    job_name = job_options.get("job_name")
    if job_name:
        submit_options["job_name"] = job_name


def get_module_option_args(submit_options: dict) -> Optional[list]:
    from ...consts import MODULE_OPTIONS_KEY

    if MODULE_OPTIONS_KEY not in submit_options:
        return None
    args = []
    for module_name, option_dict in submit_options[MODULE_OPTIONS_KEY].items():
        for option_name, option_value in option_dict.items():
            arg = f"{module_name}.{option_name}={option_value}"
            args.append(arg)
    return args

async def get_run_args(request, submit_options: dict, job_dir: str):
    from pathlib import Path
    from ...system.consts import default_assembly
    from ...util.admin_util import set_user_conf_prop

    global servermode
    job_options = submit_options.get("job_options", {})
    input_fnames = submit_options.get("input_fnames", [])
    submit_options["input_fpaths"] = [str(Path(job_dir) / fn) for fn in input_fnames]
    run_args = ["ov", "run"]
    if submit_options.get("use_server_input_files"):
        for fp in submit_options.get("input_files", []):
            run_args.append(fp)
    else:
        for fn in input_fnames:
            run_args.append(str(Path(job_dir) / fn))
    run_args.extend(["-d", job_dir])
    # Liftover assembly
    run_args.append("-l")
    assembly = job_options.get("assembly")
    if not assembly:
        assembly = default_assembly
    submit_options["assembly"] = assembly
    run_args.append(assembly)
    if servermode and mu:
        await mu.update_user_settings(request, {"lastAssembly": assembly})
    else:
        set_user_conf_prop("last_assembly", assembly)
    # Annotators
    annotators = job_options.get("annotators", [])
    if annotators and annotators[0] != "":
        annotators.sort()
        run_args.append("-a")
        run_args.extend(annotators)
    else:
        annotators = []
        run_args.append("-e")
        run_args.append("all")
    submit_options["annotators"] = annotators
    # Postaggregators
    postaggregators = job_options.get("postaggregators", [])
    if postaggregators and postaggregators[0] != "":
        postaggregators.sort()
        run_args.append("-p")
        run_args.extend(postaggregators)
    else:
        postaggregators = []
    submit_options["postaggregators"] = postaggregators
    # Reports
    reports = job_options.get("reports", [])
    if reports:
        run_args.append("-t")
        run_args.extend(job_options["reports"])
    # Note
    note = job_options.get("note")
    if note:
        run_args.append("--note")
        run_args.append(note)
    # Forced input format
    forcedinputformat = job_options.get("forcedinputformat")
    if forcedinputformat:
        run_args.append("--input-format")
        run_args.append(forcedinputformat)
    run_args.append("--writeadmindb")
    run_args.append("--logtofile")
    job_name = submit_options.get("job_name")
    if job_name:
        run_args.extend(["--jobname", f"{job_name}"])
    run_args.append("--temp-files")
    # module options
    module_option_args = get_module_option_args(job_options)
    if module_option_args:
        run_args.append("--module-option")
        run_args.extend(module_option_args)
    if job_options.get("combine_input"):
        run_args.append("--combine-input")
    return run_args


def get_job(submit_options: dict, job_dir: str):
    from datetime import datetime
    from pathlib import Path

    job = Job(job_dir)
    job.save_job_options(submit_options.get("job_options", {}))
    job.set_info_values(
        orig_input_fname=submit_options.get("input_fnames"),
        run_name=submit_options.get("run_name"),
        submission_time=datetime.now().isoformat(),
        viewable=False,
    )
    if not job.info["job_name"]:
        job_name = Path(job.info["dir"]).name
        job.set_info_values(job_name=job_name)
    submit_options["job_name"] = job.info["job_name"]
    return job


def make_job_info_json(submit_options: dict, job_dir: str):
    from datetime import datetime
    from pathlib import Path
    from json import dump

    from ...util.admin_util import get_current_package_version
    from ...exceptions import ArgumentError

    job_name = submit_options.get("job_name")
    run_name = submit_options.get("run_name")
    if not job_name:
        raise ArgumentError(msg=f"job_name not found. submit_options={submit_options}")
    if not run_name:
        raise ArgumentError(msg="run_name not found for {job_name}")
    job_options = submit_options.get("job_options", {})
    info_json = {}
    info_json["job_dir"] = job_dir
    info_json["job_name"] = job_name
    info_json["run_name"] = run_name
    info_json["assembly"] = job_options.get("genome")
    info_json["db_path"] = ""
    info_json["orig_input_fname"] = submit_options.get("input_fnames")
    info_json["orig_input_path"] = submit_options.get("input_fpaths")
    info_json["submission_time"] = datetime.now().isoformat()
    info_json["viewable"] = False
    info_json["note"] = job_options.get("note")
    pkg_ver = get_current_package_version()
    info_json["package_version"] = pkg_ver
    info_json["annotators"] = job_options.get("annotators", [])
    info_json["postaggregators"] = job_options.get("postaggregators", [])
    info_json["reports"] = job_options.get("reporters", [])
    with open(Path(job_dir) / (run_name + ".info.json"), "w") as wf:
        dump(info_json, wf, indent=2, sort_keys=True)
    return info_json


async def get_queue_item_and_job(request, job_dir) -> Tuple[dict, Job]:
    if not mu:
        raise
    submit_options = await save_job_input_files(request, job_dir)
    process_job_options(submit_options)
    job = get_job(submit_options, job_dir)
    info_json = make_job_info_json(submit_options, job_dir)
    job.set_info_values(info_json=info_json)
    uid = await mu.add_job_info(request, job)
    submit_options["uid"] = uid
    run_args = await get_run_args(request, submit_options, job_dir)
    run_args.extend(["--uid", str(uid)])
    submit_options["run_args"] = run_args
    del submit_options["input_files"]
    queue_item = {"cmd": "submit", "submit_options": submit_options}
    return queue_item, job


def add_job_uid_to_info_of_running_jobs(job_uid: int):
    info_of_running_jobs = get_info_of_running_jobs()
    job_uids = info_of_running_jobs
    job_uids.append(job_uid)
    info_of_running_jobs = job_uids


async def submit(request):
    from aiohttp.web import Response
    from aiohttp.web import json_response
    from logging import getLogger
    from .userjob import get_user_jobs_dir

    global servermode
    global job_queue
    global mu
    jobs_dir = get_user_jobs_dir(request)
    if not jobs_dir:
        return Response(body="No jobs directory found", status=500)
    ret = await pre_submit_check(request, jobs_dir)
    if ret:
        return ret
    job_dir = create_new_job_dir(jobs_dir)
    queue_item, job = await get_queue_item_and_job(request, job_dir)
    job_queue.put(queue_item)
    uid = queue_item.get("submit_options", {}).get("uid")
    if not uid:
        logger = getLogger()
        logger.error("Job UID was not obtained. submit_options={submit_options}")
        return Response(status=500)
    add_job_uid_to_info_of_running_jobs(uid)
    return json_response(job.get_info_dict())


def get_annotators(_):
    from aiohttp.web import json_response
    from ...module.local import get_local_module_infos

    out = {}
    for local_info in get_local_module_infos(types=["annotator"]):
        module_name = local_info.name
        if local_info.type == "annotator":
            out[module_name] = {
                "name": module_name,
                "version": local_info.version,
                "type": local_info.type,
                "title": local_info.title,
                "description": local_info.description,
                "developer": local_info.developer,
            }
    return json_response(out)


def get_postaggregators(_):
    from aiohttp.web import json_response
    from ...module.local import get_local_module_infos

    out = {}
    for local_info in get_local_module_infos(types=["postaggregator"]):
        module_name = local_info.name
        if local_info.type == "postaggregator":
            out[module_name] = {
                "name": module_name,
                "version": local_info.version,
                "type": local_info.type,
                "title": local_info.title,
                "description": local_info.description,
                "developer": local_info.developer,
            }
    return json_response(out)


def get_converters(_):
    from aiohttp.web import json_response
    from ...module.local import get_local_module_infos

    out = []
    modules = get_local_module_infos(types=["converter"])
    modules.sort(key=lambda x: x.name)
    for module in modules:
        out.append(
            {
                "name": module.name,
                "format": module.name.replace("-converter", ""),
                "title": module.title.replace(" Converter", ""),
                "description": module.description,
                "developer": module.developer,
            }
        )
    return json_response(out)


def find_files_by_ending(d, ending):
    from os import listdir

    fns = listdir(d)
    files = []
    for fn in fns:
        if fn.endswith(ending):
            files.append(fn)
    return files


def job_not_finished(job):
    return job.get("status") not in [FINISHED, ERROR, ABORTED]


def job_not_running(job):
    info_of_running_jobs = get_info_of_running_jobs()
    return not job.get("uid") in info_of_running_jobs


def mark_job_as_aborted(job):
    job["status"] = ABORTED


async def get_jobs(request):
    from aiohttp.web import json_response
    from aiohttp.web import Response
    from .multiuser import get_serveradmindb
    from .multiuser import get_email_from_request

    global servermode
    if mu and not await mu.is_loggedin(request):
        return Response(status=401)
    data = await request.json()
    pageno = data.get("pageno")
    pagesize = data.get("pagesize")
    admindb = await get_serveradmindb()
    email = get_email_from_request(request)
    jobs = await admindb.get_jobs_of_email(email, pageno=pageno, pagesize=pagesize)
    if jobs is None:
        return Response(status=404)
    for job in jobs:
        if job_not_finished(job) and job_not_running(job):
            mark_job_as_aborted(job)
        job["checked"] = False
    return json_response(jobs)


async def view_job(request):
    from aiohttp.web import Response
    from pathlib import Path
    from subprocess import Popen
    from .userjob import get_user_job_dbpath

    global VIEW_PROCESS
    eud = await get_eud_from_request(request)
    db_path = await get_user_job_dbpath(request, eud=eud)
    if not db_path:
        return Response(status=404)
    if not Path(db_path).exists():
        return Response(status=404)
    if VIEW_PROCESS and type(VIEW_PROCESS) == Popen:
        VIEW_PROCESS.kill()
    VIEW_PROCESS = Popen(["ov", "gui", db_path])
    return Response()


async def get_job_status(request):
    from aiohttp.web import Response
    from .serveradmindb import ServerAdminDb

    global servermode
    #if mu and not await mu.is_loggedin(request):
    #    return Response(status=401)
    queries = request.rel_url.query
    uid = queries.get("uid")
    if not uid:
        return Response(status=404)
    serveradmindb = ServerAdminDb()
    status = await serveradmindb.get_job_status(uid)
    if not status:
        return Response(status=404)
    return Response(body=status)


async def download_db(request):
    from aiohttp.web import Response
    from aiohttp.web import FileResponse
    from pathlib import Path
    from .userjob import get_user_job_dbpath

    eud = await get_eud_from_request(request)
    dbpath = eud.get("dbpath")
    if not dbpath:
        dbpath = await get_user_job_dbpath(request, eud=eud)
    if not dbpath:
        return Response(status=404)
    db_fname = Path(dbpath).name
    headers = {"Content-Disposition": "attachment; filename=" + db_fname}
    return FileResponse(dbpath, headers=headers)


async def get_job_log(request):
    from aiohttp.web import Response
    from .userjob import get_user_job_log_path
    from pathlib import Path

    eud = await get_eud_from_request(request)
    log_path = await get_user_job_log_path(request, eud=eud)
    if not log_path or not Path(log_path).exists():
        return Response(status=404)
    with open(log_path) as f:
        return Response(text=f.read())


def get_valid_report_types():
    from ...module.local import get_local_module_infos

    global valid_report_types
    if valid_report_types is not None:
        return valid_report_types
    reporter_infos = get_local_module_infos(types=["reporter"])
    valid_report_types = [x.name.split("reporter")[0] for x in reporter_infos]
    valid_report_types = [
        v for v in valid_report_types if not v in ["pandas", "stdout", "example"]
    ]
    return valid_report_types


async def get_report_types(_):
    from aiohttp.web import json_response

    valid_types = get_valid_report_types()
    return json_response({"valid": valid_types})


async def get_uid_dbpath_from_request(request) -> Tuple[Optional[str], Optional[str]]:
    # from urllib.parse import unquote
    try:
        json_data = await request.json()
    except:
        json_data = None
    # text_data = await request.text()
    # text_data = unquote(text_data, encoding='utf-8', errors='replace')
    # if text_data and "=" in text_data:
    #    return text_data.split("=")[1]
    post_data = await request.post()  # post with form
    queries = request.rel_url.query  # get
    if json_data:
        uid = json_data.get("uid", None)
        dbpath = json_data.get("dbpath", None)
    elif post_data:
        uid = post_data.get("uid", None)
        dbpath = post_data.get("dbpath", None)
    elif queries:
        uid = queries.get("uid", None)
        dbpath = queries.get("dbpath", None)
    else:
        return None, None
    return uid, dbpath


async def generate_report(request):
    from aiohttp.web import json_response
    from aiohttp.web import Response
    import asyncio
    from .userjob import get_user_job_dbpath
    from .multiuser import get_email_from_request

    global job_queue
    username = get_email_from_request(request)
    uid, dbpath = await get_uid_dbpath_from_request(request)
    if (not username or not uid) and not dbpath:
        return Response(status=404)
    report_type = request.match_info["report_type"]
    eud = {"username": username, "uid": uid, "dbpath": dbpath}
    if not dbpath:
        dbpath = await get_user_job_dbpath(request, eud)
    if not dbpath:
        return Response(status=404)
    key = uid or dbpath
    run_args = ["ov", "report", dbpath]
    run_args.extend(["-t", report_type])
    queue_item = {
        "cmd": "report",
        "run_args": run_args,
        "dbpath": dbpath,
        "uid": uid,
        "report_type": report_type,
    }
    if job_queue is None:
        return Response(status=500)
    else:
        job_queue.put(queue_item)
    while True:
        await asyncio.sleep(1)
        value = get_report_generation_ps_value(key, report_type)
        if value == REPORT_FINISHED:
            remove_from_report_generation_ps(key, report_type)
            response = "done"
            break
        elif value == REPORT_ERROR:
            remove_from_report_generation_ps(key, report_type)
            response = "fail"
            break
    return json_response(response)


async def get_report_paths(request, report_type, eud={}):
    from .userjob import get_job_dir_from_eud
    from .userjob import get_user_job_report_paths
    from pathlib import Path

    report_filenames = await get_user_job_report_paths(request, report_type, eud=eud)
    if report_filenames is None:
        return None
    job_dir = await get_job_dir_from_eud(request, eud=eud)
    if not job_dir:
        return None
    report_paths = [str(Path(job_dir) / v) for v in report_filenames]
    return report_paths


async def download_report(request):
    from aiohttp.web import HTTPNotFound
    from aiohttp.web import FileResponse
    from os.path import exists
    from os.path import basename
    from .multiuser import get_email_from_request

    uid, dbpath = await get_uid_dbpath_from_request(request)
    username = get_email_from_request(request)
    if not uid and not dbpath:
        return HTTPNotFound
    eud = {"uid": uid, "dbpath": dbpath, "username": username}
    report_type = request.match_info["report_type"]
    report_paths = await get_report_paths(request, report_type, eud=eud)
    if not report_paths:
        raise HTTPNotFound
    report_path = report_paths[0]
    if not exists(report_path):
        await generate_report(request)
    if exists(report_path):
        report_filename = basename(report_path)
        headers = {"Content-Disposition": "attachment; filename=" + report_filename}
        response = FileResponse(report_path, headers=headers)
        return response
    else:
        raise HTTPNotFound


def get_jobs_dir(_):
    from aiohttp.web import json_response
    from ...system import get_jobs_dir

    jobs_dir = get_jobs_dir()
    return json_response(jobs_dir)


def set_jobs_dir(request):
    from aiohttp.web import json_response
    from ...util.admin_util import set_jobs_dir

    queries = request.rel_url.query
    d = queries["jobsdir"]
    set_jobs_dir(d)
    return json_response(d)


async def get_system_conf_info(_):
    from aiohttp.web import json_response
    from ...system import get_system_conf_info

    info = get_system_conf_info(json=True)
    return json_response(info)


async def update_system_conf(request):
    from os.path import join
    from os.path import exists
    from aiohttp.web import json_response
    from aiohttp.web import Response
    from json import loads
    from ...system import update_system_conf_file
    from ...system import set_modules_dir

    global servermode
    if servermode and mu:
        username = await mu.get_username(request)
        if username != "admin":
            return Response(status=401)
        if not await mu.is_loggedin(request):
            return Response(status=401)
    queries = request.rel_url.query
    sysconf = loads(queries["sysconf"])
    try:
        success = update_system_conf_file(sysconf)
        if "modules_dir" in sysconf:
            modules_dir = sysconf["modules_dir"]
            cravat_yml_path = join(modules_dir, "cravat.yml")
            if exists(cravat_yml_path) == False:
                set_modules_dir(modules_dir)
        global job_queue
        queue_item = {
            "cmd": "set_max_num_concurrent_jobs",
            "max_num_concurrent_jobs": sysconf["max_num_concurrent_jobs"],
        }
        if job_queue is None:
            return Response(status=500)
        else:
            job_queue.put(queue_item)
    except:
        raise
    return json_response({"success": success, "sysconf": sysconf})


def reset_system_conf(_):
    from aiohttp.web import json_response
    from yaml import dump
    from ...system import get_modules_dir
    from ...system import get_system_conf_template
    from ...system import get_jobs_dir
    from ...system import write_system_conf_file

    d = get_system_conf_template()
    md = get_modules_dir()
    jobs_dir = get_jobs_dir()
    d["modules_dir"] = md
    d["jobs_dir"] = jobs_dir
    write_system_conf_file(d)
    return json_response({"status": "success", "dict": dump(d)})


def get_servermode(_):
    from aiohttp.web import json_response

    global servermode
    return json_response({"servermode": servermode})


async def get_package_versions(_):
    from aiohttp.web import json_response
    from ...util.admin_util import get_current_package_version

    cur_ver = get_current_package_version()
    d = {"pkg_ver": cur_ver}
    return json_response(d)


def get_last_assembly(_):
    from aiohttp.web import json_response
    from ...util.admin_util import get_last_assembly
    from ...util.admin_util import get_default_assembly

    global servermode
    last_assembly = get_last_assembly()
    default_assembly = get_default_assembly()
    if servermode and default_assembly is not None:
        assembly = default_assembly
    else:
        assembly = last_assembly
    return json_response(assembly)


async def delete_jobs(request):
    from aiohttp.web import Response
    from pathlib import Path
    from asyncio import sleep
    from .userjob import get_job_dir_from_eud
    from .multiuser import get_email_from_request

    global job_queue
    if job_queue is None:
        return Response(status=500)
    data = await request.json()
    uids = data.get("uids")
    abort_only = data.get("abort_only", False)
    if not uids:
        return Response(status=404)
    username = get_email_from_request(request)
    queue_item = {
        "cmd": "delete",
        "uids": uids,
        "username": username,
        "abort_only": abort_only,
    }
    job_queue.put(queue_item)
    job_dir_ps = []
    for uid in uids:
        p = await get_job_dir_from_eud(request, {"username": username, "uid": uid})
        if p:
            job_dir_ps.append(Path(p))
    while True:
        p_exist = False
        for p in job_dir_ps:
            if p.exists():
                p_exist = True
                break
        if not p_exist:
            break
        else:
            await sleep(1)
    return Response()


def start_worker():
    from multiprocessing import Process

    global job_worker
    global job_queue
    info_of_running_jobs = get_info_of_running_jobs()
    report_generation_ps = get_report_generation_ps()
    if job_worker == None:
        job_worker = Process(
            target=fetch_job_queue, args=(job_queue, info_of_running_jobs, report_generation_ps)
        )
        job_worker.start()


def fetch_job_queue(job_queue, info_of_running_jobs, report_generation_ps):
    from asyncio import new_event_loop
    from sys import platform
    from ...util.asyn import get_event_loop

    class JobTracker(object):
        def __init__(self, main_loop):
            from ...system import get_system_conf
            from ...system.consts import DEFAULT_MAX_NUM_CONCURRENT_JOBS

            sys_conf = get_system_conf()
            if not sys_conf:
                self.max_num_concurrent_jobs = DEFAULT_MAX_NUM_CONCURRENT_JOBS
            else:
                self.max_num_concurrent_jobs = int(sys_conf["max_num_concurrent_jobs"])
            self.processes_of_running_jobs = {}
            self.queue = []
            self.run_args = {}
            self.info_of_running_jobs = info_of_running_jobs
            self.info_of_running_jobs = []
            self.report_generation_ps = report_generation_ps
            self.loop = main_loop

        def add_job(self, queue_item):
            submit_options = queue_item.get("submit_options")
            uid = submit_options.get("uid")
            if not uid:
                print("No job UID from {submit_options}")
                return
            self.queue.append(uid)
            self.run_args[uid] = submit_options.get("run_args")
            self.info_of_running_jobs.append(uid)

        def get_process(self, uid):
            return self.processes_of_running_jobs.get(uid)

        async def cancel_job(self, uid):
            from subprocess import Popen
            from subprocess import PIPE
            from subprocess import check_output
            from os import kill
            from platform import platform
            from signal import SIGTERM
            from asyncio import sleep

            if not uid:
                return
            p = self.get_process(uid)
            if p is None:
                return
            pl = platform().lower()
            if pl.startswith("windows"):
                # proc.kill() doesn't work well on windows
                Popen(
                    "TASKKILL /F /PID {pid} /T".format(pid=p.pid),
                    stdout=PIPE,
                    stderr=PIPE,
                )
                while True:
                    await sleep(0.25)
                    if p.poll() is not None:
                        break
            else:
                cmd = f"ps -ef | grep 'ov run' | grep '\\-\\-uid {uid}'"
                lines = check_output(cmd, shell=True)
                lines = lines.decode("utf-8")
                lines = lines.split("\n")
                words = lines[0].split()
                try:
                    int(words[0])
                    idx = 0
                except:
                    try:
                        int(words[1])
                        idx = 1
                    except:
                        idx = None
                if idx is not None:
                    pids = [int(l.strip().split()[idx]) for l in lines if l != ""]
                    for pid in pids:
                        if pid == p.pid:
                            p.terminate()
                            p.kill()
                        else:
                            try:
                                kill(pid, SIGTERM)
                            except ProcessLookupError:
                                continue
                            except:
                                raise
            while True:
                p.wait(timeout=60)
                if p.poll() is None:
                    await sleep(0.5)
                    continue
                break

        def remove_process(self, uid):
            if not uid:
                return
            if uid in self.processes_of_running_jobs:
                del self.processes_of_running_jobs[uid]
            if uid in self.info_of_running_jobs:
                job_ids = self.info_of_running_jobs
                job_ids.remove(uid)
                self.info_of_running_jobs = job_ids

        async def clean_jobs(self, uid):
            from asyncio import sleep

            if uid:
                p = self.get_process(uid)
                if not p:
                    return
                while p.poll() is None:
                    await sleep(0.5)
                self.remove_process(uid)
                return
            to_del = []
            for uid, p in self.processes_of_running_jobs.items():
                if p.poll() is not None:
                    to_del.append(uid)
            for uid in to_del:
                self.remove_process(uid)

        def run_available_jobs(self):
            from subprocess import Popen

            num_available_slot = self.max_num_concurrent_jobs - len(
                self.processes_of_running_jobs
            )
            if num_available_slot > 0 and len(self.queue) > 0:
                for _ in range(num_available_slot):
                    if len(self.queue) > 0:
                        uid = self.queue.pop(0)
                        run_args = self.run_args[uid]
                        del self.run_args[uid]
                        p = Popen(run_args)
                        self.processes_of_running_jobs[uid] = p

        async def delete_jobs(self, queue_item):
            from os.path import exists
            from shutil import rmtree
            from logging import getLogger
            from .userjob import get_job_dir_from_eud
            from .multiuser import get_serveradmindb

            logger = getLogger()
            uids = queue_item.get("uids")
            username = queue_item.get("username")
            abort_only = queue_item.get("abort_only")
            for uid in uids:
                if uid in self.processes_of_running_jobs:
                    msg = "\nKilling job {}".format(uid)
                    logger.info(msg)
                    await self.cancel_job(uid)
                if abort_only:
                    serveradmindb = await get_serveradmindb()
                    await serveradmindb.mark_job_as_aborted(username=username, uid=uid)
                    continue
                job_dir = await get_job_dir_from_eud(
                    None, eud={"uid": uid, "username": username}
                )
                serveradmindb = await get_serveradmindb()
                serveradmindb.delete_job(uid)
                if job_dir and exists(job_dir):
                    rmtree(job_dir)

        async def make_report(self, queue_item):
            from pathlib import Path
            import subprocess
            from os import remove
            from logging import getLogger

            dbpath = queue_item.get("dbpath")
            uid = queue_item.get("uid")
            run_args = queue_item.get("run_args")
            report_type = queue_item.get("report_type")
            key = uid or dbpath
            suffix = ".report_being_generated." + report_type
            tmp_flag_path = Path(dbpath).with_suffix(suffix)
            with open(tmp_flag_path, "w") as wf:
                wf.write(report_type)
                wf.close()
            self.add_to_report_generation_ps(key, report_type)        
            p = subprocess.Popen(run_args, stderr=subprocess.PIPE)
            err = p.stderr.read() # type: ignore
            if len(err) > 0:
                logger = getLogger()
                logger.error(err.decode("utf-8"))
                self.change_report_generation_ps(key, report_type, REPORT_ERROR)
            else:
                self.change_report_generation_ps(key, report_type, REPORT_FINISHED)
            remove(tmp_flag_path)

        def add_to_report_generation_ps(self, key, report_type):
            d = self.report_generation_ps
            d.append(f"{key}__{report_type}==={REPORT_RUNNING}")
            self.report_generation_ps = d

        def change_report_generation_ps(self, key, report_type, value):
            d = self.report_generation_ps
            key_str = get_report_generation_key_str(key, report_type) + "==="
            for i, v in enumerate(d):
                if v.startswith(key_str):
                    d[i] = f"{key_str}{value}"
                    break
            self.report_generation_ps = d

        def set_max_num_concurrent_jobs(self, queue_item):
            from logging import getLogger

            value = queue_item["max_num_concurrent_jobs"]
            try:
                self.max_num_concurrent_jobs = int(value)
            except:
                logger = getLogger()
                logger.info(
                    "Invalid maximum number of concurrent jobs [{}]".format(value)
                )

    async def job_worker_main():
        from asyncio import sleep
        from queue import Empty
        from logging import getLogger

        while True:
            await job_tracker.clean_jobs(None)
            job_tracker.run_available_jobs()
            try:
                queue_item = job_queue.get_nowait()
                cmd = queue_item.get("cmd")
                if cmd == "submit":
                    job_tracker.add_job(queue_item)
                elif cmd == "delete":
                    await job_tracker.delete_jobs(queue_item)
                elif cmd == "report":
                    await job_tracker.make_report(queue_item)
                elif cmd == "set_max_num_concurrent_jobs":
                    job_tracker.set_max_num_concurrent_jobs(queue_item)
            except Empty:
                pass
            except Exception as e:
                import traceback
                traceback.print_exc()
                logger = getLogger()
                logger.exception(e)
            finally:
                await sleep(1)

    if platform == "win32":
        main_loop = get_event_loop()
    else:
        main_loop = new_event_loop()
    job_tracker = JobTracker(main_loop)
    try:
        main_loop.run_until_complete(job_worker_main())
    except KeyboardInterrupt:
        pass
    except:
        import traceback
        traceback.print_exc()


async def redirect_to_index(_):
    from aiohttp.web import HTTPFound

    global servermode
    url = "/index.html"
    return HTTPFound(url)


async def load_live_modules(module_names=[]):
    global live_modules
    global live_mapper
    global include_live_modules
    global exclude_live_modules
    from ...system import get_system_conf
    from ...module.local import get_local_module_infos
    from ...util.admin_util import get_user_conf

    conf = get_system_conf()
    if "live" in conf:
        live_conf = conf["live"]
        if "include" in live_conf:
            include_live_modules = live_conf["include"]
        else:
            include_live_modules = []
        if "exclude" in live_conf:
            exclude_live_modules = live_conf["exclude"]
        else:
            exclude_live_modules = []
    else:
        include_live_modules = []
        exclude_live_modules = []
    if live_mapper is None:
        cravat_conf = get_user_conf()
        if cravat_conf and "genemapper" in cravat_conf:
            default_mapper = cravat_conf["genemapper"]
        else:
            default_mapper = "hg38"
        from oakvar import get_live_mapper

        live_mapper = get_live_mapper(default_mapper)
    modules = get_local_module_infos(types=["annotator"])
    for module in modules:
        if module.name in live_modules:
            continue
        if module.name not in module_names:
            if module.name in exclude_live_modules:
                continue
            if (
                len(include_live_modules) > 0
                and module.name not in include_live_modules
            ):
                continue
            if "secondary_inputs" in module.conf:
                continue
        from oakvar import get_live_annotator

        annotator = get_live_annotator(module.name)
        if annotator is None:
            continue
        live_modules[module.name] = annotator


def clean_annot_dict(d):
    keys = d.keys()
    for key in keys:
        value = d[key]
        if value == "" or value == {}:
            d[key] = None
        elif type(value) is dict:
            d[key] = clean_annot_dict(value)
    if type(d) is dict:
        all_none = True
        for key in keys:
            if d[key] is not None:
                all_none = False
                break
        if all_none:
            d = None
    return d


async def live_annotate(input_data, annotators):
    from ...consts import mapping_parser_name
    from ...consts import all_mappings_col_name
    from ...consts import VARIANT_LEVEL_MAPPED_FILE_SUFFIX
    from ...util.inout import AllMappingsParser

    global live_modules
    global live_mapper
    response = {}
    if live_mapper is not None:
        crx_data = live_mapper.map(input_data)
        crx_data = live_mapper.live_report_substitute(crx_data)
        crx_data[mapping_parser_name] = AllMappingsParser(
            crx_data[all_mappings_col_name]
        )
        for k, v in live_modules.items():
            if annotators is not None and k not in annotators:
                continue
            try:
                annot_data = v.annotate(input_data=crx_data)
                annot_data = v.live_report_substitute(annot_data)
                if annot_data == "" or annot_data == {}:
                    annot_data = None
                elif type(annot_data) is dict:
                    annot_data = clean_annot_dict(annot_data)
                response[k] = annot_data
            except Exception as _:
                import traceback

                traceback.print_exc()
                response[k] = None
        del crx_data[mapping_parser_name]
        response[VARIANT_LEVEL_MAPPED_FILE_SUFFIX] = crx_data
    return response


async def get_live_annotation_post(request):
    from aiohttp.web import json_response

    queries = await request.post()
    response = await get_live_annotation(queries)
    return json_response(response)


async def get_live_annotation_get(request):
    from aiohttp.web import json_response

    queries = request.rel_url.query
    response = await get_live_annotation(queries)
    return json_response(response)


async def get_live_annotation(queries):
    import time

    if servermode:
        global count_single_api_access
        global time_of_log_single_api_access
        global interval_log_single_api_access
        count_single_api_access += 1
        t = time.time()
        if not time_of_log_single_api_access:
            time_of_log_single_api_access = t
        dt = t - time_of_log_single_api_access
        if dt > interval_log_single_api_access:
            if mu:
                await mu.admindb.write_single_api_access_count_to_db(
                    t, count_single_api_access
                )
            time_of_log_single_api_access = t
            count_single_api_access = 0
    chrom = queries["chrom"]
    pos = queries["pos"]
    ref_base = queries["ref_base"]
    alt_base = queries["alt_base"]
    if "uid" not in queries:
        uid = ""
    else:
        uid = queries["uid"]
    input_data = {
        "uid": uid,
        "chrom": chrom,
        "pos": int(pos),
        "ref_base": ref_base,
        "alt_base": alt_base,
    }
    if "annotators" in queries:
        annotators = queries["annotators"].split(",")
    else:
        annotators = None
    global live_modules
    global mapper
    if len(live_modules) == 0:
        await load_live_modules()
        response = await live_annotate(input_data, annotators)
    else:
        response = await live_annotate(input_data, annotators)
    return response


async def get_eud_from_request(request):
    from .multiuser import get_email_from_request

    email = get_email_from_request(request)
    uid, dbpath = await get_uid_dbpath_from_request(request)
    return {"username": email, "uid": uid, "dbpath": dbpath}


async def get_available_report_types(request):
    from pathlib import Path
    from aiohttp.web import json_response
    from .userjob import get_job_dir_from_eud
    from .userjob import get_user_job_report_paths

    eud = await get_eud_from_request(request)
    job_dir = await get_job_dir_from_eud(request, eud=eud)
    if not job_dir:
        return json_response([])
    job_dir = Path(job_dir)
    existing_reports = []
    for report_type in get_valid_report_types():
        report_paths = await get_user_job_report_paths(request, report_type, eud=eud)
        if report_paths:
            report_exist = True
            for p in report_paths:
                if not (job_dir / p).exists():
                    report_exist = False
                    break
            if report_exist:
                existing_reports.append(report_type)
    return json_response(existing_reports)


async def update_result_db(request):
    from os.path import join
    from aiohttp.web import json_response
    from asyncio import create_subprocess_shell
    from ...util.util import is_compatible_version
    from .userjob import get_job_dir_from_eud

    queries = request.rel_url.query
    job_id = queries["job_id"]
    job_dir = await get_job_dir_from_eud(request, job_id)
    if not job_dir:
        return json_response("fail")
    fns = find_files_by_ending(job_dir, ".sqlite")
    db_path = join(job_dir, fns[0])
    cmd = ["ov", "util", "update-result", db_path]
    p = await create_subprocess_shell(" ".join(cmd))
    await p.wait()
    compatible_version, _, _ = is_compatible_version(db_path)
    if compatible_version:
        msg = "success"
    else:
        msg = "fail"
    return json_response(msg)


async def import_job(request):
    from os.path import join
    from os import makedirs
    from aiohttp.web import Response
    from aiohttp.web import HTTPForbidden
    from .userjob import get_user_jobs_dir
    from ...util.run import get_new_job_dir

    jobs_dir = get_user_jobs_dir(request)
    if not jobs_dir:
        return HTTPForbidden
    _, job_dir = get_new_job_dir(jobs_dir)
    makedirs(job_dir, exist_ok=True)
    fn = request.headers["Content-Disposition"].split("filename=")[1]
    dbpath = join(job_dir, fn)
    with open(dbpath, "wb") as wf:
        async for data, _ in request.content.iter_chunks():
            wf.write(data)
    return Response()


async def get_local_module_info_web(request):
    from aiohttp.web import json_response
    from ...module.local import get_local_module_info

    module_name = request.match_info["module"]
    mi = get_local_module_info(module_name)
    if mi:
        return json_response(mi.serialize())
    else:
        return json_response({})


async def is_system_ready(request):
    from aiohttp.web import json_response
    from ...util.admin_util import system_ready

    _ = request
    return json_response(dict(system_ready()))


async def serve_favicon(request):
    from aiohttp.web import FileResponse
    from os.path import dirname
    from os.path import realpath
    from os.path import join

    _ = request
    source_dir = dirname(realpath(__file__))
    return FileResponse(join(source_dir, "..", "favicon.ico"))


async def get_system_log(_):
    from aiohttp import web
    from ...gui.util import get_log_path
    from ...gui.consts import LOG_FN

    log_path = get_log_path()
    headers = {
        "Content-Disposition": "Attachment; filename=" + LOG_FN,
        "Content-Type": "text/plain",
    }
    return web.FileResponse(log_path, headers=headers)


async def get_webapp_index(request):
    from aiohttp.web import HTTPFound

    url = request.path + "/index.html"
    if len(request.query) > 0:
        url = url + "?"
        for k, v in request.query.items():
            url += k + "=" + v + "&"
        url = url.rstrip("&")
    return HTTPFound(url)


async def get_tags_of_annotators_and_postaggregators(_):
    from aiohttp.web import json_response
    from ...module.local import get_local_module_infos_of_type

    tags = set()
    modules = get_local_module_infos_of_type("annotator").values()
    for module in modules:
        for tag in module.tags:
            tags.add(tag)
    modules = get_local_module_infos_of_type("postaggregator").values()
    for module in modules:
        for tag in module.tags:
            tags.add(tag)
    tags = list(tags)
    tags.sort()
    return json_response(tags)


async def get_login_state(request):
    from aiohttp.web import json_response

    global servermode
    global mu
    if not servermode or not mu:
        state = True
    else:
        state = await mu.is_loggedin(request)
    return json_response({"loggedin": state})


routes = []
routes.append(["GET", "/submit/annotators", get_annotators])
routes.append(["GET", "/submit/postaggregators", get_postaggregators])
routes.append(["GET", "/submit/jobs/{job_id}", view_job])
routes.append(["GET", "/submit/getjobsdir", get_jobs_dir])
routes.append(["GET", "/submit/setjobsdir", set_jobs_dir])
routes.append(["GET", "/submit/getsystemconfinfo", get_system_conf_info])
routes.append(["GET", "/submit/updatesystemconf", update_system_conf])
routes.append(["GET", "/submit/resetsystemconf", reset_system_conf])
routes.append(["GET", "/submit/lastassembly", get_last_assembly])
routes.append(["GET", "/submit/annotate", get_live_annotation_get])
routes.append(["POST", "/submit/annotate", get_live_annotation_post])
routes.append(["GET", "/", redirect_to_index])
routes.append(["GET", "/submit/updateresultdb", update_result_db])
routes.append(["POST", "/submit/import", import_job])
routes.append(["GET", "/submit/resubmit", resubmit])
routes.append(["GET", "/issystemready", is_system_ready])
routes.append(["GET", "/favicon.ico", serve_favicon])
routes.append(["GET", "/webapps/{module}", get_webapp_index])

# Below for new gui.
routes.append(["GET", "/submit/converters", get_converters])
routes.append(
    [
        "GET",
        "/submit/tags_annotators_postaggregators",
        get_tags_of_annotators_and_postaggregators,
    ]
)
routes.append(["GET", "/submit/localmodules/{module}", get_local_module_info_web])
routes.append(["POST", "/submit/jobs", get_jobs])
routes.append(["POST", "/submit/submit", submit])
routes.append(["GET", "/submit/jobstatus", get_job_status])
routes.append(["GET", "/submit/jobs/{job_id}/status", get_job_status])
routes.append(["POST", "/submit/delete_jobs", delete_jobs])
routes.append(["GET", "/submit/reporttypes", get_report_types])
routes.append(["POST", "/submit/jobs/reports", get_available_report_types])
routes.append(["GET", "/submit/servermode", get_servermode])
routes.append(["GET", "/submit/loginstate", get_login_state])
routes.append(["GET", "/submit/systemlog", get_system_log])
routes.append(["POST", "/submit/downloadreport/{report_type}", download_report])
routes.append(["GET", "/submit/joblog", get_job_log])
routes.append(["POST", "/submit/makereport/{report_type}", generate_report])
routes.append(["GET", "/submit/jobdb", download_db])
routes.append(["GET", "/submit/pkgver", get_package_versions])
