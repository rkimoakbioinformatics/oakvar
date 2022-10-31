import time
from typing import Any, Optional

report_generation_ps = {}
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
job_queue = None
run_jobs_info = {}
logger = None
mu = Any
job_statuses = {}

class WebJob(object):
    def __init__(self, job_dir, job_status_fpath, job_id=None):
        from os.path import basename
        self.info = {}
        self.info["dir"] = job_dir
        self.info["orig_input_fname"] = ""
        self.info["assembly"] = ""
        self.info["note"] = ""
        self.info["db_path"] = ""
        self.info["viewable"] = False
        self.info["reports"] = []
        self.info["annotators"] = ""
        self.info["annotator_version"] = ""
        self.info["open_cravat_version"] = None
        self.info["num_input_var"] = ""
        self.info["submission_time"] = ""
        self.info["reports_being_generated"] = []
        self.job_dir = job_dir
        self.job_status_fpath = job_status_fpath
        if not job_id:
            job_id = basename(job_dir)
        self.job_id = job_id
        self.info["id"] = job_id

    def save_job_options(self, job_options):
        self.set_values(**job_options)

    def read_info_file(self):
        from yaml import safe_load
        from os.path import exists
        if not exists(self.job_status_fpath):
            info_dict = {"status": "Error"}
        else:
            with open(self.job_status_fpath) as f:
                info_dict = safe_load(f)
        if info_dict != None:
            self.set_values(**info_dict)

    def set_info_values(self, **kwargs):
        self.set_values(**kwargs)

    def get_info_dict(self):
        return self.info

    def set_values(self, **kwargs):
        self.info.update(kwargs)


def get_next_job_id():
    from datetime import datetime
    return datetime.now().strftime(r"%y%m%d-%H%M%S")


async def resubmit(request):
    from os import listdir
    from os.path import join
    from aiohttp.web import json_response
    from json import load
    from json import dump
    global servermode
    if servermode:
        if await mu.is_loggedin(request) == False:
            return json_response({"status": "notloggedin"})
    queries = request.rel_url.query
    job_id = queries["job_id"]
    job_dir = queries["job_dir"]
    status_json = None
    status_json_path = None
    for fn in listdir(job_dir):
        if fn.endswith(".status.json"):
            status_json_path = join(job_dir, fn)
            with open(status_json_path) as f:
                status_json = load(f)
            break
    if status_json is None:
        return json_response(
            {"status": "error", "msg": "no status file exists in job folder."}
        )
    assembly = status_json["assembly"]
    input_fpaths = status_json["orig_input_path"]
    note = status_json["note"]
    annotators = status_json["annotators"]
    if "original_input" in annotators:
        annotators.remove("original_input")
    cc_cohorts_path = status_json.get("cc_cohorts_path", "")
    # Subprocess arguments
    run_args = ["ov", "run"]
    for fn in input_fpaths:
        run_args.append(fn)
    # Annotators
    if len(annotators) > 0 and annotators[0] != "":
        run_args.append("-a")
        run_args.extend(annotators)
    else:
        run_args.append("-e")
        run_args.append("all")
    # Liftover assembly
    run_args.append("-l")
    run_args.append(assembly)
    # Reports
    run_args.extend(["--skip", "reporter"])
    # Note
    if note != "":
        run_args.append("--note")
        run_args.append(note)
    run_args.append("--temp-files")
    if cc_cohorts_path != "":
        run_args.extend(["--module-option", f"casecontrol.cohorts={cc_cohorts_path}"])
    global job_queue
    global run_jobs_info
    job_ids = run_jobs_info["job_ids"]
    if job_id not in job_ids:
        job_ids.append(job_id)
        run_jobs_info["job_ids"] = job_ids
    qitem = {"cmd": "submit", "job_id": job_id, "run_args": run_args}
    if job_queue is not None:
        job_queue.put(qitem)
        status_json["status"] = "Submitted"
    if status_json_path is not None:
        with open(status_json_path, "w") as wf:
            dump(status_json, wf, indent=2, sort_keys=True)
    return json_response({"status": "resubmitted"})


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

