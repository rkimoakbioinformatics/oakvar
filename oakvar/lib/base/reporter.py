# OakVar Dual License
# 
# Copyright (c) 2023 Oak Bioinformatics, LLC
# 
# This program is dual licensed under the Affero GPL-3.0 or later for 
# non-commercial and open source use, and under a commercial license, 
# which is available for purchase, for closed-source or commercial use.
# 
# For the commercial use, please contact Oak Bioinformatics, LLC 
# for obtaining such a license. OakVar commercial license does not impose 
# the Affero GPL open-source licensing terms, conditions, and limitations. 
# To obtain a commercial-use license of OakVar, please visit our website at
# https://oakbioinformatics.com or contact us at info@oakbioinformatics.com 
# for more information.
# 
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
from typing import Union
from typing import Dict
from typing import List
from pathlib import Path
import polars as pl
from ..util.inout import ColumnDefinition


class BaseReporter:
    def __init__(
        self,
        dbpath: Union[Path, str] = "",
        report_types: List[str] = [],
        filter_path: Optional[str] = None,
        filter=None,
        filter_sql: Optional[str] = None,
        output_path: Optional[Path] = None,
        name: Optional[str] = None,
        skip_gene_summary: bool = True,
        row_per_sample: bool = False,
        output_dir: str = ".",
        run_name: str = "",
        module_options: Dict = {},
        tables_to_report: List[str] = [],
        samples_to_include: Optional[List[str]] = [],
        samples_to_exclude: Optional[List[str]] = None,
        package: Optional[str] = None,
        columns_to_include: Optional[Dict[str, List[str]]] = None,
        user: str = "",
        module_conf: Dict[str, Any] = {},
        logtofile: bool = False,
        serveradmindb=None,
        outer=None,
        use_duckdb: bool = False,
    ):
        from pathlib import Path
        from .db_filter import DbFilter
        from ..consts import VARIANT_LEVEL

        self.module_type: str = "reporter"
        self.report_types: List[str] = report_types
        self.filter_path: Optional[str] = filter_path
        self.filter: Optional[Dict[str, Any]] = filter
        self.filter_sql: Optional[str] = filter_sql
        self.output_path: Optional[Path] = None
        self.module_name: Optional[str] = name
        self.row_per_sample: bool = row_per_sample
        self.output_dir: Path = Path(".")
        self.run_name: str = run_name
        self.module_options: Dict[str, Any] = module_options
        self.tables_to_include: List[str]
        if tables_to_report:
            self.tables_to_report = tables_to_report
        else:
            self.tables_to_report = [VARIANT_LEVEL]
        self.samples_to_include: Optional[List[str]] = samples_to_include
        self.samples_to_exclude: Optional[List[str]] = samples_to_exclude
        self.package_name: Optional[str] = package
        self.columns_to_include: Optional[Dict[str, List[str]]] = columns_to_include
        self.skip_gene_summary: bool = skip_gene_summary
        self.serveradmindb: Any = serveradmindb
        self.outer: Any = outer
        self.rf: Optional[DbFilter] = None
        self.colinfo = {}
        self.colnos = {}
        self.column_groups = {}
        self.columns_to_report: Dict[str, List[str]] = {}
        self.cols_to_display = {}
        self.colnos_to_display: Dict[str, List[int]] = {}
        self.extracted_cols: Dict[str, Any] = {}
        self.extracted_col_names: Dict[str, List[str]] = {}
        self.extracted_col_nos: Dict[str, List[int]] = {}
        self.retrieved_col_names: Dict[str, List[str]] = {}
        self.conn = None
        self.module_conf: Dict[str, Any] = {}
        self.extract_columns_multilevel: Dict[str, List[str]] = {}
        self.logger = None
        self.error_logger = None
        self.unique_excs = None
        self.mapper_name: str = ""
        self.no_log = False
        self.colcount = {}
        self.columns: Dict[str, List[Dict[str, Any]]] = {}
        self.logtofile = logtofile
        self.dictrow: bool = True
        self.gene_summary_datas = {}
        self.total_norows: Optional[int] = None
        self.use_duckdb: bool = False
        self.dbpath: Path = Path("")
        self.use_new_db_schema: bool = True
        self.user: str = ""
        self.set_dbpath(dbpath)
        self.set_db_kind()
        self.set_user(user)
        self.set_module_name_and_conf(name, module_conf)
        self.set_output_dir(output_dir)
        self.check_db_is_oakvar()
        self.set_output_path(output_path)
        self.set_columns_to_include(columns_to_include)
        self.setup_logger()
        self.load_filter()

    def set_output_path(self, output_path: Optional[Path]):
        from ..exceptions import NoInput
        from ..exceptions import ArgumentError

        if not self.dbpath.name:
            raise NoInput()
        if not output_path or not output_path.name:
            raise ArgumentError(msg="output_path should be given.")
        self.output_path = output_path
        if self.output_path.parent == "":
            self.output_path = self.output_dir / self.output_path.name

    def set_output_dir(self, output_dir: str):
        if not output_dir:
            self.output_dir = Path(self.dbpath).parent
        if not self.output_dir:
            self.output_dir = Path(".").resolve()

    def set_module_name_and_conf(
        self, name: Optional[str], module_conf: Dict[str, Any]
    ):
        import sys
        import os
        from copy import deepcopy
        from ..exceptions import ModuleLoadingError
        from ..module.local import get_module_conf

        if module_conf:
            self.module_conf = deepcopy(module_conf)
        if self.__module__ == "__main__":
            fp = None
            main_fpath = None
        else:
            fp = sys.modules[self.__module__].__file__
            if not fp:
                raise ModuleLoadingError(module_name=self.__module__)
            main_fpath = Path(fp).resolve()
        if not main_fpath:
            if name:
                self.module_name = name
                self.module_dir = Path(os.getcwd()).resolve()
            else:
                raise ModuleLoadingError(msg="name argument should be given.")
        else:
            self.module_name = main_fpath.stem
            self.module_dir = main_fpath.parent
            if not self.module_conf:
                self.module_conf = get_module_conf(
                    self.module_name,
                    module_type=self.module_type,
                    module_dir=self.module_dir,
                )

    def set_user(self, user: str):
        from ..system.consts import DEFAULT_SERVER_DEFAULT_USERNAME

        if user:
            self.user = user
        else:
            self.user = DEFAULT_SERVER_DEFAULT_USERNAME

    def get_db_conn(self):
        import sqlite3
        import duckdb

        if not self.conn:
            if self.use_duckdb:
                self.conn = duckdb.connect(str(self.dbpath))
            else:
                self.conn = sqlite3.connect(self.dbpath)
        return self.conn

    def set_db_kind(self):
        from packaging.version import Version
        from ..consts import OAKVAR_VERSION_KEY
        from ..consts import RESULT_DB_SUFFIX_DUCKDB

        if self.dbpath.suffix == RESULT_DB_SUFFIX_DUCKDB:
            self.use_duckdb = True
        else:
            self.use_duckdb = False
        if self.use_duckdb:
            self.use_new_db_schema = True
        else:
            conn = self.get_db_conn()
            cursor = conn.cursor()
            q = "select colval from info where colkey=?"
            cursor.execute(q, (OAKVAR_VERSION_KEY,))
            rows = cursor.fetchall()
            ov_version: str = rows[0][0]
            if Version(ov_version) >= Version("3.0.0"):
                self.use_new_db_schema = True
            else:
                self.use_new_db_schema = False

    def check_db_is_oakvar(self):
        from ..exceptions import WrongInput

        if not self.dbpath:
            raise WrongInput(msg=f"{self.dbpath} is not an OakVar result database file.")
        if not Path(self.dbpath).exists():
            raise WrongInput(msg=self.dbpath)
        try:
            conn = self.get_db_conn()
            cursor = conn.cursor()
            cursor.execute("select colval from info where colkey='oakvar'")
            rows = cursor.fetchall()
            if len(rows) == 0:
                raise WrongInput(msg=f"{self.dbpath} is not an OakVar result database")
        except Exception:
            raise WrongInput(msg=f"{self.dbpath} is not an OakVar result database")

    def set_columns_to_include(
        self, columns_to_include: Optional[Dict[str, List[str]]]
    ):
        import json
        from copy import deepcopy

        if self.columns_to_include is not None:
            self.columns_to_include = deepcopy(columns_to_include)
        elif "columns_to_include" in self.module_options:
            v = self.module_options["columns_to_include"]
            if isinstance(v, str):
                if v.startswith("{"):  # dict
                    v = v.replace("'", '"')
                    j = json.loads(v)
                    if isinstance(j, dict):
                        self.columns_to_include = j
            elif isinstance(v, dict):
                self.columns_to_include = v

    def load_filter(self):
        from .db_filter import DbFilter

        self.rf = DbFilter.create(dbpath=self.dbpath, user=self.user, strict=False)
        self.rf.loadfilter(
            filter=self.filter,
            filterpath=self.filter_path,
            filtersql=self.filter_sql,
            include_sample=self.samples_to_include,
            exclude_sample=self.samples_to_exclude,
        )

    def should_write_level(self, level):
        if self.levels_to_write is None:
            return True
        elif level in self.levels_to_write:
            return True
        else:
            return False

    def setup_logger(self):
        import logging
        from ..util.run import set_logger_handler

        if self.no_log:
            return
        if (
            self.module_name is None
            or self.output_dir is None
            or self.output_path is None
        ):
            return
        try:
            self.logger = logging.getLogger(self.module_name)
            set_logger_handler(
                self.logger,
                output_dir=Path(self.output_dir),
                run_name=self.run_name,
                mode="a",
                logtofile=self.logtofile,
            )
        except Exception as e:
            self._log_exception(e)
        self.unique_excs = []

    def _log_exception(self, e, halt=True):
        if halt:
            raise e
        elif self.logger:
            self.logger.exception(e)

    def get_extracted_header_columns(self, table):
        cols = []
        for col in self.colinfo[table]["columns"]:
            if col["col_name"] in self.columns_to_report[table]:
                cols.append(col)
        return cols

    def get_db_col_name(self, mi, col):
        if mi.name in ["gencode", "hg38", "tagsampler"]:
            grp_name = "base"
        else:
            grp_name = mi.name
        return f"{grp_name}__{col['name']}"

    def col_is_categorical(self, col):
        return "category" in col and col["category"] in ["single", "multi"]

    def do_gene_level_summary(self):
        self.gene_summary_datas = {}
        if not self.summarizing_modules:
            return self.gene_summary_datas
        for mi, module_instance, summary_cols in self.summarizing_modules:
            gene_summary_data = module_instance.get_gene_summary_data(self.rf)
            self.gene_summary_datas[mi.name] = [gene_summary_data, summary_cols]
            columns = self.colinfo["gene"]["columns"]
            for col in summary_cols:
                if not self.col_is_categorical(col):
                    continue
                colno = None
                for i in range(len(columns)):
                    if columns[i]["col_name"] == self.get_db_col_name(mi, col):
                        colno = i
                        break
                cats = []
                for hugo in gene_summary_data:
                    val = gene_summary_data[hugo][col["name"]]
                    if val not in cats:
                        cats.append(val)
                if colno is not None:
                    columns[colno]["col_cats"] = cats

    def store_mapper(self):
        from json import loads

        conn = self.get_db_conn()
        cursor = conn.cursor()
        q = "select colval from info where colkey='mapper'"
        cursor.execute(q)
        r = cursor.fetchone()
        if r is None:
            self.mapper_name = "gencode"
        else:
            self.mapper_name = loads(r[0])[0]

    def write_log(self, msg):
        if not self.logger:
            return
        self.logger.info(msg)

    def log_run_start(self):
        from time import asctime, localtime
        import oyaml as yaml
        from ..util.run import update_status

        self.write_log("started: %s" % asctime(localtime(self.start_time)))
        if self.rf and self.rf.filter:
            self.write_log(f"filter:\n{yaml.dump(self.filter)}")
        if self.module_conf:
            status = f"started {self.module_conf['title']} ({self.module_name})"
            update_status(status, logger=self.logger, serveradmindb=self.serveradmindb)

    def get_levels_to_run(self, tab: str) -> List[str]:
        if not self.rf:
            return []
        if tab == "all":
            levels = self.rf.get_result_levels()
        else:
            levels = [tab]
        if type(levels) is not list:
            return []
        if not levels:
            return []
        return levels

    def run_df(
        self, df: pl.DataFrame, columns: List[Dict[str, Any]], output_path: str = ""
    ):
        self.write_data_df(df, columns, output_path)
        self.end()

    def run(
        self,
        *args,
        skip_gene_summary: bool=True,
        pagesize: Optional[int] = None,
        page: Optional[int] = None,
        make_filtered_table: bool = True,
        user=None,
        **kwargs,
    ):
        from ..exceptions import SetupError
        from time import time
        from time import asctime
        from time import localtime
        from ..util.run import update_status
        from ..system.consts import DEFAULT_SERVER_DEFAULT_USERNAME

        _ = args
        _ = kwargs
        if user is None:
            user = DEFAULT_SERVER_DEFAULT_USERNAME
        try:
            self.skip_gene_summary = skip_gene_summary
            if not self.rf:
                raise SetupError(self.module_name)
            self.start_time = time()
            self.log_run_start()
            if self.setup() is False:
                self.close_db()
                raise SetupError(self.module_name)
            self.ftable_uid = self.rf.make_ftables_and_ftable_uid(
                make_filtered_table=make_filtered_table
            )
            for table in self.tables_to_report:
                self.level = table
                self.make_col_infos()
                self.write_data(
                    table,
                    pagesize=pagesize,
                    page=page,
                    make_filtered_table=make_filtered_table,
                )
            self.close_db()
            if self.module_conf:
                status = f"finished {self.module_conf['title']} ({self.module_name})"
                update_status(
                    status, logger=self.logger, serveradmindb=self.serveradmindb
                )
            end_time = time()
            if not (hasattr(self, "no_log") and self.no_log) and self.logger:
                self.logger.info("finished: {0}".format(asctime(localtime(end_time))))
                run_time = end_time - self.start_time
                self.logger.info("runtime: {0:0.3f}".format(run_time))
            return self.end()
        except Exception:
            self.close_db()

    def write_preface_df(self, df, columns):
        _ = df or columns

    def write_header_df(self, columns):
        _ = columns

    def write_data_df(self, df, columns, output_path):
        import time
        import copy

        colnos = {columns[i]["name"]: i for i in range(len(columns))}
        self.write_preface_df(df, output_path)
        self.write_header_df(columns)
        row_count = 0
        ctime = time.time()
        self.vcf_format = False
        self.level = "variant"
        self.extracted_col_names = {"variant": copy.deepcopy(df.columns)}
        for datarow in df.iter_rows():
            # self.stringify_all_mapping(level, datarow)
            self.escape_characters_df(datarow)
            self.write_row_with_samples_separate_or_not_df(datarow, columns, colnos)
            row_count += 1
            if row_count % 10000 == 0:
                t = time.time()
                msg = f"Wrote {row_count} rows. {(t - ctime) / row_count}"
                if self.logger is not None:
                    self.logger.info(msg)
                elif self.outer is not None:
                    self.outer.write(msg)

    def write_data(
        self,
        table: str,
        pagesize=None,
        page=None,
        make_filtered_table=True,
    ):
        import time
        import sqlite3
        from ..exceptions import SetupError

        _ = make_filtered_table
        if self.should_write_level(table) is False:
            return
        if not self.table_exists(table):
            return
        if not self.rf:
            raise SetupError(self.module_name)
        if not self.skip_gene_summary and self.level == "gene":
            self.do_gene_level_summary()
        self.write_preface(table)
        self.extracted_cols[table] = self.get_extracted_header_columns(table)
        self.extracted_col_names[table] = [
            col_def.get("col_name") for col_def in self.extracted_cols[table]
        ]
        self.write_header(table)
        self.hugo_colno = self.colnos[table].get("base__hugo", None)
        datacols = self.rf.get_variant_data_cols()
        self.total_norows = self.rf.get_ftable_num_rows(level=table, uid=self.ftable_uid, ftype=table)  # type: ignore
        if datacols is None or self.total_norows is None:
            return
        if table == "variant" and self.row_per_sample:
            self.write_variant_sample_separately = True
        else:
            self.write_variant_sample_separately = False
        row_count = 0
        conn_read, conn_write = self.rf.get_db_conns()
        if conn_read is None or conn_write is None:
            return None
        cursor_read = conn_read.cursor()
        self.rf.get_level_data_iterator(
            table,
            page=page,
            pagesize=pagesize,
            uid=self.ftable_uid,
            var_added_cols=self.var_added_cols,
        )
        ctime = time.time()
        if isinstance(cursor_read, sqlite3.Cursor):
            self.retrieved_col_names[table] = [d[0] for d in cursor_read.description]
        else:
            if cursor_read.description is None:
                self.retrieved_col_names[table] = []
            else:
                self.retrieved_col_names[table] = [
                    d[0] for d in cursor_read.description
                ]
        self.extracted_col_nos[table] = [
            self.retrieved_col_names[table].index(col_name)
            for col_name in self.extracted_col_names[table]
        ]
        self.num_retrieved_cols = len(self.retrieved_col_names[table])
        self.colnos_to_display[table] = [
            self.retrieved_col_names[table].index(c)
            for c in self.columns_to_report[table]
        ]
        self.extracted_colnos_in_retrieved = [
            self.retrieved_col_names[table].index(c)
            for c in self.extracted_col_names[table]
        ]
        if isinstance(cursor_read, sqlite3.Cursor):
            datarow_iterator = cursor_read
        else:
            datarow_iterator = cursor_read.fetchall()
        for datarow in datarow_iterator:
            if self.dictrow:
                datarow = dict(datarow)
            else:
                datarow = list(datarow)
            if table == "gene" and not self.skip_gene_summary:
                self.add_gene_summary_data_to_gene_level(datarow)
            self.stringify_all_mapping(table, datarow)
            self.escape_characters(datarow)
            try:
                self.write_row_with_samples_separate_or_not(datarow)
            except Exception:
                import traceback
                traceback.print_exc()
                await cursor_read.close()
                await conn_read.close()
                await conn_write.close()
                if self.cf:
                    await self.cf.close_db()
            row_count += 1
            if row_count % 10000 == 0:
                msg = f"Wrote {row_count} rows."
                if self.logger is not None:
                    self.logger.info(msg)
                elif self.outer is not None:
                    self.outer.write(msg)
            if pagesize and row_count == pagesize:
                break
        cursor_read.close()
        conn_read.close()
        conn_write.close()

    def write_table_row_df(self, datarow, columns):
        _ = columns or datarow
        pass

    def write_row_with_samples_separate_or_not_df(self, datarow, columns, colnos):
        _ = colnos
        self.write_table_row_df(datarow, columns)

    def write_row_with_samples_separate_or_not(self, datarow):
        col_name = "tagsampler__samples"
        if self.write_variant_sample_separately:
            samples = datarow[col_name]
            if samples:
                samples = samples.split(";")
                for sample in samples:
                    sample_datarow = datarow
                    sample_datarow[col_name] = sample
                    self.write_table_row(self.get_extracted_row(sample_datarow))
            else:
                self.write_table_row(self.get_extracted_row(datarow))
        else:
            self.write_table_row(self.get_extracted_row(datarow))

    def escape_characters_df(self, datarow):
        for i, v in enumerate(datarow):
            if isinstance(v, str) and "\n" in v:
                datarow[i] = v.replace("\n", "%0A")

    def escape_characters(self, datarow):
        if self.dictrow:
            for k, v in datarow.items():
                if isinstance(v, str) and "\n" in v:
                    datarow[k] = v.replace("\n", "%0A")
        else:
            for col_no in range(self.num_retrieved_cols):
                v = datarow[col_no]
                if isinstance(v, str) and "\n" in v:
                    datarow[col_no] = v.replace("\n", "%0A")

    def stringify_all_mapping(self, level, datarow):
        from json import loads

        if hasattr(self, "keep_json_all_mapping") is True or level != "variant":
            return
        col_name = "base__all_mappings"
        idx: Optional[int] = None
        if self.dictrow:
            all_map = loads(datarow[col_name])
        else:
            if col_name not in self.retrieved_col_names[level]:
                return
            idx = self.retrieved_col_names[level].index(col_name)
            all_map = loads(datarow[idx])
        newvals = []
        for hugo in all_map:
            for maprow in all_map[hugo]:
                if len(maprow) == 5:
                    # TODO: remove this after a while. Now is 10/22/2022.
                    [protid, protchange, so, transcript, rnachange] = maprow
                    exonno = ""
                else:
                    [protid, protchange, so, transcript, rnachange, exonno] = maprow
                if protid is None:
                    protid = "(na)"
                if protchange is None:
                    protchange = "(na)"
                if rnachange is None:
                    rnachange = "(na)"
                newval = (
                    f"{transcript}:{hugo}:{protid}:{so}:{protchange}"
                    + f":{rnachange}:{exonno}"
                )
                newvals.append(newval)
        newvals.sort()
        newcell = "; ".join(newvals)
        if self.dictrow:
            datarow[col_name] = newcell
        elif idx is not None:
            datarow[idx] = newcell

    def add_gene_summary_data_to_gene_level(self, datarow):
        hugo = datarow["base__hugo"]
        for mi, _, _ in self.summarizing_modules:
            module_name = mi.name
            [gene_summary_data, cols] = self.gene_summary_datas[module_name]
            grp_name = "base" if self.should_be_in_base(module_name) else module_name
            if (
                hugo in gene_summary_data
                and gene_summary_data[hugo] is not None
                and len(gene_summary_data[hugo]) == len(cols)
            ):
                datarow.update(
                    {
                        f"{grp_name}__{col['name']}": gene_summary_data[hugo][
                            col["name"]
                        ]
                        for col in cols
                    }
                )
            else:
                datarow.update({f"{grp_name}__{col['name']}": None for col in cols})

    def add_gene_level_data_to_variant_level(self, datarow):
        if self.skip_gene_summary or self.hugo_colno is None or not self.rf:
            return
        generow = self.rf.get_gene_row(datarow["base__hugo"])
        if generow is None:
            datarow.update({col: None for col in self.var_added_cols})
        else:
            datarow.update({col: generow[col] for col in self.var_added_cols})

    def get_variant_colinfo(self):
        try:
            if self.setup() is False:
                self.close_db()
                return None
            self.levels = self.get_levels_to_run("all")
            self.make_col_infos()
            return self.colinfo
        except Exception:
            import traceback

            traceback.print_exc()
            self.close_db()
            return None

    def setup(self):
        pass

    def end(self):
        self.flush()

    def flush(self):
        pass

    def write_preface(self, __level__: str):
        pass

    def write_header(self, __level__: str):
        pass

    def write_table_row(self, __row__: Union[Dict[str, Any], List[Any]]):
        pass

    def get_extracted_row(self, row) -> Union[Dict[str, Any], List[Any]]:
        if not self.level:
            return row
        if self.dictrow:
            filtered_row = {col: row[col] for col in self.cols_to_display[self.level]}
        else:
            filtered_row = [row[colno] for colno in self.colnos_to_display[self.level]]
        return filtered_row

    def add_to_colnames_to_display(self, level, column):
        """
        include columns according to --cols option
        """
        col_name = column["col_name"]
        if (
            level in self.extract_columns_multilevel
            and len(self.extract_columns_multilevel[level]) > 0
        ):
            if col_name in self.extract_columns_multilevel[level]:
                incl = True
            else:
                incl = False
        else:
            incl = True
        if incl and col_name not in self.columns_to_report[level]:
            self.columns_to_report[level].append(col_name)

    def make_sorted_column_groups(self, level):
        conn = self.get_db_conn()
        cursor = conn.cursor()
        self.column_groups[level] = []
        sql = "select name, displayname, version from info_modules where parent=?"
        cursor.execute(sql, (level,))
        rows = cursor.fetchall()
        for row in rows:
            (name, displayname, version) = row
            self.column_groups[level].append(
                {"name": name, "displayname": displayname, "version": version}
            )

    def make_coldefs(self, level, group_name=None) -> List[ColumnDefinition]:
        coldefs: List[ColumnDefinition] = []
        conn = self.get_db_conn()
        cursor = conn.cursor()
        q = "select name, json from info_headers where level=?"
        cursor.execute(q, (level,))
        rows = cursor.fetchall()
        for row in rows:
            (col_name, coldef_str) = row
            [group_name, _] = col_name.split("__")
            coldef = ColumnDefinition({})
            coldef.from_json(coldef_str)
            coldefs.append(coldef)
        return coldefs

    def gather_col_categories(self, level, coldef):
        conn = self.get_db_conn()
        cursor = conn.cursor()
        if coldef.category not in ["single", "multi"] or len(coldef.categories) > 0:
            return coldef
        sql = f"select distinct {coldef.name} from {level}"
        cursor.execute(sql)
        rs = cursor.fetchall()
        for r in rs:
            coldef.categories.append(r[0])
        return coldef

    def make_columns_colnos_colnamestodisplay_columngroup(
        self, level, coldefs: List[ColumnDefinition]
    ):
        self.columns[level] = []
        self.colnos[level] = {}
        self.colcount[level] = 0
        for coldef in coldefs:
            self.colnos[level][coldef.name] = self.colcount[level]
            self.colcount[level] += 1
            if "__" not in coldef.name:
                colgrpname = "base"
            else:
                colgrpname = self.get_group_field_names(coldef.name)[0]
            column = coldef.get_colinfo()
            self.columns[level].append(column)
            self.add_to_colnames_to_display(level, column)
            for columngroup in self.column_groups[level]:
                if columngroup["name"] == colgrpname:
                    columngroup["count"] += 1

    def get_gene_level_modules_to_add_to_variant_level(self) -> List[str]:
        conn = self.get_db_conn()
        cursor = conn.cursor()
        q = "select name from gene_annotator"
        cursor.execute(q)
        gene_annotators: List[str] = [v[0] for v in cursor.fetchall()]
        modules_to_add = [m for m in gene_annotators if m != "base"]
        return modules_to_add

    def add_gene_level_displayname_to_variant_level_columngroups(
        self, module_name, coldefs
    ):
        conn = self.get_db_conn()
        cursor = conn.cursor()
        q = "select displayname from gene_annotator where name=?"
        cursor.execute(q, (module_name,))
        r = cursor.fetchall()
        displayname = r[0][0]
        self.column_groups["variant"].append(
            {"name": module_name, "displayname": displayname, "count": len(coldefs)}
        )

    def add_gene_level_columns_to_variant_level(self):
        if not self.table_exists("gene"):
            return
        modules_to_add = self.get_gene_level_modules_to_add_to_variant_level()
        for module_name in modules_to_add:
            gene_coldefs = self.make_coldefs("gene", group_name=module_name)
            if not gene_coldefs:
                continue
            self.add_gene_level_displayname_to_variant_level_columngroups(
                module_name, gene_coldefs
            )
            for gene_coldef in gene_coldefs:
                self.colnos["variant"][gene_coldef.name] = self.colcount["variant"]
                self.colcount["variant"] += 1
                gene_column = gene_coldef.get_colinfo()
                self.columns["variant"].append(gene_column)
                self.add_to_colnames_to_display("variant", gene_column)
                self.var_added_cols.append(gene_coldef.name)

    def add_gene_level_summary_columns(self):
        from os.path import dirname
        import sys
        from ..exceptions import ModuleLoadingError
        from ..module.local import get_local_module_infos_of_type
        from ..module.local import get_local_module_info
        from ..util.inout import ColumnDefinition
        from ..util.module import get_annotator
        from ..util.module import get_mapper

        conn = self.get_db_conn()
        cursor = conn.cursor()
        if self.skip_gene_summary:
            return
        q = "select name from variant_annotator"
        cursor.execute(q)
        done_var_annotators = [v[0] for v in cursor.fetchall()]
        self.summarizing_modules = []
        local_modules = get_local_module_infos_of_type("annotator")
        local_modules.update(get_local_module_infos_of_type("postaggregator"))
        summarizer_module_names = []
        for module_name in done_var_annotators:
            if module_name == self.mapper_name or module_name in [
                "base",
                "hg38",
                "hg19",
                "hg18",
                "extra_vcf_info",
                "extra_variant_info",
                "original_input",
            ]:
                continue
            if module_name not in local_modules:
                if self.logger:
                    self.logger.info(
                        f"Skipping gene level summarization with {module_name} "
                        + "as it does not exist in the system."
                    )
                continue
            module = local_modules[module_name]
            if "can_summarize_by_gene" in module.conf:
                summarizer_module_names.append(module_name)
        mapper = get_local_module_info(self.mapper_name)
        if not mapper:
            raise ModuleLoadingError(module_name=self.mapper_name)
        local_modules[self.mapper_name] = mapper
        summarizer_module_names = [self.mapper_name] + summarizer_module_names
        for module_name in summarizer_module_names:
            if not module_name:
                continue
            mi = local_modules[module_name]
            if not mi:
                continue
            cmd = {
                "serveradmindb": self.serveradmindb,
            }
            sys.path = sys.path + [dirname(mi.script_path)]
            if mi.name in done_var_annotators:
                annot = get_annotator(module_name, **cmd)
            elif mi.name == self.mapper_name:
                annot = get_mapper(module_name, **cmd)
            else:
                continue
            cols = mi.conf["gene_summary_output_columns"]
            columngroup = {
                "name": mi.name,
                "displayname": mi.title,
                "count": len(cols),
            }
            level = "gene"
            self.column_groups[level].append(columngroup)
            for col in cols:
                coldef = ColumnDefinition(col)
                coldef.name = f"{mi.name}__{coldef.name}"
                coldef.genesummary = True
                column = coldef.get_colinfo()
                self.columns[level].append(column)
                self.add_to_colnames_to_display(level, column)
                self.colnos[level][coldef.name] = len(self.colnos[level])
            self.summarizing_modules.append([mi, annot, cols])

    def get_group_field_names(self, col_name: str):
        return col_name.split("__")

    def get_group_name(self, col_name):
        return self.get_group_field_names(col_name)[0]

    def set_cols_to_display(self, level):
        self.cols_to_display[level] = []
        self.colnos_to_display[level] = []
        colno = 0
        for col in self.columns[level]:
            col_name = col["col_name"]
            if col_name in self.columns_to_report[level]:
                self.cols_to_display[level].append(col_name)
                self.colnos_to_display[level].append(colno)
            colno += 1

    def make_col_infos(self):
        prev_level = self.level
        for level in self.levels:
            self.level = level
            self.make_col_info(level)
        self.level = prev_level

    def add_column_number_stat_to_col_groups(self, level: str):
        last_columngroup_pos = 0
        for columngroup in self.column_groups.get(level, []):
            columngroup["start_column_number"] = last_columngroup_pos
            new_last_columngroup_pos = last_columngroup_pos + columngroup["count"]
            columngroup["end_colunm_number"] = new_last_columngroup_pos
            last_columngroup_pos = new_last_columngroup_pos

    def make_col_info(self, table: str):
        if not table or not self.table_exists(table):
            return
        self.store_mapper()
        self.columns_to_report[table] = []
        self.make_sorted_column_groups(table)
        coldefs = self.make_coldefs(table)
        if not coldefs:
            return
        self.make_columns_colnos_colnamestodisplay_columngroup(table, coldefs)
        if not self.skip_gene_summary and self.level == "variant":
            self.add_gene_level_columns_to_variant_level()
        if self.level == "gene" and table == "gene" and not self.skip_gene_summary:
            self.add_gene_level_summary_columns()
        self.set_display_select_columns(table)
        self.set_cols_to_display(table)
        self.add_column_number_stat_to_col_groups(table)
        self.colinfo[table] = {
            "colgroups": self.column_groups[table],
            "columns": self.columns[table],
        }

    def set_dbpath(self, dbpath: Union[Path, str] = ""):
        from os.path import exists
        from ..exceptions import NoInput
        from ..exceptions import WrongInput

        if isinstance(dbpath, str):
            dbpath = Path(dbpath)
        self.dbpath = dbpath
        if not self.dbpath.name:
            raise NoInput()
        if not exists(self.dbpath):
            raise WrongInput("dbpath does not exist.")

    def close_db(self):
        if self.conn is not None:
            self.conn.close()
        if self.rf is not None:
            self.rf.close_db()
            self.rf = None

    def table_exists(self, table_name) -> bool:
        import duckdb

        conn = self.get_db_conn()
        if isinstance(conn, duckdb.DuckDBPyConnection):
            cursor = conn.cursor()
            q = f"show all tables"
            cursor.execute(q)
            rows = cursor.pl()
            return table_name in rows["table_name"]
        else:
            cursor = conn.cursor()
            q = "select name from sqlite_master where " + 'type="table"'
            cursor.execute(q)
            rows = cursor.fetchall()
            for row in rows:
                if row[0] == table_name:
                    return True
            return False

    def get_standardized_module_option(self, v: Any) -> Any:
        from ..util.run import get_standardized_module_option

        return get_standardized_module_option(v)


CravatReport = BaseReporter
