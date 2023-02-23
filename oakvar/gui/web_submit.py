from typing import Optional
from typing import Tuple
from pathlib import Path


class Job(object):
    def __init__(self, job_dir: Path):
        self.info = {}
        self.info["dir"] = str(job_dir)
        self.info["orig_input_fname"] = ""
        self.info["assembly"] = ""
        self.info["note"] = ""
        self.info["db_path"] = ""
        self.info["viewable"] = False
        self.info["report_types"] = []
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


class SubmitProcessor:
    def __init__(
        self,
        loop=None,
        job_queue=None,
        logger=None,
        servermode=None,
        mu=None,
        info_of_running_jobs=None,
        email=None,
    ):
        self.loop = loop
        self.logger = logger
        self.job_queue = job_queue
        self.servermode = servermode
        self.mu = mu
        self.info_of_running_jobs = info_of_running_jobs
        self.email = email

    async def run(self, request):
        from ..lib.system import get_user_jobs_dir
        from aiohttp.web import Response
        from aiohttp.web import json_response

        assert self.job_queue is not None
        self.request = request
        jobs_dir = get_user_jobs_dir(self.email)
        if not jobs_dir:
            return Response(body="No jobs directory found", status=500)
        ret = await self.pre_submit_check(self.request, jobs_dir)
        if ret:
            return ret
        job_dir = self.create_new_job_dir(jobs_dir)
        queue_item, job = await self.get_queue_item_and_job(self.request, job_dir)
        self.job_queue.put(queue_item)
        uid: Optional[int] = queue_item.get("submit_options", {}).get("uid")
        if not uid:
            if self.logger:
                self.logger.error(
                    "Job UID was not obtained. submit_options={submit_options}"
                )
            return Response(status=500)
        self.add_job_uid_to_info_of_running_jobs(uid)
        return json_response(job.get_info_dict())

    def add_job_uid_to_info_of_running_jobs(self, job_uid: int):
        assert self.info_of_running_jobs is not None
        job_uids = self.info_of_running_jobs
        job_uids.append(job_uid)
        self.info_of_running_jobs = job_uids

    async def pre_submit_check(self, request, jobs_dir: Path):
        from aiohttp.web import Response
        from aiohttp.web import json_response
        from .util import is_loggedin

        ret = self.check_submit_input_size(request)
        if ret:
            return ret
        if self.mu and not await is_loggedin(request, self.servermode):
            return Response(status=401)
        if not self.job_queue:
            return json_response({"status": "server error. Job queue is not running."})
        if not self.mu:
            return json_response(
                {"status": "server error. User control is not running."}
            )
        if not jobs_dir:
            return Response(status=404)

    def check_submit_input_size(self, request):
        from aiohttp.web import HTTPLengthRequired
        from aiohttp.web import HTTPRequestEntityTooLarge
        from json import dumps
        from ..lib.system import get_system_conf

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

    def create_new_job_dir(self, jobs_dir: Path) -> Path:
        from os import makedirs
        from ..lib.util.run import get_new_job_dir

        job_dir = get_new_job_dir(jobs_dir)
        makedirs(job_dir, exist_ok=True)
        return job_dir

    async def get_queue_item_and_job(self, request, job_dir) -> Tuple[dict, Job]:
        from .serveradmindb import get_serveradmindb
        from .util import get_email_from_request

        assert self.mu is not None
        submit_options = await self.save_job_input_files(request, job_dir)
        self.process_job_options(submit_options)
        job = self.get_job(submit_options, job_dir)
        info_json = self.make_job_info_json(submit_options, job_dir)
        job.set_info_values(info_json=info_json)
        email = get_email_from_request(request, self.servermode)
        serveradmindb = await get_serveradmindb()
        uid = await serveradmindb.add_job_info(email, job)
        submit_options["uid"] = uid
        run_args = await self.get_run_args(request, submit_options, job_dir)
        run_args.extend(["--uid", str(uid)])
        submit_options["run_args"] = run_args
        del submit_options["input_files"]
        queue_item = {"cmd": "submit", "submit_options": submit_options}
        return queue_item, job

    async def save_job_input_files(self, request, job_dir: str) -> dict:
        from pathlib import Path
        from ..lib.util.util import get_unique_path

        submit_options = {}
        job_options = {}
        input_files = []
        job_options = {}
        chunk_size = 131072
        reader = await request.multipart()
        while True:
            part = await reader.next()
            if not part:
                break
            if part.name.startswith("file_"):
                input_files.append(part)
                path = Path(job_dir) / part.filename
                with open(path, "wb") as wf:
                    chunk = await part.read_chunk(size=chunk_size)
                    while chunk:
                        wf.write(chunk)
                        chunk = await part.read_chunk()
            elif part.name == "options":
                job_options = self.update_job_options(job_options, await part.json())
            elif part.name.startswith("module_option_file__"):
                [_, module_name, option_name] = part.name.split("__")
                fname = f"{module_name}__{option_name}"
                path = get_unique_path(str((Path(job_dir) / fname).absolute()))
                with open(path, "wb") as wf:
                    wf.write(await part.read())
                self.add_module_option(job_options, module_name, option_name, path)
        submit_options["job_options"] = job_options
        submit_options["input_files"] = input_files
        return submit_options

    def add_module_option(
        self, job_options: dict, module_name, option_name, option_value
    ):
        from ..lib.consts import MODULE_OPTIONS_KEY

        if not MODULE_OPTIONS_KEY in job_options:
            job_options[MODULE_OPTIONS_KEY] = {}
        if not module_name in job_options[MODULE_OPTIONS_KEY]:
            job_options[MODULE_OPTIONS_KEY][module_name] = {}
        job_options[MODULE_OPTIONS_KEY][module_name][option_name] = option_value

    def update_job_options(self, job_options: dict, data: dict):
        from ..lib.consts import MODULE_OPTIONS_KEY

        for k, v in data.items():
            if k == MODULE_OPTIONS_KEY:
                if not MODULE_OPTIONS_KEY in job_options:
                    job_options[MODULE_OPTIONS_KEY] = {}
                for module_name, option_dict in v.items():
                    if not module_name in job_options[MODULE_OPTIONS_KEY]:
                        job_options[MODULE_OPTIONS_KEY][module_name] = {}
                    for option_name, option_value in option_dict.items():
                        job_options[MODULE_OPTIONS_KEY][module_name][
                            option_name
                        ] = option_value
            else:
                job_options[k] = v
        return job_options

    def process_job_options(self, submit_options: dict):
        from pathlib import Path

        job_options = submit_options.get("job_options", {})
        input_files = submit_options.get("input_files", [])
        if (
            "inputServerFiles" in job_options
            and len(job_options["inputServerFiles"]) > 0
        ):
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

    def get_job(self, submit_options: dict, job_dir: Path):
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

    def make_job_info_json(self, submit_options: dict, job_dir: str):
        from datetime import datetime
        from pathlib import Path
        from json import dump
        from ..lib.util.admin_util import get_current_package_version
        from ..lib.exceptions import ArgumentError

        job_name = submit_options.get("job_name")
        run_name = submit_options.get("run_name")
        if not job_name:
            raise ArgumentError(
                msg=f"job_name not found. submit_options={submit_options}"
            )
        if not run_name:
            raise ArgumentError(msg="run_name not found for {job_name}")
        job_options = submit_options.get("job_options", {})
        info_json = {}
        info_json["job_dir"] = str(job_dir)
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
        info_json["report_types"] = job_options.get("reporters", [])
        with open(Path(job_dir) / (run_name + ".info.json"), "w") as wf:
            dump(info_json, wf, indent=2, sort_keys=True)
        return info_json

    async def get_run_args(self, request, submit_options: dict, job_dir: str):
        from pathlib import Path
        from ..lib.system.consts import default_assembly
        from ..lib.util.admin_util import set_user_conf_prop

        global servermode
        job_options = submit_options.get("job_options", {})
        input_fnames = submit_options.get("input_fnames", [])
        submit_options["input_fpaths"] = [
            str(Path(job_dir) / fn) for fn in input_fnames
        ]
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
            assembly = job_options.get("genome")
        if not assembly:
            assembly = default_assembly
        submit_options["assembly"] = assembly
        run_args.append(assembly)
        if self.servermode and self.mu:
            await self.mu.update_user_settings(request, {"lastAssembly": assembly})
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
        report_types = job_options.get("report_types", [])
        if report_types:
            run_args.append("-t")
            run_args.extend(job_options["report_types"])
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
        module_option_args = self.get_module_option_args(job_options)
        if module_option_args:
            run_args.append("--module-options")
            run_args.extend(module_option_args)
        if job_options.get("combine_input"):
            run_args.append("--combine-input")
        return run_args

    def get_module_option_args(self, submit_options: dict) -> Optional[list]:
        from ..lib.consts import MODULE_OPTIONS_KEY

        if MODULE_OPTIONS_KEY not in submit_options:
            return None
        args = []
        for module_name, option_dict in submit_options[MODULE_OPTIONS_KEY].items():
            for option_name, option_value in option_dict.items():
                arg = f"{module_name}.{option_name}={option_value}"
                args.append(arg)
        return args
