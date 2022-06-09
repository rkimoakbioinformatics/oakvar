from .decorators import cli_func
from .decorators import cli_entry


@cli_entry
def cli_ov_run(args):
    ret = ov_run(args)
    return ret


@cli_func
def ov_run(args):
    from asyncio import run
    from . import admin_util as au
    # nested asyncio
    import nest_asyncio
    nest_asyncio.apply()
    # Windows event loop patch
    from sys import platform, version_info
    if platform == "win32" and version_info >= (3, 8):
        from asyncio import set_event_loop_policy, WindowsSelectorEventLoopPolicy  # type: ignore
        set_event_loop_policy(WindowsSelectorEventLoopPolicy())
    # Custom system conf
    system_option = args.get("system_option", [])
    if system_option:
        from . import admin_util
        custom_system_conf = {}
        for kv in system_option:
            if "=" not in kv:
                continue
            toks = kv.split("=")
            if len(toks) != 2:
                continue
            [k, v] = toks
            try:
                v = int(v)
            except ValueError:
                pass
            custom_system_conf[k] = v
        admin_util.custom_system_conf = custom_system_conf
        admin_util.update_mic()
    au.ready_resolution_console()
    #try:
    module = Cravat(**args)
    return run(module.main())
    #except Exception as e:
    #    from .exceptions import ExpectedException
    #    if isinstance(e, ExpectedException):
    #        from sys import stderr
    #        stderr.write(str(e) + "\n")
    #    else:
    #        raise e


