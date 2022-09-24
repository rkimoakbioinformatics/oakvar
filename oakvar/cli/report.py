from ..decorators import cli_func
from ..decorators import cli_entry
import sys
import nest_asyncio

nest_asyncio.apply()
if sys.platform == "win32" and sys.version_info >= (3, 8):
    from asyncio import set_event_loop_policy, WindowsSelectorEventLoopPolicy

    set_event_loop_policy(WindowsSelectorEventLoopPolicy())


class BaseReporter:
    def __init__(self, args):
        self.cf = None
        self.filtertable = "filter"
        self.colinfo = {}
        self.colnos = {}
        self.newcolnos = {}
        self.var_added_cols = []
        self.summarizing_modules = []
        self.columngroups = {}
        self.column_subs = {}
        self.column_sub_allow_partial_match = {}
        self.colname_conversion = {}
        self.warning_msgs = []
        self.colnames_to_display = {}
        self.colnos_to_display = {}
        self.display_select_columns = {}
        self.extracted_cols = {}
        self.conn = None
        self.levels_to_write = None
        self.args = None
        self.dbpath = None
        self.filterpath = None
        self.filtername = None
        self.filterstring = None
        self.filtersql = None
        self.filter = None
        self.confs = {}
        self.output_dir = None
        self.savepath = None
        self.conf = None
        self.module_name = None
        self.module_conf = None
        self.report_types = None
        self.output_basename = None
        self.status_fpath = None
        self.nogenelevelonvariantlevel = None
        self.status_writer = None
        self.concise_report = None
        self.extract_columns_multilevel = {}
        self.logger = None
        self.error_logger = None
        self.unique_excs = None
        self.mapper_name = None
        self.level = None
        self.no_log = False
        self.parse_cmd_args(args)
        self._setup_logger()

    def parse_cmd_args(self, args):
        import sqlite3
        from os.path import dirname
        from os.path import basename
        from os.path import join
        from os.path import exists
        import json
        from ..module.local import get_module_conf
        from os.path import abspath
        from ..system import consts
        from ..exceptions import WrongInput

        if not args:
            return
        if args.get("md"):
            consts.custom_modules_dir = args.get("md")
        self.dbpath = args.get("dbpath")
        if not exists(self.dbpath):
            raise WrongInput(msg=self.dbpath)
        try:
            with sqlite3.connect(self.dbpath) as db:
                db.execute("select * from info")
        except:
            raise WrongInput(msg=f"{self.dbpath} is not an OakVar database")
        self.filterpath = args.get("filterpath")
        self.filtername = args.get("filtername")
        self.filterstring = args.get("filterstring")
        self.filtersql = args.get("filtersql")
        self.filter = args.get("filter")
        self.output_dir = args.get("output_dir")
        self.module_name = args.get("module_name")
        self.report_types = args.get("reports")
        self.savepath = args.get("savepath")
        if self.output_dir:
            self.output_dir = dirname(self.dbpath)
        if not self.output_dir:
            self.output_dir = abspath(".")
        if self.savepath and dirname(self.savepath) == "":
            self.savepath = join(self.output_dir, self.savepath)
        self.module_conf = get_module_conf(self.module_name, module_type="reporter")
        self.confs = {}
        self.conf = args.get("conf")
        if self.conf:
            if self.module_name in self.conf:
                self.confs.update(self.conf[self.module_name])
            else:
                self.confs.update(self.conf)
        # confs update from confs
        confs = args.get("confs")
        if confs:
            confs = confs.lstrip("'").rstrip("'").replace("'", '"')
            if not self.confs:
                self.confs = json.loads(confs)
            else:
                self.confs.update(json.loads(confs))
        self.output_basename = basename(self.dbpath)[:-7]
        status_fname = "{}.status.json".format(self.output_basename)
        self.status_fpath = join(self.output_dir, status_fname)
        self.nogenelevelonvariantlevel = args.get("nogenelevelonvariantlevel", False)
        inputfiles = args.get("inputfiles")
        dbpath = args.get("dbpath")
        if not inputfiles and dbpath:
            db = sqlite3.connect(dbpath)
            c = db.cursor()
            q = 'select colval from info where colkey="_input_paths"'
            c.execute(q)
            r = c.fetchone()
            if r is not None:
                args["inputfiles"] = []
                s = r[0]
                if " " in s:
                    s = s.replace("'", '"')
                s = s.replace("\\", "\\\\\\\\")
                s = json.loads(s)
                for k in s:
                    input_path = s[k]
                    args["inputfiles"].append(input_path)
            c.close()
            db.close()
        self.inputfiles = args.get("inputfiles")
        self.status_writer = args.get("status_writer")
        self.concise_report = args.get("concise_report")
        if args.get("cols"):
            self.extract_columns_multilevel = {}
            for level in ["variant", "gene", "sample", "mapping"]:
                self.extract_columns_multilevel[level] = args.get("cols")
        else:
            self.extract_columns_multilevel = self.get_standardized_module_option(
                self.confs.get("extract_columns", {})
            )
        self.args = args

    def should_write_level(self, level):
        if self.levels_to_write is None:
            return True
        elif level in self.levels_to_write:
            return True
        else:
            return False

    async def check_result_db_for_mandatory_cols(self):
        from ..exceptions import ResultMissingMandatoryColumnError

        conn = await self.get_db_conn()
        if not conn or not self.module_conf:
            return
        mandatory_columns = self.module_conf.get("mandatory_columns")
        if not mandatory_columns:
            return
        cursor = await conn.cursor()
        db_col_names = []
        for level in ["variant", "gene"]:
            q = f"select col_name from {level}_header"
            await cursor.execute(q)
            col_names = await cursor.fetchall()
            db_col_names.extend([v[0] for v in col_names])
        missing_col_names = []
        for col_name in mandatory_columns:
            if col_name not in db_col_names:
                missing_col_names.append(col_name)
        if missing_col_names:
            cols = ", ".join(missing_col_names)
            raise ResultMissingMandatoryColumnError(self.dbpath, cols)

    async def prep(self):
        await self.connect_db()
        await self.check_result_db_for_mandatory_cols()
        await self.load_filter()

    def _setup_logger(self):
        if self.module_name is None:
            return
        import logging

        if hasattr(self, "no_log") and self.no_log:
            return
        try:
            self.logger = logging.getLogger(self.module_name)
        except Exception as e:
            self._log_exception(e)
        self.error_logger = logging.getLogger("err." + self.module_name)
        self.unique_excs = []

    async def get_db_conn(self):
        import aiosqlite

        if self.dbpath is None:
            return None
        if self.conn is None:
            self.conn = await aiosqlite.connect(self.dbpath)
        return self.conn

    async def exec_db(self, func, *args, **kwargs):
        from ..exceptions import DatabaseConnectionError

        conn = await self.get_db_conn()
        if conn is None:
            raise DatabaseConnectionError(self.module_name)
        cursor = await conn.cursor()
        try:
            ret = await func(*args, conn=conn, cursor=cursor, **kwargs)
        except:
            await cursor.close()
            raise
        await cursor.close()
        return ret

    def _log_exception(self, e, halt=True):
        if halt:
            raise e
        else:
            if self.logger:
                self.logger.exception(e)

    async def getjson(self, level):
        if self.cf is None:
            from ..exceptions import SetupError

            raise SetupError()
        import json

        ret = None
        if await self.exec_db(self.table_exists, level) == False:
            return ret
        rows = await self.cf.exec_db(self.cf.getiterator, level)
        if rows is not None:
            for row in rows:
                row = self.substitute_val(level, row)
                return json.dumps(row)

    def substitute_val(self, level, row):
        import json

        for sub in self.column_subs.get(level, []):
            value = row[sub.index]
            if value is None or value == "":
                continue
            if (
                level == "variant"
                and sub.module == "base"
                and sub.col == "all_mappings"
            ):
                mappings = json.loads(row[sub.index])
                for gene in mappings:
                    for i in range(len(mappings[gene])):
                        sos = mappings[gene][i][2].split(",")
                        sos = [sub.subs.get(so, so) for so in sos]
                        mappings[gene][i][2] = ",".join(sos)
                value = json.dumps(mappings)
            elif level == "gene" and sub.module == "base" and sub.col == "all_so":
                vals = []
                for i, so_count in enumerate(value.split(",")):
                    so = so_count[:3]
                    so = sub.subs.get(so, so)
                    so_count = so + so_count[3:]
                    vals.append(so_count)
                value = ",".join(vals)
            else:
                value = sub.subs.get(value, value)
            row[sub.index] = value
        return row

    def get_extracted_header_columns(self, level):
        cols = []
        for col in self.colinfo[level]["columns"]:
            if col["col_name"] in self.colnames_to_display[level]:
                cols.append(col)
        return cols

    async def run_level(self, level, pagesize=None, page=None, make_filtered_table=True):
        from ..exceptions import SetupError
        import json
        from ..consts import legacy_gene_level_cols_to_skip
        from ..util.util import quiet_print

        if self.cf is None or self.args is None:
            raise SetupError(self.module_name)
        ret = await self.exec_db(self.table_exists, level)
        if ret == False:
            return
        if self.should_write_level(level) == False:
            return
        gene_summary_datas = {}
        if level in ["variant", "sample", "mapping"] and make_filtered_table:
            await self.cf.exec_db(self.cf.make_filtered_uid_table)
        elif level == "gene" and make_filtered_table:
            await self.cf.exec_db(self.cf.make_filtered_hugo_table)
            for mi, o, cols in self.summarizing_modules:
                if hasattr(o, "build_gene_collection"):
                    msg = "Obsolete module [{}] for gene level summarization. Update the module to get correct gene level summarization.".format(
                        mi.name
                    )
                    self.warning_msgs.append(msg)
                    quiet_print("===Warning: {}".format(msg), self.args)
                    gene_summary_data = {}
                else:
                    gene_summary_data = await o.get_gene_summary_data(self.cf)
                gene_summary_datas[mi.name] = [gene_summary_data, cols]
                for col in cols:
                    if "category" in col and col["category"] in ["single", "multi"]:
                        colinfo_col = {}
                        colno = None
                        for i in range(len(self.colinfo[level]["columns"])):
                            colinfo_col = self.colinfo[level]["columns"][i]
                            if mi.name in ["gencode", "hg38", "tagsampler"]:
                                grp_name = "base"
                            else:
                                grp_name = mi.name
                            if colinfo_col["col_name"] == grp_name + "__" + col["name"]:
                                colno = i
                                break
                        cats = []
                        for hugo in gene_summary_data:
                            val = gene_summary_data[hugo][col["name"]]
                            repsub = colinfo_col.get("reportsub", [])
                            if len(repsub) > 0:
                                if val in repsub:
                                    val = repsub[val]
                            if val not in cats:
                                cats.append(val)
                        if colno is not None:
                            self.colinfo[level]["columns"][colno]["col_cats"] = cats
        self.write_preface(level)
        self.extracted_cols[level] = self.get_extracted_header_columns(level)
        self.write_header(level)
        hugo_present = None
        if level == "variant":
            hugo_present = "base__hugo" in self.colnos["variant"]
        datacols, datarows, total_norows = await self.cf.exec_db(  # type: ignore
            self.cf.get_filtered_iterator, level=level, page=page, pagesize=pagesize
        )
        self.total_norows = total_norows
        num_total_cols = len(datacols)
        colnos_to_skip = []
        if level == "gene":
            for colno in range(len(datacols)):
                if datacols[colno] in legacy_gene_level_cols_to_skip:
                    colnos_to_skip.append(colno)
        should_skip_some_cols = len(colnos_to_skip) > 0
        sample_newcolno = None
        if level == "variant" and self.args.get("separatesample"):
            write_variant_sample_separately = True
            sample_newcolno = self.newcolnos["variant"]["base__samples"]
        else:
            write_variant_sample_separately = False
        colnos = self.colnos[level]
        cols = self.colinfo[level]["columns"]
        json_colnos = []
        for i in range(len(cols)):
            col = cols[i]
            if col["table"] == True:
                json_colnos.append(i)
        row_count = 0
        for datarow in datarows:
            if datarow is None:
                continue
            datarow = list(datarow)
            if should_skip_some_cols:
                datarow = [
                    datarow[colno]
                    for colno in range(num_total_cols)
                    if colno not in colnos_to_skip
                ]
            if level == "variant":
                # adds gene level data to variant level.
                if self.nogenelevelonvariantlevel == False and hugo_present:
                    hugo = datarow[self.colnos["variant"]["base__hugo"]]
                    generow = await self.cf.get_gene_row(hugo)
                    if generow is None:
                        datarow.extend([None for _ in range(len(self.var_added_cols))])
                    else:
                        datarow.extend(
                            [
                                generow[self.colnos["gene"][colname]]
                                for colname in self.var_added_cols
                            ]
                        )
            elif level == "gene":
                # adds summary data to gene level.
                hugo = datarow[0]
                for mi, _, _ in self.summarizing_modules:
                    module_name = mi.name
                    [gene_summary_data, cols] = gene_summary_datas[module_name]
                    if (
                        hugo in gene_summary_data
                        and gene_summary_data[hugo] is not None
                        and len(gene_summary_data[hugo]) == len(cols)
                    ):
                        datarow.extend(
                            [gene_summary_data[hugo][col["name"]] for col in cols]
                        )
                    else:
                        datarow.extend([None for _ in cols])
            # re-orders data row.
            new_datarow = []
            for colname in [col["col_name"] for col in self.colinfo[level]["columns"]]:
                if colname in self.colname_conversion[level]:
                    oldcolname = self.colname_conversion[level][colname]
                    if oldcolname in colnos:
                        colno = colnos[oldcolname]
                    else:
                        if self.logger:
                            self.logger.info(
                                "column name does not exist in data: {}".format(
                                    oldcolname
                                )
                            )
                        continue
                else:
                    colno = colnos[colname]
                value = datarow[colno]
                new_datarow.append(value)
            # does report substitution.
            new_datarow = self.substitute_val(level, new_datarow)
            if hasattr(self, "keep_json_all_mapping") == False and level == "variant":
                all_mappings_newcolno = self.newcolnos["variant"]["base__all_mappings"]
                all_map = json.loads(new_datarow[all_mappings_newcolno])
                newvals = []
                for hugo in all_map:
                    for maprow in all_map[hugo]:
                        [protid, protchange, so, transcript, rnachange] = maprow
                        if protid == None:
                            protid = "(na)"
                        if protchange == None:
                            protchange = "(na)"
                        if rnachange == None:
                            rnachange = "(na)"
                        newval = (
                            transcript
                            + ":"
                            + hugo
                            + ":"
                            + protid
                            + ":"
                            + so
                            + ":"
                            + protchange
                            + ":"
                            + rnachange
                        )
                        newvals.append(newval)
                newvals.sort()
                newcell = "; ".join(newvals)
                new_datarow[all_mappings_newcolno] = newcell
            # escape characters
            for i, v in enumerate(new_datarow):
                if isinstance(v, str):
                    if "\n" in v:
                        new_datarow[i] = v.replace("\n", "%0A")
            if write_variant_sample_separately:
                samples = new_datarow[sample_newcolno]
                if samples is not None:
                    samples = samples.split(";")
                    for sample in samples:
                        sample_datarow = new_datarow
                        sample_datarow[sample_newcolno] = sample
                        self.write_table_row(self.get_extracted_row(sample_datarow))
                else:
                    self.write_table_row(self.get_extracted_row(new_datarow))
            else:
                self.write_table_row(self.get_extracted_row(new_datarow))
            row_count += 1
            if pagesize and row_count == pagesize:
                break

    async def store_mapper(self, conn=None, cursor=None):
        from ..exceptions import DatabaseConnectionError

        if conn is None or cursor is None:
            raise DatabaseConnectionError(self.module_name)
        q = 'select colval from info where colkey="_mapper"'
        await cursor.execute(q)
        r = await cursor.fetchone()
        if r is None:
            self.mapper_name = "hg38"
        else:
            self.mapper_name = r[0].split(":")[0]

    async def run(self, tab=None, pagesize=None, page=None, make_filtered_table=True):
        from ..exceptions import SetupError
        from time import time, asctime, localtime
        import oyaml as yaml

        try:
            await self.prep()
            if self.args is None or self.cf is None or self.logger is None:
                raise SetupError(self.module_name)
            start_time = time()
            ret = None
            if not tab:
                tab = self.args.get("level")
            if not tab:
                tab = "all"
            if not getattr(self, "no_log", False):
                if self.logger:
                    self.logger.info("started: %s" % asctime(localtime(start_time)))
                    if self.cf and self.cf.filter:
                        s = f"filter:\n{yaml.dump(self.filter)}"
                        self.logger.info(s)
            if self.module_conf is not None and self.status_writer is not None:
                if not self.args.get("do_not_change_status"):
                    self.status_writer.queue_status_update(
                        "status",
                        "Started {} ({})".format(
                            self.module_conf["title"], self.module_name
                        ),
                    )
            if self.setup() == False:
                await self.close_db()
                return
            if tab == "all":
                levels = await self.cf.exec_db(self.cf.get_result_levels)
                if levels:
                    for level in levels:
                        self.level = level
                        if await self.exec_db(self.table_exists, level):
                            await self.exec_db(self.make_col_info, level)
                    for level in levels:
                        self.level = level
                        if await self.exec_db(self.table_exists, level):
                            await self.run_level(level, pagesize=pagesize, page=page, make_filtered_table=make_filtered_table)
            else:
                if tab in ["variant", "gene"]:
                    for level in ["variant", "gene"]:
                        if await self.exec_db(self.table_exists, level):
                            await self.exec_db(self.make_col_info, level)
                else:
                    await self.exec_db(self.make_col_info, tab)
                self.level = tab
                await self.run_level(tab, pagesize=pagesize, page=page, make_filtered_table=make_filtered_table)
            await self.close_db()
            if self.module_conf is not None and self.status_writer is not None:
                if not self.args.get("do_not_change_status"):
                    self.status_writer.queue_status_update(
                        "status",
                        "Finished {} ({})".format(
                            self.module_conf["title"], self.module_name
                        ),
                    )
            end_time = time()
            if not (hasattr(self, "no_log") and self.no_log):
                self.logger.info("finished: {0}".format(asctime(localtime(end_time))))
                run_time = end_time - start_time
                self.logger.info("runtime: {0:0.3f}".format(run_time))
            ret = self.end()
        except Exception as e:
            await self.close_db()
            raise e
        return ret

    async def get_variant_colinfo(self):
        try:
            await self.prep()
            if self.setup() == False:
                await self.close_db()
                return None
            level = "variant"
            if await self.exec_db(self.table_exists, level):
                await self.exec_db(self.make_col_info, level)
            level = "gene"
            if await self.exec_db(self.table_exists, level):
                await self.exec_db(self.make_col_info, level)
            return self.colinfo
        except:
            await self.close_db()
            return None

    def setup(self):
        pass

    def end(self):
        pass

    def write_preface(self, __level__):
        pass

    def write_header(self, __level__):
        pass

    def write_table_row(self, __row__):
        pass

    def get_extracted_row(self, row):
        if self.display_select_columns[self.level]:
            filtered_row = [row[colno] for colno in self.colnos_to_display[self.level]]
        else:
            filtered_row = row
        return filtered_row

    def add_conditional_to_colnames_to_display(self, level, column, module_name):
        col_name = column["col_name"]
        if (
            level in self.extract_columns_multilevel
            and len(self.extract_columns_multilevel[level]) > 0
        ):
            if col_name in self.extract_columns_multilevel[level]:
                incl = True
            else:
                incl = False
        elif self.concise_report:
            if "col_hidden" in column and column["col_hidden"] == True:
                incl = False
            else:
                incl = True
        else:
            incl = True
        if incl and col_name not in self.colnames_to_display[level]:
            if module_name == self.mapper_name:
                self.colnames_to_display[level].append(
                    col_name.replace(module_name + "__", "base__")
                )
            elif module_name == "tagsampler":
                self.colnames_to_display[level].append(
                    col_name.replace(module_name + "__", "base__")
                )
            else:
                self.colnames_to_display[level].append(col_name)

    async def make_col_info(self, level: str, conn=None, cursor=None):
        from ..exceptions import SetupError
        from os.path import dirname
        import json
        from ..util.inout import ColumnDefinition
        from ..util.util import load_class
        from types import SimpleNamespace
        from ..util.util import quiet_print
        from ..util.admin_util import get_user_conf
        from ..module.local import get_local_module_info
        from ..module.local import get_local_module_infos_of_type
        from ..exceptions import ModuleLoadingError

        if conn is None:
            pass
        if cursor is None:
            raise SetupError()
        await self.exec_db(self.store_mapper)
        self.colnames_to_display[level] = []
        priority_colgroupnames = (get_user_conf() or {}).get("report_module_order") or [
            "base",
            "gencode",
            "hg38",
            "hg19",
            "hg18",
            "tagsampler",
        ]  # level-specific column groups
        self.columngroups[level] = []
        sql = "select name, displayname from " + level + "_annotator"
        await cursor.execute(sql)
        rows = await cursor.fetchall()
        for row in rows:
            (name, displayname) = row
            self.columngroups[level].append(
                {"name": name, "displayname": displayname, "count": 0}
            )
        # level-specific column names
        header_table = level + "_header"
        coldefs = []
        sql = "select col_def from " + header_table
        await cursor.execute(sql)
        for row in await cursor.fetchall():
            coljson = row[0]
            coldef = ColumnDefinition({})
            coldef.from_json(coljson)
            coldefs.append(coldef)
        columns = []
        self.colnos[level] = {}
        colcount = 0
        # level-specific column details
        for coldef in coldefs:
            self.colnos[level][coldef.name] = colcount
            colcount += 1
            if coldef.category in ["single", "multi"] and len(coldef.categories) == 0:
                sql = "select distinct {} from {}".format(coldef.name, level)
                await cursor.execute(sql)
                rs = await cursor.fetchall()
                for r in rs:
                    coldef.categories.append(r[0])
            [colgrpname, _] = coldef.name.split("__")
            column = coldef.get_colinfo()
            columns.append(column)
            self.add_conditional_to_colnames_to_display(level, column, colgrpname)
            for columngroup in self.columngroups[level]:
                if columngroup["name"] == colgrpname:
                    columngroup["count"] += 1
        # adds gene level columns to variant level.
        if (
            self.nogenelevelonvariantlevel == False
            and level == "variant"
            and await self.exec_db(self.table_exists, "gene")
        ):
            modules_to_add = []
            q = "select name from gene_annotator"
            await cursor.execute(q)
            gene_annotators = [v[0] for v in await cursor.fetchall()]
            modules_to_add = [m for m in gene_annotators if m != "base"]
            for module in modules_to_add:
                cols = []
                q = f"select col_def from gene_header where col_name like ?"
                await cursor.execute(q, (module + "__%",))
                rs = await cursor.fetchall()
                for r in rs:
                    cd = ColumnDefinition({})
                    cd.from_json(r[0])
                    cols.append(cd)
                q = 'select displayname from gene_annotator where name=?'
                await cursor.execute(q, (module,))
                r = await cursor.fetchone()
                displayname = r[0]
                self.columngroups[level].append(
                    {"name": module, "displayname": displayname, "count": len(cols)}
                )
                for coldef in cols:
                    self.colnos[level][coldef.name] = colcount
                    colcount += 1
                    if (
                        coldef.category in ["category", "multicategory"]
                        and len(coldef.categories) == 0
                    ):
                        sql = "select distinct {} from {}".format(coldef.name, level)
                        await cursor.execute(sql)
                        rs = await cursor.fetchall()
                        for r in rs:
                            coldef.categories.append(r[0])
                    column = coldef.get_colinfo()
                    columns.append(column)
                    self.add_conditional_to_colnames_to_display(level, column, module)
                    self.var_added_cols.append(coldef.name)
        # Gene level summary columns
        if level == "gene":
            q = "select name from variant_annotator"
            await cursor.execute(q)
            done_var_annotators = [v[0] for v in await cursor.fetchall()]
            self.summarizing_modules = []
            local_modules = get_local_module_infos_of_type("annotator")
            local_modules.update(get_local_module_infos_of_type("postaggregator"))
            summarizer_module_names = []
            for module_name in done_var_annotators:
                if module_name in [
                    "gencode",
                    "base",
                    "hg19",
                    "hg18",
                    "extra_vcf_info",
                    "extra_variant_info",
                ]:
                    continue
                if module_name not in local_modules:
                    if module_name != "original_input":
                        quiet_print(
                            "            [{}] module does not exist in the system. Gene level summary for this module is skipped.".format(
                                module_name
                            ),
                            self.args,
                        )
                    continue
                module = local_modules[module_name]
                if "can_summarize_by_gene" in module.conf:
                    summarizer_module_names.append(module_name)
            local_modules[self.mapper_name] = get_local_module_info(self.mapper_name)
            summarizer_module_names = [self.mapper_name] + summarizer_module_names
            for module_name in summarizer_module_names:
                if module_name is None:
                    continue
                mi = local_modules[module_name]
                if not mi:
                    continue
                sys.path = sys.path + [dirname(mi.script_path)]
                annot_cls = None
                if module_name in done_var_annotators:
                    annot_cls = load_class(mi.script_path, "Annotator")
                    if not annot_cls:
                        annot_cls = load_class(mi.script_path, "CravatAnnotator")
                elif module_name == self.mapper_name:
                    annot_cls = load_class(mi.script_path, "Mapper")
                if annot_cls is None:
                    raise ModuleLoadingError(module_name)
                cmd = {
                    "script_path": mi.script_path,
                    "input_file": "__dummy__",
                    "output_dir": self.output_dir,
                }
                annot = annot_cls(cmd)
                cols = mi.conf["gene_summary_output_columns"]
                columngroup = {
                    "name": mi.name,
                    "displayname": mi.title,
                    "count": len(cols),
                }
                self.columngroups[level].append(columngroup)
                for col in cols:
                    coldef = ColumnDefinition(col)
                    coldef.name = columngroup["name"] + "__" + coldef.name
                    coldef.genesummary = True
                    column = coldef.get_colinfo()
                    columns.append(column)
                    self.add_conditional_to_colnames_to_display(level, column, mi.name)
                self.summarizing_modules.append([mi, annot, cols])
                for col in cols:
                    fullname = module_name + "__" + col["name"]
                    self.colnos[level][fullname] = len(self.colnos[level])
        # re-orders columns groups.
        colgrps = self.columngroups[level]
        newcolgrps = []
        for priority_colgrpname in priority_colgroupnames:
            for colgrp in colgrps:
                if colgrp["name"] == priority_colgrpname:
                    if colgrp["name"] in [self.mapper_name, "tagsampler"]:
                        newcolgrps[0]["count"] += colgrp["count"]
                    else:
                        newcolgrps.append(colgrp)
                    break
        colpos = 0
        for colgrp in newcolgrps:
            colgrp["lastcol"] = colpos + colgrp["count"]
            colpos = colgrp["lastcol"]
        colgrpnames = [
            v["displayname"] for v in colgrps if v["name"] not in priority_colgroupnames
        ]
        colgrpnames.sort()
        for colgrpname in colgrpnames:
            for colgrp in colgrps:
                if colgrp["displayname"] == colgrpname:
                    colgrp["lastcol"] = colpos + colgrp["count"]
                    newcolgrps.append(colgrp)
                    colpos += colgrp["count"]
                    break
        # re-orders columns.
        self.colname_conversion[level] = {}
        new_columns = []
        self.newcolnos[level] = {}
        newcolno = 0
        new_colnames_to_display = []
        for colgrp in newcolgrps:
            colgrpname = colgrp["name"]
            for col in columns:
                colname = col["col_name"]
                [grpname, _] = colname.split("__")
                if colgrpname == "base" and grpname in [self.mapper_name, "tagsampler"]:
                    newcolname = "base__" + colname.split("__")[1]
                    self.colname_conversion[level][newcolname] = colname
                    col["col_name"] = newcolname
                    new_columns.append(col)
                    self.newcolnos[level][newcolname] = newcolno
                    if newcolname in self.colnames_to_display[level]:
                        new_colnames_to_display.append(newcolname)
                elif grpname == colgrpname:
                    new_columns.append(col)
                    self.newcolnos[level][colname] = newcolno
                    if colname in self.colnames_to_display[level]:
                        new_colnames_to_display.append(colname)
                else:
                    continue
                newcolno += 1
        self.colinfo[level] = {"colgroups": newcolgrps, "columns": new_columns}
        self.colnames_to_display[level] = new_colnames_to_display
        # report substitution
        if level in ["variant", "gene"]:
            reportsubtable = level + "_reportsub"
            if await self.exec_db(self.table_exists, reportsubtable):
                q = "select * from {}".format(reportsubtable)
                await cursor.execute(q)
                reportsub = {r[0]: json.loads(r[1]) for r in await cursor.fetchall()}
                self.column_subs[level] = []
                for i, column in enumerate(new_columns):
                    module, col = column["col_name"].split("__")
                    if module == self.mapper_name:
                        module = "base"
                    if module in reportsub and col in reportsub[module]:
                        self.column_subs[level].append(
                            SimpleNamespace(
                                module=module,
                                col=col,
                                index=i,
                                subs=reportsub[module][col],
                            )
                        )
                        new_columns[i]["reportsub"] = reportsub[module][col]
        # display_select_columns
        if (
            level in self.extract_columns_multilevel
            and len(self.extract_columns_multilevel[level]) > 0
        ) or self.concise_report:
            self.display_select_columns[level] = True
        else:
            self.display_select_columns[level] = False
        # column numbers to display
        colno = 0
        self.colnos_to_display[level] = []
        for colgroup in self.colinfo[level]["colgroups"]:
            count = colgroup["count"]
            if count == 0:
                continue
            for col in self.colinfo[level]["columns"][colno : colno + count]:
                module_col_name = col["col_name"]
                if module_col_name in self.colnames_to_display[level]:
                    include_col = True
                else:
                    include_col = False
                if include_col:
                    self.colnos_to_display[level].append(colno)
                colno += 1

    def get_standardized_module_option(self, v):
        tv = type(v)
        if tv == str:
            if ":" in v:
                v0 = {}
                for v1 in v.split("."):
                    if ":" in v1:
                        v1toks = v1.split(":")
                        if len(v1toks) == 2:
                            level = v1toks[0]
                            v2s = v1toks[1].split(",")
                            v0[level] = v2s
                v = v0
            elif "," in v:
                v = [val for val in v.split(",") if val != ""]
        if v == "true":
            v = True
        elif v == "false":
            v = False
        return v

    async def connect_db(self, dbpath=None):
        from os.path import exists
        from ..exceptions import NoInput
        from ..exceptions import WrongInput


        if dbpath != None:
            self.dbpath = dbpath
        if not self.dbpath:
            raise NoInput()
        if not exists(self.dbpath):
            raise WrongInput()

    async def close_db(self):
        if hasattr(self, "conn") and self.conn is not None:
            await self.conn.close()
            self.conn = None
        if self.cf is not None:
            await self.cf.close_db()
            self.cf = None

    async def load_filter(self):
        from ..exceptions import SetupError
        from .. import ReportFilter

        if self.args is None:
            raise SetupError()
        self.cf = await ReportFilter.create(dbpath=self.dbpath)
        await self.cf.exec_db(
            self.cf.loadfilter,
            filter=self.filter,
            filterpath=self.filterpath,
            filtername=self.filtername,
            filterstring=self.filterstring,
            filtersql=self.filtersql,
            includesample=self.args.get("includesample"),
            excludesample=self.args.get("excludesample"),
        )

    async def table_exists(self, tablename, conn=None, cursor=None):
        if conn is None:
            pass
        if cursor is None:
            from ..exceptions import SetupError

            raise SetupError()
        sql = (
            "select name from sqlite_master where "
            + 'type="table" and name="'
            + tablename
            + '"'
        )
        await cursor.execute(sql)
        row = await cursor.fetchone()
        if row == None:
            ret = False
        else:
            ret = True
        return ret


