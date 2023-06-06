from typing import Any
from typing import Optional
from typing import Type
from typing import List
from typing import Tuple
from typing import Dict
import polars as pl
from .converter import BaseConverter
from ..module.local import LocalModule


class Runner(object):
    def __init__(self, **kwargs):
        from types import SimpleNamespace
        from sqlite3 import Connection
        from sqlite3 import Cursor
        from ..module.local import LocalModule
        from .converter import BaseConverter
        from .mapper import BaseMapper
        from .annotator import BaseAnnotator

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
        self.done_annotators: List[str] = []
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
        self.args = SimpleNamespace()
        self.main_conf = {}
        self.run_conf = {}
        self.conf_path = None
        self.conf = {}
        self.first_non_url_input = None
        self.input_paths: List[List[str]] = []
        self.run_name: List[str] = []
        self.output_dir: List[str] = []
        self.startlevel = self.runlevels["converter"]
        self.endlevel = self.runlevels["postaggregator"]
        self.excludes = []
        self.converter_name: Optional[str] = ""
        self.preparer_names = []
        self.mapper_name: Optional[str] = None
        self.annotator_names = []
        self.postaggregator_names = []
        self.reporter_names = []
        self.report_names = []
        self.preparers = {}
        self.mapper: Optional[LocalModule] = None
        self.annotators: Dict[str, LocalModule] = {}
        self.postaggregators = {}
        self.reporters = {}
        self.samples: List[str] = []
        self.ignore_sample = False
        self.fill_in_missing_ref = False
        self.total_num_converted_variants = None
        self.total_num_valid_variants = None
        self.converter_format: Optional[List[str]] = None
        self.converter_i: Optional[BaseConverter] = None
        self.mapper_i: List[BaseMapper] = []
        self.annotators_i: List[BaseAnnotator] = []
        self.genemapper = None
        self.append_mode = []
        self.exception = None
        self.genome_assemblies: List[List[str]] = []
        self.inkwargs = kwargs
        self.serveradmindb = None
        self.report_response = None
        self.outer = None
        self.error = None
        self.result_db_conn: Optional[Connection] = None
        self.result_db_cursor: Optional[Cursor] = None

    def check_valid_modules(self, module_names):
        from ..exceptions import ModuleNotExist
        from ..module.local import module_exists_local

        for module_name in module_names:
            if not module_exists_local(module_name):
                raise ModuleNotExist(module_name)

    def setup_manager(self):
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
        if len(self.run_name) != len(self.output_dir):
            raise

    def delete_output_files(self, run_no: int):
        from os import remove
        from pathlib import Path
        from ..util.util import escape_glob_pattern
        from ..consts import LOG_SUFFIX
        from ..consts import ERROR_LOG_SUFFIX

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
        from ..util.util import humanize_bytes
        from ..util.run import update_status

        if " " in ip:
            print(f"Space is not allowed in input file paths ({ip})")
            exit()
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
            return str(Path(fpath).resolve())
        except Exception:
            print("File downloading unsuccessful. Exiting.")
            exit()

    def get_logger(self, run_no: int):
        import logging
        from pathlib import Path
        from ..util.run import set_logger_handler

        if self.args is None:
            raise
        output_dir = Path(self.output_dir[run_no])
        run_name = self.run_name[run_no]
        if self.args.newlog is True:
            self.logmode = "w"
        else:
            self.logmode = "a"
        self.logger = logging.getLogger("oakvar")
        self.error_logger = logging.getLogger("err")
        set_logger_handler(self.logger, self.error_logger, output_dir=output_dir, run_name=run_name, mode=self.logmode, level=self.args.loglevel, logtofile=self.args.logtofile, clean=self.args.clean, newlog=self.args.newlog)

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

    def process_clean(self, run_no: int):
        if not self.args or not self.args.clean:
            return
        msg = f"deleting previous output files for {self.run_name[run_no]}..."
        if self.logger:
            self.logger.info(msg)
        self.delete_output_files(run_no)

    def log_input(self, run_no: int):

        if not self.args:
            raise
        if self.logger:
            for input_file in self.input_paths[run_no]:
                self.logger.info(f"input file: {input_file}")

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

    def open_result_database(self, run_no: int):
        from pathlib import Path
        import sqlite3
        from ..consts import result_db_suffix

        run_name = self.run_name[run_no]
        output_fn = f"{run_name}{result_db_suffix}"
        output_dir = self.output_dir[run_no]
        output_path = Path(output_dir) / output_fn
        self.result_db_conn = sqlite3.connect(output_path)
        self.result_db_cursor = self.result_db_conn.cursor()
        self.result_db_cursor.execute('pragma journal_mode="wal"')
        self.result_db_cursor.execute("pragma synchronous=0;")
        self.result_db_cursor.execute("pragma journal_mode=off;")
        self.result_db_cursor.execute("pragma cache_size=1000000;")
        self.result_db_cursor.execute("pragma locking_mode=EXCLUSIVE;")
        self.result_db_cursor.execute("pragma temp_store=MEMORY;")
        q: str = "drop table if exists variant"
        self.result_db_cursor.execute(q)
        self.result_db_conn.commit()

    def close_result_database(self):
        if not self.result_db_conn or not self.result_db_cursor:
            return
        self.result_db_cursor.close()
        self.result_db_conn.close()

    def collect_output_columns(self, converter: BaseConverter):
        from ..consts import VARIANT_LEVEL_PRIMARY_KEY
        from ..consts import GENE_LEVEL_PRIMARY_KEY

        coldefs = []
        for coldef in converter.output_columns:
            coldefs.append(coldef.copy())
        for module in self.mapper_i:
            for coldef in module.output_columns:
                if coldef["name"] == VARIANT_LEVEL_PRIMARY_KEY:
                    continue
                coldef_fullname = coldef.copy()
                coldefs.append(coldef_fullname)
        for module in self.annotators_i:
            module_level: str = module.conf.get("level", "variant")
            for coldef in module.output_columns:
                if coldef["name"] == VARIANT_LEVEL_PRIMARY_KEY:
                    continue
                if module_level == "gene" and coldef["name"] == GENE_LEVEL_PRIMARY_KEY:
                    continue
                coldef_fullname = coldef.copy()
                coldef_fullname["name"] = f"{module.module_name}__{coldef_fullname['name']}"
                coldefs.append(coldef_fullname)
        return coldefs

    def create_variant_table_in_result_db(self, coldefs: List[Dict[str, Any]]) -> List[str]:
        if self.result_db_conn is None:
            return []
        if self.result_db_cursor is None:
            return []
        table_col_defs: List[str] = []
        table_col_names: List[str] = []
        for coldef in coldefs:
            table_col_def = f"{coldef['name']} {coldef['type']}"
            table_col_defs.append(table_col_def)
            table_col_names.append(coldef["name"])
        table_col_def_str = ", ".join(table_col_defs)
        q = f"create table variant ({table_col_def_str})"
        self.result_db_cursor.execute(q)
        self.result_db_conn.commit()
        return table_col_names

    def create_info_modules_table_in_result_db(self):
        if not self.result_db_conn or not self.result_db_cursor:
            return
        table_name = "info_modules"
        q = f"drop table if exists {table_name}"
        self.result_db_cursor.execute(q)
        q = f"create table {table_name} (name text primary key, displayname text, version text, description text)"
        self.result_db_cursor.execute(q)
        q = f"insert into {table_name} values (?, ?, ?, ?)"
        self.result_db_cursor.execute(q, ("base", "Normalized Input", "", ""))
        mapper = self.mapper_i[0]
        q = f"insert into {table_name} values (?, ?, ?, ?)"
        self.result_db_cursor.execute(q, (mapper.module_name, mapper.conf.get("title", mapper.module_name), mapper.conf.get("version", ""), mapper.conf.get("description", "")))
        for module_name, module in self.annotators.items():
            q = f"insert into {table_name} values (?, ?, ?, ?)"
            self.result_db_cursor.execute(q, (module_name, module.conf.get("title", module_name), module.conf.get("version", ""), module.conf.get("description", "")))
        self.result_db_conn.commit()

    def create_info_headers_table_in_result_db(self, converter: BaseConverter):
        from json import dumps

        if not self.result_db_conn or not self.result_db_cursor:
            return
        table_name = "info_headers"
        q = f"drop table if exists {table_name}"
        self.result_db_cursor.execute(q)
        q = f"create table {table_name} (name text primary key, level text, json text)"
        self.result_db_cursor.execute(q)
        q = f"insert into {table_name} values (?, ?, ?)"
        print(f"@ converter output_columns={converter.output_columns}")
        for col in converter.output_columns:
            name = f"base__{col['name']}"
            self.result_db_cursor.execute(q, (name, "variant", dumps(col)))
        mapper = self.mapper_i[0]
        for col in mapper.output_columns:
            name = f"base__{col['name']}"
            self.result_db_cursor.execute(q, (name, "variant", dumps(col)))
        for module in self.annotators_i:
            for col in module.output_columns:
                name = f"{module.module_name}__{col['name']}"
                self.result_db_cursor.execute(q, (name, "variant", dumps(col)))
        self.result_db_conn.commit()

    def create_info_table_in_result_db(self):
        if not self.result_db_conn or not self.result_db_cursor:
            return
        q = "drop table if exists info"
        self.result_db_cursor.execute(q)
        q = "create table info (colkey text primary key, colval text)"
        self.result_db_cursor.execute(q)
        self.result_db_conn.commit()

    def create_auxiliary_tables_in_result_db(self, converter: BaseConverter):
        if not self.result_db_conn or not self.result_db_cursor:
            return
        self.create_info_table_in_result_db()
        self.create_info_modules_table_in_result_db()
        self.create_info_headers_table_in_result_db(converter)

    def write_df_to_db(self, df: pl.DataFrame, table_col_names: List[str]):
        if self.result_db_conn is None:
            return
        if self.result_db_cursor is None:
            return
        table_col_names_str = ", ".join(table_col_names)
        values_str = ", ".join(["?"] * len(table_col_names))
        q = f"insert into variant ({table_col_names_str}) values ({values_str})"
        for row in df.iter_rows():
            self.result_db_cursor.execute(q, row)
        self.result_db_conn.commit()

    def process_file(self, run_no: int):
        from ..exceptions import NoConverterFound

        self.open_result_database(run_no)
        input_paths = self.input_paths[run_no]
        converter = self.choose_converter(input_paths)
        if converter is None:
            raise NoConverterFound(input_paths)
        samples = self.samples or converter.collect_samples(input_paths)
        coldefs = self.collect_output_columns(converter)
        print(f"@ coldefs={coldefs}")
        table_col_names = self.create_variant_table_in_result_db(coldefs)
        self.create_auxiliary_tables_in_result_db(converter)
        self.do_step_preparer(run_no)
        for df in converter.iter_df_chunk(input_paths, samples=samples):
            if df is not None:
                df = self.do_step_mapper(df)
                df = self.do_step_annotator(df)
                self.write_df_to_db(df, table_col_names)
        self.write_info_table(run_no, converter)
        self.close_result_database()
        exit()
        self.do_step_postaggregator(run_no)
        self.do_step_reporter(run_no)

    def main(self) -> Optional[Dict[str, Any]]:
        from time import time, asctime, localtime
        from ..util.run import update_status
        from ..consts import JOB_STATUS_FINISHED
        from ..consts import JOB_STATUS_ERROR

        self.process_arguments(self.inkwargs)
        if not self.args:
            raise
        self.sanity_check_run_name_output_dir()
        self.load_wgs_reader()
        self.load_mapper()
        self.load_annotators()
        self.setup_manager()
        for run_no in range(len(self.run_name)):
            try:
                self.start_log(run_no)
                self.process_clean(run_no)
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
                    self.run_vcf2vcf(run_no)
                else:
                    self.process_file(run_no)
                end_time = time()
                runtime = end_time - self.start_time
                display_time = asctime(localtime(end_time))
                if self.logger:
                    self.logger.info(f"finished: {display_time}")
                update_status(
                    f"finished normally. Runtime: {runtime:0.3f}s",
                    logger=self.logger,
                    serveradmindb=self.serveradmindb,
                )
                if self.args and self.args.writeadmindb:
                    self.write_admin_db_final_info(runtime, run_no)
            except Exception as e:
                self.exception = e
            finally:
                import traceback

                if self.exception:
                    traceback.print_exc()
                if not self.exception:
                    update_status(JOB_STATUS_FINISHED, serveradmindb=self.serveradmindb)
                else:
                    update_status(
                        JOB_STATUS_ERROR,
                        serveradmindb=self.serveradmindb,
                    )
                    if self.logger:
                        self.logger.exception(self.exception)
                self.close_error_logger()
                self.clean_up_at_end(run_no)
                self.close_logger()
                self.shutdown_logging()
                if self.exception:
                    raise self.exception
        return self.report_response

    def process_arguments(self, args):
        from ..exceptions import SetupError

        self.set_package_conf(args)
        self.make_self_args_considering_package_conf(args)
        if self.args is None:
            raise SetupError()
        self.set_self_inputs()  # self.input_paths is list.
        self.set_and_create_output_dir()  # self.output_dir is list.
        self.set_run_name()  # self.run_name is list.
        self.set_job_name()  # self.job_name is list.
        self.set_append_mode()  # self.append_mode is list.
        self.set_genome_assemblies()  # self.genome_assemblies is list.
        self.set_preparers()
        self.set_mapper()
        self.set_annotators()
        self.set_postaggregators()
        self.add_required_modules_for_postaggregators()
        self.sort_annotators()
        self.sort_postaggregators()
        self.set_reporters()
        self.set_start_end_levels()

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
        self.samples = args.get("samples", [])
        self.fill_in_missing_ref = args.get("fill_in_missing_ref", False)
        self.args = SimpleNamespace(**args)
        self.outer = self.args.outer
        if self.args.vcf2vcf and self.args.combine_input:
            if self.outer:
                self.outer.write("--vcf2vcf is used. --combine-input is disabled.")
            self.args.combine_input = False
        self.process_module_options()

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

        if args is None:
            raise SetupError()
        self.run_conf = args.get("conf", {}).get("run", {})

    def get_secondary_annotator_names(self, module_names: List[str]):
        secondary_modules: List[str] = []
        for module_name in module_names:
            self.prepend_secondary_annotator_names(module_name, secondary_modules)
        return secondary_modules

    def process_module_options(self):
        from ..exceptions import SetupError
        from ..util.run import get_module_options

        if self.args is None or self.conf is None:
            raise SetupError()
        if isinstance(self.args.module_options, dict):
            module_options = self.args.module_options
        else:
            module_options = get_module_options(self.args.module_options, outer=self.outer)
        self.run_conf.update(module_options)

    def process_url_and_pipe_inputs(self):
        from pathlib import Path
        from ..util.util import is_url

        if not self.args:
            raise
        self.first_non_url_input = None
        if self.args.inputs is not None:
            if self.args.combine_input:
                self.input_paths = [[
                    str(Path(x).resolve()) if not is_url(x) else x
                    for x in self.args.inputs
                ]]
            else:
                self.input_paths = [
                    [str(Path(x).resolve()) if not is_url(x) else x]
                    for x in self.args.inputs
                ]
            for input_no in range(len(self.input_paths)):
                inp_l = self.input_paths[input_no]
                for fileno in range(len(inp_l)):
                    inp = inp_l[fileno]
                    if is_url(inp):
                        fpath = self.download_url_input(inp)
                        self.input_paths[input_no][fileno] = fpath
                    elif not self.first_non_url_input:
                        self.first_non_url_input = inp
        else:
            self.input_paths = []

    def remove_absent_inputs(self):
        from pathlib import Path

        old_input_paths = self.input_paths.copy()
        self.input_paths = []
        for inp_l in old_input_paths:
            new_l: List[str] = []
            for inp in inp_l:
                if "*" not in inp and Path(inp).exists():
                    new_l.append(inp)
            self.input_paths.append(new_l)

    def set_append_mode(self):
        # TODO: change the below for df workflow.
        self.append_mode = [False] * len(self.input_paths)

    def set_genome_assemblies(self):
        if self.run_name:
            self.genome_assemblies = [[] for _ in range(len(self.run_name))]
        else:
            self.genome_assemblies = []

    def set_and_create_output_dir(self):
        from pathlib import Path
        from os import getcwd
        from os import mkdir

        if not self.args:
            raise
        cwd = getcwd()
        if self.args.combine_input:
            if self.args.output_dir:
                self.output_dir = [self.args.output_dir]
            else:
                self.output_dir = [cwd]
        else:
            self.output_dir = [
                str(Path(inp[0]).resolve().parent) for inp in self.input_paths
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
            self.run_name = []
            for inp_l in self.input_paths:
                p = Path(inp_l[0])
                run_name = p.name
                if len(inp_l) > 1:
                    run_name = run_name + "_etc"
                    run_name = self.get_unique_run_name(
                        self.output_dir[0], run_name
                    )
                self.run_name.append(run_name)
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
                    if self.output_dir and len(self.output_dir) != len(
                        set(self.output_dir)
                    ):
                        raise ArgumentError(
                            msg="-n should have a unique value for each "
                            + "input when -d has duplicate directories."
                        )
                    self.run_name = self.args.run_name * len(self.input_paths)
                else:
                    if len(self.input_paths) != len(self.args.run_name):
                        raise ArgumentError(
                            msg="Just one or the same number of -n option "
                            + "values as input files should be given."
                        )
                    self.run_name = self.args.run_name

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
                if len(self.output_dir) != len(set(self.output_dir)):
                    raise ArgumentError(
                        msg="-j should have a unique value for each input "
                        + "when -d has duplicate directories. Or, give "
                        + "--combine-input to combine input files into one job."
                    )
                self.job_name = self.args.job_name * len(self.input_paths)
            else:
                if len(self.input_paths) != len(self.args.job_name):
                    raise ArgumentError(
                        msg="Just one or the same number of -j option values "
                        + "as input files should be given."
                    )
                self.job_name = self.args.job_name
            return

    def input_exists(self):
        has_input: bool = False
        for inp_l in self.input_paths:
            if inp_l:
                has_input = True
                break
        return has_input

    def set_self_inputs(self):
        from ..exceptions import NoInput

        if self.args is None:
            raise
        self.use_inputs_from_run_conf()
        self.process_url_and_pipe_inputs()
        self.remove_absent_inputs()
        if not self.input_exists():
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
        from ..exceptions import SetupError
        from ..module.local import get_local_module_info_by_name

        if self.args is None or self.conf is None:
            raise SetupError()
        if self.args.mapper_name:
            self.mapper_name = self.args.mapper_name[0]
        self.mapper_name = self.get_package_conf_run_value("mapper")
        if not self.mapper_name:
            self.mapper_name = self.main_conf.get("genemapper")
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
        secondary_module_names = self.get_secondary_annotator_names(self.annotator_names)
        self.annotator_names[:0] = secondary_module_names
        self.annotators = get_local_module_infos_by_names(self.annotator_names)

    def get_package_argument_run_value(self, field: str):
        if not self.package_conf:
            return None
        if not self.package_conf.get("run"):
            return None
        return self.package_conf["run"].get(field)

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
        self.postaggregator_names = sorted(
            list(
                set(self.postaggregator_names).union(set(default_postaggregator_names))
            )
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
            if not module:
                return None
            required_module_names = module.conf.get("requires", [])
            if required_module_names:
                if isinstance(required_module_names, list):
                    self.sort_module_names_by_requirement(
                        required_module_names, final_module_names, module_type
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
                self.report_names = self.package_conf["run"]["reports"]
            else:
                self.report_names = []
        if "reporter" in self.args.skip:
            self.reporters = {}
        else:
            self.reporter_names = [v + "reporter" for v in self.report_names]
            self.check_valid_modules(self.reporter_names)
            self.reporters = get_local_module_infos_by_names(self.reporter_names)

    def prepend_secondary_annotator_names(self, module_name: str, ret: List[str]):
        module_names = self.get_secondary_module_names(module_name)
        for module_name in module_names:
            if module_name not in ret:
                ret.insert(0, module_name)
            self.prepend_secondary_annotator_names(module_name, ret)

    def get_module_output_path(self, module, run_no: int):
        import os
        from ..consts import VARIANT_LEVEL_OUTPUT_SUFFIX
        from ..consts import GENE_LEVEL_OUTPUT_SUFFIX

        run_name, output_dir = self.get_run_name_output_dir_by_run_no(run_no)
        if module.level == "variant":
            postfix = VARIANT_LEVEL_OUTPUT_SUFFIX
        elif module.level == "gene":
            postfix = GENE_LEVEL_OUTPUT_SUFFIX
        else:
            return None
        path = os.path.join(output_dir, run_name + "." + module.name + postfix)
        return path

    def annotator_columns_missing(self, module: LocalModule, df_cols: List[str]) -> bool:
        cols_to_check = module.conf.get("output_columns", {}).keys()
        tf_l = [v in df_cols for v in cols_to_check]
        return False in tf_l

    def get_secondary_module_names(self, primary_module_name: str) -> List[str]:
        from ..module.local import get_local_module_info

        module:  Optional[LocalModule] = get_local_module_info(primary_module_name)
        if not module:
            return []
        secondary_module_names: List[str] = [
            module_name
            for module_name in module.secondary_module_names
        ]
        return secondary_module_names

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

    def get_run_name_output_dir_by_run_no(self, run_no: int) -> Tuple[str, str]:
        run_name = self.run_name[run_no]
        output_dir = self.output_dir[run_no]
        return run_name, output_dir

    def get_dbpath(self, run_no: int):
        from pathlib import Path

        run_name, output_dir = self.get_run_name_output_dir_by_run_no(run_no)
        dbpath = str(Path(output_dir) / (run_name + ".sqlite"))
        return dbpath

    def write_info_row(self, key: str, value: Any):
        import json

        if not self.result_db_cursor:
            return
        q = "insert into info values (?, ?)"
        if isinstance(value, list) or isinstance(value, dict):
            value = json.dumps(value)
        self.result_db_cursor.execute(q, (key, value))

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

    def refresh_info_table_modified_time(self):
        from datetime import datetime

        if self.result_db_conn is None or self.result_db_cursor is None:
            return
        modified = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        q = "insert or replace into info values ('modified_at', ?)"
        self.result_db_cursor.execute(q, (modified,))
        self.result_db_conn.commit()

    def write_info_table_create_data_if_needed(self, run_no: int, converter: BaseConverter):
        from datetime import datetime
        import json
        from ..exceptions import DatabaseError

        if self.result_db_conn is None or self.result_db_cursor is None:
            return
        if not self.job_name or not self.args:
            raise
        inputs = self.input_paths[run_no]
        job_name = self.job_name[run_no]
        created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.write_info_row("created_at", created)
        self.write_info_row("inputs", inputs)
        self.write_info_row("genome_assemblies", converter.genome_assemblies)
        q = "select count(*) from variant"
        self.result_db_cursor.execute(q)
        r = self.result_db_cursor.fetchone()
        if r is None:
            raise DatabaseError(msg="table variant does not exist.")
        no_input = str(r[0])
        self.write_info_row("num_variants", no_input)
        self.write_info_row("oakvar", self.pkg_ver)
        mapper_conf = self.mapper_i[0].conf
        mapper_title = mapper_conf.get("title")
        mapper_version = mapper_conf.get("version", mapper_conf.get("code_version"))
        gene_mapper_str = f"{mapper_title}=={mapper_version}"
        self.write_info_row("mapper", gene_mapper_str)
        input_paths = self.input_paths[run_no]
        self.write_info_row("input_paths", input_paths)
        self.write_info_row(
            "primary_transcript", ",".join(self.args.primary_transcript)
        )
        self.write_info_row("job_name", job_name)
        self.write_info_row("converter_format", converter.format_name)
        self.result_db_conn.commit()

    def write_info_table(self, run_no: int, converter: BaseConverter):
        if not self.result_db_conn:
            return
        self.refresh_info_table_modified_time()
        self.write_info_table_create_data_if_needed(run_no, converter)

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

    def write_admin_db_final_info(self, runtime: float, run_no: int):
        import sqlite3
        from json import dumps
        from ...gui.serveradmindb import get_admindb_path

        if self.args is None or not self.output_dir:
            raise
        if runtime is None or self.total_num_converted_variants is None:
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
        db = sqlite3.connect(str(admindb_path))
        cursor = db.cursor()
        q = "update jobs set runtime=?, numinput=?, info_json=? where dir=? and name=?"
        cursor.execute(
            q,
            (
                runtime,
                self.total_num_converted_variants,
                info_json_s,
                self.output_dir[run_no],
                self.args.job_name[run_no],
            ),
        )
        db.commit()
        cursor.close()
        db.close()

    def write_initial_info_json(self, run_no: int):
        from datetime import datetime
        from pathlib import Path
        from ..util.admin_util import oakvar_version

        if not self.args:
            raise
        run_name = self.run_name[run_no]
        output_dir = self.output_dir[run_no]
        self.info_json = {}
        self.info_json["job_dir"] = self.output_dir
        self.info_json["job_name"] = self.args.job_name
        self.info_json["run_name"] = run_name
        self.info_json["db_path"] = str(Path(output_dir) / (run_name + ".sqlite"))
        self.info_json["orig_input_fname"] = []
        for inp_l in self.input_paths:
            self.info_json["orig_input_fname"].extend([Path(x).name for x in inp_l])
        self.info_json["orig_input_path"] = self.input_paths
        self.info_json["submission_time"] = datetime.now().isoformat()
        self.info_json["viewable"] = False
        self.info_json["note"] = self.args.note
        self.info_json["report_types"] = (
            self.args.report_types if self.args.report_types is not None else []
        )
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
            if v not in ["vcfinfo"]
        ]
        postagg_names.sort()
        self.info_json["postaggregators"] = postagg_names

    def run_preparers(self, run_no: int):
        from ..util.util import load_class
        from ..consts import MODULE_OPTIONS_KEY
        from ..exceptions import ModuleLoadingError
        from .preparer import BasePreparer

        if self.conf is None:
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
            if not issubclass(module_cls, BasePreparer):
                raise ModuleLoadingError(module_name=module.name)
            module_ins = module_cls(**kwargs)
            self.log_time_of_func(module_ins.run, work=module_name)

    def run_postaggregators(self, run_no: int):
        from time import time
        from ..util.run import announce_module
        from ..exceptions import SetupError
        from ..exceptions import ModuleLoadingError
        from ..util.util import load_class
        from ..util.run import update_status
        from ..system.consts import default_postaggregator_names
        from ..consts import MODULE_OPTIONS_KEY
        from ..base.postaggregator import BasePostAggregator

        if self.conf is None:
            raise SetupError()
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
            post_agg_cls = load_class(module.script_path)
            if not issubclass(post_agg_cls, BasePostAggregator):
                raise ModuleLoadingError(module_name=module.name)
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

    def run_vcf2vcf(self, run_no: int):
        from time import time
        from os.path import abspath
        from types import SimpleNamespace
        import traceback
        from ..util.util import load_class
        from ..util.run import update_status
        from ..base import vcf2vcf
        from ..exceptions import ModuleLoadingError
        from ..base.vcf2vcf import VCF2VCF

        if (
            self.conf is None
            or not self.args
            or not self.output_dir
            or not self.run_name
        ):
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
        if not issubclass(Module, VCF2VCF):
            raise ModuleLoadingError(msg="VCF2VCF class could not be loaded.")
        m = Module(**arg_dict)
        stime = time()
        try:
            ran_ok = m.run()
        except Exception:
            ran_ok = False
            traceback.print_exc()
        report_type = "vcf2vcf"
        response[report_type] = ran_ok
        rtime = time() - stime
        update_status(
            f"vcf2vcf finished in {rtime:.3f}s",
            logger=self.logger,
            serveradmindb=self.serveradmindb,
        )
        self.report_response = response

    def run_reporter(self, run_no: int):
        from pathlib import Path
        from ..module.local import get_local_module_info
        from ..util.module import get_reporter_class
        from ..util.run import update_status
        from ..exceptions import ModuleNotExist
        from ..exceptions import ModuleLoadingError
        from ..util.run import announce_module
        from ..consts import MODULE_OPTIONS_KEY
        from .reporter import BaseReporter

        if (
            not self.run_name
            or self.conf is None
            or not self.args
            or not self.output_dir
            or not self.input_paths
        ):
            raise
        run_name = self.run_name[run_no]
        output_dir = Path(self.output_dir[run_no])
        if len(self.reporters) > 0:
            module_names = [v for v in self.reporters.keys()]
            report_types = [v.replace("reporter", "") for v in self.reporters.keys()]
        else:
            module_names = []
            report_types = []
        response = {}
        for report_type, module_name in zip(report_types, module_names):
            reporter = None
            module = get_local_module_info(module_name)
            announce_module(module, serveradmindb=self.serveradmindb)
            if module is None:
                raise ModuleNotExist(module_name)
            arg_dict = {}  # dict(vars(self.args))
            arg_dict["dbpath"] = output_dir / (run_name + ".sqlite")
            arg_dict["savepath"] = output_dir / run_name
            arg_dict["output_dir"] = output_dir
            arg_dict["run_name"] = run_name
            arg_dict[MODULE_OPTIONS_KEY] = self.run_conf.get(module_name, {})
            Reporter: Type[BaseReporter] = get_reporter_class(module_name)
            if not issubclass(Reporter, BaseReporter):
                raise ModuleLoadingError(module_name=module.name)
            reporter = Reporter(**arg_dict)
            response_t = self.log_time_of_func(reporter.run, work=module_name)
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
            response[report_type] = response_t
        return response

    def should_run_step(self, step: str):
        return (
            self.endlevel >= self.runlevels[step]
            and self.startlevel <= self.runlevels[step]
            and (self.args and step not in self.args.skip)
        )

    def choose_converter(self, input_paths: List[str]) -> Optional[BaseConverter]:
        from ..module.local import get_local_module_infos_of_type
        from ..module.local import get_local_module_info
        from ..module.local import LocalModule
        from ..util.module import get_converter_class
        import traceback


        chosen_converter: Optional[BaseConverter] = None
        module_infos: List[LocalModule] = []
        if self.converter_name:
            module_info = get_local_module_info(self.converter_name)
            if module_info is None:
                raise Exception(f" {self.converter_name} does not exist. Please check --converter-name option was given correctly, or consider installing {self.converter_name} module with \"ov module install {self.converter_name}\" command, if the module is in the OakVar store.")
            module_infos.append(module_info)
        elif self.args.input_format:
            module_name = self.args.input_format + "-converter"
            module_info = get_local_module_info(module_name)
            if module_info is None:
                raise Exception(module_name + f" does not exist. Please check --input-format option was given correctly, or consider installing {module_name} module with \"ov module install {module_name}\" command, if the module is in the OakVar store.")
            module_infos.append(module_info)
        else:
            module_infos = list(get_local_module_infos_of_type("converter").values())
        for module_info in module_infos:
            try:
                cls = get_converter_class(module_info.name)
                converter = cls(wgs_reader=self.wgs_reader, ignore_sample=self.ignore_sample, module_options=self.run_conf.get(module_info.name, {}))
            except Exception as e:
                if self.logger:
                    self.logger.error(f"{traceback.format_exc()}\nSkipping {module_info.name} as it could not be loaded. ({e})")
                continue
            try:
                check_success = converter.check_format(input_paths[0])
            except Exception:
                if self.error_logger:
                    self.error_logger.error(traceback.format_exc())
                check_success = False
            if check_success:
                chosen_converter = converter
                break
        if chosen_converter:
            if self.logger:
                self.logger.info(f"Using {chosen_converter.name} for {' '.join(input_paths)}")
            return chosen_converter

    def load_wgs_reader(self):
        from ..util.seq import get_wgs_reader

        self.wgs_reader = get_wgs_reader()

    def load_mapper(self):
        from ..util.module import get_mapper

        if not self.mapper:
            return
        self.mapper_i = [get_mapper(self.mapper.name, wgs_reader=self.wgs_reader)]

    def load_annotators(self, df: Optional[pl.DataFrame]=None):
        from ..util.module import get_annotator

        self.done_annotators = []
        if df is not None:
            df_cols = df.columns
            for mname, module in self.annotators.items():
                if not self.annotator_columns_missing(module, df_cols):
                    self.done_annotators.append(mname)
        self.annotators_to_run = {
            aname: self.annotators[aname]
            for aname in set(self.annotators) - set(self.done_annotators)
        }
        self.annotators_i = []
        for module_name, module in self.annotators_to_run.items():
            module = get_annotator(module_name)
            self.annotators_i.append(module)

    def do_step_preparer(self, run_no: int):
        step = "preparer"
        if not self.should_run_step(step):
            return
        self.log_time_of_func(self.run_preparers, run_no, work=f"{step} step")

    def do_step_mapper(self, df: pl.DataFrame) -> pl.DataFrame:
        for module in self.mapper_i:
            df = module.run_df(df)
        return df

    def do_step_annotator(self, df: pl.DataFrame) -> pl.DataFrame:
        for module in self.annotators_i:
            df = module.run_df(df)
        return df

    def do_step_postaggregator(self, run_no: int):
        step = "postaggregator"
        if self.should_run_step(step):
            self.log_time_of_func(
                self.run_postaggregators, run_no, work=f"{step} step"
            )

    def do_step_reporter(self, run_no: int):
        step = "reporter"
        if self.should_run_step(step) and self.reporters:
            self.report_response = self.log_time_of_func(
                self.run_reporter, run_no, work=f"{step} step"
            )

    def log_time_of_func(self, func, *args, work="", **kwargs):
        from time import time
        from ..util.run import update_status

        stime = time()
        update_status(
            f"starting {work}...",
            logger=self.logger,
            serveradmindb=self.serveradmindb,
        )
        ret = func(*args, **kwargs)
        rtime = time() - stime
        update_status(
            f"{work} finished in {rtime:.3f}s",
            logger=self.logger,
            serveradmindb=self.serveradmindb,
        )
        return ret