class Cravat(object):

    def __init__(self, **kwargs):
        self.runlevels = {
            "converter": 1,
            "mapper": 2,
            "annotator": 3,
            "aggregator": 4,
            "postaggregator": 5,
            "reporter": 6,
        }
        self.should_run_converter = False
        self.should_run_genemapper = False
        self.should_run_annotators = True
        self.should_run_aggregator = True
        self.should_run_reporter = True
        self.mapper_ran = False
        self.annotator_ran = False
        self.aggregator_ran = False
        self.done_annotators = {}
        self.status_json_path = None
        self.status_json = None
        self.pkg_ver = None
        self.logger = None
        self.logmode = "w"
        self.log_path = None
        self.error_logger = None
        self.log_handler = None
        self.error_log_handler = None
        self.start_time = None
        self.unique_logs = None
        self.manager = None
        self.status_writer = None
        self.run_annotators = {}
        self.result_path = None
        self.package_conf = {}
        self.args = None
        self.main_conf = {}
        self.conf_run = {}
        self.conf_path = None
        self.conf = {}
        self.num_input = None
        self.first_non_url_input = None
        self.inputs = None
        self.run_name = None
        self.output_dir = None
        self.input_assembly = None
        self.startlevel = self.runlevels["converter"]
        self.endlevel = self.runlevels["postaggregator"]
        self.verbose = False
        self.cleandb = False
        self.excludes = []
        self.annotator_names = []
        self.mapper_name = None
        self.mapper = None
        self.postaggregator_names = []
        self.postaggregators = {}
        self.report_names = []
        self.reports = {}
        self.reporter_names = []
        self.crvinput = None
        self.crxinput = None
        self.crginput = None
        self.crv_present = False
        self.crx_present = False
        self.crg_present = False
        self.annot_names = []
        self.numinput = None
        self.converter_format = None
        self.genemapper = None
        self.ordered_summarizers = []
        from sys import executable
        self.pythonpath = executable
        self.annotators = {}
        self.append_mode = False
        self.pipeinput = False
        self.inkwargs = kwargs
        self.exception = None

    def check_valid_modules(self, module_names):
        from .exceptions import ModuleNotExist
        from . import admin_util as au
        for module_name in module_names:
            if not au.module_exists_local(module_name):
                raise ModuleNotExist(module_name)

    def close_logger(self):
        import logging
        if self.log_handler:
            self.log_handler.close()
            if self.logger is not None:
                self.logger.removeHandler(self.log_handler)
        if self.error_log_handler:
            self.error_log_handler.close()
            if self.error_logger:
                self.error_logger.removeHandler(self.error_log_handler)
        logging.shutdown()

    def delete_output_files(self):
        if self.run_name is None or self.output_dir is None:
            from .exceptions import SetupError
            raise SetupError()
        import os
        import glob
        from .util import quiet_print
        fns = glob.glob(os.path.join(self.output_dir, self.run_name + ".*"))
        for fn in fns:
            quiet_print(f"  Removing {fn}", self.args)
            os.remove(fn)

    def download_url_input(self, input_no):
        if self.inputs is None:
            from .exceptions import NoInputException
            raise NoInputException()
        from .util import is_url, humanize_bytes
        ip = self.inputs[input_no]
        if " " in ip:
            print(f"Space is not allowed in input file paths ({ip})")
            exit()
        if is_url(ip):
            import os
            import requests
            from .util import quiet_print
            quiet_print(f"Fetching {ip}... ", self.args)
            try:
                r = requests.head(ip)
                r = requests.get(ip, stream=True)
                fn = os.path.basename(ip)
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
                            f"[{cur_prog}{rem_prog}] {humanize_bytes(cur_size)} / {humanize_bytes(total_size)} ({perc * 100.0:.0f}%)",
                            end="\r",
                            flush=True,
                        )
                        if cur_size == total_size:
                            print("\n")
                self.inputs[input_no] = os.path.abspath(fpath)
            except:
                print(f"File downloading unsuccessful. Exiting.")
                exit()
            return None
        else:
            return ip

    def get_logger(self):
        if self.args is None or self.run_name is None or self.output_dir is None or self.run_name is None:
            from .exceptions import SetupError
            raise SetupError()
        import os
        import logging
        if self.args.newlog == True:
            self.logmode = "w"
        else:
            self.logmode = "a"
        self.logger = logging.getLogger("oakvar")
        self.logger.setLevel("INFO")
        self.log_path = os.path.join(self.output_dir, self.run_name + ".log")
        if os.path.exists(self.log_path):
            os.remove(self.log_path)
        self.log_handler = logging.FileHandler(self.log_path,
                                               mode=self.logmode)
        formatter = logging.Formatter("%(asctime)s %(name)-20s %(message)s",
                                      "%Y/%m/%d %H:%M:%S")
        self.log_handler.setFormatter(formatter)
        self.logger.addHandler(self.log_handler)
        # individual input line error log
        self.error_logger = logging.getLogger("error")
        self.error_logger.setLevel("INFO")
        error_log_path = os.path.join(self.output_dir, self.run_name + ".err")
        if os.path.exists(error_log_path):
            os.remove(error_log_path)
        self.error_log_handler = logging.FileHandler(error_log_path,
                                                     mode=self.logmode)
        formatter = logging.Formatter("SOURCE:%(name)-20s %(message)s")
        self.error_log_handler.setFormatter(formatter)
        self.error_logger.addHandler(self.error_log_handler)

    """def handle_exception(self, e):
        if self.args is None:
            from .exceptions import SetupError
            raise SetupError()
        from sys import stderr
        try:
            from .exceptions import ExpectedException
            if isinstance(e, ExpectedException):
                if hasattr(self, "logger") and self.logger and not getattr(
                        e, "nolog", False):
                    self.logger.error(e)
                stderr.write(str(e) + "\n")
                stderr.flush()
            else:
                if hasattr(self, "logger") and self.logger:
                    self.logger.exception("An unexpected exception occurred.")
        except Exception as e2:
            stderr.write(str(e) + "\n")
            stderr.flush()
            raise e2"""

    def log_versions(self):
        if self.args is None:
            from .exceptions import SetupError
            raise SetupError()
        import os
        from . import admin_util as au
        if self.logger:
            self.logger.info(
                f"version: oakvar {au.get_current_package_version()} {os.path.dirname(os.path.abspath(__file__))}"
            )
            if self.package_conf is not None and len(self.package_conf) > 0:
                self.logger.info(
                    f'package: {self.args.package} {self.package_conf["version"]}'
                )
            for _, module in self.annotators.items():
                self.logger.info(
                    f"version: {module.name} {module.conf['version']} {os.path.dirname(module.script_path)}"
                )
            if "mapper" not in self.args.skip:
                module = self.mapper
                if module is None:
                    from .exceptions import ModuleLoadingError
                    raise ModuleLoadingError("mapper")
                self.logger.info(
                    f'version: {module.name} {module.conf["version"]} {os.path.dirname(module.script_path)}'
                )
            for _, module in self.reports.items():
                self.logger.info(
                    f"version: {module.name} {module.conf['version']} {os.path.dirname(module.script_path)}"
                )

    async def main(self):
        from .util import quiet_print
        from time import time, asctime, localtime
        from multiprocessing.managers import SyncManager
        from sys import argv
        report_response = None
        self.aggregator_ran = False
        try:
            self.start_time = time()
            self.make_args_namespace(self.inkwargs)
            if self.args is None:
                from .exceptions import SetupError
                raise SetupError("Cravat")
            if self.args.clean_run:
                quiet_print("Deleting previous output files...", self.args)
                self.delete_output_files()
            self.get_logger()
            if self.logger:
                self.logger.info(f'{" ".join(argv)}')
                self.logger.info("started: {0}".format(
                    asctime(localtime(self.start_time))))
                if self.conf_path != "":
                    self.logger.info("conf file: {}".format(
                        self.conf_path))
            self.write_initial_status_json()
            self.unique_logs = {}
            self.manager = SyncManager()
            self.manager.register("StatusWriter", StatusWriter)
            self.manager.start()
            self.status_writer = self.manager.StatusWriter(  # type: ignore
                self.status_json_path)
            self.update_status("Started OakVar", force=True)
            if self.inputs is None:
                from .exceptions import NoInputException
                raise NoInputException()
            if self.pipeinput == False:
                input_files_str = ", ".join(self.inputs)
            else:
                input_files_str = "stdin"
            if self.logger:
                self.logger.info("input files: {}".format(input_files_str))
                self.logger.info("input assembly: {}".format(
                    self.input_assembly))
            self.log_versions()
            self.set_and_check_input_files()
            if (self.endlevel >= self.runlevels["converter"]
                    and self.startlevel <= self.runlevels["converter"]
                    and not "converter" in self.args.skip):
                quiet_print("Running converter...", self.args)
                stime = time()
                self.run_converter()
                rtime = time() - stime
                quiet_print("finished in {0:.3f}s".format(rtime), self.args)
                if self.numinput == 0:
                    msg = "No variant found in input"
                    quiet_print(msg, self.args)
                    if self.logger:
                        self.logger.info(msg)
                    exit()
            self.mapper_ran = False
            if (self.endlevel >= self.runlevels["mapper"]
                    and self.startlevel <= self.runlevels["mapper"]
                    and not "mapper" in self.args.skip):
                quiet_print(f'Running gene mapper...{" "*18}', self.args)
                stime = time()
                #multicore_mapper_mode = self.main_conf.get("multicore_mapper_mode")
                self.run_genemapper_mp()
                #if multicore_mapper_mode:
                #    self.run_genemapper_mp()
                #else:
                #    self.run_genemapper()
                rtime = time() - stime
                quiet_print("finished in {0:.3f}s".format(rtime), self.args)
                self.mapper_ran = True
            self.annotator_ran = False
            self.done_annotators = {}
            self.populate_secondary_annotators()
            for mname, module in self.annotators.items():
                if self.check_module_output(module) is not None:
                    self.done_annotators[mname] = module
            self.run_annotators = {
                aname: self.annotators[aname]
                for aname in set(self.annotators) - set(self.done_annotators)
            }
            if (self.endlevel >= self.runlevels["annotator"]
                    and self.startlevel <= self.runlevels["annotator"]
                    and not "annotator" in self.args.skip
                    and (self.mapper_ran or len(self.run_annotators) > 0)):
                quiet_print("Running annotators...", self.args)
                stime = time()
                self.run_annotators_mp()
                rtime = time() - stime
                quiet_print(
                    "\tannotator(s) finished in {0:.3f}s".format(rtime),
                    self.args)
            if (self.endlevel >= self.runlevels["aggregator"]
                    and self.startlevel <= self.runlevels["aggregator"]
                    and not "aggregator" in self.args.skip
                    and (self.mapper_ran or self.annotator_ran
                         or self.startlevel == self.runlevels["aggregator"])):
                quiet_print("Running aggregator...", self.args)
                self.result_path = self.run_aggregator()
                await self.write_job_info()
                self.write_smartfilters()
                self.aggregator_ran = True
            if (self.endlevel >= self.runlevels["postaggregator"]
                    and self.startlevel <= self.runlevels["postaggregator"]
                    and not "postaggregator" in self.args.skip):
                quiet_print("Running postaggregators...", self.args)
                self.run_postaggregators()
            if (self.endlevel >= self.runlevels["reporter"]
                    and self.startlevel <= self.runlevels["reporter"]
                    and not "reporter" in self.args.skip
                    and self.aggregator_ran and self.reports):
                quiet_print("Running reporter...", self.args)
                report_response = await self.run_reporter()
            self.update_status("Finished", force=True)
        except Exception as e:
            self.exception = e
            #self.handle_exception(e)
        finally:
            end_time = time()
            display_time = asctime(localtime(end_time))
            self.logger = getattr(self, "logger", None)
            self.status_writer = getattr(self, "status_writer", None)
            runtime = None
            if self.start_time:
                runtime = end_time - self.start_time
            if not self.exception:
                if self.logger:
                    self.logger.info("finished: {0}".format(display_time))
                    if runtime:
                        self.logger.info("runtime: {0:0.3f}s".format(runtime))
                    quiet_print(
                        "Finished normally. Runtime: {0:0.3f}s".format(
                            runtime), self.args)
            else:
                #if self.args and not self.args.quiet:
                #if isinstance(exception, ExpectedException):
                #if self.logger and self.log_path:
                #from sys import stderr
                #stderr.write(
                #    "Log file at {}".format(self.log_path) + "\n")
                #stderr.flush()
                if self.status_writer:
                    self.update_status("Error", force=True)
            if self.logger:
                self.close_logger()
            if self.status_writer and self.status_writer and self.args and self.args.do_not_change_status != True:
                self.status_writer.flush()
            if not self.exception and self.args and not self.args.temp_files and self.aggregator_ran:
                self.clean_up_at_end()
            if self.args and self.args.writeadmindb:
                await self.write_admin_db(runtime, self.numinput)
            if self.exception:
                raise self.exception
            return report_response

    def update_status(self, status, force=False):
        if self.args is None:
            from .exceptions import SetupError
            raise SetupError()
        if self.args.do_not_change_status != True:
            if self.status_writer:
                self.status_writer.queue_status_update("status",
                                                       status,
                                                       force=force)

    def make_args_namespace(self, args):
        self.set_package_conf(args)
        self.make_self_args_considering_package_conf(args)
        if self.args is None:
            from .exceptions import SetupError
            raise SetupError()
        if self.args.show_version:
            from .cli_version import cli_version
            from .exceptions import NormalExit
            cli_version({"to": "stdout"})
            raise NormalExit
        self.set_self_inputs()
        self.set_output_dir()
        self.set_run_name()
        self.set_append_mode()
        if self.args.skip is None:
            self.args.skip = []
        self.set_md()
        self.set_mapper()
        self.set_annotators()
        self.set_postaggregators()
        self.set_reporters()
        self.verbose = self.args.verbose == True
        self.set_genome_assembly()
        self.set_start_end_levels()
        self.cleandb = self.args.cleandb
        if self.args.note == None:
            self.args.note = ""

    def make_self_args_considering_package_conf(self, args):
        from types import SimpleNamespace
        full_args = args
        # package including -a (add) and -A (replace)
        if "run" in self.package_conf:
            for k, v in self.package_conf["run"].items():
                if k == "annotators" and v and isinstance(v, list):
                    if not full_args["annotators_replace"]:
                        for v2 in v:
                            if v2 not in full_args["annotators"]:
                                full_args["annotators"].append(v2)
                else:
                    if k not in full_args or not full_args[k]:
                        full_args[k] = v
        self.conf_path = full_args.get("confpath", None)
        self.make_self_conf(full_args)
        from .admin_util import get_main_conf
        self.main_conf = get_main_conf()
        self.conf_run = self.conf.get("run", {})
        for k, v in self.conf_run.items():
            if k not in full_args or (not full_args[k] and v):
                full_args[k] = v
        if full_args["annotators_replace"]:
            full_args["annotators"] = full_args["annotators_replace"]
        from sys import stderr
        self.args = SimpleNamespace(**full_args)
        self.process_module_options()

    def make_self_conf(self, args):
        if args is None:
            from .exceptions import SetupError
            raise SetupError()
        import json
        from .util import quiet_print
        self.conf_run = args.get("conf", {}).get("run", {})
        confs = args.get("confs")
        if confs:
            conf_bak = self.conf
            try:
                confs_conf = json.loads(confs.replace("'", '"'))
                self.conf.update(confs_conf)
            except Exception:
                quiet_print(
                    "Error in processing cs option. --cs option was not applied.",
                    self.args)
                self.conf = conf_bak

    def populate_secondary_annotators(self):
        import os
        secondaries = {}
        for module in self.annotators.values():
            self._find_secondary_annotators(module, secondaries)
        self.annotators.update(secondaries)
        annot_names = [v.name for v in self.annotators.values()]
        annot_names = list(set(annot_names))
        filenames = os.listdir(self.output_dir)
        for filename in filenames:
            toks = filename.split(".")
            if len(toks) == 3:
                extension = toks[2]
                if toks[0] == self.run_name and (extension == "var"
                                                 or extension == "gen"):
                    annot_name = toks[1]
                    if annot_name not in annot_names:
                        annot_names.append(annot_name)
        annot_names.sort()
        if self.status_writer is not None and self.startlevel <= self.runlevels[
                "annotator"]:
            self.status_writer.queue_status_update("annotators",
                                                   annot_names,
                                                   force=True)
        self.annot_names = annot_names

    def process_module_options(self):
        if self.args is None or self.conf is None:
            from .exceptions import SetupError
            raise SetupError()
        from .util import quiet_print
        if self.args.module_option is not None:
            for opt_str in self.args.module_option:
                toks = opt_str.split("=")
                if len(toks) != 2:
                    quiet_print(
                        "Ignoring invalid module option {opt_str}. module-option should be module_name.key=value.",
                        self.args)
                    continue
                k = toks[0]
                if k.count(".") != 1:
                    quiet_print(
                        "Ignoring invalid module option {opt_str}. module-option should be module_name.key=value.",
                        self.args)
                    continue
                [module_name, key] = k.split(".")
                if module_name not in self.conf_run:
                    self.conf_run[module_name] = {}
                v = toks[1]
                self.conf_run[module_name][key] = v

    def process_url_and_pipe_inputs(self):
        if self.args is None:
            from .exceptions import SetupError
            raise SetupError()
        from .util import is_url
        self.first_non_url_input = None
        if (self.args.inputs is not None and len(self.args.inputs) == 1
                and self.args.inputs[0] == "-"):
            self.pipeinput = True
            if self.args.forcedinputformat is None:
                from .exceptions import InvalidInputFormat
                raise InvalidInputFormat(
                    fmt="--input-format is needed for pipe input.")
        if self.args.inputs is not None:
            import os
            self.inputs = [
                os.path.abspath(x) if not is_url(x) and x != "-" else x
                for x in self.args.inputs
            ]
            if self.inputs is None:
                from .exceptions import NoInputException
                raise NoInputException()
            for input_no in range(len(self.inputs)):
                if (self.download_url_input(input_no) is not None
                        and self.first_non_url_input is None):
                    self.first_non_url_input = self.inputs[input_no]
        else:
            self.inputs = []

    def regenerate_from_db(self):
        if self.inputs is None or len(self.inputs) == 0:
            from .exceptions import NoInputException
            raise NoInputException
        import sqlite3
        from .constants import crv_def, crx_def, crg_def
        from .inout import CravatWriter
        dbpath = self.inputs[0]
        db = sqlite3.connect(dbpath)
        c = db.cursor()
        # Variant
        if not self.crv_present:
            crv = CravatWriter(self.crvinput, columns=crv_def)
            crv.write_definition()
        else:
            crv = None
        if not self.crx_present:
            crx = CravatWriter(self.crxinput, columns=crx_def)
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
            crg = CravatWriter(self.crginput, columns=crg_def)
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
        import os
        import shutil
        if self.inputs is None or self.num_input is None:
            from .exceptions import NoInputException
            raise NoInputException()
        if self.run_name is None or self.args is None:
            from .exceptions import SetupError
            raise SetupError()
        if self.num_input > 0 and self.inputs[0].endswith(".sqlite"):
            self.append_mode = True
            if self.args.skip is None:
                self.args.skip = ["converter", "mapper"]
            else:
                if "converter" not in self.args.skip:
                    self.args.skip.append("converter")
                if "mapper" not in self.args.skip:
                    self.args.skip.append("mapper")
            if self.args.output_dir:
                if self.run_name.endswith(".sqlite"):
                    target_name = self.run_name
                else:
                    target_name = self.run_name + ".sqlite"
                target_path = os.path.join(self.args.output_dir, target_name)
                shutil.copyfile(self.inputs[0], target_path)
                self.inputs[0] = target_path
            if self.run_name.endswith(".sqlite"):
                self.run_name = self.run_name[:-7]

    def set_genome_assembly(self):
        if self.args is None:
            from .exceptions import SetupError
            raise SetupError()
        from .sysadmin_const import default_assembly_key
        if self.args.genome is None:
            if default_assembly_key in self.main_conf:
                self.input_assembly = self.main_conf[default_assembly_key]
            else:
                from .exceptions import NoGenomeException
                raise NoGenomeException()
        else:
            self.input_assembly = self.args.genome

    def set_output_dir(self):
        if self.args is None:
            from .exceptions import SetupError
            raise SetupError()
        import os
        self.output_dir = self.args.output_dir
        if self.output_dir == None:
            if self.num_input == 0 or self.first_non_url_input is None:
                self.output_dir = os.getcwd()
            else:
                self.output_dir = os.path.dirname(
                    os.path.abspath(self.first_non_url_input))
        else:
            self.output_dir = os.path.abspath(self.output_dir)
        if os.path.exists(self.output_dir) == False:
            os.mkdir(self.output_dir)

    def set_package_conf(self, args):
        from . import admin_util as au
        package_name = args.get("package", None)
        if package_name:
            if package_name in au.get_mic().get_local():
                self.package_conf = au.get_mic().get_local()[package_name].conf
            else:
                self.package_conf = {}
        else:
            self.package_conf = {}

    def set_run_name(self):
        if self.inputs is None or self.num_input is None:
            from .exceptions import NoInputException
            raise NoInputException()
        if self.args is None:
            from .exceptions import SetupError
            raise SetupError()
        import os
        self.run_name = self.args.run_name
        if self.run_name == None:
            if self.num_input == 0 or self.pipeinput:
                self.run_name = "ovjob"
            else:
                self.run_name = os.path.basename(self.inputs[0])
                if self.num_input > 1:
                    self.run_name += "_and_" + str(len(self.inputs) -
                                                   1) + "_files"

    def set_self_inputs(self):
        if self.args is None:
            from .exceptions import SetupError
            raise SetupError()
        from .util import quiet_print
        if self.args.inputs is not None and len(self.args.inputs) == 0:
            if "inputs" in self.conf_run:
                if type(self.conf_run["inputs"]) == list:
                    self.args.inputs = self.conf_run["inputs"]
                else:
                    quiet_print("inputs in conf file is invalid", self.args)
            else:
                from .exceptions import NoInputException
                raise NoInputException()
        self.process_url_and_pipe_inputs()
        if self.inputs is None:
            from .exceptions import NoInputException
            raise NoInputException()
        self.num_input = len(self.inputs)

    def set_start_end_levels(self):
        if self.args is None:
            from .exceptions import SetupError
            raise SetupError()
        if self.append_mode and self.args.endat is None:
            self.args.endat = "aggregator"
        try:
            self.startlevel = self.runlevels[self.args.startat]
        except KeyError:
            self.startlevel = 0
        try:
            self.endlevel = self.runlevels[self.args.endat]
        except KeyError:
            self.endlevel = max(self.runlevels.values())

    def set_and_check_input_files(self):
        if self.run_name is None or self.output_dir is None:
            from .exceptions import SetupError
            raise SetupError()
        if self.inputs is None or len(self.inputs) == 0:
            from .exceptions import NoInputException
            raise NoInputException
        import os
        self.crvinput = os.path.join(self.output_dir, self.run_name + ".crv")
        self.crxinput = os.path.join(self.output_dir, self.run_name + ".crx")
        self.crginput = os.path.join(self.output_dir, self.run_name + ".crg")
        if os.path.exists(self.crvinput):
            self.crv_present = True
        else:
            self.crv_present = False
        if os.path.exists(self.crxinput):
            self.crx_present = True
        else:
            self.crx_present = False
        if os.path.exists(self.crginput):
            self.crg_present = True
        else:
            self.crg_present = False
        if self.append_mode:
            self.regenerate_from_db()
        return True

    def set_annotators(self):
        if self.args is None:
            from .exceptions import SetupError
            raise SetupError()
        from . import admin_util as au
        self.excludes = self.args.excludes
        if len(self.args.annotators) > 0:
            if self.args.annotators == ["all"]:
                self.annotator_names = sorted(
                    list(
                        au.get_local_module_infos_of_type("annotator").keys()))
            else:
                self.annotator_names = self.args.annotators
        elif (self.package_conf is not None and "run" in self.package_conf
              and "annotators" in self.package_conf["run"]):
            self.annotator_names = self.package_conf["run"]["annotators"]
        else:
            self.annotator_names = []
        if "annotator" in self.args.skip:
            self.annotator_names = []
        elif len(self.excludes) > 0:
            if "all" in self.excludes:
                self.annotator_names = []
            else:
                for m in self.excludes:
                    if m in self.annotator_names:
                        self.annotator_names.remove(m)
        self.check_valid_modules(self.annotator_names)
        self.annotators = au.get_local_module_infos_by_names(
            self.annotator_names)

    def set_mapper(self):
        if self.args is None or self.conf is None:
            from .exceptions import SetupError
            raise SetupError()
        from . import admin_util as au
        if self.args.mapper_name:
            self.mapper_name = self.args.mapper_name[0]
        elif (self.package_conf is not None and "run" in self.package_conf
              and "mapper" in self.package_conf["run"]):
            self.mapper_name = self.package_conf.get("run", {}).get("mapper")
        else:
            self.mapper_name = self.main_conf.get("genemapper")
        self.check_valid_modules([self.mapper_name])
        self.mapper = au.get_local_module_info_by_name(self.mapper_name)

    def set_md(self):
        if self.args is None:
            from .exceptions import SetupError
            raise SetupError()
        from . import sysadmin_const
        if self.args.md is not None:
            sysadmin_const.custom_modules_dir = self.args.md

    def set_postaggregators(self):
        if self.args is None:
            from .exceptions import SetupError
            raise SetupError()
        from .sysadmin_const import default_postaggregator_names
        from . import admin_util as au
        if len(self.args.postaggregators) > 0:
            self.postaggregator_names = self.args.postaggregators
        elif (self.package_conf is not None and "run" in self.package_conf
              and "postaggregators" in self.package_conf["run"]):
            self.postaggregator_names = sorted(
                list(
                    au.get_local_module_infos_by_names(
                        self.package_conf["run"]["postaggregators"])))
        else:
            self.postaggregator_names = []
        if "postaggregator" in self.args.skip:
            self.postaggregators = {}
        else:
            self.postaggregator_names = sorted(
                list(
                    set(self.postaggregator_names).union(
                        set(default_postaggregator_names))))
            if "casecontrol" in self.postaggregator_names:
                if au.module_exists_local("casecontrol") == False:
                    self.postaggregator_names.remove("casecontrol")
            self.check_valid_modules(self.postaggregator_names)
            self.postaggregators = au.get_local_module_infos_by_names(
                self.postaggregator_names)

    def set_reporters(self):
        if self.args is None:
            from .exceptions import SetupError
            raise SetupError()
        from . import admin_util as au
        if len(self.args.reports) > 0:
            self.report_names = self.args.reports
        elif (self.package_conf is not None and "run" in self.package_conf
              and "reports" in self.package_conf["run"]):
            self.report_names = self.package_conf["run"]["reports"]
        else:
            self.report_names = []
        if "reporter" in self.args.skip:
            self.reports = {}
        else:
            self.reporter_names = [v + "reporter" for v in self.report_names]
            self.check_valid_modules(self.reporter_names)
            self.reports = au.get_local_module_infos_by_names(
                self.reporter_names)

    def _find_secondary_annotators(self, module, ret):
        sannots = self.get_secondary_modules(module)
        for sannot in sannots:
            if sannot is not None:
                ret[sannot.name] = sannot
                self._find_secondary_annotators(sannot, ret)

    def get_module_output_path(self, module):
        if self.run_name is None or self.output_dir is None:
            from .exceptions import SetupError
            raise SetupError()
        import os
        if module.level == "variant":
            postfix = ".var"
        elif module.level == "gene":
            postfix = ".gen"
        else:
            return None
        path = os.path.join(self.output_dir,
                            self.run_name + "." + module.name + postfix)
        return path

    def check_module_output(self, module):
        import os
        path = self.get_module_output_path(module)
        if path is not None and os.path.exists(path):
            return path
        else:
            return None

    def get_secondary_modules(self, primary_module):
        from . import admin_util as au
        secondary_modules = [
            au.get_local_module_info(module_name)
            for module_name in primary_module.secondary_module_names
        ]
        return secondary_modules

    def run_converter(self):
        import os
        from .util import load_class
        from types import SimpleNamespace
        if self.conf is None or self.args is None:
            from .exceptions import SetupError
            raise SetupError()
        converter_path = os.path.join(os.path.dirname(__file__),
                                      "cravat_convert.py")
        module = SimpleNamespace(title="Converter",
                                 name="converter",
                                 script_path=converter_path)
        arg_dict = {
            "path": module.script_path,
            "inputs": self.inputs,
            "name": self.run_name,
            "output_dir": self.output_dir,
            "genome": self.input_assembly,
        }
        arg_dict["conf"] = self.conf_run
        if self.args.forcedinputformat is not None:
            arg_dict["format"] = self.args.forcedinputformat
        if self.args.unique_variants:
            arg_dict["unique_variants"] = True
        self.announce_module(module)
        if self.verbose:
            print(
                " ".join([str(k) + "=" + str(v) for k, v in arg_dict.items()]),
                self.args)
        arg_dict["status_writer"] = self.status_writer
        converter_class = load_class(module.script_path,
                                     "MasterCravatConverter")
        converter = converter_class(arg_dict)
        self.numinput, self.converter_format = converter.run()

    def run_genemapper(self):
        if self.args is None:
            from .exceptions import SetupError
            raise SetupError()
        from .util import load_class
        from . import admin_util as au
        from .util import quiet_print
        module = au.get_local_module_info(self.main_conf.get("genemapper"))
        if module is None:
            from .exceptions import ModuleLoadingError
            raise ModuleLoadingError(self.main_conf.get("genemapper"))
        self.genemapper = module
        cmd = [
            module.script_path,
            self.crvinput,
            "-n",
            self.run_name,
            "-d",
            self.output_dir,
        ]
        if self.args.primary_transcript is not None:
            if "mane" not in self.args.primary_transcript:
                self.args.primary_transcript.append("mane")
            cmd.extend(["--primary-transcript"])
            cmd.extend(self.args.primary_transcript)
        if self.verbose:
            quiet_print(" ".join(cmd), self.args)
        genemapper_class = load_class(module.script_path, "Mapper")
        genemapper = genemapper_class(cmd, self.status_writer)
        genemapper.run()

    def run_genemapper_mp(self):
        if self.args is None or self.output_dir is None:
            from .exceptions import SetupError
            raise SetupError()
        import os
        import glob
        import multiprocessing as mp
        from .mp_runners import init_worker, mapper_runner
        from .inout import CravatReader
        from .sysadmin import get_max_num_concurrent_annotators_per_job
        num_workers = get_max_num_concurrent_annotators_per_job()
        if self.args.mp is not None:
            try:
                self.args.mp = int(self.args.mp)
                if self.args.mp >= 1:
                    num_workers = self.args.mp
            except:
                if self.logger:
                    self.logger.exception("error handling mp argument:")
        if self.logger:
            self.logger.info("num_workers: {}".format(num_workers))
        reader = CravatReader(self.crvinput)
        num_lines, chunksize, poss, len_poss, max_num_lines = reader.get_chunksize(
            num_workers)
        if self.logger:
            self.logger.info(
                f"input line chunksize={chunksize} total number of input lines={num_lines} number of chunks={len_poss}"
            )
        pool = mp.Pool(num_workers, init_worker)
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
                            self.run_name,
                            self.output_dir,
                            self.status_writer,
                            self.mapper_name,
                            pos_no,
                            ";".join(self.args.primary_transcript),
                        ),
                    )
                else:
                    job = pool.apply_async(
                        mapper_runner,
                        (
                            self.crvinput,
                            seekpos,
                            chunksize,
                            self.run_name,
                            self.output_dir,
                            self.status_writer,
                            self.mapper_name,
                            pos_no,
                            ";".join(self.args.primary_transcript),
                        ),
                    )
                jobs.append(job)
                pos_no += 1
            for job in jobs:
                job.get()
        pool.close()
        # collects crx.
        crx_path = os.path.join(self.output_dir, f"{self.run_name}.crx")
        wf = open(crx_path, "w")
        fns = sorted(glob.glob(crx_path + "[.]*"))
        fn = fns[0]
        f = open(fn)
        for line in f:
            wf.write(line)
        f.close()
        os.remove(fn)
        for fn in fns[1:]:
            f = open(fn)
            for line in f:
                if line[0] != "#":
                    wf.write(line)
            f.close()
            os.remove(fn)
        wf.close()
        # collects crg.
        crg_path = os.path.join(self.output_dir, f"{self.run_name}.crg")
        wf = open(crg_path, "w")
        unique_hugos = {}
        fns = sorted(glob.glob(crg_path + "[.]*"))
        fn = fns[0]
        f = open(fn)
        for line in f:
            if line[0] != "#":
                hugo = line.split()[0]
                if hugo not in unique_hugos:
                    # wf.write(line)
                    unique_hugos[hugo] = line
            else:
                wf.write(line)
        f.close()
        os.remove(fn)
        for fn in fns[1:]:
            f = open(fn)
            for line in f:
                if line[0] != "#":
                    hugo = line.split()[0]
                    if hugo not in unique_hugos:
                        # wf.write(line)
                        unique_hugos[hugo] = line
            f.close()
            os.remove(fn)
        hugos = list(unique_hugos.keys())
        hugos.sort()
        for hugo in hugos:
            wf.write(unique_hugos[hugo])
        wf.close()
        del unique_hugos
        del hugos
        # collects crt.
        crt_path = os.path.join(self.output_dir, f"{self.run_name}.crt")
        """
        wf = open(crt_path, 'w')
        """
        unique_trs = {}
        fns = sorted(glob.glob(crt_path + "[.]*"))
        fn = fns[0]
        """
        f = open(fn)
        for line in f:
            if line[0] != '#':
                [tr, alt] = line.split()[:1]
                if tr not in unique_trs:
                    unique_trs[tr] = {}
                if alt not in unique_trs[tr]:
                    unique_trs[tr][alt] = True
                    wf.write(line)
            else:
                wf.write(line)
        f.close()
        """
        os.remove(fn)
        for fn in fns[1:]:
            """
            f = open(fn)
            for line in f:
                if line[0] != '#':
                    [tr, alt] = line.split()[:1]
                    if tr not in unique_trs:
                        unique_trs[tr] = {}
                    if alt not in unique_trs[tr]:
                        unique_trs[tr][alt] = True
                        wf.write(line)
            f.close()
            """
            os.remove(fn)
        wf.close()
        del unique_trs

    def run_aggregator(self):
        from time import time
        from .aggregator import Aggregator
        from .util import quiet_print
        # Variant level
        quiet_print("\t{0:30s}\t".format("Variants"), self.args)
        stime = time()
        cmd = [
            "donotremove",
            "-i",
            self.output_dir,
            "-d",
            self.output_dir,
            "-l",
            "variant",
            "-n",
            self.run_name,
        ]
        if self.cleandb:
            cmd.append("-x")
        if self.append_mode:
            cmd.append("--append")
        if self.verbose:
            quiet_print(" ".join(cmd), self.args)
        self.update_status(
            "Running {title} ({level})".format(title="Aggregator",
                                               level="variant"),
            force=True,
        )
        v_aggregator = Aggregator(cmd, self.status_writer)
        v_aggregator.run()
        rtime = time() - stime
        quiet_print("finished in {0:.3f}s".format(rtime), self.args)
        # Gene level
        quiet_print("\t{0:30s}\t".format("Genes"), self.args)
        stime = time()
        cmd = [
            "donotremove",
            "-i",
            self.output_dir,
            "-d",
            self.output_dir,
            "-l",
            "gene",
            "-n",
            self.run_name,
        ]
        if self.append_mode:
            cmd.append("--append")
        if self.verbose:
            quiet_print(" ".join(cmd), self.args)
        self.update_status(
            "Running {title} ({level})".format(title="Aggregator",
                                               level="gene"),
            force=True,
        )
        g_aggregator = Aggregator(cmd, self.status_writer)
        g_aggregator.run()
        rtime = time() - stime
        quiet_print("finished in {0:.3f}s".format(rtime), self.args)
        # Sample level
        if not self.append_mode:
            quiet_print("\t{0:30s}\t".format("Samples"), self.args)
            stime = time()
            cmd = [
                "donotremove",
                "-i",
                self.output_dir,
                "-d",
                self.output_dir,
                "-l",
                "sample",
                "-n",
                self.run_name,
            ]
            if self.verbose:
                quiet_print(" ".join(cmd), self.args)
            self.update_status(
                "Running {title} ({level})".format(title="Aggregator",
                                                   level="sample"),
                force=True,
            )
            s_aggregator = Aggregator(cmd, self.status_writer)
            s_aggregator.run()
            rtime = time() - stime
            quiet_print("finished in {0:.3f}s".format(rtime), self.args)
        # Mapping level
        if not self.append_mode:
            quiet_print("\t{0:30s}\t".format("Tags"), self.args)
            cmd = [
                "donotremove",
                "-i",
                self.output_dir,
                "-d",
                self.output_dir,
                "-l",
                "mapping",
                "-n",
                self.run_name,
            ]
            if self.verbose:
                quiet_print(" ".join(cmd), self.args)
            self.update_status(
                "Running {title} ({level})".format(title="Aggregator",
                                                   level="mapping"),
                force=True,
            )
            m_aggregator = Aggregator(cmd, self.status_writer)
            m_aggregator.run()
            rtime = time() - stime
            quiet_print("finished in {0:.3f}s".format(rtime), self.args)
        return v_aggregator.db_path

    def run_postaggregators(self):
        if self.conf is None:
            from .exceptions import SetupError
            raise SetupError()
        from time import time
        from .util import load_class
        import json
        from .util import quiet_print
        for module_name, module in self.postaggregators.items():
            cmd = [
                module.script_path, "-d", self.output_dir, "-n", self.run_name
            ]
            postagg_conf = {}
            postagg_conf.update(self.conf_run.get(module_name, {}))
            if postagg_conf:
                confs = json.dumps(postagg_conf)
                confs = "'" + confs.replace("'", '"') + "'"
                cmd.extend(["--confs", confs])
            if self.verbose:
                quiet_print(" ".join(cmd), self.args)
            post_agg_cls = load_class(module.script_path,
                                      "CravatPostAggregator")
            post_agg = post_agg_cls(cmd, self.status_writer)
            if post_agg.should_run_annotate:
                self.announce_module(module)
            stime = time()
            post_agg.run()
            rtime = time() - stime
            if post_agg.should_run_annotate:
                quiet_print("finished in {0:.3f}s".format(rtime), self.args)

    async def run_reporter(self):
        if self.run_name is None or self.conf is None or self.args is None or self.output_dir is None:
            from .exceptions import SetupError
            raise SetupError()
        if self.inputs is None:
            from .exceptions import NoInputException
            raise NoInputException()
        from time import time
        import os
        from .util import load_class
        from . import admin_util as au
        from .util import quiet_print
        if len(self.reports) > 0:
            module_names = [v for v in self.reports.keys()]
            report_types = [
                v.replace("reporter", "") for v in self.reports.keys()
            ]
        else:
            module_names = []
            report_types = []
        response = {}
        for report_type, module_name in zip(report_types, module_names):
            reporter = None
            module = au.get_local_module_info(module_name)
            self.announce_module(module)
            if module is None:
                from .exceptions import ModuleNotExist
                raise ModuleNotExist(module_name)
            arg_dict = dict(vars(self.args))
            arg_dict["script_path"] = module.script_path
            arg_dict["dbpath"] = os.path.join(self.output_dir, self.run_name + ".sqlite")
            arg_dict["savepath"] = os.path.join(self.output_dir, self.run_name)
            arg_dict["output_dir"] = self.output_dir
            arg_dict["module_name"] = module_name
            """
            if self.conf_path is not None:
                arg_dict["confpath"] = self.conf_path
            arg_dict["conf"] = self.conf_run.get(module_name, {})
            if self.pipeinput == False:
                arg_dict["inputfiles"] = []
                for input_file in self.inputs:
                    arg_dict["inputfiles"].append(f"{input_file}")
            if self.args.separatesample:
                arg_dict["separatesample"] = True
            if self.verbose:
                print(
                    " ".join(
                        [str(k) + "=" + str(v) for k, v in arg_dict.items()]),
                    self.args)
            arg_dict["status_writer"] = self.status_writer
            arg_dict["reports"] = [module_name.replace("reporter", "")]
            arg_dict["concise_report"] = self.args.concise_report
            arg_dict["package"] = self.args.package
            arg_dict["filtersql"] = self.args.filtersql
            arg_dict["includesample"] = self.args.includesample
            arg_dict["excludesample"] = self.args.excludesample
            arg_dict["filter"] = self.args.filter
            arg_dict["filterpath"] = self.args.filterpath
            arg_dict["md"] = self.args.md
            """
            arg_dict["conf"] = self.conf
            Reporter = load_class(module.script_path, "Reporter")
            reporter = Reporter(arg_dict)
            await reporter.prep()
            stime = time()
            response_t = await reporter.run()
            output_fns = None
            response_type = type(response_t)
            if response_type == list:
                output_fns = " ".join(response_t)
            elif response_type == str:
                output_fns = response_t
            if output_fns is not None:
                quiet_print(f"report created: {output_fns} ", self.args)
            response[report_type] = response_t
            rtime = time() - stime
            quiet_print("finished in {0:.3f}s".format(rtime), self.args)
        return response

    def run_annotators_mp(self):
        if self.args is None or self.manager is None or self.run_name is None or self.output_dir is None:
            from .exceptions import SetupError
            raise SetupError()
        import os
        import logging
        from .mp_runners import init_worker, annot_from_queue
        from multiprocessing import Pool
        from .sysadmin import get_max_num_concurrent_annotators_per_job
        num_workers = get_max_num_concurrent_annotators_per_job()
        if self.args.mp is not None:
            try:
                self.args.mp = int(self.args.mp)
                if self.args.mp >= 1:
                    num_workers = self.args.mp
            except:
                if self.logger:
                    self.logger.exception("error handling mp argument:")
        if self.logger:
            self.logger.info("num_workers: {}".format(num_workers))
        run_args = {}
        for module in self.run_annotators.values():
            inputpath = None
            # Make command
            if module.level == "variant":
                if "input_format" in module.conf:
                    input_format = module.conf["input_format"]
                    if input_format == "crv":
                        inputpath = self.crvinput
                    elif input_format == "crx":
                        inputpath = self.crxinput
                    else:
                        raise Exception("Incorrect input_format value")
                        # inputpath = self.input
                else:
                    inputpath = self.crvinput
            elif module.level == "gene":
                inputpath = self.crginput
            # secondary_opts = []
            secondary_inputs = []
            if "secondary_inputs" in module.conf:
                secondary_module_names = module.conf["secondary_inputs"]
                for secondary_module_name in secondary_module_names:
                    secondary_module = self.annotators[secondary_module_name]
                    secondary_output_path = self.get_module_output_path(
                        secondary_module)
                    if secondary_output_path is None:
                        if self.logger:
                            self.logger.warning(
                                f"secondary output file does not exist for {secondary_module_name}"
                            )
                    else:
                        secondary_inputs.append(
                            secondary_module.name.replace("=", r"\=") + "=" +
                            os.path.join(self.output_dir, secondary_output_path
                                         ).replace("=", r"\="))
            kwargs = {
                "script_path": module.script_path,
                "input_file": inputpath,
                "secondary_inputs": secondary_inputs,
                "quiet": self.args.quiet,
                "log_path": self.log_path,
            }
            if self.run_name != None:
                kwargs["run_name"] = self.run_name
            if self.output_dir != None:
                kwargs["output_dir"] = self.output_dir
            run_args[module.name] = (module, kwargs)
        if self.logger and self.log_handler:
            self.logger.removeHandler(self.log_handler)
        start_queue = self.manager.Queue()
        end_queue = self.manager.Queue()
        all_mnames = set(self.run_annotators)
        assigned_mnames = set()
        done_mnames = set(self.done_annotators)
        queue_populated = self.manager.Value("c_bool", False)
        pool_args = [[
            start_queue, end_queue, queue_populated, self.status_writer
        ]] * num_workers
        with Pool(num_workers, init_worker) as pool:
            _ = pool.starmap_async(
                annot_from_queue,
                pool_args,
                error_callback=lambda _, mp_pool=pool: mp_pool.terminate(),
            )
            pool.close()
            for mname, module in self.run_annotators.items():
                if (mname not in assigned_mnames
                        and set(module.secondary_module_names) <= done_mnames):
                    start_queue.put(run_args[mname])
                    assigned_mnames.add(mname)
            while (assigned_mnames != all_mnames
                   ):  # TODO not handling case where parent module errors out
                finished_module = end_queue.get()
                done_mnames.add(finished_module)
                for mname, module in self.run_annotators.items():
                    if (mname not in assigned_mnames and
                            set(module.secondary_module_names) <= done_mnames):
                        start_queue.put(run_args[mname])
                        assigned_mnames.add(mname)
            queue_populated = True
            pool.join()
        self.log_path = os.path.join(self.output_dir, self.run_name + ".log")
        self.log_handler = logging.FileHandler(self.log_path, "a")
        formatter = logging.Formatter("%(asctime)s %(name)-20s %(message)s",
                                      "%Y/%m/%d %H:%M:%S")
        self.log_handler.setFormatter(formatter)
        if self.logger:
            self.logger.addHandler(self.log_handler)
        if len(self.run_annotators) > 0:
            self.annotator_ran = True

    def table_exists(self, cursor, table):
        sql = ('select name from sqlite_master where type="table" and ' +
               'name="' + table + '"')
        cursor.execute(sql)
        if cursor.fetchone() == None:
            return False
        else:
            return True

    async def get_converter_format_from_crv(self):
        if self.run_name is None or self.output_dir is None:
            from .exceptions import SetupError
            raise SetupError()
        import os
        converter_format = None
        fn = os.path.join(self.output_dir, self.run_name + ".crv")
        if os.path.exists(fn):
            f = open(fn)
            for line in f:
                if line.startswith("#input_format="):
                    converter_format = line.strip().split("=")[1]
                    break
            f.close()
        return converter_format

    async def get_mapper_info_from_crx(self):
        if self.run_name is None or self.output_dir is None:
            from .exceptions import SetupError
            raise SetupError()
        import os
        title = None
        version = None
        modulename = None
        fn = os.path.join(self.output_dir, self.run_name + ".crx")
        if os.path.exists(fn):
            f = open(fn)
            for line in f:
                if line.startswith("#title="):
                    title = line.strip().split("=")[1]
                elif line.startswith("#version="):
                    version = line.strip().split("=")[1]
                elif line.startswith("#modulename="):
                    modulename = line.strip().split("=")[1]
                elif line.startswith("#") == False:
                    break
            f.close()
        return title, version, modulename

    async def write_job_info(self):
        if self.run_name is None or self.input_assembly is None or self.args is None or self.output_dir is None:
            from .exceptions import SetupError
            raise SetupError()
        if self.inputs is None:
            from .exceptions import NoInputException
            raise NoInputException()
        import os
        import aiosqlite
        from datetime import datetime
        import json
        from . import admin_util as au
        dbpath = os.path.join(self.output_dir, self.run_name + ".sqlite")
        conn = await aiosqlite.connect(dbpath)
        cursor = await conn.cursor()
        if not self.append_mode:
            q = "drop table if exists info"
            await cursor.execute(q)
            q = "create table info (colkey text primary key, colval text)"
            await cursor.execute(q)
        modified = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        q = ('insert or replace into info values ("Result modified at", "' +
             modified + '")')
        await cursor.execute(q)
        if not self.append_mode:
            created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            q = 'insert into info values ("Result created at", "' + created + '")'
            await cursor.execute(q)
            q = 'insert into info values ("Input file name", "{}")'.format(
                ";".join(self.inputs))
            await cursor.execute(q)
            q = ('insert into info values ("Input genome", "' +
                 self.input_assembly + '")')
            await cursor.execute(q)
            q = "select count(*) from variant"
            await cursor.execute(q)
            r = await cursor.fetchone()
            if r is None:
                from .exceptions import DatabaseError
                raise DatabaseError(msg="table variant does not exist.")
            no_input = str(r[0])
            q = (
                'insert into info values ("Number of unique input variants", "'
                + no_input + '")')
            await cursor.execute(q)
            q = 'insert into info values ("oakvar", "{}")'.format(self.pkg_ver)
            await cursor.execute(q)
            q = 'insert into info values ("_converter_format", "{}")'.format(
                await self.get_converter_format_from_crv())
            await cursor.execute(q)
            (
                mapper_title,
                mapper_version,
                mapper_modulename,
            ) = await self.get_mapper_info_from_crx()
            genemapper_str = "{} ({})".format(mapper_title, mapper_version)
            q = 'insert into info values ("Gene mapper", "{}")'.format(
                genemapper_str)
            await cursor.execute(q)
            q = 'insert into info values ("_mapper", "{}:{}")'.format(
                mapper_modulename, mapper_version)
            await cursor.execute(q)
            f = open(os.path.join(self.output_dir, self.run_name + ".crm"))
            for line in f:
                if line.startswith("#input_paths="):
                    input_path_dict_str = "=".join(
                        line.strip().split("=")[1:]).replace('"', "'")
                    q = 'insert into info values ("_input_paths", "{}")'.format(
                        input_path_dict_str)
                    await cursor.execute(q)
            q = f'insert into info values ("primary_transcript", "{",".join(self.args.primary_transcript)}")'
            await cursor.execute(q)
        q = 'select colval from info where colkey="annotators_desc"'
        await cursor.execute(q)
        r = await cursor.fetchone()
        if r is None:
            annotator_desc_dict = {}
        else:
            annotator_desc_dict = json.loads(r[0])
        q = "select name, displayname, version from variant_annotator"
        await cursor.execute(q)
        rows = list(await cursor.fetchall())
        q = "select name, displayname, version from gene_annotator"
        await cursor.execute(q)
        tmp_rows = list(await cursor.fetchall())
        if tmp_rows is not None:
            rows.extend(tmp_rows)
        annotators_str = ""
        annotator_version = {}
        annotators = []
        for row in rows:
            (name, displayname, version) = row
            if name in ["base", "tagsampler", "hg19", "hg18"]:
                continue
            if version is not None and version != "":
                annotators_str += "{} ({}), ".format(displayname, version)
                annotators.append("{}:{}".format(name, version))
            else:
                annotators_str += "{}, ".format(displayname)
                annotators.append("{}:".format(name))
            annotator_version[name] = version
            module_info = au.get_local_module_info(name)
            if module_info is not None and module_info.conf is not None:
                annotator_desc_dict[name] = module_info.conf["description"]
        q = 'insert or replace into info values ("_annotator_desc", "{}")'.format(
            json.dumps(annotator_desc_dict).replace('"', "'"))
        await cursor.execute(q)
        if self.args.do_not_change_status != True:
            if self.status_writer:
                self.status_writer.queue_status_update("annotator_version",
                                                       annotator_version,
                                                       force=True)
        q = ('insert or replace into info values ("Annotators", "' +
             annotators_str + '")')
        await cursor.execute(q)
        q = 'insert or replace into info values ("_annotators", "{}")'.format(
            ",".join(annotators))
        await cursor.execute(q)
        await conn.commit()
        await cursor.close()
        await conn.close()

    def run_summarizers(self):
        for module in self.ordered_summarizers:
            self.announce_module(module)
            self.run_summarizer(module)

    def run_summarizer(self, module):
        if self.args is None:
            from .exceptions import SetupError
            raise SetupError()
        from .util import load_class
        cmd = [module.script_path, "-l", "variant"]
        if self.run_name != None:
            cmd.extend(["-n", self.run_name])
        if self.output_dir != None:
            cmd.extend(["-d", self.output_dir])
        if self.verbose:
            if not self.args.quiet:
                print(" ".join(cmd))
        summarizer_cls = load_class(module.script_path, "")
        summarizer = summarizer_cls(cmd)
        summarizer.run()

    def announce_module(self, module):
        if self.args is None:
            from .exceptions import SetupError
            raise SetupError()
        if not self.args.quiet:
            print(
                "\t{0:30s}\t".format(module.title + " (" + module.name + ")"),
                end="",
                flush=True,
            )
        self.update_status(
            "Running {title} ({name})".format(title=module.title,
                                              name=module.name),
            force=True,
        )

    def clean_up_at_end(self):
        if self.output_dir is None or self.run_name is None:
            from .exceptions import SetupError
            raise SetupError()
        import os
        fns = os.listdir(self.output_dir)
        for fn in fns:
            fn_path = os.path.join(self.output_dir, fn)
            if os.path.isfile(fn_path) == False:
                continue
            if fn.startswith(self.run_name):
                fn_end = fn.split(".")[-1]
                if fn_end in [
                        "var", "gen", "crv", "crx", "crg", "crs", "crm", "crt"
                ]:
                    os.remove(os.path.join(self.output_dir, fn))
                if fn.split(".")[-2:] == ["status", "json"]:
                    os.remove(os.path.join(self.output_dir, fn))

    async def write_admin_db(self, runtime, numinput):
        if self.args is None:
            from .exceptions import SetupError
            raise SetupError()
        import os
        import aiosqlite
        from .admin_util import get_admindb_path
        from .util import quiet_print
        if runtime is None or numinput is None:
            return
        if os.path.exists(get_admindb_path()) == False:
            s = "{} does not exist.".format(get_admindb_path())
            if self.logger:
                self.logger.info(s)
            quiet_print(s, self.args)
            return
        db = await aiosqlite.connect(get_admindb_path())
        cursor = await db.cursor()
        q = 'update jobs set runtime={}, numinput={} where jobid="{}"'.format(
            runtime, numinput, self.args.jobid)
        await cursor.execute(q)
        await db.commit()
        await cursor.close()
        await db.close()

    def write_initial_status_json(self):
        if self.run_name is None or self.inputs is None or self.args is None or self.output_dir is None:
            from .exceptions import SetupError
            raise SetupError()
        import os
        from datetime import datetime
        import json
        from . import admin_util as au
        status_fname = "{}.status.json".format(self.run_name)
        self.status_json_path = os.path.join(self.output_dir, status_fname)
        if os.path.exists(self.status_json_path) == True:
            with open(self.status_json_path) as f:
                try:
                    self.status_json = json.load(f)
                    self.pkg_ver = self.status_json["open_cravat_version"]
                except:
                    self.pkg_ver = au.get_current_package_version()
            if self.status_json and self.status_json["status"] == "Submitted":
                self.status_json["job_dir"] = self.output_dir
                self.status_json["id"] = os.path.basename(
                    os.path.normpath(self.output_dir))
                self.status_json["run_name"] = self.run_name
                self.status_json["assembly"] = self.input_assembly
                self.status_json["db_path"] = os.path.join(
                    self.output_dir, self.run_name + ".sqlite")
                self.status_json["orig_input_fname"] = [
                    os.path.basename(x) for x in self.inputs
                ]
                self.status_json["orig_input_path"] = self.inputs
                self.status_json["submission_time"] = datetime.now().isoformat(
                )
                self.status_json["viewable"] = False
                self.status_json["note"] = self.args.note
                self.status_json["status"] = "Starting"
                self.status_json["reports"] = (
                    self.args.reports if self.args.reports != None else [])
                self.pkg_ver = au.get_current_package_version()
                self.status_json["open_cravat_version"] = self.pkg_ver
                annot_names = list(self.annotators.keys())
                annot_names.sort()
                if "original_input" in annot_names:
                    annot_names.remove("original_input")
                self.status_json["annotators"] = annot_names
                with open(self.status_json_path, "w") as wf:
                    wf.write(
                        json.dumps(self.status_json, indent=2, sort_keys=True))
        else:
            self.status_json = {}
            self.status_json["job_dir"] = self.output_dir
            self.status_json["id"] = os.path.basename(
                os.path.normpath(self.output_dir))
            self.status_json["run_name"] = self.run_name
            self.status_json["assembly"] = self.input_assembly
            self.status_json["db_path"] = os.path.join(
                self.output_dir, self.run_name + ".sqlite")
            self.status_json["orig_input_fname"] = [
                os.path.basename(x) for x in self.inputs
            ]
            self.status_json["orig_input_path"] = self.inputs
            self.status_json["submission_time"] = datetime.now().isoformat()
            self.status_json["viewable"] = False
            self.status_json["note"] = self.args.note
            self.status_json["status"] = "Starting"
            self.status_json["reports"] = (self.args.reports if
                                           self.args.reports != None else [])
            self.pkg_ver = au.get_current_package_version()
            self.status_json["open_cravat_version"] = self.pkg_ver
            annot_names = list(self.annotators.keys())
            annot_names.sort()
            self.status_json["annotators"] = annot_names
            with open(self.status_json_path, "w") as wf:
                wf.write(json.dumps(self.status_json, indent=2,
                                    sort_keys=True))

    def write_smartfilters(self):
        if self.run_name is None or self.args is None or self.output_dir is None:
            from .exceptions import SetupError
            raise SetupError()
        from time import time
        import os
        import json
        import sqlite3
        from .util import filter_affected_cols
        from .constants import base_smartfilters
        from .util import quiet_print
        quiet_print("Indexing", self.args)
        dbpath = os.path.join(self.output_dir, self.run_name + ".sqlite")
        conn = sqlite3.connect(dbpath)
        cursor = conn.cursor()
        q = "create table if not exists smartfilters (name text primary key, definition text)"
        cursor.execute(q)
        ins_template = (
            "insert or replace into smartfilters (name, definition) values (?, ?);"
        )
        cols_to_index = set()
        for sf in base_smartfilters:
            cols_to_index |= filter_affected_cols(sf["filter"])
        if self.annotator_ran:
            for linfo in self.annotators.values():
                if linfo.smartfilters is not None:
                    for sf in linfo.smartfilters:
                        cols_to_index |= filter_affected_cols(sf["filter"])
                    mname = linfo.name
                    json_info = json.dumps(linfo.smartfilters)
                    cursor.execute(ins_template, (mname, json_info))
        cursor.execute("pragma table_info(variant)")
        variant_cols = {row[1] for row in cursor}
        cursor.execute("pragma table_info(gene)")
        gene_cols = {row[1] for row in cursor}
        cursor.execute('select name from sqlite_master where type="index"')
        existing_indices = {row[0] for row in cursor}
        for col in cols_to_index:
            if col in variant_cols:
                index_name = f"sf_variant_{col}"
                if index_name not in existing_indices:
                    q = f"create index if not exists {index_name} on variant ({col})"
                    quiet_print(f"\tvariant {col}", self.args)
                    st = time()
                    cursor.execute(q)
                    quiet_print(f"\tfinished in {time()-st:.3f}s", self.args)
            if col in gene_cols:
                index_name = f"sf_gene_{col}"
                if index_name not in existing_indices:
                    q = f"create index if not exists {index_name} on gene ({col})"
                    quiet_print(f"\tgene {col}", self.args)
                    st = time()
                    cursor.execute(q)
                    quiet_print(f"\tfinished in {time()-st:.3f}s", self.args)
        # Package filter
        if hasattr(self.args, "filter") and self.args.filter is not None:
            q = "create table if not exists viewersetup (datatype text, name text, viewersetup text, unique (datatype, name))"
            cursor.execute(q)
            filter_set = json.dumps({"filterSet": self.args.filter})
            q = f'insert or replace into viewersetup values ("filter", "quicksave-name-internal-use", \'{filter_set}\')'
            cursor.execute(q)
        conn.commit()
        cursor.close()
        conn.close()