async def submit(request):
    from os.path import join
    from os.path import basename
    from os import makedirs
    from datetime import datetime
    from aiohttp.web import json_response
    from aiohttp.web import HTTPForbidden
    from json import dump
    from ...util.admin_util import set_user_conf_prop
    from ...util.admin_util import get_current_package_version
    from ...system.consts import default_assembly
    from .userjob import get_user_jobs_dir
    from ...consts import status_suffix


    global servermode
    ret = check_submit_input_size(request)
    if ret:
        return ret
    if not await mu.is_loggedin(request):
        return json_response({"status": "notloggedin"})
    jobs_dir = get_user_jobs_dir(request)
    if not jobs_dir:
        return HTTPForbidden()
    job_id = get_next_job_id()
    job_dir = join(jobs_dir, job_id)
    makedirs(job_dir, exist_ok=True)
    reader = await request.multipart()
    job_options = {}
    input_files = []
    cc_cohorts_path = None
    while True:
        part = await reader.next()
        if not part:
            break
        if part.name.startswith("file_"):
            input_files.append(part)
            wfname = part.filename
            wpath = join(job_dir, wfname)
            with open(wpath, "wb") as wf:
                wf.write(await part.read())
        elif part.name == "options":
            job_options = await part.json()
        elif part.name == "casecontrol":
            cc_cohorts_path = join(job_dir, part.filename)
            with open(cc_cohorts_path, "wb") as wf:
                wf.write(await part.read())
    use_server_input_files = False
    if "inputServerFiles" in job_options and len(job_options["inputServerFiles"]) > 0:
        input_files = job_options["inputServerFiles"]
        input_fnames = [basename(fn) for fn in input_files]
        use_server_input_files = True
    else:
        input_fnames = [fp.filename for fp in input_files]
    run_name = input_fnames[0]
    if len(input_fnames) > 1:
        run_name += "_and_" + str(len(input_fnames) - 1) + "_files"
    info_fname = f"{run_name}{status_suffix}"
    job_info_fpath = join(job_dir, info_fname)
    # Job name
    job_name = job_options.get("job_name", "")
    if job_name:
        job_id = job_name
    # Initial save of job
    job = WebJob(job_dir, job_info_fpath, job_id=job_id)
    job.save_job_options(job_options)
    job.set_info_values(
        orig_input_fname=input_fnames,
        run_name=run_name,
        submission_time=datetime.now().isoformat(),
        viewable=False,
    )
    # Subprocess arguments
    input_fpaths = [join(job_dir, fn) for fn in input_fnames]
    run_args = ["ov", "run"]
    if use_server_input_files:
        for fp in input_files:
            run_args.append(fp)
        run_args.extend(["-d", job_dir])
    else:
        for fn in input_fnames:
            run_args.append(join(job_dir, fn))
    # Annotators
    if (
        "annotators" in job_options
        and len(job_options["annotators"]) > 0
        and job_options["annotators"][0] != ""
    ):
        annotators = job_options["annotators"]
        annotators.sort()
        run_args.append("-a")
        run_args.extend(annotators)
    else:
        annotators = ""
        run_args.append("-e")
        run_args.append("all")
    # Liftover assembly
    run_args.append("-l")
    if "assembly" in job_options:
        assembly = job_options["assembly"]
    else:
        assembly = default_assembly
    run_args.append(assembly)
    if servermode:
        await mu.update_user_settings(request, {"lastAssembly": assembly})
    else:
        set_user_conf_prop("last_assembly", assembly)
    # Reports
    if "reports" in job_options and len(job_options["reports"]) > 0:
        run_args.append("-t")
        run_args.extend(job_options["reports"])
    else:
        run_args.extend(["--skip", "reporter"])
    # Note
    note = job_options.get("note", "")
    if note:
        run_args.append("--note")
        run_args.append(note)
    # Forced input format
    if "forcedinputformat" in job_options and job_options["forcedinputformat"]:
        run_args.append("--input-format")
        run_args.append(job_options["forcedinputformat"])
    run_args.append("--writeadmindb")
    run_args.extend(["--jobname", f"{job_id}"])
    run_args.append("--temp-files")
    if cc_cohorts_path is not None:
        run_args.extend(["--module-option", f"casecontrol.cohorts={cc_cohorts_path}"])
    global job_queue
    global run_jobs_info
    job_ids = run_jobs_info["job_ids"]
    job_ids.append(job_id)
    run_jobs_info["job_ids"] = job_ids
    qitem = {"cmd": "submit", "job_id": job_id, "run_args": run_args}
    if job_queue is not None:
        job_queue.put(qitem)
        status = {"status": "Submitted"}
        job.set_info_values(status=status)
        if mu:
            await mu.add_job_info(request, job)
        # makes temporary status.json
        status_json = {}
        status_json["job_dir"] = job_dir
        status_json["id"] = job_id
        status_json["run_name"] = run_name
        status_json["assembly"] = assembly
        status_json["db_path"] = ""
        status_json["orig_input_fname"] = input_fnames
        status_json["orig_input_path"] = input_fpaths
        status_json["submission_time"] = datetime.now().isoformat()
        status_json["viewable"] = False
        status_json["note"] = note
        status_json["status"] = "Submitted"
        status_json["reports"] = []
        pkg_ver = get_current_package_version()
        status_json["open_cravat_version"] = pkg_ver
        status_json["annotators"] = annotators
        if cc_cohorts_path is not None:
            status_json["cc_cohorts_path"] = cc_cohorts_path
        else:
            status_json["cc_cohorts_path"] = ""
        with open(join(job_dir, run_name + ".status.json"), "w") as wf:
            dump(status_json, wf, indent=2, sort_keys=True)
    return json_response(job.get_info_dict())