@cli_entry
def cli_report(args):
    return report(args)


@cli_func
def report(args, __name__="report"):
    from os.path import dirname
    from os.path import basename
    from os.path import join
    from asyncio import get_event_loop
    from ..util.util import is_compatible_version
    from importlib.util import spec_from_file_location
    from importlib.util import module_from_spec
    from ..exceptions import ModuleNotExist
    from ..exceptions import IncompatibleResult
    from ..util.util import quiet_print
    from ..module.local import get_local_module_info
    from ..system import consts
    from ..__main__ import handle_exception

    dbpath = args.get("dbpath")
    compatible_version, _, _ = is_compatible_version(dbpath)
    if not compatible_version:
        raise IncompatibleResult()
    report_types = args.get("reports")
    md = args.get("md")
    if md:
        consts.custom_modules_dir = md
    package = args.get("package")
    if not report_types:
        if package:
            m_info = get_local_module_info(package)
            if m_info:
                package_conf = m_info.conf
                if "run" in package_conf and "reports" in package_conf["run"]:
                    report_types = package_conf["run"]["reports"]
    output_dir = args.get("output_dir")
    if not output_dir:
        output_dir = dirname(dbpath)
    savepath = args.get("savepath")
    if not savepath:
        run_name = basename(dbpath).rstrip("sqlite").rstrip(".")
        args["savepath"] = join(output_dir, run_name)
    else:
        savedir = dirname(savepath)
        if savedir != "":
            output_dir = savedir
    module_options = {}
    module_option = args.get("module_option")
    if module_option:
        for opt_str in module_option:
            toks = opt_str.split("=")
            if len(toks) != 2:
                quiet_print(
                    "Ignoring invalid module option {opt_str}. module-option should be module_name.key=value.",
                    args,
                )
                continue
            k = toks[0]
            if k.count(".") != 1:
                quiet_print(
                    "Ignoring invalid module option {opt_str}. module-option should be module_name.key=value.",
                    args,
                )
                continue
            [module_name, key] = k.split(".")
            if module_name not in module_options:
                module_options[module_name] = {}
            v = toks[1]
            module_options[module_name][key] = v
    loop = get_event_loop()
    response = {}
    module_names = [v + "reporter" for v in report_types]
    for report_type, module_name in zip(report_types, module_names):
        try:
            module_info = get_local_module_info(module_name)
            if module_info is None:
                raise ModuleNotExist(report_type + "reporter")
            quiet_print(f"Generating {report_type} report... ", args)
            module_name = module_info.name
            spec = spec_from_file_location(  # type: ignore
                module_name, module_info.script_path  # type: ignore
            )
            if not spec:
                continue
            module = module_from_spec(spec)  # type: ignore
            if not module or not spec.loader:
                continue
            spec.loader.exec_module(module)
            args["module_name"] = module_name
            args["do_not_change_status"] = True
            if module_name in module_options:
                args["conf"] = module_options[module_name]
            reporter = module.Reporter(args)
            response_t = None
            response_t = loop.run_until_complete(reporter.run())
            output_fns = None
            if type(response_t) == list:
                output_fns = " ".join(response_t)
            else:
                output_fns = response_t
            if output_fns is not None and type(output_fns) == str:
                quiet_print(f"report created: {output_fns}", args)
            response[report_type] = response_t
        except Exception as e:
            handle_exception(e)
    return response


