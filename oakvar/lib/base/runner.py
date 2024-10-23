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

from typing import Any
from typing import Optional
from typing import Type
from typing import List
from typing import Set
from typing import Tuple
from typing import Dict


class Runner(object):
    def __init__(self, **kwargs):
        from pathlib import Path
        from ..module.local import LocalModule

        self.runlevels = {
            "converter": 1,
            "preparer": 2,
            "mapper": 3,
            "annotator": 4,
            "aggregator": 5,
            "postaggregator": 6,
            "reporter": 7,
        }
        self.mapper_ran = False
        self.annotator_ran = False
        self.aggregator_ran = False
        self.annotators_to_run = {}
        self.done_annotators = {}
        self.info_json = None
        self.pkg_ver = None
        self.logger = None
        self.logmode = "w"
        self.log_path = None
        self.error_logger = None
        self.log_handler = None
        self.error_log_handler = None
        self.start_time = None
        self.manager = None
        self.result_path = None
        self.package_conf = {}
        self.args = None
        self.main_conf = {}
        self.run_conf = {}
        self.conf_path = None
        self.conf = {}
        self.first_non_url_input = None
        self.inputs: List[Path] = []
        self.run_name: Optional[List[str]] = None
        self.output_dir: Optional[List[str]] = None
        self.startlevel = self.runlevels["converter"]
        self.endlevel = self.runlevels["postaggregator"]
        self.cleandb = False
        self.excludes = []
        self.preparer_names = []
        self.mapper_name = None
        self.annotator_names = []
        self.postaggregator_names = []
        self.reporter_names = []
        self.report_names = []
        self.preparers = {}
        self.mapper = None
        self.annotators: Dict[str, LocalModule] = {}
        self.postaggregators = {}
        self.reporters = {}
        self.crvinput = None
        self.crxinput = None
        self.crginput = None
        self.crv_present = False
        self.crx_present = False
        self.crg_present = False
        self.total_num_unique_variants: int = 0
        self.converter_format: Optional[List[str]] = None
        self.genemapper = None
        self.append_mode = []
        self.exception = None
        self.genome_assemblies: List[List[str]] = []
        self.inkwargs = kwargs
        self.serveradmindb = None
        self.report_response = None
        self.filtersql = None
        self.outer = None
        self.error = None

    def check_valid_modules(self, module_names):
        from ..exceptions import ModuleNotExist
        from ..module.local import module_exists_local

        for module_name in module_names:
            if not module_exists_local(module_name):
                raise ModuleNotExist(module_name)

    async def setup_manager(self):
        from multiprocessing.managers import SyncManager

        self.manager = SyncManager()
        self.manager.start()

    def close_logger(self, error_log_only=False):
        if self.log_handler and not error_log_only:
            self.log_handler.close()
            if self.logger is not None:
                self.logger.removeHandler(self.log_handler)
        if self.error_log_handler:
            self.error_log_handler.close()
            if self.error_logger:
                self.error_logger.removeHandler(self.error_log_handler)

    def close_error_logger(self):
        if self.error_log_handler:
            self.error_log_handler.close()
            if self.error_logger:
                self.error_logger.removeHandler(self.error_log_handler)

    def shutdown_logging(self):
        import logging

        logging.shutdown()

    def sanity_check_run_name_output_dir(self):
        if not self.run_name or not self.output_dir:
            raise
        if len(self.run_name) != len(self.output_dir):
            raise

    def delete_output_files(self, run_no: int):
        from os import remove
        from pathlib import Path
        from ..util.util import escape_glob_pattern
        from ..consts import LOG_SUFFIX
        from ..consts import ERROR_LOG_SUFFIX

        if not self.run_name or not self.output_dir:
            return
        run_name = self.run_name[run_no]
        output_dir = self.output_dir[run_no]
        pattern = escape_glob_pattern(run_name) + ".*"
        log_fn = Path(output_dir) / (run_name + LOG_SUFFIX)
        error_log_fn = Path(output_dir) / (run_name + ERROR_LOG_SUFFIX)
        fns = [
            v
            for v in Path(output_dir).glob(pattern)
            if v != log_fn and v != error_log_fn
        ]
        for fn in fns:
            msg = f"deleting {fn}"
            if self.logger:
                self.logger.info(msg)
            remove(fn)

    def download_url_input(self, ip):
        import requests
        from pathlib import Path
        from ..util.util import is_url, humanize_bytes
        from ..util.run import update_status

        if " " in ip:
            print(f"Space is not allowed in input file paths ({ip})")
            exit()
        if not is_url(ip):
            return
        update_status(
            f"Fetching {ip}... ",
            logger=self.logger,
            serveradmindb=self.serveradmindb,
        )
        try:
            r = requests.head(ip)
            r = requests.get(ip, stream=True)
            fn = Path(ip).name
            fpath = fn
            cur_size = 0.0
            num_total_star = 40.0
            total_size = float(r.headers["content-length"])
            with open(fpath, "wb") as wf:
                for chunk in r.iter_content(chunk_size=8192):
                    wf.write(chunk)
                    cur_size += float(len(chunk))
                    perc = cur_size / total_size
                    cur_star = int(perc * num_total_star)
                    rem_stars = int(num_total_star - cur_star)
                    cur_prog = "*" * cur_star
                    rem_prog = " " * rem_stars
                    print(
                        f"[{cur_prog}{rem_prog}] {humanize_bytes(cur_size)} "
                        + f"/ {humanize_bytes(total_size)} ({perc * 100.0:.0f}%)",
                        end="\r",
                        flush=True,
                    )
                    if cur_size == total_size:
                        print("\n")
            return str(Path(fpath).absolute())
        except Exception:
            print("File downloading unsuccessful. Exiting.")
            exit()

    def get_logger(self, run_no: int):
        import logging
        from pathlib import Path
        from ..util.run import set_logger_handler

        if self.args is None or self.run_name is None or self.output_dir is None:
            raise
        output_dir = Path(self.output_dir[run_no])
        run_name = self.run_name[run_no]
        if self.args.newlog is True:
            self.logmode = "w"
        else:
            self.logmode = "a"
        self.logger = logging.getLogger("oakvar")
        self.error_logger = logging.getLogger("err")
        self.log_path, self.error_log_path = set_logger_handler(
            self.logger,
            self.error_logger,
            output_dir=output_dir,
            run_name=run_name,
            mode=self.logmode,
            level=self.args.loglevel,
            logtofile=self.args.logtofile,
            clean=self.args.clean,
            newlog=self.args.newlog,
        )

    def log_versions(self):
        from ..util import admin_util as au
        from ..exceptions import ModuleLoadingError
        from ..util.util import log_module

        if not self.args:
            raise
        if not self.logger:
            return
        self.logger.info(
            f"system: oakvar=={au.get_current_package_version()} {au.get_packagedir()}"
        )
        if len(self.package_conf) > 0:
            self.logger.info(
                f'package: {self.args.package} {self.package_conf.get("version")}'
            )
        for _, module in self.annotators.items():
            log_module(module, self.logger)
        if "mapper" not in self.args.skip:
            module = self.mapper
            if module is None:
                raise ModuleLoadingError(module_name="mapper")
            log_module(module, self.logger)
        for _, module in self.reporters.items():
            log_module(module, self.logger)

    async def process_clean(self, run_no: int):
        if not self.args or not self.args.clean or not self.run_name:
            return
        msg = f"deleting previous output files for {self.run_name[run_no]}..."
        if self.logger:
            self.logger.info(msg)
        self.delete_output_files(run_no)

    def log_input(self, run_no: int):
        if not self.args:
            raise
        if self.logger:
            if self.args.combine_input:
                for input_file in self.inputs:
                    self.logger.info(f"input file: {input_file}")
            else:
                self.logger.info(f"input file: {self.inputs[run_no]}")

    def start_log(self, run_no: int):
        from time import asctime, localtime
        from sys import argv

        self.get_logger(run_no)
        if not self.logger:
            return
        self.logger.info(f'{" ".join(argv)}')
        self.logger.info("started: {0}".format(asctime(localtime(self.start_time))))
        if self.conf_path != "":
            self.logger.info("conf file: {}".format(self.conf_path))

    async def process_file(self, run_no: int):
        await self.do_step_converter(run_no)
        await self.do_step_preparer(run_no)
        await self.do_step_mapper(run_no)
        await self.do_step_annotator(run_no)
        await self.do_step_aggregator(run_no)
        await self.do_step_postaggregator(run_no)
        await self.do_step_reporter(run_no)

    async def main(self) -> Optional[Dict[str, Any]]:
        from time import time, asctime, localtime
        from ..util.run import update_status
        from ..consts import JOB_STATUS_FINISHED
        from ..consts import JOB_STATUS_ERROR

        await self.process_arguments(self.inkwargs)
        if not self.args or not self.run_name:
            raise
        self.sanity_check_run_name_output_dir()
        await self.setup_manager()
        for run_no in range(len(self.run_name)):
            try:
                self.start_log(run_no)
                if self.logger:
                    self.logger.info(f"Processing {self.inputs[run_no]}")
                await self.process_clean(run_no)
                self.connect_admindb_if_needed(run_no)
                self.start_time = time()
                update_status(
                    "started OakVar",
                    logger=self.logger,
                    serveradmindb=self.serveradmindb,
                )
                self.write_initial_info_json(run_no)
                self.log_input(run_no)
                self.set_and_check_input_files(run_no)
                self.log_versions()
                if self.args and self.args.vcf2vcf:
                    await self.run_vcf2vcf(run_no)
                else:
                    await self.process_file(run_no)
                end_time = time()
                runtime = end_time - self.start_time
                display_time = asctime(localtime(end_time))
                if self.logger:
                    self.logger.info(f"finished: {display_time}")
                update_status(
                    "finished normally. Runtime: {0:0.3f}s".format(runtime),
                    logger=self.logger,
                    serveradmindb=self.serveradmindb,
                )
                if self.args and self.args.writeadmindb:
                    await self.write_admin_db_final_info(runtime, run_no)
            except Exception as e:
                self.exception = e
            finally:
                import traceback

                if self.exception:
                    s = traceback.format_exc().strip()
                    if s != "NoneType: None":
                        print(s)
                if not self.exception:
                    update_status(JOB_STATUS_FINISHED, serveradmindb=self.serveradmindb)
                else:
                    update_status(
                        JOB_STATUS_ERROR,
                        serveradmindb=self.serveradmindb,
                    )
                    if self.logger:
                        self.logger.error(self.exception)
                self.close_error_logger()
                self.clean_up_at_end(run_no)
                self.close_logger()
                self.shutdown_logging()
        return self.report_response

    async def process_arguments(self, args):
        from ..exceptions import SetupError

        self.set_package_conf(args)
        self.make_self_args_considering_package_conf(args)
        if self.args is None:
            raise SetupError()
        self.cleandb = self.args.cleandb
        self.set_preparers()
        self.set_mapper()
        self.set_annotators()
        self.set_postaggregators()
        self.set_reporters()
        self.add_required_modules_for_reporters()
        self.add_required_modules_for_postaggregators()
        self.sort_annotators()
        self.sort_postaggregators()
        self.process_module_options()
        self.set_start_end_levels()
        self.set_self_inputs()  # self.inputs is list.
        self.set_and_create_output_dir()  # self.output_dir is list.
        self.set_run_name()  # self.run_name is list.
        self.set_job_name()  # self.job_name is list.
        self.set_append_mode()  # self.append_mode is list.
        self.set_genome_assemblies()  # self.genome_assemblies is list.

    def update_module_options(self, options: Dict[str, Any], incoming: Dict[str, Any]):
        from ..exceptions import ModuleLoadingError

        if not incoming:
            return
        if not isinstance(incoming, dict):
            e = ModuleLoadingError(
                msg=f"Module loading error: module_options in {incoming} should be a dict. Consider contacting the module developers or correct the module yml file. Running `ov module info {options}` will show the module developer contact information as well as the location of the module files."
            )
            e.traceback = False
            raise e
        for k, v in incoming.items():
            if k not in options:
                options[k] = v
            elif isinstance(v, list):
                options[k] += v
            elif isinstance(v, dict):
                self.update_module_options(options[k], v)

    def process_module_options(self):
        from ..exceptions import SetupError
        from ..util.run import get_module_options

        if self.args is None:
            raise SetupError()
        module_options: Dict[str, Dict[str, Any]] = {}
        if self.mapper is not None:
            self.update_module_options(module_options, self.mapper.conf.get("module_options", {}))
        for annotator in self.annotators.values():
            # module_options by other modules
            self.update_module_options(module_options, annotator.conf.get("module_options", {}))
            # module_options by self overwrites.
            module_options.get(annotator.name, {}).update(
                annotator.conf.get("module_options", {})
            )
        # CLI module_options from args overwrites.
        module_options.update(
            get_module_options(self.args.module_options, outer=self.outer)
        )
        # dict module_options passed overwrites.
        if isinstance(self.args.module_options, dict):
            module_options.update(**self.args.module_options)
        self.run_conf.update(module_options)

    def make_self_args_considering_package_conf(self, args):
        from types import SimpleNamespace
        from ..util.admin_util import get_user_conf

        # package including -a (add) and -A (replace)
        run_conf = self.package_conf.get("run", {})
        for k, v in run_conf.items():
            if k == "annotators" and v and isinstance(v, list):
                if not args.get("annotators_replace"):
                    for v2 in v:
                        if v2 not in args.get("annotators", []):
                            args["annotators"].append(v2)
            else:
                if k not in args or not args[k]:
                    args[k] = v
        self.conf_path = args.get("confpath", None)
        self.make_self_conf(args)
        self.main_conf = get_user_conf() or {}
        self.run_conf = self.conf.get("run", {})
        for k, v in self.run_conf.items():
            if k not in args or (not args[k] and v):
                args[k] = v
        if args.get("annotators_replace"):
            args["annotators"] = args.get("annotators_replace")
        self.ignore_sample = args.get("ignore_sample", False)
        self.args = SimpleNamespace(**args)
        self.outer = self.args.outer
        if self.args.vcf2vcf and self.args.combine_input:
            if self.outer:
                self.outer.write("--vcf2vcf is used. --combine-input is disabled.")
            self.args.combine_input = False
        self.filtersql = args.get("filtersql", None)

    def connect_admindb_if_needed(self, run_no: int):
        from ...gui.serveradmindb import ServerAdminDb

        if not self.output_dir or not self.job_name:
            raise
        if self.args and self.args.writeadmindb:
            self.serveradmindb = ServerAdminDb(
                job_dir=self.output_dir[run_no], job_name=self.job_name[run_no]
            )

    def make_self_conf(self, args):
        from ..exceptions import SetupError
        from ..util.util import load_yml_conf

        if args is None:
            raise SetupError()
        if self.conf_path is not None:
            self.conf = load_yml_conf(self.conf_path)
        elif args.get("conf") is not None:
            self.conf = args.get("conf", {})
        else:
            self.conf = {}

    def populate_secondary_annotators(self, run_no):
        from os import listdir
        from ..consts import VARIANT_LEVEL_OUTPUT_SUFFIX
        from ..consts import GENE_LEVEL_OUTPUT_SUFFIX

        run_name, output_dir = self.get_run_name_output_dir_by_run_no(run_no)
        secondaries = {}
        for module in self.annotators.values():
            self._find_secondary_annotators(module, secondaries)
        self.annotators.update(secondaries)
        annot_names = [v.name for v in self.annotators.values()]
        annot_names = list(set(annot_names))
        filenames = listdir(output_dir)
        for filename in filenames:
            toks = filename.split(".")
            if len(toks) == 3:
                extension = toks[2]
                if toks[0] == run_name and (
                    extension == VARIANT_LEVEL_OUTPUT_SUFFIX
                    or extension == GENE_LEVEL_OUTPUT_SUFFIX
                ):
                    annot_name = toks[1]
                    if annot_name not in annot_names:
                        annot_names.append(annot_name)
        annot_names.sort()

    def remove_absent_inputs(self):
        inputs_to_remove = [
            v for v in self.inputs if not v.exists() and "*" not in str(v)
        ]
        for v in inputs_to_remove:
            self.inputs.remove(v)

    def process_url_and_pipe_inputs(self):
        from pathlib import Path
        from ..util.util import is_url

        if not self.args:
            raise
        self.first_non_url_input = None
        if self.args.inputs is not None:
            self.inputs = [  # type: ignore
                Path(x).resolve() if not is_url(x) and x != "-" else x
                for x in self.args.inputs
            ]
            for input_no in range(len(self.inputs)):
                inp = self.inputs[input_no]
                if is_url(str(inp)):
                    fpath = self.download_url_input(inp)
                    if fpath:
                        self.inputs[input_no] = Path(fpath)
                elif not self.first_non_url_input:
                    self.first_non_url_input = inp
        else:
            self.inputs = []

    def regenerate_from_db(self, run_no: int):
        import sqlite3
        from ..util.inout import FileWriter
        from ..util.util import get_crv_def
        from ..util.util import get_crx_def
        from ..util.util import get_crg_def

        if not self.inputs:
            raise
        dbpath = self.inputs[run_no]
        db = sqlite3.connect(dbpath)
        c = db.cursor()
        crv_def = get_crv_def()
        crx_def = get_crx_def()
        crg_def = get_crg_def()
        # Variant
        if not self.crv_present:
            crv = FileWriter(self.crvinput, columns=crv_def)
            crv.write_definition()
        else:
            crv = None
        if not self.crx_present:
            crx = FileWriter(self.crxinput, columns=crx_def)
            crx.write_definition()
        else:
            crx = None
        if crv or crx:
            colnames = [x["name"] for x in crx_def]
            sel_cols = ", ".join(["base__" + x for x in colnames])
            q = f"select {sel_cols} from variant"
            c.execute(q)
            for r in c:
                rd = {x[0]: x[1] for x in zip(colnames, r)}
                if crv:
                    crv.write_data(rd)
                if crx:
                    crx.write_data(rd)
            if crv:
                crv.close()
            if crx:
                crx.close()
            self.crv_present = True
            self.crx_present = True
        # Gene
        if not self.crg_present:
            crg = FileWriter(self.crginput, columns=crg_def)
            crg.write_definition()
            colnames = [x["name"] for x in crg_def]
            sel_cols = ", ".join(["base__" + x for x in colnames])
            q = f"select {sel_cols} from gene"
            c.execute(q)
            for r in c:
                rd = {x[0]: x[1] for x in zip(colnames, r)}
                crg.write_data(rd)
            crg.close()
            self.crg_present = True
        c.close()
        db.close()

    def set_append_mode(self):
        import shutil
        from pathlib import Path

        if not self.inputs:
            raise
        if not self.run_name or not self.output_dir or not self.args:
            raise
        self.append_mode = [False] * len(self.run_name)
        for run_no in range(len(self.run_name)):
            inp = self.inputs[run_no]
            run_name = self.run_name[run_no]
            output_dir = self.output_dir[run_no]
            if not inp.suffix == ".sqlite":
                continue
            self.append_mode[run_no] = True
            if run_name.endswith(".sqlite"):
                self.run_name[run_no] = run_name[:-7]
            if "converter" not in self.args.skip:
                self.args.skip.append("converter")
            if "mapper" not in self.args.skip:
                self.args.skip.append("mapper")
            target_name = run_name + ".sqlite"
            target_path = Path(output_dir) / target_name
            shutil.copyfile(inp, target_path)
            self.inputs[run_no] = target_path

    def set_genome_assemblies(self):
        if self.run_name:
            self.genome_assemblies = [[] for _ in range(len(self.run_name))]
        else:
            self.genome_assemblies = []

    def set_and_create_output_dir(self):
        from pathlib import Path
        from os import getcwd
        from os import mkdir
        from ..exceptions import ArgumentError

        if not self.args or not self.inputs:
            raise
        cwd = getcwd()
        if not self.args.output_dir:
            if self.args.combine_input:
                self.output_dir = [cwd]
            else:
                self.output_dir = [
                    str(Path(inp).absolute().parent) for inp in self.inputs
                ]
        else:
            if self.args.combine_input:
                if len(self.args.output_dir) != 1:
                    raise ArgumentError(
                        msg="-d should have one value when --combine-input is used."
                    )
                self.output_dir = [
                    str(Path(v).absolute()) for v in self.args.output_dir
                ]
            else:
                if len(self.args.output_dir) == 1:
                    self.output_dir = [self.args.output_dir[0]] * len(self.inputs)
                else:
                    if len(self.args.output_dir) != len(self.inputs):
                        raise ArgumentError(
                            msg="-d should have the same number of values as inputs."
                        )
                    self.output_dir = [
                        str(Path(v).absolute()) for v in self.args.output_dir
                    ]
        for output_dir in self.output_dir:
            if not Path(output_dir).exists():
                mkdir(output_dir)

    def set_package_conf(self, args):
        from ..module.cache import get_module_cache

        package_name = args.get("package", None)
        if package_name:
            if package_name in get_module_cache().get_local():
                self.package_conf: dict = (
                    get_module_cache().get_local()[package_name].conf
                )
            else:
                self.package_conf = {}
        else:
            self.package_conf = {}

    def get_unique_run_name(self, output_dir: str, run_name: str):
        from pathlib import Path
        from ..consts import result_db_suffix

        if not self.output_dir:
            return run_name
        dbpath_p = Path(output_dir) / f"{run_name}{result_db_suffix}"
        if not dbpath_p.exists():
            return run_name
        count = 0
        while dbpath_p.exists():
            dbpath_p = Path(output_dir) / f"{run_name}_{count}{result_db_suffix}"
            count += 1
        return f"{run_name}_{count}"

    def set_run_name(self):
        from pathlib import Path
        from ..exceptions import ArgumentError

        if not self.args or not self.output_dir:
            raise
        if not self.args.run_name:
            if self.inputs:
                if self.args.combine_input:
                    run_name = Path(self.inputs[0]).name
                    if len(self.inputs) > 1:
                        run_name = run_name + "_etc"
                        run_name = self.get_unique_run_name(
                            self.output_dir[0], run_name
                        )
                    self.run_name = [run_name]
                else:
                    self.run_name = [Path(v).name for v in self.inputs]
        else:
            if self.args.combine_input:
                if len(self.args.run_name) != 1:
                    raise ArgumentError(
                        msg="-n should have only one value when --combine-input "
                        + "is given."
                    )
                self.run_name = self.args.run_name
            else:
                if len(self.args.run_name) == 1:
                    if self.inputs:
                        if self.output_dir and len(self.output_dir) != len(
                            set(self.output_dir)
                        ):
                            raise ArgumentError(
                                msg="-n should have a unique value for each "
                                + "input when -d has duplicate directories."
                            )
                        self.run_name = self.args.run_name * len(self.inputs)
                    else:
                        raise
                else:
                    if self.inputs:
                        if len(self.inputs) != len(self.args.run_name):
                            raise ArgumentError(
                                msg="Just one or the same number of -n option "
                                + "values as input files should be given."
                            )
                        self.run_name = self.args.run_name
                    else:
                        raise

    def set_job_name(self):
        from pathlib import Path
        from ..exceptions import ArgumentError
        from ..util.run import get_new_job_name

        if not self.args or not self.output_dir:
            raise
        if not self.args.job_name:
            self.args.job_name = [
                f"{get_new_job_name(Path(output_dir))}_{i}"
                for i, output_dir in enumerate(self.output_dir)
            ]
        if self.args.combine_input:
            if len(self.args.job_name) != 1:
                raise ArgumentError(
                    msg="--j should have only one value when --combine-input is given."
                )
            self.job_name = self.args.job_name
        else:
            if len(self.args.job_name) == 1:
                if self.inputs:
                    if len(self.output_dir) != len(set(self.output_dir)):
                        raise ArgumentError(
                            msg="-j should have a unique value for each input "
                            + "when -d has duplicate directories. Or, give "
                            + "--combine-input to combine input files into one job."
                        )
                    self.job_name = self.args.job_name * len(self.inputs)
                else:
                    raise
            else:
                if self.inputs:
                    if len(self.inputs) != len(self.args.job_name):
                        raise ArgumentError(
                            msg="Just one or the same number of -j option values "
                            + "as input files should be given."
                        )
                    self.job_name = self.args.job_name
            return

    def set_self_inputs(self):
        from ..exceptions import NoInput

        if self.args is None:
            raise
        self.use_inputs_from_run_conf()
        self.process_url_and_pipe_inputs()
        self.remove_absent_inputs()
        if not self.inputs:
            raise NoInput()

    def use_inputs_from_run_conf(self):
        if self.args and not self.args.inputs:
            inputs = self.run_conf.get("inputs")
            if inputs:
                if type(inputs) == list:
                    self.args.inputs = inputs
                else:
                    if self.outer:
                        self.outer.write(
                            f"inputs in conf file should be a list (received {inputs})."
                        )

    def set_start_end_levels(self):
        from ..exceptions import SetupError

        if self.args is None:
            raise SetupError()
        self.startlevel = self.runlevels.get(self.args.startat, 0)
        if not self.args.endat:
            if self.report_names:
                self.args.endat = "reporter"
            else:
                self.args.endat = "postaggregator"
        self.endlevel = self.runlevels.get(
            self.args.endat, max(self.runlevels.values())
        )

    def set_and_check_input_files(self, run_no: int):
        from pathlib import Path
        from ..consts import STANDARD_INPUT_FILE_SUFFIX
        from ..consts import VARIANT_LEVEL_MAPPED_FILE_SUFFIX
        from ..consts import GENE_LEVEL_MAPPED_FILE_SUFFIX

        if not self.run_name or not self.output_dir:
            raise
        if not self.inputs:
            raise
        if not self.append_mode:
            raise
        run_name = self.run_name[run_no]
        output_dir = self.output_dir[run_no]
        self.crvinput = str(Path(output_dir) / (run_name + STANDARD_INPUT_FILE_SUFFIX))
        self.crxinput = str(
            Path(output_dir) / (run_name + VARIANT_LEVEL_MAPPED_FILE_SUFFIX)
        )
        self.crginput = str(
            Path(output_dir) / (run_name + GENE_LEVEL_MAPPED_FILE_SUFFIX)
        )
        if Path(self.crvinput).exists():
            self.crv_present = True
        else:
            self.crv_present = False
        if Path(self.crxinput).exists():
            self.crx_present = True
        else:
            self.crx_present = False
        if Path(self.crginput).exists():
            self.crg_present = True
        else:
            self.crg_present = False
        if self.append_mode[run_no]:
            self.regenerate_from_db(run_no)
        return True

    def get_package_conf_run_value(self, key: str):
        return self.package_conf.get("run", {}).get(key)

    def set_preparers(self):
        from ..exceptions import SetupError
        from ..module.local import get_local_module_infos_by_names

        if self.args is None:
            raise SetupError()
        self.excludes = self.args.excludes
        if len(self.args.preparers) > 0:
            self.preparer_names = self.args.preparers
        else:
            package_conf_preparers = self.get_package_conf_run_value("preparers")
            if package_conf_preparers:
                self.preparer_names = package_conf_preparers
            else:
                self.preparer_names = []
        if "preparer" in self.args.skip:
            self.preparer_names = []
        elif len(self.excludes) > 0:
            for m in self.excludes:
                if self.preparer_names and m in self.preparer_names:
                    self.preparer_names.remove(m)
        self.check_valid_modules(self.preparer_names)
        self.preparers = get_local_module_infos_by_names(self.preparer_names)

    def is_in_annotators_or_postaggregators(self, module_name):
        return (
            module_name in self.annotator_names
            or module_name in self.postaggregator_names
        )

    def add_required_modules_for_reporters(self):
        from ..module.local import get_local_module_info_by_name
        from ..exceptions import ModuleNotExist

        for reporter in self.reporters.values():
            required_module_names = reporter.conf.get("requires", [])
            for module_name in required_module_names:
                if not self.is_in_annotators_or_postaggregators(module_name):
                    module = get_local_module_info_by_name(module_name)
                    if not module:
                        msg = (
                            f"{module_name} is required by {reporter.name}"
                            + ", but does not exist."
                        )
                        raise ModuleNotExist(module_name, msg=msg)
                    if module.type == "annotator" and self.annotator_names is not None:
                        self.annotator_names.append(module_name)
                        self.annotators[module_name] = module
                    elif (
                        module.type == "postaggregator"
                        and self.postaggregator_names is not None
                    ):
                        self.postaggregator_names.append(module_name)
                        self.postaggregators[module_name] = module

    def add_required_modules_for_postaggregators(self):
        from ..module.local import get_local_module_info_by_name
        from ..exceptions import ModuleNotExist

        for postaggregator in self.postaggregators.values():
            required_module_names = postaggregator.conf.get("requires", [])
            for module_name in required_module_names:
                if not self.is_in_annotators_or_postaggregators(module_name):
                    module = get_local_module_info_by_name(module_name)
                    if not module:
                        msg = (
                            f"{module_name} is required by {postaggregator.name}"
                            + ", but does not exist."
                        )
                        raise ModuleNotExist(module_name, msg=msg)
                    if module.type == "annotator" and self.annotator_names is not None:
                        self.annotator_names.append(module_name)
                        self.annotators[module_name] = module
                    elif (
                        module.type == "postaggregator"
                        and self.postaggregator_names is not None
                    ):
                        self.postaggregator_names.append(module_name)
                        self.postaggregators[module_name] = module

    def set_mapper(self):
        from ..module.local import get_local_module_info_by_name
        from ..exceptions import SetupError
        from ..system import get_modules_dir

        if self.args is None:
            raise SetupError()
        if self.args.mapper_name:
            self.mapper_name = self.args.mapper_name[0]
        else:
            self.mapper_name = self.get_package_conf_run_value("mapper")
        if not self.mapper_name:
            self.mapper_name = self.main_conf.get("genemapper")
        if not self.mapper_name:
            modules_dir = get_modules_dir()
            mapper_module_dirs = []
            if modules_dir:
                mappers_dir = modules_dir / "mappers"
                entries = mappers_dir.glob("*")
                for entry in entries:
                    if not entry.is_dir():
                        continue
                    yml_path = entry / (entry.name + ".yml")
                    if yml_path.exists():
                        mapper_module_dirs.append(entry)
            if len(mapper_module_dirs) == 1:
                self.mapper_name = mapper_module_dirs[0].name
        if not self.mapper_name:
            raise SetupError(msg="Mapper is not defined. Please use -m option to define a mapper module name, such as gencode, or if you are using -c option, add \"run: mapper_name: MAPPER_MODULE_NAME\" in the yml file for the -c option.")
        self.check_valid_modules([self.mapper_name])
        self.mapper = get_local_module_info_by_name(self.mapper_name)

    def set_annotators(self):
        from ..exceptions import SetupError
        from ..module.local import get_local_module_infos_of_type
        from ..module.local import get_local_module_infos_by_names

        if self.args is None:
            raise SetupError()
        annotator_names_from_package = (
            self.get_package_argument_run_value("annotators") or []
        )
        if len(self.args.annotators) > 0:
            if self.args.annotators == ["all"]:
                self.annotator_names = sorted(
                    list(get_local_module_infos_of_type("annotator").keys())
                )
            else:
                self.annotator_names = self.args.annotators
        elif annotator_names_from_package:
            self.annotator_names = annotator_names_from_package
        else:
            self.annotator_names = []
        if "annotator" in self.args.skip:
            self.annotator_names = []
        elif len(self.excludes) > 0:
            self.excludes = self.args.excludes
            if "all" in self.excludes:
                self.annotator_names = []
            else:
                for m in self.excludes:
                    if self.annotator_names and m in self.annotator_names:
                        self.annotator_names.remove(m)
        self.check_valid_modules(self.annotator_names)
        self.annotators = get_local_module_infos_by_names(self.annotator_names)

    def get_package_argument_run_value(self, field: str):
        if not self.package_conf:
            return None
        if not self.package_conf.get("run"):
            return None
        return self.package_conf["run"].get(field, None)

    def set_postaggregators(self):
        from ..exceptions import SetupError
        from ..system.consts import default_postaggregator_names
        from ..module.local import get_local_module_infos_by_names

        if self.args is None:
            raise SetupError()
        postaggregators_from_package = self.get_package_argument_run_value(
            "postaggregators"
        )
        if len(self.args.postaggregators) > 0:
            self.postaggregator_names = self.args.postaggregators
        elif postaggregators_from_package:
            self.postaggregator_names = sorted(
                list(get_local_module_infos_by_names(postaggregators_from_package))
            )
        else:
            self.postaggregator_names = []
        if "postaggregator" in self.args.skip:
            self.postaggregators = {}
            return
        self.postaggregator_names = (
            default_postaggregator_names + self.postaggregator_names
        )
        self.check_valid_modules(self.postaggregator_names)
        self.postaggregators = get_local_module_infos_by_names(
            self.postaggregator_names
        )

    def sort_module_names(self, module_names: list, module_type: str):
        if not module_names:
            return []
        new_module_names = []
        self.sort_module_names_by_requirement(
            module_names, new_module_names, module_type
        )
        return new_module_names

    def sort_annotators(self):
        from ..module.local import get_local_module_infos_by_names

        self.annotator_names = self.sort_module_names(self.annotator_names, "annotator")
        self.annotators = get_local_module_infos_by_names(self.annotator_names)

    def sort_postaggregators(self):
        from ..module.local import get_local_module_infos_by_names

        self.postaggregator_names = self.sort_module_names(
            self.postaggregator_names, "postaggregator"
        )
        self.postaggregators = get_local_module_infos_by_names(
            self.postaggregator_names
        )

    def sort_module_names_by_requirement(
        self, input_module_names, final_module_names: list, module_type: str
    ):
        from ..module.local import get_local_module_info

        if isinstance(input_module_names, list):
            for module_name in input_module_names:
                module = get_local_module_info(module_name)
                if not module:
                    continue
                sub_list = self.sort_module_names_by_requirement(
                    module_name, final_module_names, module_type
                )
                if sub_list:
                    final_module_names.extend(sub_list)
                if (
                    module
                    and module.conf.get("type") == module_type
                    and module_name not in final_module_names
                ):
                    final_module_names.append(module_name)
        elif isinstance(input_module_names, str):
            module_name = input_module_names
            module = get_local_module_info(module_name)
            if not module or module.type != "annotator":
                return None
            final_module_names.append(module_name)
            required_module_names: List[str] = module.conf.get("requires", [])
            if required_module_names:
                if isinstance(required_module_names, list):
                    tsr: Set[str] = set(required_module_names).difference(
                        set(final_module_names)
                    )
                    tsrl: List[str] = list(tsr)
                    self.sort_module_names_by_requirement(
                        tsrl, final_module_names, module_type
                    )
                else:
                    raise Exception(
                        f"module requirement configuration error: {module_name} "
                        + f"=> {required_module_names}"
                    )
            else:
                if module_name in final_module_names:
                    return None
                elif module.conf.get("type") != module_type:
                    return None
                else:
                    return [module_name]

    def set_reporters(self):
        from ..module.local import get_local_module_infos_by_names
        from ..exceptions import SetupError

        if self.args is None:
            raise SetupError()
        if self.args.report_types:
            self.report_names = self.args.report_types
        else:
            package_conf_reports = self.get_package_conf_run_value("reports")
            if package_conf_reports:
                self.report_names = self.get_package_argument_run_value("reports")
            if not self.report_names:
                self.report_names = []
        if "reporter" in self.args.skip:
            self.reporters = {}
        else:
            self.reporter_names = [
                v if v.endswith("reporter") else v + "reporter"
                for v in self.report_names
            ]
            self.check_valid_modules(self.reporter_names)
            self.reporters = get_local_module_infos_by_names(self.reporter_names)

    def _find_secondary_annotators(self, module, ret):
        sannots = self.get_secondary_modules(module)
        for sannot in sannots:
            if sannot is not None:
                ret[sannot.name] = sannot
                self._find_secondary_annotators(sannot, ret)

    def get_module_output_path(self, module, run_no: int):
        import os
        from ..consts import VARIANT_LEVEL_OUTPUT_SUFFIX
        from ..consts import GENE_LEVEL_OUTPUT_SUFFIX

        if not self.run_name or not self.output_dir:
            raise
        run_name, output_dir = self.get_run_name_output_dir_by_run_no(run_no)
        if module.level == "variant":
            postfix = VARIANT_LEVEL_OUTPUT_SUFFIX
        elif module.level == "gene":
            postfix = GENE_LEVEL_OUTPUT_SUFFIX
        else:
            return None
        path = os.path.join(output_dir, run_name + "." + module.name + postfix)
        return path

    def check_module_output(self, module, run_no: int):
        import os

        path = self.get_module_output_path(module, run_no)
        if path is not None and os.path.exists(path):
            return path
        else:
            return None

    def get_secondary_modules(self, primary_module):
        from ..module.local import get_local_module_info

        secondary_modules = [
            get_local_module_info(module_name)
            for module_name in primary_module.secondary_module_names
        ]
        return secondary_modules

    def get_num_workers(self) -> int:
        from ..system import get_max_num_concurrent_modules_per_job
        from psutil import cpu_count

        num_workers = get_max_num_concurrent_modules_per_job()
        if self.args and self.args.mp:
            try:
                self.args.mp = int(self.args.mp)
                if self.args.mp >= 1:
                    num_workers = self.args.mp
            except Exception:
                if self.logger:
                    self.logger.exception(
                        f"error handling --mp argument: {self.args.mp}"
                    )
        if not num_workers:
            num_workers = cpu_count()
        if self.logger:
            self.logger.info("num_workers: {}".format(num_workers))
        return num_workers

    def collect_crxs(self, run_no: int):
        from ..util.util import escape_glob_pattern
        from os import remove
        from pathlib import Path

        run_name, output_dir = self.get_run_name_output_dir_by_run_no(run_no)
        if not output_dir:
            return
        crx_path = Path(output_dir) / f"{run_name}.crx"
        wf = open(str(crx_path), "w")
        fns = sorted(
            [
                str(v)
                for v in Path(output_dir).glob(escape_glob_pattern(run_name) + ".crx.*")
            ]
        )
        fn = fns[0]
        f = open(fn)
        for line in f:
            wf.write(line)
        f.close()
        remove(fn)
        for fn in fns[1:]:
            f = open(fn)
            for line in f:
                if line[0] != "#":
                    wf.write(line)
            f.close()
            remove(fn)
        wf.close()

    def collect_crgs(self, run_no: int):
        from os import remove
        from pathlib import Path
        from ..util.util import escape_glob_pattern
        from ..consts import GENE_LEVEL_MAPPED_FILE_SUFFIX

        run_name, output_dir = self.get_run_name_output_dir_by_run_no(run_no)
        if not output_dir:
            return
        crg_path = Path(output_dir) / f"{run_name}{GENE_LEVEL_MAPPED_FILE_SUFFIX}"
        wf = open(str(crg_path), "w")
        unique_hugos = {}
        fns = sorted(
            [
                str(v)
                for v in crg_path.parent.glob(escape_glob_pattern(crg_path.name) + ".*")
            ]
        )
        fn = fns[0]
        f = open(fn)
        for line in f:
            if line[0] != "#":
                hugo = line.split()[0]
                if hugo not in unique_hugos:
                    unique_hugos[hugo] = line
            else:
                wf.write(line)
        f.close()
        remove(fn)
        for fn in fns[1:]:
            f = open(fn)
            for line in f:
                if line[0] != "#":
                    hugo = line.split()[0]
                    if hugo not in unique_hugos:
                        # wf.write(line)
                        unique_hugos[hugo] = line
            f.close()
            remove(fn)
        hugos = list(unique_hugos.keys())
        hugos.sort()
        for hugo in hugos:
            wf.write(unique_hugos[hugo])
        wf.close()
        del unique_hugos
        del hugos

    def table_exists(self, cursor, table):
        sql = (
            'select name from sqlite_master where type="table" and '
            + 'name="'
            + table
            + '"'
        )
        cursor.execute(sql)
        if cursor.fetchone() is None:
            return False
        else:
            return True

    async def get_mapper_info_from_crx(
        self, run_no: int
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        from pathlib import Path
        from ..consts import VARIANT_LEVEL_MAPPED_FILE_SUFFIX

        run_name, output_dir = self.get_run_name_output_dir_by_run_no(run_no)
        title = None
        version = None
        modulename = None
        fn = Path(output_dir) / (run_name + VARIANT_LEVEL_MAPPED_FILE_SUFFIX)
        if fn.exists():
            f = open(fn)
            for line in f:
                if line.startswith("#title="):
                    title = line.strip().split("=")[1]
                elif line.startswith("#version="):
                    version = line.strip().split("=")[1]
                elif line.startswith("#modulename="):
                    modulename = line.strip().split("=")[1]
                elif line.startswith("#") is False:
                    break
            f.close()
        return title, version, modulename

    def get_run_name_output_dir_by_run_no(self, run_no: int) -> Tuple[str, str]:
        if not self.output_dir or not self.run_name:
            raise
        run_name = self.run_name[run_no]
        output_dir = self.output_dir[run_no]
        return run_name, output_dir

    def get_dbpath(self, run_no: int):
        from pathlib import Path

        run_name, output_dir = self.get_run_name_output_dir_by_run_no(run_no)
        dbpath = str(Path(output_dir) / (run_name + ".sqlite"))
        return dbpath

    async def write_info_row(self, key: str, value: Any, cursor):
        import json

        q = "insert or replace into info values (?, ?)"
        if isinstance(value, list) or isinstance(value, dict):
            value = json.dumps(value)
        await cursor.execute(q, (key, value))

    def get_input_paths_from_mapping_file(self, run_no: int) -> Optional[dict]:
        from pathlib import Path
        import json
        from ..consts import MAPPING_FILE_SUFFIX

        run_name, output_dir = self.get_run_name_output_dir_by_run_no(run_no)
        f = open(Path(output_dir) / (run_name + MAPPING_FILE_SUFFIX))
        for line in f:
            if line.startswith("#input_paths="):
                new_line = "=".join(line.strip().split("=")[1:])
                input_paths = json.loads(new_line)
                return input_paths

    async def create_info_table_if_needed(self, run_no: int, cursor):
        if not self.append_mode[run_no]:
            q = "drop table if exists info"
            await cursor.execute(q)
            q = "create table info (colkey text primary key, colval text)"
            await cursor.execute(q)

    async def refresh_info_table_modified_time(self, cursor):
        from datetime import datetime

        modified = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        q = "insert or replace into info values ('modified_at', ?)"
        await cursor.execute(q, (modified,))

    async def write_info_table_create_data_if_needed(self, run_no: int, cursor):
        from datetime import datetime
        import json
        from ..exceptions import DatabaseError

        if self.append_mode[run_no]:
            return
        if not self.inputs or not self.job_name or not self.args:
            raise
        if self.args.combine_input:
            inputs = self.inputs
        else:
            inputs = [self.inputs[run_no]]
        inputs = [str(v) for v in inputs]
        job_name = self.job_name[run_no]
        genome_assemblies = (
            list(set(self.genome_assemblies[run_no])) if self.genome_assemblies else []
        )
        created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        await self.write_info_row("created_at", created, cursor)
        await self.write_info_row("inputs", json.dumps(inputs), cursor)
        await self.write_info_row(
            "genome_assemblies", json.dumps(genome_assemblies), cursor
        )
        q = "select count(*) from variant"
        await cursor.execute(q)
        r = await cursor.fetchone()
        if r is None:
            raise DatabaseError(msg="table variant does not exist.")
        no_input = str(r[0])
        await self.write_info_row("num_variants", no_input, cursor)
        await self.write_info_row("oakvar", self.pkg_ver, cursor)
        (
            mapper_title,
            mapper_version,
            _,
        ) = await self.get_mapper_info_from_crx(run_no)
        gene_mapper_str = f"{mapper_title}=={mapper_version}"
        await self.write_info_row("mapper", gene_mapper_str, cursor)
        input_paths = self.get_input_paths_from_mapping_file(run_no)
        if input_paths:
            await self.write_info_row("input_paths", json.dumps(input_paths), cursor)
        await self.write_info_row(
            "primary_transcript", ",".join(self.args.primary_transcript), cursor
        )
        await self.write_info_row("job_name", job_name, cursor)
        await self.write_info_row(
            "converter_format", json.dumps(self.converter_format), cursor
        )

    async def write_info_table_annotator_info(self, cursor):
        import json
        from ..module.local import get_local_module_info

        q = 'select colval from info where colkey="annotators_desc"'
        await cursor.execute(q)
        r = await cursor.fetchone()
        if r is None:
            annotator_descs = {}
        else:
            annotator_descs = json.loads(r[0])
        q = "select name, displayname, version from variant_annotator"
        await cursor.execute(q)
        rows = list(await cursor.fetchall())
        q = "select name, displayname, version from gene_annotator"
        await cursor.execute(q)
        tmp_rows = list(await cursor.fetchall())
        if tmp_rows is not None:
            rows.extend(tmp_rows)
        annotator_titles = []
        annotators = []
        for row in rows:
            (name, displayname, version) = row
            if name in ["base", "tagsampler", "hg19", "hg18"]:
                continue
            if version is not None and version != "":
                annotators.append("{}=={}".format(name, version))
            else:
                annotators.append("{}==?".format(name))
            annotator_titles.append(displayname)
            module_info = get_local_module_info(name)
            if module_info is not None and module_info.conf is not None:
                annotator_descs[name] = module_info.conf.get("description", "")
        await self.write_info_row(
            "annotator_descs", json.dumps(annotator_descs), cursor
        )
        await self.write_info_row(
            "annotator_titles", json.dumps(annotator_titles), cursor
        )
        await self.write_info_row("annotators", json.dumps(annotators), cursor)

    async def write_info_table(self, run_no):
        import aiosqlite

        dbpath = self.get_dbpath(run_no)
        conn = await aiosqlite.connect(dbpath)
        cursor = await conn.cursor()
        try:
            await self.create_info_table_if_needed(run_no, cursor)
            await self.refresh_info_table_modified_time(cursor)
            await self.write_info_table_create_data_if_needed(run_no, cursor)
            await self.write_info_table_annotator_info(cursor)
            await conn.commit()
            await cursor.close()
            await conn.close()
        except:
            await cursor.close()
            await conn.close()
            raise

    def clean_up_at_end(self, run_no: int):
        from os import listdir
        from os import remove
        from os.path import getsize
        from pathlib import Path
        from re import compile
        from ..consts import VARIANT_LEVEL_OUTPUT_SUFFIX
        from ..consts import GENE_LEVEL_OUTPUT_SUFFIX
        from ..consts import STANDARD_INPUT_FILE_SUFFIX
        from ..consts import VARIANT_LEVEL_MAPPED_FILE_SUFFIX
        from ..consts import GENE_LEVEL_MAPPED_FILE_SUFFIX
        from ..consts import SAMPLE_FILE_SUFFIX
        from ..consts import MAPPING_FILE_SUFFIX
        from ..consts import ERROR_LOG_SUFFIX

        if (
            self.exception
            or not self.args
            or self.args.keep_temp
            or not self.aggregator_ran
        ):
            return
        if not self.output_dir or not self.run_name:
            raise
        run_name = self.run_name[run_no]
        output_dir = self.output_dir[run_no]
        fns = listdir(output_dir)
        pattern = compile(
            f"{run_name}(\\..*({VARIANT_LEVEL_OUTPUT_SUFFIX}|{GENE_LEVEL_OUTPUT_SUFFIX})|({STANDARD_INPUT_FILE_SUFFIX}|{VARIANT_LEVEL_MAPPED_FILE_SUFFIX}|{GENE_LEVEL_MAPPED_FILE_SUFFIX}|{SAMPLE_FILE_SUFFIX}|{MAPPING_FILE_SUFFIX}))"
        )
        error_logger_pattern = compile(f"{run_name}{ERROR_LOG_SUFFIX}")
        for fn in fns:
            fn_path = Path(output_dir) / fn
            if fn_path.is_file() is False:
                continue
            if pattern.match(fn):
                if self.logger:
                    self.logger.info(f"removing {fn_path}")
                remove(str(fn_path))
            if error_logger_pattern.match(fn) and getsize(fn_path) == 0:
                if self.logger:
                    self.logger.info(f"removing {fn_path}")
                try:  # Windows does not allow deleting a file when it is open.
                    remove(str(fn_path))
                except Exception:
                    pass

    async def write_admin_db_final_info(self, runtime: float, run_no: int):
        import aiosqlite
        from json import dumps
        from ...gui.serveradmindb import get_admindb_path

        if self.args is None or not self.output_dir:
            raise
        if runtime is None or not self.total_num_unique_variants:
            return
        admindb_path = get_admindb_path()
        if not admindb_path or admindb_path.exists() is False:
            s = "{} does not exist.".format(str(admindb_path))
            if self.logger:
                self.logger.info(s)
            if self.outer:
                self.outer.write(s)
            return
        try:
            info_json_s = dumps(self.info_json)
        except Exception as e:
            if self.logger:
                self.logger.exception(e)
            info_json_s = ""
        db = await aiosqlite.connect(str(admindb_path))
        cursor = await db.cursor()
        q = "update jobs set runtime=?, numinput=?, info_json=? where dir=? and name=?"
        await cursor.execute(
            q,
            (
                runtime,
                self.total_num_unique_variants,
                info_json_s,
                self.output_dir[run_no],
                self.args.job_name[run_no],
            ),
        )
        await db.commit()
        await cursor.close()
        await db.close()

    def write_initial_info_json(self, run_no: int):
        from datetime import datetime
        from pathlib import Path
        from ..util.admin_util import oakvar_version

        if not self.run_name or not self.inputs or not self.args or not self.output_dir:
            raise
        run_name = self.run_name[run_no]
        output_dir = self.output_dir[run_no]
        self.info_json = {}
        self.info_json["job_dir"] = self.output_dir
        self.info_json["job_name"] = self.args.job_name
        self.info_json["run_name"] = run_name
        self.info_json["db_path"] = str(Path(output_dir) / (run_name + ".sqlite"))
        self.info_json["orig_input_fname"] = [Path(x).name for x in self.inputs]
        self.info_json["orig_input_path"] = [str(v) for v in self.inputs]
        self.info_json["submission_time"] = datetime.now().isoformat()
        self.info_json["viewable"] = False
        self.info_json["note"] = self.args.note
        self.info_json["report_types"] = (
            self.args.report_types if self.args.report_types is not None else []
        )
        self.info_json["reports"] = self.info_json["report_types"]
        self.pkg_ver = oakvar_version()
        self.info_json["package_version"] = self.pkg_ver
        annot_names = [
            v for v in list(self.annotators.keys()) if v not in ["original_input"]
        ]
        annot_names.sort()
        self.info_json["annotators"] = annot_names
        postagg_names = [
            v
            for v in list(self.postaggregators.keys())
            if v not in ["tagsampler", "vcfinfo"]
        ]
        postagg_names.sort()
        self.info_json["postaggregators"] = postagg_names

    async def run_converter(self, run_no: int):
        import os
        from ..util.util import load_class
        from types import SimpleNamespace
        from ..util.admin_util import get_packagedir
        from ..util.run import announce_module

        if not self.args or not self.inputs or not self.run_name or not self.output_dir:
            raise
        if self.args.combine_input:
            input_files = self.inputs
        else:
            input_files = [self.inputs[run_no]]
        converter_path = os.path.join(
            get_packagedir(), "lib", "base", "master_converter.py"
        )
        module = SimpleNamespace(
            title="Converter", name="converter", script_path=converter_path
        )
        announce_module(module, logger=self.logger, serveradmindb=self.serveradmindb)
        converter_class = load_class(module.script_path, "MasterConverter")
        if not converter_class:
            converter_class = load_class(module.script_path, "MasterCravatConverter")
        if converter_class is None:
            return
        converter = converter_class(
            inputs=input_files,
            name=self.run_name[run_no],
            output_dir=self.output_dir[run_no],
            genome=self.args.genome,
            input_format=self.args.input_format,
            converter_module=self.args.converter_module,
            serveradmindb=self.serveradmindb,
            ignore_sample=self.ignore_sample,
            module_options=self.run_conf,
            skip_variant_deduplication=self.args.skip_variant_deduplication,
            mp=self.args.mp,
            keep_liftover_failed=self.args.keep_liftover_failed,
            outer=self.outer,
        )
        ret = converter.run()
        self.total_num_unique_variants = ret.get("num_unique_variants", 0)
        self.converter_format = ret.get("input_formats") or []
        genome_assembly: List[str] = ret.get("assemblies") or []
        self.genome_assemblies[run_no] = genome_assembly

    async def run_preparers(self, run_no: int):
        from ..util.util import load_class
        from ..consts import MODULE_OPTIONS_KEY

        if not self.run_name or not self.output_dir:
            raise
        run_name = self.run_name[run_no]
        output_dir = self.output_dir[run_no]
        for module_name, module in self.preparers.items():
            module_conf = self.run_conf.get(module_name, {})
            kwargs = {
                "script_path": module.script_path,
                "input_file": self.crvinput,
                "run_name": run_name,
                "output_dir": output_dir,
                MODULE_OPTIONS_KEY: module_conf,
                "serveradmindb": self.serveradmindb,
            }
            module_cls = load_class(module.script_path, "Preparer")
            if not module_cls:
                if self.error_logger:
                    self.error_logger.error(
                        f"{module_name} does not exist. Skipping the module."
                    )
                continue
            module_ins = module_cls(kwargs)
            await self.log_time_of_func(module_ins.run, work=module_name)

    async def run_mapper(self, run_no: int):
        import multiprocessing as mp
        from ..base.mp_runners import init_worker, mapper_runner
        from ..util.inout import FileReader

        if not self.args or not self.run_name or not self.output_dir:
            raise
        run_name = self.run_name[run_no]
        output_dir = self.output_dir[run_no]
        num_workers = self.get_num_workers()
        reader = FileReader(self.crvinput)
        num_lines, chunksize, poss, len_poss, max_num_lines = reader.get_chunksize(
            num_workers
        )
        if self.logger:
            self.logger.info(
                f"input line chunksize={chunksize} total number of "
                + f"input lines={num_lines} number of chunks={len_poss}"
            )
        pool = mp.get_context("spawn").Pool(num_workers, init_worker)
        pos_no = 0
        while pos_no < len_poss:
            jobs = []
            for _ in range(num_workers):
                if pos_no == len_poss:
                    break
                (seekpos, num_lines) = poss[pos_no]
                if pos_no == len_poss - 1:
                    job = pool.apply_async(
                        mapper_runner,
                        (
                            self.crvinput,
                            seekpos,
                            max_num_lines - num_lines,
                            run_name,
                            output_dir,
                            self.mapper_name,
                            pos_no,
                            ";".join(self.args.primary_transcript),
                            self.serveradmindb,
                        ),
                    )
                else:
                    job = pool.apply_async(
                        mapper_runner,
                        (
                            self.crvinput,
                            seekpos,
                            chunksize,
                            run_name,
                            output_dir,
                            self.mapper_name,
                            pos_no,
                            ";".join(self.args.primary_transcript),
                            self.serveradmindb,
                        ),
                    )
                jobs.append(job)
                pos_no += 1
            for job in jobs:
                job.get()
        pool.close()
        self.collect_crxs(run_no)
        self.collect_crgs(run_no)

    async def run_annotators(self, run_no: int):
        import os
        from ..base.mp_runners import init_worker, annot_from_queue
        from multiprocessing import Pool
        from ..system import get_max_num_concurrent_modules_per_job
        from ..consts import INPUT_LEVEL_KEY
        from ..consts import VARIANT_LEVEL_KEY

        if (
            not self.args
            or not self.manager
            or not self.run_name
            or not self.output_dir
        ):
            raise
        run_name = self.run_name[run_no]
        output_dir = self.output_dir[run_no]
        num_workers = get_max_num_concurrent_modules_per_job()
        if self.args.mp is not None:
            try:
                self.args.mp = int(self.args.mp)
                if self.args.mp >= 1:
                    num_workers = self.args.mp
            except Exception:
                if self.logger:
                    self.logger.exception("error handling mp argument:")
        if self.logger:
            self.logger.info("num_workers: {}".format(num_workers))
        run_args = {}
        for module in self.annotators_to_run.values():
            inputpath = None
            if module.level == "variant":
                if module.conf.get("input_format"):
                    input_format = module.conf["input_format"]
                    if input_format == INPUT_LEVEL_KEY:
                        inputpath = self.crvinput
                    elif input_format == VARIANT_LEVEL_KEY:
                        inputpath = self.crxinput
                    else:
                        raise Exception("Incorrect input_format value")
                else:
                    inputpath = self.crxinput
            elif module.level == "gene":
                inputpath = self.crginput
            secondary_inputs = []
            if "secondary_inputs" in module.conf:
                secondary_module_names = module.conf["secondary_inputs"]
                for secondary_module_name in secondary_module_names:
                    secondary_module = self.annotators[secondary_module_name]
                    secondary_output_path = self.get_module_output_path(
                        secondary_module, run_no
                    )
                    if secondary_output_path is None:
                        if self.logger:
                            self.logger.warning(
                                "secondary output file does not exist for "
                                + f"{secondary_module_name}"
                            )
                    else:
                        secondary_inputs.append(
                            secondary_module.name.replace("=", r"\=")
                            + "="
                            + os.path.join(output_dir, secondary_output_path).replace(
                                "=", r"\="
                            )
                        )
            kwargs = {
                "input_file": inputpath,
                "secondary_inputs": secondary_inputs,
                "module_options": self.run_conf.get(module.name, {}),
            }
            kwargs["run_name"] = run_name
            kwargs["output_dir"] = output_dir
            run_args[module.name] = (module, kwargs)
        start_queue = self.manager.Queue()
        end_queue = self.manager.Queue()
        all_mnames = set(self.annotators_to_run)
        assigned_mnames = set()
        done_mnames = set(self.done_annotators)
        queue_populated = self.manager.Value("c_bool", False)
        pool_args = [
            [
                start_queue,
                end_queue,
                queue_populated,
                self.serveradmindb,
                self.args.logtofile,
                self.log_path,
            ]
        ] * num_workers
        with Pool(num_workers, init_worker) as pool:
            _ = pool.starmap_async(
                annot_from_queue,
                pool_args,
                error_callback=lambda _, mp_pool=pool: mp_pool.terminate(),
            )
            pool.close()
            for mname, module in self.annotators_to_run.items():
                if (
                    mname not in assigned_mnames
                    and set(module.secondary_module_names) <= done_mnames
                ):
                    start_queue.put(run_args[mname])
                    assigned_mnames.add(mname)
            while (
                assigned_mnames != all_mnames
            ):  # TODO not handling case where parent module errors out
                finished_module = end_queue.get()
                done_mnames.add(finished_module)
                for mname, module in self.annotators_to_run.items():
                    if (
                        mname not in assigned_mnames
                        and set(module.secondary_module_names) <= done_mnames
                    ):
                        start_queue.put(run_args[mname])
                        assigned_mnames.add(mname)
            queue_populated = True
            pool.join()
        if len(self.annotators_to_run) > 0:
            self.annotator_ran = True

    async def run_aggregator(self, run_no: int):
        db_path = await self.run_aggregator_level("variant", run_no)
        await self.run_aggregator_level("gene", run_no)
        await self.run_aggregator_level("sample", run_no)
        await self.run_aggregator_level("mapping", run_no)
        return db_path

    async def run_aggregator_level(self, level, run_no: int):
        from time import time
        from ..base.aggregator import Aggregator
        from ..util.run import update_status

        if self.append_mode[run_no] and level not in ["variant", "gene"]:
            return
        if not self.run_name or not self.output_dir:
            raise
        run_name = self.run_name[run_no]
        output_dir = self.output_dir[run_no]
        update_status(
            f"running Aggregator ({level})",
            logger=self.logger,
            serveradmindb=self.serveradmindb,
        )
        stime = time()
        arg_dict = {
            "input_dir": output_dir,
            "output_dir": output_dir,
            "level": level,
            "run_name": run_name,
            "serveradmindb": self.serveradmindb,
        }
        if self.cleandb and level == "variant":
            arg_dict["delete"] = True
        if self.append_mode[run_no]:
            arg_dict["append"] = True
        v_aggregator = Aggregator(**arg_dict)
        v_aggregator.run()
        rtime = time() - stime
        update_status(
            f"Aggregator {level} finished in {rtime:.3f}s",
            logger=self.logger,
            serveradmindb=self.serveradmindb,
        )
        return v_aggregator.db_path

    async def run_postaggregators(self, run_no: int):
        from time import time
        from ..util.run import announce_module
        from ..util.util import load_class
        from ..util.run import update_status
        from ..system.consts import default_postaggregator_names
        from ..consts import MODULE_OPTIONS_KEY

        if not self.run_name or not self.output_dir:
            raise
        run_name = self.run_name[run_no]
        output_dir = self.output_dir[run_no]
        for module_name, module in self.postaggregators.items():
            if self.append_mode[run_no] and module_name in default_postaggregator_names:
                continue
            arg_dict = {
                "module_name": module_name,
                "run_name": run_name,
                "output_dir": output_dir,
                "serveradmindb": self.serveradmindb,
            }
            postagg_conf = self.run_conf.get(module_name, {})
            if postagg_conf:
                arg_dict[MODULE_OPTIONS_KEY] = postagg_conf
            post_agg_cls = load_class(module.script_path, "PostAggregator")
            if not post_agg_cls:
                post_agg_cls = load_class(module.script_path, "CravatPostAggregator")
            if not post_agg_cls:
                if self.error_logger:
                    self.error_logger.error(
                        f"{module_name} does not exist. Skipping the module."
                    )
                continue
            post_agg = post_agg_cls(**arg_dict)
            announce_module(module, serveradmindb=self.serveradmindb)
            stime = time()
            post_agg.run()
            rtime = time() - stime
            update_status(
                f"{module_name} finished in {rtime:.3f}s",
                logger=self.logger,
                serveradmindb=self.serveradmindb,
            )

    async def run_vcf2vcf(self, run_no: int):
        from time import time
        from os.path import abspath
        from types import SimpleNamespace
        from ..util.util import load_class
        from ..util.run import update_status
        from ..base import vcf2vcf
        from ..exceptions import ModuleNotExist

        if not self.args or not self.output_dir or not self.run_name:
            raise
        if not self.inputs:
            raise
        response = {}
        module = {
            "name": "vcf2vcf",
            "title": "VCF to VCF",
            "script_path": abspath(vcf2vcf.__file__),
        }
        module = SimpleNamespace(**module)
        arg_dict = dict(vars(self.args))
        arg_dict["output_dir"] = self.output_dir[run_no]
        arg_dict["module_name"] = module.name
        arg_dict["conf"] = self.conf
        arg_dict["mapper_name"] = self.mapper_name
        arg_dict["annotator_names"] = self.annotator_names
        arg_dict["run_name"] = self.run_name[run_no]
        Module = load_class(module.script_path, "VCF2VCF")
        if not Module:
            raise ModuleNotExist("vcf2vcf", "VCF2VCF module does not exist.")
        m = Module(**arg_dict)
        stime = time()
        response_t = m.run()
        output_fns = None
        response_type = type(response_t)
        if response_type == list:
            output_fns = " ".join(response_t)
        elif response_type == str:
            output_fns = response_t
        if output_fns is not None:
            update_status(
                f"report created: {output_fns} ",
                logger=self.logger,
                serveradmindb=self.serveradmindb,
            )
        report_type = "vcf2vcf"
        response[report_type] = response_t
        rtime = time() - stime
        update_status(
            f"vcf2vcf finished in {rtime:.3f}s",
            logger=self.logger,
            serveradmindb=self.serveradmindb,
        )
        self.report_response = response

    async def run_reporter(self, run_no: int, head_n: Optional[int] = None):
        from pathlib import Path
        from ..util.util import load_class
        from ..util.run import update_status
        from ..exceptions import ModuleNotExist
        from ..util.run import announce_module
        from ..consts import MODULE_OPTIONS_KEY
        from .reporter import BaseReporter

        if not self.run_name or not self.args or not self.output_dir or not self.inputs:
            raise
        run_name = self.run_name[run_no]
        output_dir = Path(self.output_dir[run_no])
        response = {}
        for module_name, module in self.reporters.items():
            reporter = None
            announce_module(module, serveradmindb=self.serveradmindb)
            if module is None:
                raise ModuleNotExist(module_name)
            arg_dict = {}  # dict(vars(self.args))
            arg_dict["dbpath"] = output_dir / (run_name + ".sqlite")
            arg_dict["savepath"] = output_dir / run_name
            arg_dict["output_dir"] = output_dir
            arg_dict["run_name"] = run_name
            arg_dict["module_name"] = module_name
            arg_dict["filtersql"] = self.filtersql
            arg_dict[MODULE_OPTIONS_KEY] = self.run_conf.get(module_name, {})
            Reporter: Type[BaseReporter] = load_class(module.script_path, "Reporter")  # type: ignore
            reporter = Reporter(**arg_dict)
            response_t = await self.log_time_of_func(
                reporter.run, head_n=head_n, work=module_name
            )
            output_fns = None
            if isinstance(response_t, list):
                output_fns = " ".join(response_t)
            elif isinstance(response_t, str):
                output_fns = response_t
            if output_fns is not None:
                update_status(
                    f"report created: {output_fns} ",
                    logger=self.logger,
                    serveradmindb=self.serveradmindb,
                )
            report_type: str = module_name.replace("reporter", "")
            response[report_type] = response_t
        return response

    def should_run_step(self, step: str):
        return (
            self.endlevel >= self.runlevels[step]
            and self.startlevel <= self.runlevels[step]
            and (self.args and step not in self.args.skip)
        )

    async def do_step_converter(self, run_no: int):
        from ..util.run import update_status

        if not self.inputs or not self.args:
            raise
        step = "converter"
        if not self.should_run_step("converter"):
            return
        await self.log_time_of_func(self.run_converter, run_no, work=f"{step} step")
        if self.total_num_unique_variants == 0:
            msg = "No variant found in input"
            update_status(msg, logger=self.logger, serveradmindb=self.serveradmindb)
            if self.logger:
                self.logger.info(msg)

    async def do_step_preparer(self, run_no: int):
        step = "preparer"
        if not self.should_run_step(step):
            return
        await self.log_time_of_func(self.run_preparers, run_no, work=f"{step} step")

    async def do_step_mapper(self, run_no: int):
        step = "mapper"
        self.mapper_ran = False
        if self.should_run_step("mapper"):
            await self.log_time_of_func(self.run_mapper, run_no, work=f"{step} step")
            self.mapper_ran = True

    async def do_step_annotator(self, run_no: int):
        step = "annotator"
        self.annotator_ran = False
        self.done_annotators = {}
        self.populate_secondary_annotators(run_no)
        for mname, module in self.annotators.items():
            if self.check_module_output(module, run_no) is not None:
                self.done_annotators[mname] = module
        self.annotators_to_run = {
            aname: self.annotators[aname]
            for aname in set(self.annotators) - set(self.done_annotators)
        }
        if self.should_run_step(step) and (
            self.mapper_ran or len(self.annotators_to_run) > 0
        ):
            await self.log_time_of_func(
                self.run_annotators, run_no, work=f"{step} step"
            )
            self.annotator_ran = True

    async def do_step_aggregator(self, run_no: int):
        step = "aggregator"
        self.aggregator_ran = False
        if self.should_run_step(step) and (
            self.mapper_ran
            or self.annotator_ran
            or self.startlevel == self.runlevels["aggregator"]
        ):
            self.result_path = await self.log_time_of_func(
                self.run_aggregator, run_no, work=f"{step} step"
            )
            await self.write_info_table(run_no)
            self.aggregator_ran = True

    async def do_step_postaggregator(self, run_no: int):
        step = "postaggregator"
        if self.should_run_step(step):
            await self.log_time_of_func(
                self.run_postaggregators, run_no, work=f"{step} step"
            )

    async def do_step_reporter(self, run_no: int):
        step = "reporter"
        if self.should_run_step(step) and self.reporters:
            self.report_response = await self.log_time_of_func(
                self.run_reporter, run_no, work=f"{step} step"
            )

    async def log_time_of_func(self, func, *args, work="", **kwargs):
        from time import time
        from ..util.run import update_status

        stime = time()
        update_status(
            f"starting {work}...",
            logger=self.logger,
            serveradmindb=self.serveradmindb,
        )
        ret = await func(*args, **kwargs)
        rtime = time() - stime
        update_status(
            f"{work} finished in {rtime:.3f}s",
            logger=self.logger,
            serveradmindb=self.serveradmindb,
        )
        return ret