def count_lines(f):
    n = 0
    for _ in f:
        n += 1
    return n


def get_expected_runtime(num_lines, annotators):
    mapper_vps = 1000
    annot_vps = 5000
    agg_vps = 8000
    return num_lines * (1 / mapper_vps + len(annotators) / annot_vps + 1 / agg_vps)


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
        out.append({
            "name": module.name,
            "format": module.name.replace("-converter", ""),
            "title": module.title.replace(" Converter", ""),
            "description": module.description,
            "developer": module.developer,
        })
    return json_response(out)

def find_files_by_ending(d, ending):
    from os import listdir
    fns = listdir(d)
    files = []
    for fn in fns:
        if fn.endswith(ending):
            files.append(fn)
    return files


async def get_job(request, job_id):
    from os.path import join
    from os.path import exists
    from os.path import basename
    from os.path import dirname
    from packaging.version import Version
    from pathlib import Path
    from ...util.admin_util import get_max_version_supported_for_migration
    from .userjob import get_user_job_report_paths
    from .userjob import get_user_job_dir
    from .userjob import get_user_job_status_path

    global run_jobs_info
    global job_statuses
    job_id_or_dbpath = await get_job_id_or_dbpath(request)
    if not job_id_or_dbpath:
        return None
    job_dir = await get_user_job_dir(request, job_id_or_dbpath)
    if not job_dir:
        return None
    job_dir_p = Path(job_dir)
    err_job = WebJob(job_dir, None)
    err_job.info["status"] = "Error"
    if not job_dir_p.exists() or not job_dir_p.is_dir():
        return err_job
    status_path = await get_user_job_status_path(request, job_id_or_dbpath, job_dir=job_dir)
    if not status_path:
        return err_job
    job = WebJob(job_dir, status_path)
    job.read_info_file()
    if "status" not in job.info:
        if job_id in job_statuses:
            job.info["status"] = job_statuses[job_id]
        else:
            job.info["status"] = "Aborted"
    elif (
        job.info["status"] not in ["Finished", "Error"]
        and job_id not in run_jobs_info["job_ids"]
    ):
        job.info["status"] = "Aborted"
    job_statuses[job_id] = job.info["status"]
    if job.info["status"] in ["Finished", "Error", "Aborted"]:
        del job_statuses[job_id]
    fns = find_files_by_ending(job_dir, ".sqlite")
    if len(fns) > 0:
        db_path = join(job_dir, fns[0])
    else:
        db_path = ""
    job_viewable = exists(db_path)
    job.set_info_values(
        viewable=job_viewable,
        db_path=db_path,
        status=job.info["status"],
    )
    existing_reports = []
    reports_being_generated = []
    for report_type in get_valid_report_types():
        report_paths = await get_user_job_report_paths(request, job_id, report_type)
        if report_paths is not None:
            report_exist = True
            for p in report_paths:
                if exists(join(job_dir, p)) == False:
                    report_exist = False
                    break
            if exists(
                join(job_dir, job_id + ".report_being_generated." + report_type)
            ):
                report_exist = False
            if report_exist:
                existing_reports.append(report_type)
                global report_generation_ps
                if (
                    job_id in report_generation_ps
                    and report_type in report_generation_ps[job_id]
                ):
                    del report_generation_ps[job_id][report_type]
            else:
                if (
                    job_id in report_generation_ps
                    and report_type in report_generation_ps[job_id]
                ):
                    reports_being_generated.append(report_type)
    job.info["reports_being_generated"] = reports_being_generated
    job.set_info_values(reports=existing_reports)
    job.info["username"] = basename(dirname(job_dir))
    if "open_cravat_version" not in job.info or not job.info["open_cravat_version"] or Version(job.info["open_cravat_version"]) < get_max_version_supported_for_migration():
        job.info["result_available"] = False
    else:
        job.info["result_available"] = True
    for annot_to_del in ["extra_vcf_info", "extra_variant_info"]:
        if annot_to_del in job.info["annotators"]:
            job.info["annotators"].remove(annot_to_del)
    return job