def cravat_report_entrypoint():
    args = get_parser_fn_report().parse_args(sys.argv[1:])
    cli_report(args)


def get_parser_fn_report():
    from argparse import ArgumentParser, SUPPRESS

    parser_ov_report = ArgumentParser(
        prog="ov report dbpath ...",
        description="Generate reports from result SQLite files",
        epilog="dbpath must be the first argument.",
    )
    parser_ov_report.add_argument("dbpath", help="Path to aggregator output")
    parser_ov_report.add_argument(
        "-t",
        dest="reports",
        nargs="+",
        default=[],
        help="report types",
    )
    parser_ov_report.add_argument(
        "-f", dest="filterpath", default=None, help="Path to filter file"
    )
    parser_ov_report.add_argument("--filter", default=None, help=SUPPRESS)
    parser_ov_report.add_argument("--filtersql", default=None, help="Filter SQL")
    parser_ov_report.add_argument(
        "-F",
        dest="filtername",
        default=None,
        help="Name of filter (stored in aggregator output)",
    )
    parser_ov_report.add_argument(
        "--filterstring", dest="filterstring", default=None, help=SUPPRESS
    )
    parser_ov_report.add_argument(
        "-s", dest="savepath", default=None, help="Path to save file"
    )
    parser_ov_report.add_argument("-c", dest="confpath", help="path to a conf file")
    parser_ov_report.add_argument(
        "--module-name", dest="module_name", default=None, help="report module name"
    )
    parser_ov_report.add_argument(
        "--nogenelevelonvariantlevel",
        dest="nogenelevelonvariantlevel",
        action="store_true",
        default=False,
        help="Use this option to prevent gene level result from being added to variant level result.",
    )
    parser_ov_report.add_argument(
        "--confs", dest="confs", default="{}", help="Configuration string"
    )
    parser_ov_report.add_argument(
        "--inputfiles",
        nargs="+",
        dest="inputfiles",
        default=None,
        help="Original input file path",
    )
    parser_ov_report.add_argument(
        "--separatesample",
        dest="separatesample",
        action="store_true",
        default=False,
        help="Write each variant-sample pair on a separate line",
    )
    parser_ov_report.add_argument(
        "-d", dest="output_dir", default=None, help="directory for output files"
    )
    parser_ov_report.add_argument(
        "--do-not-change-status",
        dest="do_not_change_status",
        action="store_true",
        default=False,
        help="Job status in status.json will not be changed",
    )
    parser_ov_report.add_argument(
        "--quiet",
        action="store_true",
        default=None,
        help="Suppress output to STDOUT",
    )
    parser_ov_report.add_argument(
        "--system-option",
        dest="system_option",
        nargs="*",
        help="System option in key=value syntax. For example, --system-option modules_dir=/home/user/oakvar/modules",
    )
    parser_ov_report.add_argument(
        "--module-option",
        dest="module_option",
        nargs="*",
        help="Module-specific option in module_name.key=value syntax. For example, --module-option vcfreporter.type=separate",
    )
    parser_ov_report.add_argument(
        "--concise-report",
        dest="concise_report",
        action="store_true",
        default=False,
        help="Generate concise report with default columns defined by annotation modules",
    )
    parser_ov_report.add_argument(
        "--includesample",
        dest="includesample",
        nargs="+",
        default=None,
        help="Sample IDs to include",
    )
    parser_ov_report.add_argument(
        "--excludesample",
        dest="excludesample",
        nargs="+",
        default=None,
        help="Sample IDs to exclude",
    )
    parser_ov_report.add_argument(
        "--package", help="Use filters and report types in a package"
    )
    parser_ov_report.add_argument(
        "--md",
        default=None,
        help="Specify the root directory of OakVar modules (annotators, etc)",
    )
    parser_ov_report.add_argument(
        "--cols",
        dest="cols",
        nargs="+",
        default=None,
        help="columns to include in reports",
    )
    parser_ov_report.add_argument(
        "--level",
        default=None,
        help="Level to make a report for. 'all' to include all levels. Other possible levels include 'variant' and 'gene'.",
    )
    parser_ov_report.set_defaults(func=cli_report)
    return parser_ov_report

CravatReport = BaseReporter
