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
from typing import Any
from typing import Dict


class BasePostAggregator(object):
    cr_type_to_sql = {"string": "text", "int": "integer", "float": "real"}

    def __init__(
        self,
        module_name: str,
        run_name: Optional[str] = None,
        output_dir: Optional[str] = None,
        serveradmindb=None,
        outer=None,
        module_options: Dict = {},
    ):
        from ..exceptions import ArgumentError
        from ..util.util import get_result_dbpath

        self.serveradmindb = serveradmindb
        self.run_name = run_name
        self.output_dir = output_dir
        self.level = None
        self.levelno = None
        self.module_options = None
        self.db_path = None
        self.logger = None
        self.error_logger = None
        self.unique_excs = []
        self.module_name = module_name
        if not self.output_dir:
            raise ArgumentError(msg="Output directory was not given.")
        if not self.run_name:
            raise ArgumentError(msg="run_name was not given.")
        self.db_path = get_result_dbpath(self.output_dir, self.run_name)
        self.module_options = module_options
        self._setup_logger()
        self.make_conf_and_level()
        self.fix_col_names()
        self.dbconn = None
        self.cursor = None
        self.cursor_w = None
        self.columns_v: Optional[str] = None
        self.columns_g: Optional[str] = None
        self.from_v: Optional[str] = None
        self.from_g: Optional[str] = None
        self.where_v: Optional[str] = None
        self.where_g: Optional[str] = None
        self.q_v: Optional[str] = None
        self.q_g: Optional[str] = None
        self.outer = outer
        self.should_run_annotate = self.check()
        self._close_db_connection()

    def make_conf_and_level(self):
        from ..module.local import get_module_conf
        from ..exceptions import SetupError
        from ..consts import LEVELS

        self.conf = get_module_conf(self.module_name, module_type="postaggregator")
        if self.conf and self.conf.get("level"):
            self.level = self.conf.get("level")
        if not self.level:
            raise SetupError(msg="level is not defined in {self.module_name}")
        self.levelno = LEVELS[self.level]

    def check(self) -> bool:
        """
        Return boolean indicating whether main 'annotate' loop should be run.
        Should be overridden in sub-classes.
        """
        return True

    def fix_col_names(self):
        from ..exceptions import ConfigurationError

        if not self.conf or not self.module_name:
            raise ConfigurationError()
        for col in self.conf["output_columns"]:
            col["name"] = self.module_name + "__" + col["name"]

    def _log_exception(self, e, halt=True):
        if halt:
            raise e
        else:
            if self.logger:
                self.logger.exception(e)

    def handle_legacy_data(self, output_dict: dict):
        from json import dumps

        for colname in self.json_colnames:
            delflag = False
            json_data = output_dict.get(colname, None)
            if json_data and "__" in colname:
                shortcolname = colname.split("__")[1]
                json_data = output_dict.get(shortcolname, None)
                delflag = json_data is not None
            else:
                shortcolname = colname
            if json_data:
                if type(json_data) is list:
                    for rowidx in range(len(json_data)):
                        row = json_data[rowidx]
                        if type(row) is list:
                            pass
                        elif type(row) is dict:
                            list_data = []
                            table_header = self.table_headers[colname]
                            for i in range(len(table_header)):
                                header = table_header[i]
                                if header in row:
                                    v = row[header]
                                else:
                                    v = None
                                list_data.append(v)
                            json_data[rowidx] = list_data
                json_data = dumps(json_data)
                out = json_data
            else:
                out = None
            output_dict[colname] = out
            if delflag:
                del output_dict[shortcolname]
        return output_dict

    def make_result_level_columns(self):
        from ..consts import LEVELS

        if not self.db_path or not self.dbconn:
            return None, None
        self.result_level_columns = {}
        cursor = self.dbconn.cursor()
        for level in LEVELS.keys():
            q = f"select name from pragma_table_info('{level}') as tblinfo"
            cursor.execute(q)
            columns = [v[0] for v in cursor.fetchall()]
            if columns:
                self.result_level_columns[level] = columns

    def get_result_module_columns(self, module_name):
        from ..consts import LEVELS

        if not self.db_path or not self.dbconn:
            return None, None
        self.cursor = self.dbconn.cursor()
        for level in LEVELS.keys():
            q = f"select name from pragma_table_info('{level}') as tblinfo"
            self.cursor.execute(q)
            columns = [
                v[0]
                for v in self.cursor.fetchall()
                if v[0].startswith(f"{module_name}__")
            ]
            if columns:
                return level, columns
        return None, None

    def get_result_module_column(self, query_column_name):
        for level, column_names in self.result_level_columns.items():
            for column_name in column_names:
                if column_name == query_column_name:
                    return level, column_name
        return None, None

    def setup_input_columns(self):
        from ..consts import VARIANT
        from ..consts import GENE

        if not self.conf:
            return
        self._open_db_connection()
        self.make_result_level_columns()
        self.input_columns = {}
        input_columns = self.conf.get("input_columns")
        requires = self.conf.get("requires")
        if input_columns:
            for input_column_name in input_columns:
                level, column_name = self.get_result_module_column(input_column_name)
                if level and column_name:
                    if self.input_columns.get(level) is None:
                        self.input_columns[level] = []
                    self.input_columns[level].append(column_name)
        elif requires:
            if "base" not in requires:
                requires.append("base")
            for module_name in requires:
                level, column_names = self.get_result_module_columns(module_name)
                if level and column_names:
                    if self.input_columns.get(level) is None:
                        self.input_columns[level] = []
                    self.input_columns[level].extend(column_names)
        else:
            self.input_columns = None
        if self.input_columns:
            if self.levelno == VARIANT:
                if "base__uid" not in self.input_columns["variant"]:
                    self.input_columns["variant"].append("base__uid")
                if (
                    "gene" in self.input_columns
                    and "base__hugo" not in self.input_columns["variant"]
                ):
                    self.input_columns["variant"].append("base__hugo")
            elif (
                self.levelno == GENE and "base__hugo" not in self.input_columns["gene"]
            ):
                self.input_columns["gene"].append("base__hugo")
        self._close_db_connection()

    def setup_output_columns(self):
        if not self.conf:
            return
        output_columns = self.conf["output_columns"]
        for col in output_columns:
            if "table" in col and col["table"] is True:
                self.json_colnames.append(col["name"])
                self.table_headers[col["name"]] = []
                for h in col["table_header"]:
                    self.table_headers[col["name"]].append(h["name"])

    def get_df(
        self,
        level: str = "variant",
        sql: Optional[str] = None,
        num_cores: int = 1,
        conn=None,
    ):
        from ..util.util import get_df_from_db

        if not self.db_path:
            return None
        df = get_df_from_db(
            self.db_path,
            table_name=level,
            sql=sql,
            num_cores=num_cores,
            conn=conn,
        )
        return df

    def save_df(self, df, level: str):
        if not self.conf:
            return
        assert self.dbconn is not None
        ref_colnames = {
            "variant": "base__uid",
            "gene": "base__hugo",
            "sample": "base__uid",
            "mapping": "base__uid",
        }
        ref_colname = ref_colnames.get(level)
        if not ref_colname:
            return
        c = self.dbconn.cursor()
        output_columns = self.conf["output_columns"]
        for coldef in output_columns:
            print(coldef)
            col_name = f"{coldef['name']}"
            ref_ids = df[ref_colname]
            for ref_id in ref_ids:
                value = df[ref_colname == ref_id, col_name]
                q = f"update {level} set {col_name}=? where {ref_colname}=?"
                c.execute(q, (value, ref_id))
        self.dbconn.commit()
        c.close()

    def run(self):
        from time import time, asctime, localtime
        from ..exceptions import ConfigurationError
        from ..exceptions import LoggerError
        from ..util.run import update_status

        if self.conf is None:
            raise ConfigurationError()
        if self.logger is None:
            raise LoggerError()
        if not self.should_run_annotate:
            self.base_cleanup()
            return
        start_time = time()
        status = f"started {self.conf['title']} ({self.module_name})"
        update_status(status, logger=self.logger, serveradmindb=self.serveradmindb)
        self.logger.info("started: {0}".format(asctime(localtime(start_time))))
        self.base_setup()
        self.json_colnames = []
        self.table_headers = {}
        self.setup_input_columns()
        self.setup_output_columns()
        self.process_file()
        self.fill_categories()
        if self.dbconn:
            self.dbconn.commit()
        self.postprocess()
        self.base_cleanup()
        end_time = time()
        run_time = end_time - start_time
        self.logger.info("finished: {0}".format(asctime(localtime(end_time))))
        self.logger.info("runtime: {0:0.3f}".format(run_time))
        status = f"Finished {self.conf['title']} ({self.module_name})"
        update_status(status, logger=self.logger, serveradmindb=self.serveradmindb)

    def process_file(self):
        from ..exceptions import ConfigurationError
        from ..util.run import update_status

        if self.conf is None:
            raise ConfigurationError()
        self._open_db_connection()
        if not self.dbconn or not self.cursor_w:
            return
        lnum = 0
        self.cursor_w.execute("begin")
        for input_data in self._get_input():
            try:
                output_dict = self.annotate(input_data)
                if not output_dict:
                    continue
                output_dict = self.handle_legacy_data(output_dict)
                self.write_output(output_dict, input_data=input_data)
                lnum += 1
                if lnum % 100000 == 0:
                    status = (
                        f"Running {self.conf['title']} ({self.module_name}): row {lnum}"
                    )
                    update_status(
                        status, logger=self.logger, serveradmindb=self.serveradmindb
                    )
                    self.cursor_w.execute("commit")
                    self.cursor_w.execute("begin")
            except Exception as e:
                self._log_runtime_exception(input_data, e)
        self.cursor_w.execute("commit")
        self._close_db_connection()

    def postprocess(self):
        pass

    def fill_categories(self):
        from ..exceptions import ConfigurationError
        from ..exceptions import SetupError
        from ..util.inout import ColumnDefinition

        if self.conf is None:
            raise ConfigurationError()
        self.open_db_connection()
        if not self.cursor or not self.cursor_w:
            raise SetupError()
        self._open_db_connection()
        self.cursor_w.execute("begin")
        for col_d in self.conf["output_columns"]:
            col_def = ColumnDefinition(col_d)
            if col_def.category not in ["single", "multi"]:
                continue
            col_name = col_def.name
            q = "select distinct {} from {}".format(col_name, self.level)
            self.cursor.execute(q)
            col_cats = []
            for r in self.cursor:
                col_cat_str = r[0] if r[0] is not None else ""
                for col_cat in col_cat_str.split(";"):
                    if col_cat not in col_cats:
                        col_cats.append(col_cat)
            col_cats.sort()
            col_def.categories = col_cats
            q = "update {}_header set col_def=? where col_name=?".format(self.level)
            self.cursor_w.execute(q, [col_def.get_json(), col_def.name])
        self.cursor_w.execute("commit")
        self.close_db_connection()

    def write_output(
        self, output_dict, input_data=None, base__uid=None, base__hugo=None
    ):
        from ..exceptions import ConfigurationError
        from ..exceptions import SetupError
        from ..consts import VARIANT, GENE

        if self.conf is None:
            raise ConfigurationError()
        if self.level is None or self.cursor is None or self.cursor_w is None:
            raise SetupError()
        vals = []
        set_strs = []
        for col_def in self.conf["output_columns"]:
            col_name = col_def["name"]
            shortcol_name = col_name.split("__")[1]
            if shortcol_name in output_dict:
                val = output_dict[shortcol_name]
                if val is None:
                    continue
                vals.append(val)
                set_strs.append(f"{col_name}=?")
        if len(vals) == 0:
            return
        set_str = ", ".join(set_strs)
        q = f"update {self.level} set {set_str} where "
        if self.levelno == VARIANT:
            q += "base__uid=?"
            if input_data:
                vals.append(input_data["base__uid"])
            elif base__uid:
                vals.append(base__uid)
            else:
                return
        elif self.levelno == GENE:
            q += "base__hugo=?"
            if input_data:
                vals.append(input_data["base__hugo"])
            elif base__hugo:
                vals.append(base__hugo)
            else:
                return
        self.cursor_w.execute(q, vals)

    def _log_runtime_exception(self, input_data, e):
        import traceback
        from ..exceptions import LoggerError

        if self.logger is None or self.error_logger is None:
            raise LoggerError(module_name=self.module_name)
        try:
            err_str = traceback.format_exc().rstrip()
            if err_str not in self.unique_excs:
                self.unique_excs.append(err_str)
                self.logger.error(err_str)
            if "base__uid" in input_data:
                self.error_logger.error(f"{input_data['base__uid']}\t{str(e)}")
            elif "base__hugo" in input_data:
                self.error_logger.error(f"{input_data['base__hugo']}\t{str(e)}")
            else:
                self.error_logger.error(f"{input_data}\t{str(e)}")
        except Exception as e:
            self._log_exception(e, halt=False)

    # Setup function for the base_annotator, different from self.setup()
    # which is intended to be for the derived annotator.
    def base_setup(self):
        self._open_db_connection()
        self._alter_tables()
        self.setup()
        self._close_db_connection()

    def open_db_connection(self):
        self._open_db_connection()

    def _open_db_connection(self):
        from sqlite3 import connect
        import os
        from ..exceptions import SetupError

        if self.db_path is None:
            raise SetupError()
        if os.path.exists(self.db_path):
            self.dbconn = connect(self.db_path)
            self.cursor = self.dbconn.cursor()
            self.cursor_w = self.dbconn.cursor()
            self.cursor_w.execute("pragma synchronous=0;")
            self.cursor_w.execute("pragma journal_mode=off;")
            self.cursor_w.execute("pragma cache_size=1000000;")
            self.cursor_w.execute("pragma locking_mode=EXCLUSIVE;")
            self.cursor_w.execute("pragma temp_store=MEMORY;")
            self.dbconn.isolation_level = None
        else:
            msg = str(self.db_path) + " not found"
            if self.logger:
                self.logger.error(msg)
            import sys

            sys.exit(msg)

    def close_db_connection(self):
        self._close_db_connection()

    def _close_db_connection(self):
        if self.cursor is not None:
            try:
                self.cursor.close()
            except Exception:
                pass
            self.cursor = None
        if self.cursor_w is not None:
            try:
                self.cursor_w.execute("pragma locking_mode=NORMAL")
                self.cursor_w.execute("commit")
            except Exception:
                pass
            try:
                self.cursor_w.close()
            except Exception:
                pass
            self.cursor_w = None
        if self.dbconn is not None:
            try:
                self.dbconn.commit()
                self.dbconn.close()
            except Exception:
                pass
            self.dbconn = None

    def _alter_tables(self):
        from ..util.inout import ColumnDefinition
        from ..exceptions import SetupError

        if (
            self.level is None
            or self.conf is None
            or self.cursor is None
            or self.cursor_w is None
        ):
            raise SetupError()
        self.cursor_w.execute("begin")
        # annotator table
        q = 'insert or replace into {:} values ("{:}", "{:}", "{}")'.format(
            self.level + "_annotator",
            self.module_name,
            self.conf["title"],
            self.conf["version"],
        )
        self.cursor_w.execute(q)
        # data table and header table
        header_table_name = self.level + "_header"
        for col_d in self.conf["output_columns"]:
            col_def = ColumnDefinition(col_d)
            colname = col_def.name
            coltype = col_def.type
            # data table
            try:
                self.cursor.execute(f"select {colname} from {self.level} limit 1")
            except Exception:
                if coltype is not None:
                    q = (
                        "alter table "
                        + self.level
                        + " add column "
                        + colname
                        + " "
                        + self.cr_type_to_sql[coltype]
                    )
                    self.cursor_w.execute(q)
            # header table
            # use prepared statement to allow " characters in colcats and coldesc
            q = "insert or replace into {} values (?, ?)".format(header_table_name)
            self.cursor_w.execute(q, [colname, col_def.get_json()])
        self.cursor_w.execute("commit")

    # Placeholder, intended to be overridded in derived class
    def setup(self):
        pass

    def base_cleanup(self):
        self.cleanup()
        self._close_db_connection()

    def cleanup(self):
        pass

    def _setup_logger(self):
        import logging

        if not self.module_name:
            return
        try:
            self.logger = logging.getLogger("oakvar." + self.module_name)
        except Exception as e:
            self._log_exception(e)
        self.error_logger = logging.getLogger("err." + self.module_name)

    def make_default_query_components(self):
        from ..consts import VARIANT
        from ..consts import GENE

        if self.levelno == VARIANT:
            self.from_v = "variant"
            self.where_v = ""
            self.columns_v = "*"
            self.from_g = "gene"
            self.where_g = "base__hugo=?"
            self.columns_g = "*"
        elif self.levelno == GENE:
            self.from_v = None
            self.where_v = None
            self.columns_v = None
            self.from_g = "gene"
            self.where_g = ""
            self.columns_g = "*"

    def make_custom_query_components(self):
        from ..consts import VARIANT
        from ..consts import GENE

        if self.levelno == VARIANT:
            if "gene" in self.result_level_columns:
                self.from_v = "variant"
                self.where_v = None
                self.from_g = "gene"
                self.where_g = "base__hugo=?"
            else:
                self.from_v = "variant"
                self.where_v = None
                self.from_g = None
                self.where_g = None
        elif self.levelno == GENE:
            self.from_g = "gene"
            self.where_g = None
            if "variant" in self.result_level_columns:
                self.from_v = "variant"
                self.where_v = "base__hugo=?"
            else:
                self.from_v = None
                self.where_v = None
        else:
            raise Exception(
                f"Unknown module level: {self.level} for {self.module_name}"
            )
        self.columns_v = self.get_result_level_input_columns("variant")
        self.columns_g = self.get_result_level_input_columns("gene")

    def get_result_level_input_columns(self, level) -> Optional[str]:
        if not self.input_columns:
            raise
        if level not in self.result_level_columns:
            return None
        if level not in self.input_columns:
            return None
        return ",".join(
            [
                column_name
                for column_name in self.result_level_columns[level]
                if column_name in self.input_columns[level]
            ]
        )

    def make_query_components(self):
        if not self.input_columns:
            self.make_default_query_components()
        else:
            self.make_custom_query_components()

    def make_queries(self):
        self.make_query_components()
        if self.columns_v and self.from_v:
            self.q_v = f"select {self.columns_v} from {self.from_v}"
            if self.where_v:
                self.q_v += f" where {self.where_v}"
        if self.columns_g and self.from_g:
            self.q_g = f"select {self.columns_g} from {self.from_g}"
            if self.where_g:
                self.q_g += f" where {self.where_g}"

    def get_column_names_of_table(self, table_name):
        assert self.dbconn is not None
        c = self.dbconn.cursor()
        q = f"pragma table_info('{table_name}')"
        c.execute(q)
        column_names = [row[1] for row in c.fetchall()]
        return column_names

    def _get_input(self):
        from ..exceptions import SetupError
        from ..consts import VARIANT
        from ..consts import GENE

        if self.db_path is None or self.level is None or not self.dbconn:
            raise SetupError()
        self.c_var = self.dbconn.cursor()
        self.c_gen = self.dbconn.cursor()
        self.make_queries()
        if self.levelno == VARIANT and self.q_v:
            self.c_var.execute(self.q_v)
            cursor = self.c_var
        elif self.levelno == GENE and self.q_g:
            self.c_gen.execute(self.q_g)
            cursor = self.c_gen
        else:
            raise
        col_names_gen = self.get_column_names_of_table("gene")
        for row in cursor:
            try:
                input_data = {}
                for i in range(len(row)):
                    input_data[cursor.description[i][0]] = row[i]
                if self.levelno == VARIANT and self.q_g and self.columns_g:
                    if input_data["base__hugo"] is None:
                        for col_name in col_names_gen:
                            input_data[col_name] = None
                    else:
                        self.c_gen.execute(self.q_g, (input_data["base__hugo"],))
                        for gen_row in self.c_gen:
                            for i in range(len(gen_row)):
                                input_data[self.c_gen.description[i][0]] = gen_row[i]
                            break  # only 1 row should be returned.
                elif self.levelno == GENE and self.q_v and self.columns_v:
                    for column_name in self.columns_v:
                        input_data[column_name] = []
                    self.c_var.execute(self.q_v, (input_data["base__hugo"],))
                    for var_row in self.c_var:
                        for i in range(len(var_row)):
                            input_data[self.c_var.description[i][0]].append(var_row[i])
                yield input_data
            except Exception as e:
                self._log_runtime_exception(row, e)
        cursor.close()
        if self.c_var:
            self.c_var.close()
        if self.c_gen:
            self.c_gen.close()

    def annotate(self, input_data) -> Optional[Dict[str, Any]]:
        _ = input_data
        raise NotImplementedError()
