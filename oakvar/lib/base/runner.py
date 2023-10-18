from typing import Any
from typing import Optional
from typing import Union
from typing import List
from typing import Tuple
from typing import Dict
import polars as pl
from pathlib import Path
from .converter import BaseConverter
from .mapper import BaseMapper
from .annotator import BaseAnnotator


class Runner(object):
    def __init__(self, **kwargs):
        from types import SimpleNamespace
        import sqlite3
        import duckdb
        from ..module.local import LocalModule
        from .converter import BaseConverter
        from .mapper import BaseMapper
        from .annotator import BaseAnnotator
        from .postaggregator import BasePostAggregator
        from ..consts import DEFAULT_CONVERTER_READ_SIZE

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
        self.log_handler = None
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
        self.ignore_sample = False
        self.fill_in_missing_ref = False
        self.total_num_converted_variants = None
        self.total_num_valid_variants = None
        self.total_num_unique_variants: int = 0
        self.converter_format: Optional[List[str]] = None
        self.converter_i: Optional[BaseConverter] = None
        self.mapper_i: List[BaseMapper] = []
        self.annotators_i: List[BaseAnnotator] = []
        self.postaggregators_i: List[BasePostAggregator] = []
        self.genemapper = None
        self.append_mode = []
        self.exception = None
        self.genome_assemblies: Dict[str, Dict[str, str]] = {}
        self.inkwargs = kwargs
        self.serveradmindb = None
        self.report_response = None
        self.outer = None
        self.error = None
        self.result_db_conn: Optional[
            Union[sqlite3.Connection, duckdb.DuckDBPyConnection]
        ] = None
        self.df_mode: bool = False
        self.pool = []
        self.table_names_by_level: Dict[str, List[str]] = {}
        self.batch_size: int = DEFAULT_CONVERTER_READ_SIZE

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
        set_logger_handler(
            self.logger,
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

    def get_result_database_path(self, run_no: int) -> Path:
        from ..consts import RESULT_DB_SUFFIX_SQLITE
        from ..consts import RESULT_DB_SUFFIX_DUCKDB

        if self.args.use_duckdb:
            suffix = RESULT_DB_SUFFIX_DUCKDB
        else:
            suffix = RESULT_DB_SUFFIX_SQLITE
        run_name = self.run_name[run_no]
        db_fn = f"{run_name}{suffix}"
        output_dir = self.output_dir[run_no]
        dbpath = Path(output_dir) / db_fn
        return dbpath

    def open_result_database(self, dbpath: Path, clean: bool = False):
        from ..util.run import open_result_database

        self.result_db_conn = open_result_database(
            dbpath, self.args.use_duckdb, clean=clean
        )

    def close_result_database(self):
        if not self.result_db_conn:
            return
        self.result_db_conn.close()

    def add_coldefs(
        self,
        module_level: Optional[str],
        module_name: str,
        coldefs: Dict[str, List[Dict[str, Any]]],
        output: Dict[str, Dict[str, Any]],
        result_table_names: List[str],
        include_key_col: bool = False,
        ignore_tables: List[str] = [],
    ):
        from ..consts import VARIANT_LEVEL
        from ..consts import GENE_LEVEL
        from ..consts import VARIANT_LEVEL_PRIMARY_KEY_COLDEF
        from ..consts import GENE_LEVEL_PRIMARY_KEY_COLDEF
        from ..consts import OUTPUT_COLS_KEY

        print(f"@ ignore_tables={ignore_tables}")
        for table_name, table_output in output.items():
            print(f"@ table_name={table_name}")
            if table_name in ignore_tables:
                continue
            if table_name not in coldefs:
                coldefs[table_name] = []
                result_table_names.append(table_name.replace("-", "_"))
            table_coldefs: List[Dict[str, Any]] = []
            table_level: str = (
                table_output.get("level", module_level) or module_level or table_name
            )
            table_output_columns: List[Dict[str, Any]] = table_output.get(
                OUTPUT_COLS_KEY, []
            )
            print(f"@ table_output_columns={table_output_columns}")
            for coldef in table_output_columns:
                if "level" not in coldef:
                    coldef["level"] = table_level
                if "module_name" not in coldef:
                    coldef["module_name"] = module_name
                coldef_copy = coldef.copy()
                table_coldefs.append(coldef_copy)
            if table_coldefs and include_key_col:
                if table_level == VARIANT_LEVEL:
                    table_coldefs.insert(0, VARIANT_LEVEL_PRIMARY_KEY_COLDEF)
                elif table_level == GENE_LEVEL:
                    table_coldefs.insert(0, GENE_LEVEL_PRIMARY_KEY_COLDEF)
                else:
                    raise
            if table_coldefs:
                print(f"@ table_coldefs={table_coldefs}")
                coldefs[table_name].extend(table_coldefs)
                if table_level not in self.table_names_by_level:
                    self.table_names_by_level[table_level] = []
                if table_name not in self.table_names_by_level[table_level]:
                    self.table_names_by_level[table_level].append(table_name)

    def collect_output_coldefs(
        self, converter: BaseConverter
    ) -> Tuple[Dict[str, List[Dict[str, Any]]], List[str]]:
        from ..consts import VARIANT_LEVEL
        from ..consts import ERR_LEVEL

        coldefs: Dict[str, List[Dict[str, Any]]] = {}
        result_table_names: List[str] = []
        self.table_names_by_level = {}
        self.add_coldefs(
            None,
            "base",
            coldefs,
            converter.output,
            result_table_names,
            include_key_col=False,
        )
        for module_set in [self.mapper_i, self.annotators_i, self.postaggregators_i]:
            for module in module_set:
                module_level: str = module.conf.get("level", "")
                print(f"@@@ {module.module_name}: {module.output}")
                self.add_coldefs(
                    module_level,
                    module.module_name,
                    coldefs,
                    module.output,
                    result_table_names,
                    ignore_tables=[ERR_LEVEL],
                )
        return coldefs, result_table_names

    def create_tables_in_result_db(
        self, coldefs: Dict[str, List[Dict[str, Any]]], result_table_names: List[str]
    ):
        from ..consts import GENE_LEVEL
        from ..consts import GENE_LEVEL_PRIMARY_KEY

        table_col_names: Dict[str, List[str]] = {
            level: [] for level in result_table_names
        }
        if self.result_db_conn is None:
            return
        for table_name in result_table_names:
            q = f"drop table if exists {table_name}"
            print(f"@ q={q}")
            self.result_db_conn.execute(q)
            table_col_defs = []
            for coldef in coldefs[table_name]:
                table_col_def = f"\"{coldef['name']}\" {coldef['type']}"
                if (
                    coldef["name"] == GENE_LEVEL_PRIMARY_KEY
                    and table_name == GENE_LEVEL
                ):
                    table_col_def += " PRIMARY KEY"
                table_col_defs.append(f"{table_col_def}")
                table_col_names[table_name].append(coldef["name"])
            if table_col_defs:
                table_col_def_str = ", ".join(table_col_defs)
                q = f"create table {table_name} ({table_col_def_str})"
                print(f"@ q={q}")
                self.result_db_conn.execute(q)
            # if table_name == GENE_LEVEL:
            #    q = f"create unique index {GENE_LEVEL}_uidx on {GENE_LEVEL} ({GENE_LEVEL_PRIMARY_KEY})"
            #    self.result_db_conn.execute(q)
        self.result_db_conn.commit()

    def create_info_modules_table_in_result_db(self):
        if not self.result_db_conn:
            return
        info_module_table_name = "info_modules"
        q = f"drop table if exists {info_module_table_name}"
        self.result_db_conn.execute(q)
        q = f"create table {info_module_table_name} (name text primary key, displayname text, type text, level text, version text, description text)"
        self.result_db_conn.execute(q)
        for module_set in [self.mapper_i, self.annotators_i, self.postaggregators_i, self.reporters_i]:
            for module in module_set:
                conf = module.conf
                q = f"insert into {info_module_table_name} values (?, ?, ?, ?, ?, ?)"
                self.result_db_conn.execute(
                    q,
                    (
                        module.module_name,
                        conf.get("title", module.module_name),
                        conf.get("type", ""),
                        conf.get("level", ""),
                        conf.get("version", ""),
                        conf.get("description", ""),
                    ),
                )
        self.result_db_conn.commit()

    def create_info_module_groups_table_in_result_db(self):
        if not self.result_db_conn:
            return
        info_module_table_name = "info_module_groups"
        q = f"drop table if exists {info_module_table_name}"
        self.result_db_conn.execute(q)
        q = f"create table {info_module_table_name} (name text primary key, displayname text, parent text, description text)"
        self.result_db_conn.execute(q)
        q = f"insert into {info_module_table_name} values (?, ?, ?, ?)"
        self.result_db_conn.execute(
            q, ("base", "Base annotation", "", "Mapping and variant information")
        )
        for module_set in [self.mapper_i, self.annotators_i, self.postaggregators_i]:
            for module in module_set:
                conf = module.conf or {}
                output: Dict[str, Dict[str, Any]] = conf.get("output", {})
                for table_name, table_info in output.items():
                    if table_name in ["variant", "gene"]:
                        continue
                    q = f"insert into {info_module_table_name} values (?, ?, ?, ?)"
                    self.result_db_conn.execute(
                        q,
                        (
                            table_name,
                            table_info.get("title", ""),
                            table_info.get("parent", ""),
                            conf.get("desc", ""),
                        ),
                    )
        self.result_db_conn.commit()

    def create_info_tables_table_in_result_db(self, converter: BaseConverter):
        from ..consts import VARIANT_LEVEL
        from ..consts import GENE_LEVEL
        from ..consts import ERR_LEVEL

        if not self.result_db_conn:
            return
        write_table_name = "info_tables"
        written_tables: List[str] = []
        q = f"drop table if exists {write_table_name}"
        self.result_db_conn.execute(q)
        q = f"create table {write_table_name} (name text primary key, displayname text, parent text, description text)"
        self.result_db_conn.execute(q)
        q = f"insert into {write_table_name} values (?, ?, ?, ?)"
        self.result_db_conn.execute(
            q, (VARIANT_LEVEL, "Variant table", "", "Variant level information")
        )
        self.result_db_conn.execute(
            q, ("gene", "Gene table", "", "Gene level information")
        )
        self.result_db_conn.execute(
            q, ("err", "Error table", "", "Error information")
        )
        written_tables.extend([VARIANT_LEVEL, GENE_LEVEL, ERR_LEVEL])
        for sample in converter.samples:
            table_name = f"sample__{sample}"
            self.result_db_conn.execute(
                q, (f"{table_name}", f"Sample {sample}", VARIANT_LEVEL, f"Variant information for sample {sample}")
            )
            written_tables.append(table_name)
        for module_set in [self.mapper_i, self.annotators_i, self.postaggregators_i]:
            for module in module_set:
                conf = module.conf
                output: Dict[str, Dict[str, Any]] = conf.get("output", {})
                for table_name, table_info in output.items():
                    if table_name in written_tables:
                        continue
                    self.result_db_conn.execute(
                        q,
                        (
                            table_name,
                            table_info.get("title", conf.get("title", "")),
                            table_info.get("level", conf.get("level", "")),
                            table_info.get("description", conf.get("description", "")),
                        ),
                    )
        self.result_db_conn.commit()

    def create_info_headers_table_in_result_db(self, converter: BaseConverter):
        from json import dumps
        from ..consts import OUTPUT_COLS_KEY

        if not self.result_db_conn:
            return
        table_name = "info_headers"
        q = f"drop table if exists {table_name}"
        self.result_db_conn.execute(q)
        q = f"create table {table_name} (name text, tbl text, json text)"
        self.result_db_conn.execute(q)
        q = f"insert into {table_name} values (?, ?, ?)"
        for module_set in [[converter], self.mapper_i, self.annotators_i, self.postaggregators_i]:
            for module in module_set:
                conf = module.conf or {}
                output = conf.get("output", {})
                for table_name, table_output in output.items():
                    coldefs = table_output.get(OUTPUT_COLS_KEY, [])
                    for col in coldefs:
                        name = col['name']
                        self.result_db_conn.execute(q, (name, table_name, dumps(col)))
        self.result_db_conn.commit()

    def get_offset_levels(self, converter: BaseConverter) -> List[str]:
        from ..consts import VARIANT_LEVEL

        offset_levels: List[str] = []
        for table_name, table_output in converter.output.items():
            if (
                table_output.get("level", VARIANT_LEVEL) == VARIANT_LEVEL
                and table_name not in offset_levels
            ):
                offset_levels.append(table_name)
        mapper = self.mapper_i[0]
        for table_name, table_output in mapper.output.items():
            if (
                table_output.get("level", VARIANT_LEVEL) == VARIANT_LEVEL
                and table_name not in offset_levels
            ):
                offset_levels.append(table_name)
        for m in self.annotators_i:
            for table_name, table_output in m.output.items():
                if (
                    table_output.get("level", m.level) == VARIANT_LEVEL
                    and table_name not in offset_levels
                ):
                    offset_levels.append(table_name)
        return offset_levels

    def create_info_table_in_result_db(self):
        if not self.result_db_conn:
            return
        q = "drop table if exists info"
        self.result_db_conn.execute(q)
        q = "create table info (colkey text primary key, colval text)"
        self.result_db_conn.execute(q)
        self.result_db_conn.commit()

    def create_auxiliary_tables_in_result_db(self, converter: BaseConverter):
        if not self.result_db_conn:
            return []
        self.create_info_table_in_result_db()
        self.create_info_modules_table_in_result_db()
        self.create_info_module_groups_table_in_result_db()
        self.create_info_tables_table_in_result_db(converter)
        self.create_info_headers_table_in_result_db(converter)

    def create_result_database(
        self, dbpath: Path, converter: BaseConverter, clean: bool = False
    ):
        coldefs, result_table_names = self.collect_output_coldefs(converter)
        self.open_result_database(dbpath, clean=clean)
        self.create_tables_in_result_db(coldefs, result_table_names)
        self.create_auxiliary_tables_in_result_db(converter)
        self.close_result_database()

    def process_file(self, run_no: int, clean: bool = True):
        from ..exceptions import NoConverterFound
        from .worker import Worker
        from ..util.run import update_status
        from .converter import VALID
        from .converter import ERROR
        from .converter import NO_ALT_ALLELE

        if self.mapper_name is None:
            return
        self.load_mapper()
        self.load_annotators()
        self.load_postaggregators()
        self.load_reporters()
        input_paths = self.input_paths[run_no]
        converter = self.choose_converter(input_paths)
        if converter is None:
            raise NoConverterFound(input_paths)
        converter.setup_df(input_paths, batch_size=self.batch_size)
        dbpath = self.get_dbpath(run_no)
        offset_levels: List[str] = self.get_offset_levels(converter)
        self.create_result_database(dbpath, converter, clean=clean)
        self.do_step_preparer(run_no)
        if self.num_core > 1:
            import ray
            import logging
            import os

            os.environ["GRPC_ENABLE_FORK_SUPPORT"] = "false"
            logger = logging.getLogger("ray")
            fmt = logging.Formatter(
                "%(asctime)s %(name)-20s %(message)s", "%Y/%m/%d %H:%M:%S"
            )
            log_handler = logging.StreamHandler()
            log_handler.setFormatter(fmt)
            logger.addHandler(log_handler)
            self.make_pool(run_no, converter, offset_levels)
            num_actors: int = len(self.pool)
            ret = []
            offset: int = 0
            for fileno, input_path in enumerate(input_paths):
                update_status(
                    f"Starting to process: {input_path}",
                    logger=self.logger,
                    serveradmindb=self.serveradmindb,
                )
                ret = []
                for actor_num, worker in enumerate(self.pool):
                    ret.append(worker.setup_file.remote(input_path, fileno=fileno))
                for r in ret:
                    ray.get(r)
                while True:
                    update_status(
                        f"Processing: {input_path} line {converter.start_line_no}",
                        logger=self.logger,
                        serveradmindb=self.serveradmindb,
                    )
                    (
                        lines,
                        line_nos,
                        num_lines,
                        num_lines_by_batch,
                        num_alts_by_batch,
                        has_more_data,
                    ) = converter.get_variant_lines(
                        input_path,
                        num_core=self.num_core,
                        batch_size=self.batch_size,
                    )
                    lines_ref = ray.put(lines)
                    line_nos_ref = ray.put(line_nos)
                    ret = []
                    for actor_num, worker in enumerate(self.pool):
                        r = worker.run_df.remote(
                            actor_num,
                            num_actors,
                            num_lines,
                            num_lines_by_batch,
                            num_alts_by_batch,
                            lines_ref,
                            line_nos_ref,
                        )
                        ret.append(r)
                    ray.get(ret)
                    for worker in self.pool:
                        last_val: int = ray.get(worker.renumber_uid.remote(offset))  # type: ignore
                        offset = last_val + 1
                        ray.get(worker.save_df.remote(dbpath))
                    if has_more_data is False:
                        break
                conversion_stats: Optional[Dict[str, int]] = None
                for worker in self.pool:
                    cs: Dict[str, int] = ray.get(worker.get_conversion_stats.remote())  # type: ignore
                    if conversion_stats is None:
                        conversion_stats = cs
                    else:
                        conversion_stats[VALID] += cs[VALID]
                        conversion_stats[ERROR] += cs[ERROR]
                        conversion_stats[NO_ALT_ALLELE] += cs[NO_ALT_ALLELE]
                converter.log_conversion_stats(conversion_stats=conversion_stats)
            update_status(
                f"Created result database: {dbpath}",
                logger=self.logger,
                serveradmindb=self.serveradmindb,
            )
            self.delete_pool()
        else:
            worker = Worker(
                input_paths=input_paths,
                converter=converter,
                mapper=self.mapper_i[0],
                annotators=self.annotators_i,
                ignore_sample=self.ignore_sample,
                run_conf=self.run_conf,
                genome=self.args.genome,
                batch_size=self.batch_size,
                offset_levels=offset_levels,
                use_duckdb=self.args.use_duckdb,
            )
            for fileno, input_path in enumerate(input_paths):
                update_status(
                    f"Starting to process: {input_path}",
                    logger=self.logger,
                    serveradmindb=self.serveradmindb,
                )
                worker.setup_file(input_path, fileno=fileno)
                while True:
                    update_status(
                        f"Processing: {input_path} line {converter.start_line_no}",
                        logger=self.logger,
                        serveradmindb=self.serveradmindb,
                    )
                    has_more_data = worker.run_df()
                    worker.save_df(dbpath)
                    if has_more_data is False:
                        break
                worker.close_db()
                converter.log_conversion_stats()
            update_status(
                f"Created result database: {dbpath}",
                logger=self.logger,
                serveradmindb=self.serveradmindb,
            )
            self.do_step_postaggregator(run_no)
        self.write_info_table(run_no, dbpath, converter)
        self.do_step_reporter(run_no)
        return

    def make_pool(
        self,
        run_no: int,
        converter: BaseConverter,
        offset_levels: List[str],
    ):
        from .worker import ParallelWorker

        if not self.mapper_name:
            return
        self.pool = []
        for _ in range(self.num_core):
            w = ParallelWorker.remote(input_paths=self.input_paths[run_no], converter_name=converter.name, mapper_name=self.mapper_name, annotator_names=self.annotator_names, ignore_sample=self.ignore_sample, run_conf=self.run_conf, genome=self.args.genome, batch_size=self.batch_size, output=converter.output, df_headers=converter.df_headers, offset_levels=offset_levels, use_duckdb=self.args.use_duckdb)  # type: ignore
            self.pool.append(w)

    def delete_pool(self):
        import ray

        ray.shutdown()

    def main(self) -> Optional[Dict[str, Any]]:
        from time import time, asctime, localtime
        from ..util.run import update_status
        from ..consts import JOB_STATUS_FINISHED
        from ..consts import JOB_STATUS_ERROR

        self.process_arguments(self.inkwargs)
        if not self.args:
            raise
        self.sanity_check_run_name_output_dir()
        self.make_annotators_to_run()
        # self.setup_manager()
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
                    self.process_file(run_no, clean=True)
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
        self.set_reporters()
        self.add_required_modules_for_reporters()
        self.add_required_modules_for_postaggregators()
        self.sort_annotators()
        self.sort_postaggregators()
        self.set_start_end_levels()
        self.set_misc_variables()

    def set_misc_variables(self):
        if self.args.batch_size:
            self.batch_size = self.args.batch_size

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
        self.fill_in_missing_ref = args.get("fill_in_missing_ref", False)
        self.args = SimpleNamespace(**args)
        self.outer = self.args.outer
        if self.args.vcf2vcf and self.args.combine_input:
            if self.outer:
                self.outer.write("--vcf2vcf is used. --combine-input is disabled.")
            self.args.combine_input = False
        self.process_module_options()
        self.num_core = self.get_num_workers()

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
            module_options = get_module_options(
                self.args.module_options, outer=self.outer
            )
        self.run_conf.update(module_options)

    def process_url_and_pipe_inputs(self):
        from pathlib import Path
        from ..util.util import is_url

        if not self.args:
            raise
        self.first_non_url_input = None
        if self.args.inputs is not None:
            if self.args.combine_input:
                self.input_paths = [
                    [
                        str(Path(x).resolve()) if not is_url(x) else x
                        for x in self.args.inputs
                    ]
                ]
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
                        if fpath:
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
            self.genome_assemblies = {}
        else:
            self.genome_assemblies = {}

    def set_and_create_output_dir(self):
        from pathlib import Path
        from os import getcwd
        from os import mkdir

        if not self.args:
            raise
        cwd = getcwd()
        if self.args.output_dir:
            self.output_dir = [str(Path(v).resolve()) for v in self.args.output_dir]
        else:
            if self.args.combine_input:
                self.output_dir = [cwd]
            else:
                self.output_dir = [
                    str(Path(inp[0]).parent.resolve()) for inp in self.input_paths
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

    def get_dbpath(self, run_no: int, run_name: str = "") -> Path:
        output_dir: str = self.output_dir[run_no]
        if not run_name:
            run_name = self.run_name[run_no]
        if self.args.use_duckdb:
            return self.get_duckdb_dbpath(output_dir, run_name)
        else:
            return self.get_sqlite_dbpath(output_dir, run_name)

    def get_duckdb_dbpath(self, output_dir: str, run_name: str):
        from ..consts import RESULT_DB_SUFFIX_DUCKDB

        dbpath_p = Path(output_dir) / f"{run_name}{RESULT_DB_SUFFIX_DUCKDB}"
        return dbpath_p

    def get_sqlite_dbpath(self, output_dir: str, run_name: str):
        from ..consts import RESULT_DB_SUFFIX_SQLITE

        dbpath_p = Path(output_dir) / f"{run_name}{RESULT_DB_SUFFIX_SQLITE}"
        return dbpath_p

    def get_unique_run_name(self, run_no: int, run_name: str):
        from pathlib import Path
        from ..consts import RESULT_DB_SUFFIX_DUCKDB
        from ..consts import RESULT_DB_SUFFIX_SQLITE

        if self.args.use_duckdb:
            suffix = RESULT_DB_SUFFIX_DUCKDB
        else:
            suffix = RESULT_DB_SUFFIX_SQLITE
        dbpath_p = self.get_dbpath(run_no, run_name=run_name)
        output_dir: str = self.output_dir[run_no]
        if not dbpath_p.exists():
            return run_name
        count = 0
        while dbpath_p.exists():
            dbpath_p = Path(output_dir) / f"{run_name}_{count}{suffix}"
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
                    run_name = self.get_unique_run_name(0, run_name)
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
        secondary_module_names = self.get_secondary_annotator_names(
            self.annotator_names
        )
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

    def get_secondary_module_names(self, primary_module_name: str) -> List[str]:
        from ..module.local import get_local_module_info
        from ..module.local import LocalModule

        module: Optional[LocalModule] = get_local_module_info(primary_module_name)
        if not module:
            return []
        secondary_module_names: List[str] = [
            module_name for module_name in module.secondary_module_names
        ]
        return secondary_module_names

    def get_num_workers(self) -> int:
        from ..system import get_max_num_concurrent_modules_per_job
        from psutil import cpu_count

        num_workers = get_max_num_concurrent_modules_per_job()
        if self.args.mp:
            try:
                self.args.mp = int(self.args.mp)
                if self.args.mp >= 1:
                    num_workers = self.args.mp
            except Exception:
                if self.logger:
                    self.logger.exception(f"Invalid --mp argument: {self.args.mp}")
        if not num_workers:
            num_workers = cpu_count()
        if self.logger:
            self.logger.info("num_workers: {}".format(num_workers))
        return num_workers

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

    def write_info_row(self, key: str, value: Any):
        import json

        if not self.result_db_conn:
            return
        q = "insert or replace into info values (?, ?)"
        if isinstance(value, list) or isinstance(value, dict):
            value = json.dumps(value)
        self.result_db_conn.execute(q, (key, value))

    def refresh_info_table_modified_time(self):
        from datetime import datetime

        if self.result_db_conn is None:
            return
        modified = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        q = "INSERT OR REPLACE into info values ('modified_at', ?)"
        self.result_db_conn.execute(q, (modified,))
        self.result_db_conn.commit()

    def result_database_table_exists(self, table_name):
        if self.result_db_conn is None:
            return
        cursor = self.result_db_conn.cursor()
        if self.args.use_duckdb:
            cursor.execute("pragma show_tables")
        else:
            cursor.execute("select name from sqlite_master where type='table'")
        r = cursor.fetchall()
        table_names = [v[0] for v in r]
        return table_name in table_names

    def write_info_table_create_data_if_needed(
        self, run_no: int, converter: BaseConverter
    ):
        from datetime import datetime

        if self.result_db_conn is None:
            return
        inputs = self.input_paths[run_no]
        job_name = self.job_name[run_no]
        created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.write_info_row("created_at", created)
        self.write_info_row("inputs", inputs)
        self.write_info_row("genome_assemblies", converter.genome_assemblies)
        cursor = self.result_db_conn.cursor()
        q = f"select count(*) from variant"
        cursor.execute(q)
        r = cursor.fetchall()
        num_input = str(r[0][0])  # type: ignore
        self.write_info_row("num_variants", num_input)
        self.write_info_row("oakvar", self.pkg_ver)
        mapper_conf = self.mapper_i[0].conf
        mapper_version = mapper_conf.get("version", mapper_conf.get("code_version"))
        self.write_info_row("mapper", [f"{self.mapper_name}=={mapper_version}"])
        self.write_info_row(
            "annotators",
            [f"{m.module_name}=={m.conf['version']}" for m in self.annotators_i],
        )
        self.write_info_row(
            "postaggregators",
            [f"{m.module_name}=={m.conf['version']}" for m in self.postaggregators_i],
        )
        input_paths = self.input_paths[run_no]
        self.write_info_row("input_paths", input_paths)
        self.write_info_row(
            "primary_transcript", ",".join(self.args.primary_transcript)
        )
        self.write_info_row("job_name", job_name)
        self.write_info_row("converter_format", converter.format_name)
        self.write_info_row("converter", f"{converter.name}=={converter.conf.get('version')}")
        self.write_info_row("samples", converter.samples)
        self.result_db_conn.commit()

    def write_info_table(self, run_no: int, dbpath: Path, converter: BaseConverter):
        self.open_result_database(dbpath)
        self.refresh_info_table_modified_time()
        self.write_info_table_create_data_if_needed(run_no, converter)
        self.close_result_database()

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
            f"{run_name}(\\..*({VARIANT_LEVEL_OUTPUT_SUFFIX}|{GENE_LEVEL_OUTPUT_SUFFIX})|({STANDARD_INPUT_FILE_SUFFIX}|{VARIANT_LEVEL_MAPPED_FILE_SUFFIX}|{GENE_LEVEL_MAPPED_FILE_SUFFIX}|{SAMPLE_FILE_SUFFIX}))"
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
        db = sqlite3.connect(str(admindb_path))
        cursor = db.cursor()
        q = "update jobs set runtime=?, numinput=?, info_json=? where dir=? and name=?"
        cursor.execute(
            q,
            (
                runtime,
                self.total_num_unique_variants,
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
            v for v in list(self.postaggregators.keys()) if v not in ["vcfinfo"]
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
            module_cls = load_class(module.script_path, class_name="Preparer")
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
        from ..base.postaggregator import BasePostAggregator

        if self.conf is None:
            raise SetupError()
        run_name = self.run_name[run_no]
        output_dir = self.output_dir[run_no]
        for module_name, module in self.postaggregators.items():
            if self.append_mode[run_no] and module_name in default_postaggregator_names:
                continue
            postagg_conf = self.run_conf.get(module_name, {})
            post_agg_cls = load_class(module.script_path)
            if not issubclass(post_agg_cls, BasePostAggregator):
                raise ModuleLoadingError(module_name=module.name)
            post_agg = post_agg_cls(
                module_name=module_name,
                run_name=run_name,
                output_dir=output_dir,
                serveradmindb=self.serveradmindb,
                module_options=postagg_conf,
            )
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
        Module = load_class(module.script_path, class_name="VCF2VCF")
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
        from ..util.module import get_reporter
        from ..util.run import update_status
        from ..exceptions import ModuleNotExist
        from ..util.run import announce_module

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
            dbpath: Path = self.get_result_database_path(run_no)
            output_path: Path = output_dir / run_name
            output_dir: Path = output_dir
            run_name: str = run_name
            module_options = self.run_conf.get(module_name, {})
            reporter = get_reporter(
                module_name,
                dbpath=str(dbpath),
                output_path=output_path,
                output_dir=str(output_dir),
                run_name=run_name,
                module_options=module_options,
                use_duckdb=self.args.use_duckdb,
            )
            response_t = self.log_time_of_func(reporter.run, work=module_name)
            output_fns = None
            response_type = type(response_t)
            if response_type == list and response_t:
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
        from ..util.module import get_converter
        import traceback

        chosen_converter: Optional[BaseConverter] = None
        module_infos: List[LocalModule] = []
        if self.converter_name:
            module_info = get_local_module_info(self.converter_name)
            if module_info is None:
                raise Exception(
                    f' {self.converter_name} does not exist. Please check --converter-name option was given correctly, or consider installing {self.converter_name} module with "ov module install {self.converter_name}" command, if the module is in the OakVar store.'
                )
            module_infos.append(module_info)
        elif self.args.input_format:
            module_name = self.args.input_format + "-converter"
            module_info = get_local_module_info(module_name)
            if module_info is None:
                raise Exception(
                    module_name
                    + f' does not exist. Please check --input-format option was given correctly, or consider installing {module_name} module with "ov module install {module_name}" command, if the module is in the OakVar store.'
                )
            module_infos.append(module_info)
        else:
            module_infos = list(get_local_module_infos_of_type("converter").values())
        for module_info in module_infos:
            if module_info.name == "cravat-converter": continue
            try:
                converter = get_converter(
                    module_info.name,
                    ignore_sample=self.ignore_sample,
                    module_options=self.run_conf.get(module_info.name, {}),
                    genome=self.args.genome,
                )
            except Exception as e:
                if self.logger:
                    self.logger.error(
                        f"{traceback.format_exc()}\nSkipping {module_info.name} as it could not be loaded. ({e})"
                    )
                continue
            try:
                check_success = converter.check_format(input_paths[0])
            except Exception:
                traceback.print_exc()
                check_success = False
            if check_success:
                chosen_converter = converter
                break
        if chosen_converter:
            if self.logger:
                self.logger.info(
                    f"module: {chosen_converter.name}=={chosen_converter.code_version}"
                )
                self.logger.info(
                    f"Using {chosen_converter.name} for {' '.join(input_paths)}"
                )
            return chosen_converter

    def make_annotators_to_run(self):
        self.done_annotators = []
        self.annotators_to_run = {
            aname: self.annotators[aname]
            for aname in set(self.annotators) - set(self.done_annotators)
        }

    def mapper_run_df_wrapper(self, args: Tuple[BaseMapper, Dict[str, pl.DataFrame]]):
        fn, dfs = args
        return fn.run_df(dfs)

    def annotator_run_df_wrapper(
        self, args: Tuple[BaseAnnotator, Dict[str, pl.DataFrame]]
    ):
        fn, dfs = args
        return fn.run_df(dfs)

    def load_mapper(self):
        from ..util.module import get_mapper

        self.mapper_i = [get_mapper(self.mapper_name, use_duckdb=self.args.use_duckdb)]

    def load_annotators(self):
        from ..util.module import get_annotator
        from .annotator import BaseAnnotator

        self.annotators_i: List[BaseAnnotator] = []
        for module_name in self.annotator_names:
            self.annotators_i.append(get_annotator(module_name))

    def load_postaggregators(self):
        from ..util.module import get_postaggregator
        from .postaggregator import BasePostAggregator

        self.postaggregators_i: List[BasePostAggregator] = []
        for module_name in self.postaggregator_names:
            self.postaggregators_i.append(get_postaggregator(module_name))

    def load_reporters(self):
        from ..util.module import get_reporter
        from .reporter import BaseReporter

        self.reporters_i: List[BaseReporter] = []
        for module_name in self.reporter_names:
            self.reporters_i.append(get_reporter(module_name))

    def do_step_preparer(self, run_no: int):
        step = "preparer"
        if not self.should_run_step(step):
            return
        self.log_time_of_func(self.run_preparers, run_no, work=f"{step} step")

    def do_step_mapper(self, dfs: Dict[str, pl.DataFrame]) -> Dict[str, pl.DataFrame]:
        dfs = self.mapper_i[0].run_df(dfs)
        return dfs

    def do_step_annotator(
        self, dfs: Dict[str, pl.DataFrame]
    ) -> Dict[str, pl.DataFrame]:
        for module in self.annotators_i:
            dfs = module.run_df(dfs)
        return dfs

    def do_step_postaggregator(self, run_no: int):
        step = "postaggregator"
        if self.should_run_step(step):
            self.log_time_of_func(self.run_postaggregators, run_no, work=f"{step} step")

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