async def get_jobs(request):
    from aiohttp.web import json_response
    from .multiuser import get_admindb
    from .multiuser import get_email_from_request
    global servermode
    if not await mu.is_loggedin(request):
        return json_response({"status": "notloggedin"})
    queries = request.rel_url.query # get
    pageno = queries.get("pageno")
    pagesize = queries.get("pagesize")
    admindb = await get_admindb()
    email = get_email_from_request(request)
    jobs = await admindb.get_jobs_of_email(email, pageno=pageno, pagesize=pagesize)
    return json_response(jobs)


async def view_job(request):
    from aiohttp.web import Response
    from pathlib import Path
    from subprocess import Popen
    from .userjob import get_user_job_dbpath

    global VIEW_PROCESS
    job_id_or_dbpath = await get_job_id_or_dbpath(request)
    db_path = await get_user_job_dbpath(request, job_id_or_dbpath)
    if not db_path:
        return Response(status=404)
    if not Path(db_path).exists():
        return Response(status=404)
    if VIEW_PROCESS and type(VIEW_PROCESS) == Popen:
        VIEW_PROCESS.kill()
    VIEW_PROCESS = Popen(["ov", "gui", db_path])
    return Response()


async def get_job_status(request):
    from aiohttp.web import json_response
    from aiohttp.web import Response
    from yaml import safe_load
    from .userjob import get_user_job_status_path

    job_id_or_dbpath = await get_job_id_or_dbpath(request)
    status_path = await get_user_job_status_path(request, job_id_or_dbpath)
    if not status_path:
        return Response(status=404)
    with open(status_path) as f:
        status = safe_load(f)
        return json_response(status)


async def download_db(request):
    from aiohttp.web import Response
    from aiohttp.web import FileResponse
    from .userjob import get_user_job_dbpath

    job_id_or_dbpath = await get_job_id_or_dbpath(request)
    if not job_id_or_dbpath:
        return Response(status=404)
    db_path = await get_user_job_dbpath(request, job_id_or_dbpath)
    db_fname = job_id_or_dbpath + ".sqlite"
    headers = {"Content-Disposition": "attachment; filename=" + db_fname}
    if not db_path:
        return Response(status=404)
    return FileResponse(db_path, headers=headers)


