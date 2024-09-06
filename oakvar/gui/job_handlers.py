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
from typing import Tuple
from typing import List
from pathlib import Path

REPORT_RUNNING = 1
REPORT_FINISHED = 2
REPORT_ERROR = 3


class JobHandlers:
    FINISHED = "Finished"
    ABORTED = "Aborted"
    ERROR = "Error"

    def __init__(
        self,
        servermode: bool = False,
        mu=None,
        logger=None,
        job_queue=None,
        info_of_running_jobs=None,
        report_generation_ps=None,
        loop=None,
    ):
        self.loop = loop
        self.servermode: bool = servermode
        self.mu = mu
        self.logger = logger
        self.job_queue = job_queue
        self.info_of_running_jobs = info_of_running_jobs
        self.report_generation_ps = report_generation_ps
        self.valid_report_types = None
        self.add_routes()

    def add_routes(self):
        self.routes = []
        self.routes.append(["GET", "/submit/converters", self.get_converters])
        self.routes.append(
            [
                "GET",
                "/submit/tags_annotators_postaggregators",
                self.get_tags_of_annotators_and_postaggregators,
            ]
        )
        self.routes.append(["POST", "/submit/jobs", self.get_jobs])
        self.routes.append(["POST", "/submit/submit", self.submit])
        self.routes.append(["GET", "/submit/jobstatus", self.get_job_status])
        self.routes.append(["GET", "/submit/jobs/{job_id}/status", self.get_job_status])
        self.routes.append(["POST", "/submit/delete_jobs", self.delete_jobs])
        self.routes.append(
            ["POST", "/submit/jobs/reports", self.get_available_report_types]
        )
        self.routes.append(
            ["POST", "/submit/downloadreport/{report_type}", self.download_report]
        )
        self.routes.append(["GET", "/submit/joblog", self.get_job_log])
        self.routes.append(
            ["POST", "/submit/makereport/{report_type}", self.generate_report]
        )
        self.routes.append(["GET", "/submit/jobdb", self.download_db])
        self.routes.append(["GET", "/submit/reporttypes", self.get_report_types])
        self.routes.append(
            ["POST", "/submit/jobinfo", self.get_job_info_by_username_uid]
        )

    async def get_tags_of_annotators_and_postaggregators(self, _):
        from aiohttp.web import json_response
        from ..lib.module.local import get_local_module_infos_of_type

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

    def get_converters(self, _):
        from aiohttp.web import json_response
        from ..lib.module.local import get_local_module_infos

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

    async def download_db(self, request):
        from aiohttp.web import Response
        from aiohttp.web import FileResponse
        from pathlib import Path
        from .userjob import get_user_job_dbpath

        eud = await self.get_eud_from_request(request)
        dbpath = eud.get("dbpath")
        if not dbpath:
            dbpath = await get_user_job_dbpath(request, eud=eud)
        if not dbpath:
            return Response(status=404)
        db_fname = Path(dbpath).name
        headers = {"Content-Disposition": "attachment; filename=" + db_fname}
        return FileResponse(dbpath, headers=headers)

    async def get_eud_from_request(self, request):
        from .util import get_email_from_request

        email = get_email_from_request(request, self.servermode)
        uid, dbpath = await self.get_uid_dbpath_from_request(request)
        return {"username": email, "uid": uid, "dbpath": dbpath}

    async def generate_report(self, request):
        from aiohttp.web import json_response
        from aiohttp.web import Response
        import asyncio
        import sys
        from .userjob import get_user_job_dbpath
        from .util import get_email_from_request

        global job_queue
        username = get_email_from_request(request, self.servermode)
        uid, dbpath = await self.get_uid_dbpath_from_request(request)
        if (not username or not uid) and not dbpath:
            return Response(status=404)
        report_type = request.match_info["report_type"]
        eud = {"username": username, "uid": uid, "dbpath": dbpath}
        if not dbpath:
            dbpath = await get_user_job_dbpath(request, eud)
        if not dbpath:
            return Response(status=404)
        key = uid or dbpath
        python_path = sys.executable
        run_args = [python_path, "-m", "oakvar", "report", dbpath]
        run_args.extend(["-t", report_type])
        queue_item = {
            "cmd": "report",
            "run_args": run_args,
            "dbpath": dbpath,
            "uid": uid,
            "report_type": report_type,
        }
        if self.job_queue is None:
            return Response(status=500)
        else:
            self.job_queue.put(queue_item)
        while True:
            await asyncio.sleep(1)
            value = self.get_report_generation_ps_value(key, report_type)
            if value == REPORT_FINISHED:
                self.remove_from_report_generation_ps(key, report_type)
                response = "done"
                break
            elif value == REPORT_ERROR:
                self.remove_from_report_generation_ps(key, report_type)
                response = "fail"
                break
        return json_response(response)

    def remove_from_report_generation_ps(self, key, report_type):
        assert self.report_generation_ps is not None
        del_num = None
        key_str = self.get_report_generation_key_str(key, report_type) + "==="
        for i, v in enumerate(self.report_generation_ps):
            if v.startswith(key_str):
                del_num = i
                break
        if del_num is not None:
            del self.report_generation_ps[del_num]

    def get_report_generation_ps_value(self, key, report_type):
        assert self.report_generation_ps is not None
        key_str = self.get_report_generation_key_str(key, report_type) + "==="
        for v in self.report_generation_ps:
            if v.startswith(key_str):
                return int(v.split("===")[1])

    def get_report_generation_key_str(self, key, report_type):
        return f"{key}__{report_type}"

    async def get_job_log(self, request):
        from aiohttp.web import Response
        from .userjob import get_user_job_log_path
        from pathlib import Path

        eud = await self.get_eud_from_request(request)
        log_path = await get_user_job_log_path(request, eud=eud)
        if not log_path or not Path(log_path).exists():
            return Response(status=404)
        with open(log_path) as f:
            return Response(text=f.read())

    async def make_download_zip(
        self,
        fpaths: List[Path],
        report_type: str,
        uid: Optional[str],
        dbpath: Optional[str],
    ):
        from zipfile import ZipFile
        from pathlib import Path

        if uid:
            zpath = fpaths[0].parent / f"{uid}.{report_type}.zip"
        elif dbpath:
            dbpath_p: Path = Path(dbpath)
            if not dbpath.endswith(".sqlite"):
                raise Exception("No result database to make reports with.")
            zpath = dbpath_p.parent / f"{dbpath_p.name[:-7]}.{report_type}.zip"
        else:
            raise Exception("UID or database path should be given to make a report.")
        with ZipFile(zpath, "w") as wf:
            for fpath in fpaths:
                wf.write(fpath, arcname=Path(fpath).name)
        return zpath

    async def download_report(self, request):
        from aiohttp.web import HTTPNotFound
        from aiohttp.web import FileResponse
        from pathlib import Path
        from .util import get_email_from_request

        uid, dbpath = await self.get_uid_dbpath_from_request(request)
        username = get_email_from_request(request, self.servermode)
        if not uid and not dbpath:
            return HTTPNotFound
        eud = {"uid": uid, "dbpath": dbpath, "username": username}
        report_type = request.match_info["report_type"]
        report_paths = await self.get_existing_report_file_paths(
            request, report_type, eud=eud
        )
        if not report_paths:
            raise HTTPNotFound
        if len(report_paths) == 1:
            report_path = Path(report_paths[0])
            report_filename = report_path.name
            headers = {"Content-Disposition": "attachment; filename=" + report_filename}
            response = FileResponse(report_path, headers=headers)
            return response
        else:
            zpath = await self.make_download_zip(report_paths, report_type, uid, dbpath)
            report_filename = zpath.name
            headers = {"Content-Disposition": "attachment; filename=" + report_filename}
            response = FileResponse(zpath, headers=headers)
            return response

    async def get_existing_report_file_paths(
        self, request, report_type, eud={}
    ) -> List[Path]:
        from pathlib import Path
        from .userjob import get_job_dir_from_eud
        from .userjob import get_user_job_report_paths

        job_dir = await get_job_dir_from_eud(request, eud=eud)
        if not job_dir:
            return []
        report_filenames = await get_user_job_report_paths(
            request, report_type, eud=eud
        )
        if not report_filenames:
            return []
        job_dir = Path(job_dir)
        existing_reports = []
        for report_filename in report_filenames:
            for fpath in job_dir.glob(report_filename):
                existing_reports.append(fpath)
        return existing_reports

    async def get_report_types(self, _):
        from aiohttp.web import json_response

        valid_types = self.get_valid_report_types()
        return json_response({"valid": valid_types})

    def get_valid_report_types(self):
        from ..lib.module.local import get_local_module_infos

        if self.valid_report_types is not None:
            return self.valid_report_types
        reporter_infos = get_local_module_infos(types=["reporter"])
        self.valid_report_types = [x.name.split("reporter")[0] for x in reporter_infos]
        self.valid_report_types = [
            v
            for v in self.valid_report_types
            if v not in ["pandas", "stdout", "example"]
        ]
        return self.valid_report_types

    async def get_available_report_types(self, request):
        from pathlib import Path
        from aiohttp.web import json_response
        from .userjob import get_job_dir_from_eud

        eud = await self.get_eud_from_request(request)
        job_dir = await get_job_dir_from_eud(request, eud=eud)
        if not job_dir:
            return json_response([])
        job_dir = Path(job_dir)
        existing_report_types = []
        for report_type in self.get_valid_report_types():
            report_paths = await self.get_existing_report_file_paths(
                request, report_type, eud=eud
            )
            if report_paths:
                existing_report_types.append(report_type)
        return json_response(existing_report_types)

    async def delete_jobs(self, request):
        from aiohttp.web import Response
        from pathlib import Path
        from asyncio import sleep
        from .userjob import get_job_dir_from_eud
        from .util import get_email_from_request

        global job_queue
        if self.job_queue is None:
            return Response(status=500)
        data = await request.json()
        uids = data.get("uids")
        abort_only = data.get("abort_only", False)
        if not uids:
            return Response(status=404)
        username = get_email_from_request(request, self.servermode)
        queue_item = {
            "cmd": "delete",
            "uids": uids,
            "username": username,
            "abort_only": abort_only,
        }
        self.job_queue.put(queue_item)
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

    async def get_job_info_by_username_uid(self, request):
        from aiohttp.web import json_response
        from .serveradmindb import get_serveradmindb
        import json

        eud = await self.get_eud_from_request(request)
        username = eud.get("username")
        uid = eud.get("uid")
        if not username or not uid:
            return json_response({})
        serveradmindb = await get_serveradmindb()
        job_info = serveradmindb.get_job_info_by_username_uid(username, uid)
        if not job_info:
            return json_response({})
        try:
            job_info = json.loads(job_info)
        except Exception as e:
            print(f"Error loading job info: {e}")
            return json_response({})
        return json_response(job_info)

    async def get_job_status(self, request):
        from aiohttp.web import Response
        from .serveradmindb import ServerAdminDb

        queries = request.rel_url.query
        uid = queries.get("uid")
        if not uid:
            return Response(status=404)
        serveradmindb = ServerAdminDb()
        status = await serveradmindb.get_job_status(uid)
        if not status:
            return Response(status=404)
        return Response(body=status)

    async def submit(self, request):
        from .web_submit import SubmitProcessor
        from .util import get_email_from_request

        global job_queue
        global mu
        assert self.job_queue is not None
        email = get_email_from_request(request, self.servermode)
        submit_processor = SubmitProcessor(
            loop=self.loop,
            job_queue=self.job_queue,
            logger=self.logger,
            servermode=self.servermode,
            mu=self.mu,
            info_of_running_jobs=self.info_of_running_jobs,
            email=email,
        )
        ret = await submit_processor.run(request)
        return ret

    async def get_jobs(self, request):
        from aiohttp.web import json_response
        from aiohttp.web import Response
        from .serveradmindb import get_serveradmindb
        from .util import get_email_from_request
        from .util import is_loggedin

        if self.mu and not await is_loggedin(request, self.servermode):
            return Response(status=401)
        data = await request.json()
        pageno = data.get("pageno")
        pagesize = data.get("pagesize")
        admindb = await get_serveradmindb()
        email = get_email_from_request(request, self.servermode)
        jobs = await admindb.get_jobs_of_email(email, pageno=pageno, pagesize=pagesize)
        if jobs is None:
            return Response(status=404)
        for job in jobs:
            if self.job_not_finished(job) and self.job_not_running(job):
                self.mark_job_as_aborted(job)
            job["checked"] = False
        return json_response(jobs)

    def job_not_running(self, job):
        return job.get("uid") not in self.info_of_running_jobs

    def job_not_finished(self, job):
        return job.get("status") not in [self.FINISHED, self.ERROR, self.ABORTED]

    def mark_job_as_aborted(self, job):
        job["status"] = self.ABORTED

    async def get_uid_dbpath_from_request(
        self, request
    ) -> Tuple[Optional[str], Optional[str]]:
        # from urllib.parse import unquote
        try:
            json_data = await request.json()
        except Exception:
            json_data = None
        try:
            post_data = await request.post()  # post with form
        except Exception:
            post_data = None
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