class StatusWriter:

    def __init__(self, status_json_path):
        from time import time
        self.status_json_path = status_json_path
        self.status_queue = []
        self.status_json = None
        self.load_status_json()
        self.t = time()
        self.lock = False

    def load_status_json(self):
        import json
        f = open(self.status_json_path)
        lines = "\n".join(f.readlines())
        self.status_json = json.loads(lines)
        f.close()

    def queue_status_update(self, k, v, force=False):
        from time import time
        if self.status_json:
            self.status_json[k] = v
            tdif = time() - self.t
            if force == True or (tdif > 3 and self.lock == False):
                self.lock = True
                self.update_status_json()
                self.t = time()
                self.lock = False

    def update_status_json(self):
        import json
        with open(self.status_json_path, "w") as wf:
            json.dump(self.status_json, wf, indent=2, sort_keys=True)

    def get_status_json(self):
        return self.status_json

    def flush(self):
        from time import time
        self.lock = True
        self.update_status_json()
        self.t = time()
        self.lock = False


def get_parser_ov_run():
    from argparse import ArgumentParser, SUPPRESS
    parser_ov_run = ArgumentParser(
        prog="ov run input_file_path_1 input_file_path_2 ...",
        description=
        "OakVar genomic variant interpreter. https://github.com/rkimoakbioinformatics/oakvar. Use input_file_path arguments before any option or define them in a conf file (option -c).",
        epilog="inputs should be the first option",
    )
    parser_ov_run.add_argument(
        "inputs",
        nargs="*",
        default=[],
        help=
        "Input file(s). One or more variant files in a supported format like VCF.  "
        +
        "See the -i/--input-format flag for supported formats. In the special case "
        +
        "where you want to add annotations to an existing OakVar analysis, " +
        "provide the output sqlite database from the previous run as input instead of a variant input file.",
    )
    parser_ov_run.add_argument(
        "-a",
        nargs="+",
        dest="annotators",
        default=[],
        help=
        "Annotator module names or directories. If --package is used also, annotator modules defined with -a will be added.",
    )
    parser_ov_run.add_argument(
        "-A",
        nargs="+",
        dest="annotators_replace",
        default=[],
        help=
        "Annotator module names or directories. If --package option also is used, annotator modules defined with -A will replace those defined with --package. -A has priority over -a.",
    )
    parser_ov_run.add_argument("-e",
                               nargs="+",
                               dest="excludes",
                               default=[],
                               help="annotators to exclude")
    parser_ov_run.add_argument("-n",
                               dest="run_name",
                               help="name of oakvar run")
    parser_ov_run.add_argument("-d",
                               dest="output_dir",
                               default=None,
                               help="directory for output files")
    parser_ov_run.add_argument(
        "--startat",
        dest="startat",
        choices=[
            "converter",
            "mapper",
            "annotator",
            "aggregator",
            "postaggregator",
            "reporter",
        ],
        default=None,
        help="starts at given stage",
    )
    parser_ov_run.add_argument(
        "--endat",
        dest="endat",
        choices=[
            "converter",
            "mapper",
            "annotator",
            "aggregator",
            "postaggregator",
            "reporter",
        ],
        default=None,
        help="ends after given stage.",
    )
    parser_ov_run.add_argument(
        "--skip",
        dest="skip",
        nargs="+",
        choices=[
            "converter",
            "mapper",
            "annotator",
            "aggregator",
            "postaggregator",
            "reporter",
        ],
        default=None,
        help="skips given stage(s).",
    )
    parser_ov_run.add_argument("-c",
                               "--confpath",
                               dest="confpath",
                               default=None,
                               help="path to a conf file")
    parser_ov_run.add_argument("--cs",
                               dest="confs",
                               default=None,
                               help="configuration string")
    parser_ov_run.add_argument("-v",
                               dest="verbose",
                               action="store_true",
                               default=None,
                               help="verbose")
    parser_ov_run.add_argument(
        "-t",
        nargs="+",
        dest="reports",
        default=[],
        help="Reporter types or reporter module directories",
    )
    parser_ov_run.add_argument(
        "-l",
        "--liftover",
        dest="genome",
        default=None,
        help=
        "reference genome of input. OakVar will lift over to hg38 if needed.",
    )
    parser_ov_run.add_argument(
        "-x",
        dest="cleandb",
        action="store_true",
        help="deletes the existing result database and creates a new one.",
    )
    parser_ov_run.add_argument(
        "--newlog",
        dest="newlog",
        action="store_true",
        default=None,
        help="deletes the existing log file and creates a new one.",
    )
    parser_ov_run.add_argument(
        "--note",
        dest="note",
        default=None,
        help="note will be written to the run status file (.status.json)",
    )
    parser_ov_run.add_argument(
        "--mp",
        dest="mp",
        default=None,
        help="number of processes to use to run annotators")
    parser_ov_run.add_argument(
        "-i",
        "--input-format",
        dest="forcedinputformat",
        default=None,
        help="Force input format",
    )
    parser_ov_run.add_argument(
        "--temp-files",
        dest="temp_files",
        action="store_true",
        default=None,
        help="Leave temporary files after run is complete.",
    )
    parser_ov_run.add_argument(
        "--writeadmindb",
        dest="writeadmindb",
        action="store_true",
        default=None,
        help="Write job information to admin db after job completion",
    )
    parser_ov_run.add_argument("--jobid",
                               dest="jobid",
                               default=None,
                               help="Job ID for server version")
    parser_ov_run.add_argument(
        "--version",
        dest="show_version",
        action="store_true",
        default=None,
        help="Shows OakVar version.",
    )
    parser_ov_run.add_argument(
        "--separatesample",
        dest="separatesample",
        action="store_true",
        default=None,
        help="Separate variant results by sample",
    )
    parser_ov_run.add_argument(
        "--unique-variants",
        dest="unique_variants",
        action="store_true",
        default=None,
        help="Set to get only unique variants in output",
    )
    parser_ov_run.add_argument(
        "--primary-transcript",
        dest="primary_transcript",
        nargs="+",
        default=["mane"],
        help=
        '"mane" for MANE transcripts as primary transcripts, or a path to a file of primary transcripts. MANE is default.',
    )
    parser_ov_run.add_argument(
        "--cleanrun",
        dest="clean_run",
        action="store_true",
        default=None,
        help=
        "Deletes all previous output files for the job and generate new ones.",
    )
    parser_ov_run.add_argument(
        "--do-not-change-status",
        dest="do_not_change_status",
        action="store_true",
        default=None,
        help="Job status in status.json will not be changed",
    )
    parser_ov_run.add_argument(
        "--module-option",
        dest="module_option",
        nargs="*",
        help=
        "Module-specific option in module_name.key=value syntax. For example, --module-option vcfreporter.type=separate",
    )
    parser_ov_run.add_argument(
        "--system-option",
        dest="system_option",
        nargs="*",
        default=[],
        help=
        "System option in key=value syntax. For example, --system-option modules_dir=/home/user/oakvar/modules",
    )
    parser_ov_run.add_argument("--quiet",
                               action="store_true",
                               default=True,
                               help="Runs quietly.")
    parser_ov_run.add_argument(
        "--concise-report",
        dest="concise_report",
        action="store_true",
        default=None,
        help=
        "Generate concise reports with default columns defined by each annotation module",
    )
    parser_ov_run.add_argument("--package",
                               dest="package",
                               default=None,
                               help="Use package")
    parser_ov_run.add_argument("--filtersql", default=None, help="Filter SQL")
    parser_ov_run.add_argument("--includesample",
                               nargs="+",
                               default=None,
                               help="Sample IDs to include")
    parser_ov_run.add_argument("--excludesample",
                               nargs="+",
                               default=None,
                               help="Sample IDs to exclude")
    parser_ov_run.add_argument("--filter", default=None, help=SUPPRESS)
    parser_ov_run.add_argument("-f",
                               dest="filterpath",
                               default=None,
                               help="Path to a filter file")
    parser_ov_run.add_argument(
        "--md",
        default=None,
        help="Specify the root directory of OakVar modules (annotators, etc)",
    )
    parser_ov_run.add_argument(
        "-m",
        dest="mapper_name",
        nargs="+",
        default=[],
        help="Mapper module name or mapper module directory",
    )
    parser_ov_run.add_argument(
        "-p",
        nargs="+",
        dest="postaggregators",
        default=[],
        help=
        "Postaggregators to run. Additionally, tagsampler, casecontrol, varmeta, and vcfinfo will automatically run depending on conditions.",
    )
    parser_ov_run.set_defaults(func=cli_ov_run)
    return parser_ov_run