async def get_job_log(request):
    from aiohttp.web import Response
    from .userjob import get_user_job_log

    job_id_or_dbpath = await get_job_id_or_dbpath(request)
    log_path = await get_user_job_log(request, job_id_or_dbpath)
    if not log_path:
        return Response(text="log file does not exist.")
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
        v
        for v in valid_report_types
        if not v in ["pandas", "stdout", "example"]
    ]
    return valid_report_types


async def get_report_types(_):
    from aiohttp.web import json_response
    valid_types = get_valid_report_types()
    return json_response({"valid": valid_types})


async def get_job_id_or_dbpath(request) -> Optional[str]:
    from urllib.parse import unquote
    try:
        json_data = await request.json()
    except:
        json_data = None
    text_data = await request.text()
    text_data = unquote(text_data, encoding='utf-8', errors='replace')
    if text_data and "=" in text_data:
        return text_data.split("=")[1]
    post_data = await request.post() # post with form
    queries = request.rel_url.query # get
    if json_data:
        job_id = json_data.get("job_id", None)
        dbpath = json_data.get("dbpath", None)
    elif post_data:
        job_id = post_data.get("job_id", None)
        dbpath = post_data.get("dbpath", None)
    elif queries:
        job_id = queries.get("job_id", None)
        dbpath = queries.get("dbpath", None)
    else:
        return None
    if job_id:
        return job_id
    elif dbpath:
        return str(dbpath)
    else:
        return None

async def generate_report(request):
    from os.path import join
    from os.path import dirname
    from os import remove
    from aiohttp.web import json_response
    from aiohttp.web import Response
    from asyncio import create_subprocess_shell
    from asyncio.subprocess import PIPE
    from logging import getLogger
    from .userjob import get_user_job_dbpath

    job_id_or_dbpath = await get_job_id_or_dbpath(request)
    if not job_id_or_dbpath:
        return Response(status=404)
    report_type = request.match_info["report_type"]
    job_db_path = await get_user_job_dbpath(request, job_id_or_dbpath)
    if not job_db_path:
        return Response(status=404)
    run_args = ["ov", "report", job_db_path]
    run_args.extend(["-t", report_type])
    if job_id_or_dbpath not in report_generation_ps:
        report_generation_ps[job_id_or_dbpath] = {}
    report_generation_ps[job_id_or_dbpath][report_type] = True
    tmp_flag_path = join(
        dirname(job_db_path), job_id_or_dbpath + ".report_being_generated." + report_type
    )
    wf = open(tmp_flag_path, "w")
    wf.write(report_type)
    wf.close()
    p = await create_subprocess_shell(
        " ".join(run_args), stderr=PIPE
    )
    _, err = await p.communicate()
    remove(tmp_flag_path)
    if report_type in report_generation_ps[job_id_or_dbpath]:
        del report_generation_ps[job_id_or_dbpath][report_type]
    if job_id_or_dbpath in report_generation_ps and len(report_generation_ps[job_id_or_dbpath]) == 0:
        del report_generation_ps[job_id_or_dbpath]
    response = "done"
    if len(err) > 0:
        logger = getLogger()
        logger.error(err.decode("utf-8"))
        response = "fail"
    return json_response(response)


async def get_report_paths(request, job_id_or_dbpath, report_type):
    from .userjob import get_user_job_dir
    from .userjob import get_user_job_report_paths
    from pathlib import Path

    report_filenames = await get_user_job_report_paths(request, job_id_or_dbpath, report_type)
    if report_filenames is None:
        return None
    job_dir = await get_user_job_dir(request, job_id_or_dbpath)
    if not job_dir:
        return None
    report_paths = [str(Path(job_dir) / v) for v in report_filenames]
    return report_paths