def fetch_job_queue(job_queue, info_of_running_jobs, report_generation_ps):
    from asyncio import new_event_loop
    from sys import platform
    from ..lib.util.asyn import get_event_loop

    class JobTracker(object):
        def __init__(self, main_loop):
            from ..lib.system import get_system_conf
            from ..lib.system.consts import DEFAULT_MAX_NUM_CONCURRENT_JOBS

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
                except Exception:
                    try:
                        int(words[1])
                        idx = 1
                    except Exception:
                        idx = None
                if idx is not None:
                    pids = [
                        int(line.strip().split()[idx]) for line in lines if line != ""
                    ]
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
            from .serveradmindb import get_serveradmindb

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
            err = p.stderr.read()  # type: ignore
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
            key_str = self.get_report_generation_key_str(key, report_type) + "==="
            for i, v in enumerate(d):
                if v.startswith(key_str):
                    d[i] = f"{key_str}{value}"
                    break
            self.report_generation_ps = d

        def get_report_generation_key_str(self, key, report_type):
            return f"{key}__{report_type}"

        def set_max_num_concurrent_jobs(self, queue_item):
            from logging import getLogger

            value = queue_item["max_num_concurrent_jobs"]
            try:
                self.max_num_concurrent_jobs = int(value)
            except Exception:
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
    except Exception:
        import traceback

        traceback.print_exc()
