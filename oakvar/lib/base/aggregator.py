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
from typing import List


class Aggregator(object):
    cr_type_to_sql = {"string": "text", "int": "integer", "float": "real"}
    commit_threshold = 10000

    def __init__(
        self,
        input_dir: str,
        level: str,
        run_name: str,
        output_dir: Optional[str] = None,
        delete: bool = False,
        append: bool = False,
        serveradmindb=None,
    ):
        self.input_dir = input_dir
        self.level = level
        self.run_name = run_name
        self.output_dir = output_dir
        self.delete = delete
        self.append = append
        self.serveradmindb = serveradmindb
        self.annotators = []
        self.ipaths = {}
        self.readers = {}
        self.base_fpath = None
        self.input_base_fname = None
        self.output_base_fname = None
        self.key_name = None
        self.table_name = None
        self.logger = None
        self.error_logger = None
        self.unique_excs = []
        self.base_reader = None
        self.reportsub = None
        self.cursor = None
        self.db_path = None
        self.dbconn = None
        self.db_fname = None
        self.header_table_name = None
        self.reportsub_table_name = None
        self.base_prefix = "base"
        self.setup_directories()
        self._setup_logger()

    def setup_directories(self):
        from pathlib import Path
        from os import makedirs

        if not self.output_dir:
            self.output_dir = self.input_dir
        self.set_input_base_fname()
        if self.input_base_fname is None:
            raise
        self.set_output_base_fname()
        if not Path(self.output_dir).exists():
            makedirs(self.output_dir)

    def _setup_logger(self):
        from logging import getLogger

        self.logger = getLogger("oakvar.aggregator")
        self.logger.info("level: {0}".format(self.level))
        self.logger.info("input directory: %s" % self.input_dir)
        self.error_logger = getLogger("err.aggregator")

    def run(self):
        from time import time, asctime, localtime
        from ..util.run import update_status

        self.setup()
        if self.input_base_fname is None:
            return
        if self.dbconn is None:
            return
        if self.cursor is None:
            return
        if self.base_reader is None:
            return
        if self.key_name is None:
            return
        start_time = time()
        status = f"started aggregator ({self.level})"
        update_status(status, logger=self.logger, serveradmindb=self.serveradmindb)
        if self.logger is not None:
            self.logger.info("started: %s" % asctime(localtime(start_time)))
        self.dbconn.commit()
        n = 0
        if not self.append:
            col_names = self.base_reader.get_column_names()
            columns = ",".join(col_names)
            placeholders = ",".join(["?"] * len(col_names))
            q = f"insert into {self.table_name} ({columns}) values ({placeholders});"
            batch_size = 1_000_000
            value_batch = []
            for lnum, line, rd in self.base_reader.loop_data():
                try:
                    n += 1
                    vals = [rd.get(c) for c in col_names]
                    value_batch.append(vals)
                    if len(value_batch) == batch_size:
                        self.cursor.executemany(q, value_batch)
                        self.dbconn.commit()
                        value_batch = []
                    if lnum % 100000 == 0:
                        status = f"Running Aggregator ({self.level}:base): line {lnum}"
                        update_status(
                            status, logger=self.logger, serveradmindb=self.serveradmindb
                        )
                except Exception as e:
                    self._log_runtime_error(lnum, line, e, fn=self.base_reader.path)
            if value_batch:
                self.cursor.executemany(q, value_batch)
                self.dbconn.commit()
        for annot_name in self.annotators:
            reader = self.readers[annot_name]
            n = 0
            ordered_cnames = [
                cname for cname in reader.get_column_names() if cname != self.key_name
            ]
            if len(ordered_cnames) == 0:
                continue
            update_template = "update {} set {} where {}=?".format(
                self.table_name,
                ", ".join([f"{cname}=?" for cname in ordered_cnames]),
                self.base_prefix + "__" + self.key_name,
            )
            for lnum, line, rd in reader.loop_data():
                try:
                    n += 1
                    key_val = rd[self.key_name]
                    ins_vals = [rd.get(cname) for cname in ordered_cnames]
                    ins_vals.append(key_val)
                    self.cursor.execute(update_template, ins_vals)
                    if n % self.commit_threshold == 0:
                        self.dbconn.commit()
                    if lnum % 100000 == 0:
                        status = f"Running Aggregator ({self.level}:{annot_name}): line {lnum}"
                        update_status(
                            status, logger=self.logger, serveradmindb=self.serveradmindb
                        )
                except Exception as e:
                    self._log_runtime_error(lnum, line, e, fn=reader.path)
            self.dbconn.commit()
        self.fill_categories()
        # self.cursor.execute("pragma synchronous=2;")
        # self.cursor.execute("pragma journal_mode=delete;")
        end_time = time()
        if self.logger is not None:
            self.logger.info("finished: %s" % asctime(localtime(end_time)))
            runtime = end_time - start_time
            self.logger.info("runtime: %s" % round(runtime, 3))
        self._cleanup()
        status = f"finished aggregator ({self.level})"
        update_status(status, logger=self.logger, serveradmindb=self.serveradmindb)

    def make_reportsub(self):
        if self.cursor is None:
            return
        from json import loads

        if self.level in ["variant", "gene"]:
            q = f"select * from {self.level}_reportsub"
            self.cursor.execute(q)
            self.reportsub = {}
            for r in self.cursor.fetchall():
                (col_name, sub) = r
                self.reportsub[col_name] = loads(sub)
        else:
            self.reportsub = {}

    def do_reportsub_col_cats(self, col_name, col_cats):
        if self.reportsub is None:
            return
        (module_name, col) = col_name.split("__")
        if module_name in self.reportsub and col in self.reportsub[module_name]:
            sub = self.reportsub[module_name][col]
            for k, v in sub.items():
                for i, _ in enumerate(col_cats):
                    col_cats[i] = col_cats[i].replace(k, v)
        return col_cats

    def fill_categories(self):
        if self.level is None:
            return
        if self.dbconn is None or self.cursor is None:
            return
        from ..util.inout import ColumnDefinition

        header_table = self.level + "_header"
        coldefs: List[ColumnDefinition] = []
        sql = f"select col_def from {header_table}"
        self.cursor.execute(sql)
        for row in self.cursor:
            coljson = row[0]
            coldef = ColumnDefinition({})
            coldef.from_json(coljson)
            coldefs.append(coldef)
        for coldef in coldefs:
            col_cats = coldef.categories
            if coldef.category in ["single", "multi"]:
                name: str = coldef.name or ""
                if col_cats is not None and len(col_cats) == 0:
                    q = f"select distinct {name} from {self.level}"
                    self.cursor.execute(q)
                    col_set = set([])
                    for r in self.cursor:
                        if r[0] is None:
                            continue
                        col_set.update(r[0].split(";"))
                    col_cats = list(col_set)
                    col_cats = self.do_reportsub_col_cats(name, col_cats)
                else:
                    col_cats = self.do_reportsub_col_cats(name, col_cats)
                if col_cats is not None:
                    col_cats.sort()
                coldef.categories = col_cats
                self.update_col_def(coldef)
        self.dbconn.commit()

    def update_col_def(self, col_def):
        if self.cursor is None:
            return
        q = f"update {self.level}_header set col_def=? where col_name=?"
        self.cursor.execute(q, [col_def.get_json(), col_def.name])

    def _cleanup(self):
        if self.dbconn is None or self.cursor is None:
            return
        self.cursor.close()
        self.dbconn.close()

    def set_input_base_fname(self):
        from os import listdir
        from ..consts import STANDARD_INPUT_FILE_SUFFIX
        from ..consts import VARIANT_LEVEL_MAPPED_FILE_SUFFIX
        from ..consts import GENE_LEVEL_MAPPED_FILE_SUFFIX
        from ..consts import SAMPLE_FILE_SUFFIX
        from ..consts import MAPPING_FILE_SUFFIX

        crv_fname = self.run_name + STANDARD_INPUT_FILE_SUFFIX
        crx_fname = self.run_name + VARIANT_LEVEL_MAPPED_FILE_SUFFIX
        crg_fname = self.run_name + GENE_LEVEL_MAPPED_FILE_SUFFIX
        crs_fname = self.run_name + SAMPLE_FILE_SUFFIX
        crm_fname = self.run_name + MAPPING_FILE_SUFFIX
        for fname in listdir(self.input_dir):
            if self.level == "variant":
                if fname == crx_fname:
                    self.input_base_fname = fname
                elif fname == crv_fname and not self.input_base_fname:
                    self.input_base_fname = fname
            elif self.level == "gene" and fname == crg_fname:
                self.input_base_fname = fname
            elif self.level == "sample" and fname == crs_fname:
                self.input_base_fname = fname
            elif self.level == "mapping" and fname == crm_fname:
                self.input_base_fname = fname

    def set_output_base_fname(self):
        self.output_base_fname = self.run_name

    def setup(self):
        if self.level is None:
            return
        if self.run_name is None:
            return
        if self.input_base_fname is None:
            return
        if self.input_dir is None:
            from ..exceptions import SetupError

            raise SetupError()
        from os.path import join
        from os import listdir

        if self.level == "variant":
            self.key_name = "uid"
        elif self.level == "gene":
            self.key_name = "hugo"
        elif self.level == "sample":
            self.key_name = ""
        elif self.level == "mapping":
            self.key_name = ""
        self.table_name = self.level
        self.header_table_name = self.table_name + "_header"
        self.reportsub_table_name = self.table_name + "_reportsub"
        prefix = self.run_name + "."
        len_prefix = len(prefix)
        for fname in listdir(self.input_dir):
            if fname.startswith(prefix):
                body = fname[len_prefix:]
                if self.level == "variant" and fname.endswith(".var"):
                    annot_name = body[:-4]
                    if "." not in annot_name:
                        self.annotators.append(annot_name)
                        self.ipaths[annot_name] = join(self.input_dir, fname)
                elif self.level == "gene" and fname.endswith(".gen"):
                    annot_name = body[:-4]
                    if "." not in annot_name:
                        self.annotators.append(annot_name)
                        self.ipaths[annot_name] = join(self.input_dir, fname)
        self.base_fpath = join(self.input_dir, self.input_base_fname)
        self._setup_io()
        self.annotators.sort()
        self._setup_table()

    def _setup_table(self):
        if self.level is None:
            return
        if self.dbconn is None or self.cursor is None:
            return
        if self.base_reader is None:
            return
        import sys
        from json import loads, dumps
        from collections import OrderedDict
        from ..util.inout import ColumnDefinition

        columns = []
        unique_names = set()
        # annotator table
        annotator_table = self.level + "_annotator"
        if not self.append:
            q = f"drop table if exists {annotator_table}"
            self.cursor.execute(q)
            q = (
                f"create table {annotator_table} (name text primary key, "
                + "displayname text, version text)"
            )
            self.cursor.execute(q)
            q = (
                f'insert into {annotator_table} values ("base", '
                + '"Variant Annotation", "")'
            )
            self.cursor.execute(q)
        for _, col_def in self.base_reader.get_all_col_defs().items():
            col_name = self.base_prefix + "__" + col_def.name
            col_def.change_name(col_name)
            columns.append(col_def)
            unique_names.add(col_name)
        for annot_name in self.annotators:
            reader = self.readers[annot_name]
            annotator_name = reader.get_annotator_name()
            if annotator_name == "":
                annotator_name = annot_name
            annotator_displayname = reader.get_annotator_displayname()
            if annotator_displayname == "":
                annotator_displayname = annotator_name.upper()
            annotator_version = reader.get_annotator_version()
            q = f"insert or replace into {annotator_table} values (?, ?, ?)"
            self.cursor.execute(
                q, [annotator_name, annotator_displayname, annotator_version]
            )
            orded_col_index = sorted(list(reader.get_all_col_defs().keys()))
            for col_index in orded_col_index:
                col_def = reader.get_col_def(col_index)
                reader_col_name = col_def.name
                if reader_col_name == self.key_name:
                    continue
                col_def.change_name(f"{annot_name}__{reader_col_name}")
                if col_def.name in unique_names and not self.append:
                    err_msg = "Duplicate column name %s found in %s. " % (
                        col_def.name,
                        reader.path,
                    )
                    sys.exit(err_msg)
                else:
                    columns.append(col_def)
                    unique_names.add(col_def.name)
        # data table
        col_def_strings = []
        for col_def in columns:
            name = col_def.name
            sql_type = self.cr_type_to_sql[col_def.type]
            s = f"{name} {sql_type}"
            col_def_strings.append(s)
        if not self.append:
            q = f"drop table if exists {self.table_name}"
            self.cursor.execute(q)
            q = 'create table "{}" ({});'.format(
                self.table_name,
                ", ".join(col_def_strings),
            )
            self.cursor.execute(q)
            # index tables
            index_n = 0
            # index_columns is a list of columns to include in this index
            for index_columns in self.base_reader.get_index_columns():
                cols = ["base__{0}".format(x) for x in index_columns]
                q = "create index {}_idx_{} on {} ({});".format(
                    self.table_name,
                    index_n,
                    self.table_name,
                    ", ".join(cols),
                )
                self.cursor.execute(q)
                index_n += 1
        else:
            q = f"pragma table_info({self.table_name})"
            self.cursor.execute(q)
            cur_cols = set([x[1] for x in self.cursor])
            for cds in col_def_strings:
                col_name = cds.split(" ")[0].strip('"')
                if col_name in cur_cols:
                    if col_name.startswith("base"):
                        continue
                    q = f"update {self.table_name} set {col_name} = null"
                else:
                    q = f"alter table {self.table_name} add column {cds}"
                self.cursor.execute(q)
        # header table
        if not self.append:
            q = f"drop table if exists {self.header_table_name}"
            self.cursor.execute(q)
            q = (
                f"create table {self.header_table_name} (col_name text "
                + "primary key, col_def text);"
            )
            self.cursor.execute(q)
        q = f"select col_name, col_def from {self.header_table_name}"
        self.cursor.execute(q)
        cdefs: OrderedDict[str, ColumnDefinition] = OrderedDict()
        for cname, cjson in self.cursor:
            annot_name = cname.split("__")[0]
            cdefs[cname] = ColumnDefinition(loads(cjson))
        if cdefs:
            self.cursor.execute(f"delete from {self.header_table_name}")
        for cdef in columns:
            cdefs[cdef.name] = cdef
        insert_template = f"insert into {self.header_table_name} values (?, ?)"
        for cdef in cdefs.values():
            self.cursor.execute(insert_template, [cdef.name, cdef.get_json()])
        # report substitution table
        if self.level in ["variant", "gene"]:
            if not self.append:
                q = f"drop table if exists {self.reportsub_table_name}"
                self.cursor.execute(q)
                q = (
                    f"create table {self.reportsub_table_name} (module text "
                    + "primary key, subdict text)"
                )
                self.cursor.execute(q)
                if hasattr(self.base_reader, "report_substitution"):
                    sub = self.base_reader.report_substitution
                    if sub:
                        q = (
                            f"insert into {self.reportsub_table_name} values "
                            + '("base", ?)'
                        )
                        self.cursor.execute(q, [dumps(sub)])
            for module in self.readers:
                if hasattr(self.base_reader, "report_substitution"):
                    sub = self.readers[module].report_substitution
                    if sub:
                        q = (
                            f"insert or replace into {self.reportsub_table_name} "
                            + "values (?, ?)"
                        )
                        self.cursor.execute(q, [module, dumps(sub)])
        self.make_reportsub()
        # filter and layout save table
        if not self.append:
            q = "drop table if exists viewersetup"
            self.cursor.execute(q)
            q = (
                "create table viewersetup (datatype text, name text, "
                + "viewersetup text, unique (datatype, name))"
            )
            self.cursor.execute(q)
        self.dbconn.commit()

    def _setup_io(self):
        from ..exceptions import SetupError

        if self.output_base_fname is None:
            return
        if self.output_dir is None:
            raise SetupError()
        from os.path import join, exists
        from os import remove
        from sqlite3 import connect
        from ..util.inout import FileReader

        self.base_reader = FileReader(self.base_fpath, logger=self.logger)
        for annot_name in self.annotators:
            self.readers[annot_name] = FileReader(self.ipaths[annot_name])
        self.db_fname = self.output_base_fname + ".sqlite"
        self.db_path = join(self.output_dir, self.db_fname)
        if self.delete and exists(self.db_path):
            remove(self.db_path)
        self.dbconn = connect(self.db_path)
        self.cursor = self.dbconn.cursor()
        self.cursor.execute("pragma synchronous=0;")
        self.cursor.execute("pragma journal_mode=off;")
        self.cursor.execute("pragma cache_size=1000000;")
        self.cursor.execute("pragma locking_mode=EXCLUSIVE;")
        self.cursor.execute("pragma temp_store=MEMORY;")

    def _log_runtime_error(self, ln, line, e, fn=None):
        if self.logger is None:
            return
        if self.error_logger is None:
            return
        from traceback import format_exc

        err_str = format_exc().rstrip()
        if ln is not None and line is not None:
            if err_str not in self.unique_excs:
                self.unique_excs.append(err_str)
                self.logger.error(err_str)
            self.error_logger.error(f"{fn}:{ln}\t{str(e)}")
            # self.error_logger.error(
            #    "\nLINE:{:d}\nINPUT:{}\nERROR:{}\n#".format(ln, line[:-1], str(e))
            # )
        else:
            self.logger.error(err_str)