async def download_report(request):
    from aiohttp.web import HTTPNotFound
    from aiohttp.web import FileResponse
    from os.path import exists
    from os.path import basename
    job_id_or_dbpath = await get_job_id_or_dbpath(request)
    if not job_id_or_dbpath:
        return HTTPNotFound
    report_type = request.match_info["report_type"]
    report_paths = await get_report_paths(request, job_id_or_dbpath, report_type)
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
            return json_response(
                {"success": False, "msg": "Only admin can change the settings."}
            )
        r = await mu.is_loggedin(request)
        if r == False:
            return json_response(
                {
                    "success": False,
                    "mgs": "Only logged-in admin can change the settings.",
                }
            )
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
        qitem = {
            "cmd": "set_max_num_concurrent_jobs",
            "max_num_concurrent_jobs": sysconf["max_num_concurrent_jobs"],
        }
        if job_queue is None:
            return Response(status=500)
        else:
            job_queue.put(qitem)
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
    d = {"current": cur_ver}
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


async def delete_job(request):
    from aiohttp.web import Response
    from pathlib import Path
    from asyncio import sleep
    from .userjob import get_user_job_dir

    global job_queue
    job_id_or_dbpath = await get_job_id_or_dbpath(request)
    job_dir = await get_user_job_dir(request, job_id_or_dbpath)
    if not job_dir:
        return Response(status=404)
    qitem = {"cmd": "delete", "job_id": job_id_or_dbpath, "job_dir": job_dir}
    if job_queue is None:
        return Response(status=500)
    job_queue.put(qitem)
    job_dir_p = Path(job_dir)
    while True:
        if not job_dir_p.exists():
            break
        else:
            await sleep(1)
    return Response()


def start_worker():
    global job_worker
    global job_queue
    global run_jobs_info
    from multiprocessing import Process
    from multiprocessing import Manager
    from multiprocessing import Queue
    job_queue = Queue()
    run_jobs_info = Manager().dict()
    if job_worker == None:
        job_worker = Process(target=fetch_job_queue, args=(job_queue, run_jobs_info))
        job_worker.start()


def fetch_job_queue(job_queue, run_jobs_info):
    from asyncio import new_event_loop
    class JobTracker(object):
        def __init__(self, main_loop):
            from ...system import get_system_conf
            from ...system.consts import DEFAULT_MAX_NUM_CONCURRENT_JOBS
            sys_conf = get_system_conf()
            if not sys_conf:
                self.max_num_concurrent_jobs = DEFAULT_MAX_NUM_CONCURRENT_JOBS
            else:
                self.max_num_concurrent_jobs = int(sys_conf["max_num_concurrent_jobs"])
            self.running_jobs = {}
            self.queue = []
            self.run_args = {}
            self.run_jobs_info = run_jobs_info
            self.run_jobs_info["job_ids"] = []
            self.loop = main_loop

        def add_job(self, qitem):
            self.queue.append(qitem["job_id"])
            self.run_args[qitem["job_id"]] = qitem["run_args"]

        def get_process(self, uid):
            # Return the process for a job
            return self.running_jobs.get(uid)

        async def cancel_job(self, uid):
            from subprocess import Popen
            from subprocess import PIPE
            from subprocess import check_output
            from os import kill
            from platform import platform
            from signal import SIGTERM
            from asyncio import sleep
            p = self.running_jobs.get(uid)
            if p is not None:
                p.poll()
                pl = platform().lower()
                if p:
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
                    elif pl.startswith("darwin") or pl.startswith("macos"):
                        lines = check_output(
                            'ps -ef | grep {} | grep "ov"'.format(uid), shell=True
                        )
                        lines = lines.decode("utf-8")
                        lines = lines.split("\n")
                        pids = [int(l.strip().split(" ")[0]) for l in lines if l != ""]
                        for pid in pids:
                            if pid == p.pid:
                                p.kill()
                            else:
                                try:
                                    kill(pid, SIGTERM)
                                except ProcessLookupError:
                                    continue
                    else:
                        p.kill()
                self.clean_jobs(id)

        def clean_jobs(self, uid):
            # Clean up completed jobs
            to_del = []
            for uid, p in self.running_jobs.items():
                if p.poll() is not None:
                    to_del.append(uid)
            for uid in to_del:
                del self.running_jobs[uid]
                job_ids = self.run_jobs_info["job_ids"]
                job_ids.remove(uid)
                self.run_jobs_info["job_ids"] = job_ids

        def list_running_jobs(self):
            # List currently tracked jobs
            return list(self.running_jobs.keys())

        def run_available_jobs(self):
            from subprocess import Popen
            num_available_slot = self.max_num_concurrent_jobs - len(self.running_jobs)
            if num_available_slot > 0 and len(self.queue) > 0:
                for _ in range(num_available_slot):
                    if len(self.queue) > 0:
                        job_id = self.queue.pop(0)
                        run_args = self.run_args[job_id]
                        del self.run_args[job_id]
                        p = Popen(run_args)
                        self.running_jobs[job_id] = p

        async def delete_job(self, qitem):
            from os.path import exists
            from shutil import rmtree
            from logging import getLogger
            logger = getLogger()
            job_id = qitem["job_id"]
            if self.get_process(job_id) is not None:
                msg = "\nKilling job {}".format(job_id)
                logger.info(msg)
                await self.cancel_job(job_id)
            job_dir = qitem["job_dir"]
            if exists(job_dir):
                rmtree(job_dir)

        def set_max_num_concurrent_jobs(self, qitem):
            from logging import getLogger
            value = qitem["max_num_concurrent_jobs"]
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
            job_tracker.clean_jobs(None)
            job_tracker.run_available_jobs()
            try:
                qitem = job_queue.get_nowait()
                cmd = qitem["cmd"]
                if cmd == "submit":
                    job_tracker.add_job(qitem)
                elif cmd == "delete":
                    await job_tracker.delete_job(qitem)
                elif cmd == "set_max_num_concurrent_jobs":
                    job_tracker.set_max_num_concurrent_jobs(qitem)
            except Empty:
                pass
            except Exception as e:
                logger = getLogger()
                logger.exception(e)
            finally:
                await sleep(1)

    main_loop = new_event_loop()
    job_tracker = JobTracker(main_loop)
    main_loop.run_until_complete(job_worker_main())
    job_tracker.loop.close()
    main_loop.close()


async def redirect_to_index(request):
    from aiohttp.web import HTTPFound
    global servermode
    if servermode and mu:
        r = await mu.is_loggedin(request)
        if r == False:
            url = "/server/nocache/login.html"
        else:
            url = "/submit/nocache/index.html"
    else:
        url = "/submit/nocache/index.html"
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
        response["crx"] = crx_data
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


async def get_available_report_types(request):
    from os.path import join
    from os.path import exists
    from aiohttp.web import json_response
    from .userjob import get_user_job_dir
    from .userjob import get_user_job_report_paths

    job_id_or_dbpath = await get_job_id_or_dbpath(request)
    job_dir = await get_user_job_dir(request, job_id_or_dbpath)
    if not job_dir:
        return json_response([])
    existing_reports = []
    for report_type in get_valid_report_types():
        report_paths = await get_user_job_report_paths(request, job_id_or_dbpath, report_type)
        if report_paths:
            report_exist = True
            for p in report_paths:
                if exists(join(job_dir, p)) == False:
                    report_exist = False
                    break
            if report_exist:
                existing_reports.append(report_type)
    return json_response(existing_reports)


def get_status_json_in_dir(job_dir):
    from os.path import join
    from json import load
    from glob import glob
    if job_dir is None:
        status_json = None
    else:
        fns = glob(job_dir + "/*.status.json")
        fns.sort()
        if len(fns) == 0:
            status_json = None
        else:
            with open(join(job_dir, fns[0])) as f:
                status_json = load(f)
    return status_json


async def update_result_db(request):
    from os.path import join
    from aiohttp.web import json_response
    from json import load
    from json import dump
    from asyncio import create_subprocess_shell
    from ...util.util import is_compatible_version
    from .userjob import get_user_job_dir

    queries = request.rel_url.query
    job_id = queries["job_id"]
    job_dir = await get_user_job_dir(request, job_id)
    if not job_dir:
        return json_response("fail")
    fns = find_files_by_ending(job_dir, ".sqlite")
    db_path = join(job_dir, fns[0])
    cmd = ["ov", "util", "update-result", db_path]
    p = await create_subprocess_shell(" ".join(cmd))
    await p.wait()
    compatible_version, db_version, _ = is_compatible_version(db_path)
    if compatible_version:
        msg = "success"
        fn = find_files_by_ending(job_dir, ".status.json")[0]
        path = join(job_dir, fn)
        with open(path) as f:
            status_json = load(f)
        status_json["open_cravat_version"] = str(db_version)
        wf = open(path, "w")
        dump(status_json, wf, indent=2, sort_keys=True)
        wf.close()
    else:
        msg = "fail"
    return json_response(msg)


async def import_job(request):
    from os.path import join
    from os import makedirs
    from aiohttp.web import Response
    from aiohttp.web import HTTPForbidden
    from json import dump
    from ...cli.util import status_from_db
    from .userjob import get_user_jobs_dir

    jobs_dir = get_user_jobs_dir(request)
    if not jobs_dir:
        return HTTPForbidden
    job_id = get_next_job_id()
    job_dir = join(jobs_dir, job_id)
    makedirs(job_dir, exist_ok=True)
    fn = request.headers["Content-Disposition"].split("filename=")[1]
    dbpath = join(job_dir, fn)
    with open(dbpath, "wb") as wf:
        async for data, _ in request.content.iter_chunks():
            wf.write(data)
    status_d = status_from_db(dbpath)
    status_path = dbpath + ".status.json"
    with open(status_path, "w") as wf:
        dump(status_d, wf)
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
    headers = {"Content-Disposition": "Attachment; filename=" + LOG_FN, "Content-Type": "text/plain"}
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


routes = []
routes.append(["POST", "/submit/submit", submit])
routes.append(["GET", "/submit/annotators", get_annotators])
routes.append(["GET", "/submit/postaggregators", get_postaggregators])
routes.append(["GET", "/submit/jobs", get_jobs])
routes.append(["GET", "/submit/jobs/{job_id}", view_job])
routes.append(["DELETE", "/submit/jobs/{job_id}", delete_job])
routes.append(["GET", "/submit/jobs/{job_id}/db", download_db])
routes.append(["GET", "/submit/reporttypes", get_report_types])
routes.append(["POST", "/submit/jobs/reports", get_available_report_types])
routes.append(["POST", "/submit/makereport/{report_type}", generate_report])
routes.append(["POST", "/submit/downloadreport/{report_type}", download_report])
routes.append(["GET", "/submit/jobs/{job_id}/log", get_job_log])
routes.append(["GET", "/submit/getjobsdir", get_jobs_dir])
routes.append(["GET", "/submit/setjobsdir", set_jobs_dir])
routes.append(["GET", "/submit/getsystemconfinfo", get_system_conf_info])
routes.append(["GET", "/submit/updatesystemconf", update_system_conf])
routes.append(["GET", "/submit/resetsystemconf", reset_system_conf])
routes.append(["GET", "/submit/servermode", get_servermode])
routes.append(["GET", "/submit/packageversions", get_package_versions])
routes.append(["GET", "/submit/lastassembly", get_last_assembly])
routes.append(["GET", "/submit/annotate", get_live_annotation_get])
routes.append(["POST", "/submit/annotate", get_live_annotation_post])
routes.append(["GET", "/", redirect_to_index])
routes.append(["GET", "/submit/jobs/{job_id}/status", get_job_status])
routes.append(["GET", "/submit/updateresultdb", update_result_db])
routes.append(["POST", "/submit/import", import_job])
routes.append(["GET", "/submit/resubmit", resubmit])
routes.append(["GET", "/issystemready", is_system_ready])
routes.append(["GET", "/submit/systemlog", get_system_log])
routes.append(["GET", "/favicon.ico", serve_favicon])
routes.append(["GET", "/webapps/{module}", get_webapp_index])
# Below for new gui.
routes.append(["GET", "/submit/converters", get_converters])
routes.append(["GET", "/submit/tags_annotators_postaggregators", get_tags_of_annotators_and_postaggregators])
routes.append(["GET", "/submit/localmodules/{module}", get_local_module_info_web])
