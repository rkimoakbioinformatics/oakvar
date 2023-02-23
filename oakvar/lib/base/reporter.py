from typing import Any
from typing import Optional
from typing import Dict
from typing import List


class BaseReporter:
    def __init__(
        self,
        dbpath: str,
        report_types: List[str] = [],
        filterpath: Optional[str] = None,
        filter=None,
        filtersql: Optional[str] = None,
        filtername: Optional[str] = None,
        filterstring: Optional[str] = None,
        savepath: Optional[str] = None,
        confpath: Optional[str] = None,
        module_name: Optional[str] = None,
        nogenelevelonvariantlevel: bool = False,
        inputfiles: Optional[List[str]] = None,
        separatesample: bool = False,
        output_dir: Optional[str] = None,
        module_options: Dict = {},
        includesample: Optional[List[str]] = [],
        excludesample: Optional[List[str]] = None,
        package: Optional[str] = None,
        cols: Optional[List[str]] = None,
        level: Optional[str] = None,
        user: Optional[str] = None,
        no_summary: bool = False,
        serveradmindb=None,
        outer=None,
    ):
        from ..system.consts import DEFAULT_SERVER_DEFAULT_USERNAME

        self.dbpath = dbpath
        self.report_types = report_types
        self.filterpath = filterpath
        self.filter = filter
        self.filtersql = filtersql
        self.filtername = filtername
        self.filterstring = filterstring
        self.savepath = savepath
        self.confpath = confpath
        self.module_name = module_name
        self.nogenelevelonvariantlevel = nogenelevelonvariantlevel
        self.inputfiles = inputfiles
        self.separatesample = separatesample
        self.output_dir = output_dir
        self.module_options = module_options
        self.includesample = includesample
        self.excludesample = excludesample
        self.package = package
        self.cols = cols
        self.level = level
        if user:
            self.user = user
        else:
            self.user = DEFAULT_SERVER_DEFAULT_USERNAME
        self.no_summary = no_summary
        self.serveradmindb = serveradmindb
        self.outer = outer
        self.cf = None
        self.colinfo = {}
        self.colnos = {}
        self.var_added_cols = []
        self.summarizing_modules = []
        self.columngroups = {}
        self.column_subs = {}
        self.warning_msgs = []
        self.colnames_to_display = {}
        self.cols_to_display = {}
        self.colnos_to_display = {}
        self.display_select_columns = {}
        self.extracted_cols = {}
        self.conn = None
        self.levels_to_write = None
        self.conf = None
        self.module_conf = None
        self.output_basename = None
        self.extract_columns_multilevel = {}
        self.logger = None
        self.error_logger = None
        self.unique_excs = None
        self.mapper_name: str = ""
        self.no_log = False
        self.colcount = {}
        self.columns = {}
        self.conns = []
        self.gene_summary_datas = {}
        self.total_norows: Optional[int] = None
        self.legacy_samples_col = False
        self.modules_to_add_to_base = []
        self.check_and_setup_args()
        self._setup_logger()

    async def exec_db(self, func, *args, **kwargs):
        from ..exceptions import DatabaseConnectionError

        conn = await self.get_db_conn()
        if not conn:
            raise DatabaseConnectionError(self.module_name)
        cursor = await conn.cursor()
        try:
            ret = await func(*args, conn=conn, cursor=cursor, **kwargs)
        except:
            await cursor.close()
            raise
        await cursor.close()
        return ret

    def check_and_setup_args(self):
        import sqlite3
        import json
        from pathlib import Path
        from ..module.local import get_module_conf
        from ..exceptions import WrongInput

        if not Path(self.dbpath).exists():
            raise WrongInput(msg=self.dbpath)
        try:
            with sqlite3.connect(self.dbpath) as db:
                db.execute("select count(*) from info")
                db.execute("select count(*) from variant")
                db.execute("select count(*) from gene")
        except:
            raise WrongInput(msg=f"{self.dbpath} is not an OakVar result database")
        if not self.output_dir:
            self.output_dir = str(Path(self.dbpath).parent)
        if not self.output_dir:
            self.output_dir = str(Path(".").absolute())
        if self.savepath and Path(self.savepath).parent == "":
            self.savepath = str(Path(self.output_dir) / self.savepath)
        self.module_conf = get_module_conf(self.module_name, module_type="reporter")
        self.confs = self.module_options  # TODO: backward compatibility. Delete later.
        self.output_basename = Path(self.dbpath).name[:-7]
        if not self.inputfiles and self.dbpath:
            db = sqlite3.connect(self.dbpath)
            c = db.cursor()
            q = 'select colval from info where colkey="_input_paths"'
            c.execute(q)
            r = c.fetchone()
            if r is not None:
                self.inputfiles = []
                s = r[0]
                if " " in s:
                    s = s.replace("'", '"')
                s = s.replace("\\", "\\\\\\\\")
                s = json.loads(s)
                for k in s:
                    input_path = s[k]
                    self.inputfiles.append(input_path)
            c.close()
            db.close()
        if self.cols:
            self.extract_columns_multilevel = {}
            for level in ["variant", "gene", "sample", "mapping"]:
                self.extract_columns_multilevel[level] = self.cols
        else:
            self.extract_columns_multilevel = self.get_standardized_module_option(
                self.module_options.get("extract_columns", {})
            )
        self.add_summary = not self.no_summary

    def should_write_level(self, level):
        if self.levels_to_write is None:
            return True
        elif level in self.levels_to_write:
            return True
        else:
            return False

    async def connect_db(self, dbpath=None):
        _ = dbpath

    async def set_legacy_samples_column_flag(self):
        from sqlite3 import connect

        if not self.dbpath:
            raise
        conn = connect(self.dbpath)
        cursor = conn.cursor()
        q = f"pragma table_info(variant)"
        cursor.execute(q)
        header_cols = [row[1] for row in cursor.fetchall()]
        if "tagsampler__samples" in header_cols:
            self.legacy_samples_col = False
        elif "base__samples" in header_cols:
            self.legacy_samples_col = True
        else:
            raise
        cursor.close()
        conn.close()

    async def prep(self, user=None):
        from ..system.consts import DEFAULT_SERVER_DEFAULT_USERNAME

        if user is None:
            user = DEFAULT_SERVER_DEFAULT_USERNAME
        await self.set_dbpath()
        await self.connect_db(dbpath=self.dbpath)
        await self.set_legacy_samples_column_flag()
        await self.load_filter(user=user)

    def _setup_logger(self):
        if self.module_name is None:
            return
        import logging

        if getattr(self, "no_log", False):
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
        if not self.conn:
            self.conn = await aiosqlite.connect(self.dbpath)
            self.conns.append(self.conn)
        return self.conn

    def _log_exception(self, e, halt=True):
        if halt:
            raise e
        elif self.logger:
            self.logger.exception(e)

    def substitute_val(self, level, row):
        from json import loads
        from json import dumps

        for sub in self.column_subs.get(level, []):
            col_name = f"{sub.module}__{sub.col}"
            value = row[col_name]
            if value is None or value == "" or value == "{}":
                continue
            if (
                level == "variant"
                and sub.module == "base"
                and sub.col == "all_mappings"
            ):
                mappings = loads(value)
                for gene in mappings:
                    for i in range(len(mappings[gene])):
                        sos = mappings[gene][i][2].split(",")
                        sos = [sub.subs.get(so, so) for so in sos]
                        mappings[gene][i][2] = ",".join(sos)
                value = dumps(mappings)
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
            row[col_name] = value
        return row

    def get_extracted_header_columns(self, level):
        cols = []
        for col in self.colinfo[level]["columns"]:
            if col["col_name"] in self.colnames_to_display[level]:
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

    async def do_gene_level_summary(self, add_summary=True):
        _ = add_summary
        self.gene_summary_datas = {}
        if not self.summarizing_modules:
            return self.gene_summary_datas
        for mi, module_instance, summary_cols in self.summarizing_modules:
            gene_summary_data = await module_instance.get_gene_summary_data(self.cf)
            self.gene_summary_datas[mi.name] = [gene_summary_data, summary_cols]
            columns = self.colinfo["gene"]["columns"]
            for col in summary_cols:
                if not self.col_is_categorical(col):
                    continue
                colinfo_col = {}
                colno = None
                for i in range(len(columns)):
                    if columns[i]["col_name"] == self.get_db_col_name(mi, col):
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
                    columns[colno]["col_cats"] = cats

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
            self.mapper_name = str(r[0].split(":")[0])

    def write_log(self, msg):
        if not self.logger:
            return
        self.logger.info(msg)

    def log_run_start(self):
        from time import asctime, localtime
        import oyaml as yaml
        from ..util.run import update_status

        self.write_log("started: %s" % asctime(localtime(self.start_time)))
        if self.cf and self.cf.filter:
            self.write_log(f"filter:\n{yaml.dump(self.filter)}")
        if self.module_conf:
            status = f"started {self.module_conf['title']} ({self.module_name})"
            update_status(status, logger=self.logger, serveradmindb=self.serveradmindb)

    async def get_levels_to_run(self, tab: str) -> List[str]:
        if not self.cf:
            return []
        if tab == "all":
            levels = await self.cf.exec_db(self.cf.get_result_levels)
        else:
            levels = [tab]
        if type(levels) is not list:
            return []
        if not levels:
            return []
        return levels

    async def run(
        self,
        tab="all",
        add_summary=None,
        pagesize=None,
        page=None,
        make_filtered_table=True,
        user=None,
        dictrow=False,
    ):
        from ..exceptions import SetupError
        from time import time
        from time import asctime
        from time import localtime
        from ..util.run import update_status
        from ..system.consts import DEFAULT_SERVER_DEFAULT_USERNAME

        if user is None:
            user = DEFAULT_SERVER_DEFAULT_USERNAME
        try:
            # TODO: disabling gene level summary for now. Enable later.
            add_summary = False
            if add_summary is None:
                add_summary = self.add_summary
            self.dictrow = dictrow
            await self.prep()
            if not self.cf or not self.logger:
                raise SetupError(self.module_name)
            self.start_time = time()
            ret = None
            tab = tab or self.level or "all"
            self.log_run_start()
            if self.setup() == False:
                await self.close_db()
                raise SetupError(self.module_name)
            self.ftable_uid = await self.cf.make_ftables_and_ftable_uid(
                make_filtered_table=make_filtered_table
            )
            self.levels = await self.get_levels_to_run(tab)
            for level in self.levels:
                self.level = level
                await self.make_col_infos(add_summary=add_summary)
                await self.write_data(
                    level,
                    pagesize=pagesize,
                    page=page,
                    make_filtered_table=make_filtered_table,
                    add_summary=add_summary,
                )
            await self.close_db()
            if self.module_conf:
                status = "finished {self.module_conf['title']} ({self.module_name})"
                update_status(
                    status, logger=self.logger, serveradmindb=self.serveradmindb
                )
            end_time = time()
            if not (hasattr(self, "no_log") and self.no_log):
                self.logger.info("finished: {0}".format(asctime(localtime(end_time))))
                run_time = end_time - self.start_time
                self.logger.info("runtime: {0:0.3f}".format(run_time))
            ret = self.end()
            return ret
        except Exception as e:
            await self.close_db()
            import traceback

            traceback.print_exc()
            raise e

    async def write_data(
        self,
        level,
        add_summary=True,
        pagesize=None,
        page=None,
        make_filtered_table=True,
    ):
        from ..exceptions import SetupError

        _ = make_filtered_table
        if self.should_write_level(level) == False:
            return
        if not await self.exec_db(self.table_exists, level):
            return
        if not self.cf:
            raise SetupError(self.module_name)
        if add_summary and self.level == "gene":
            await self.do_gene_level_summary(add_summary=add_summary)
        self.write_preface(level)
        self.extracted_cols[level] = self.get_extracted_header_columns(level)
        self.write_header(level)
        self.hugo_colno = self.colnos[level].get("base__hugo", None)
        datacols = await self.cf.exec_db(self.cf.get_variant_data_cols)
        self.total_norows = await self.cf.exec_db(self.cf.get_ftable_num_rows, level=level, uid=self.ftable_uid, ftype=level)  # type: ignore
        if datacols is None or self.total_norows is None:
            return
        if level == "variant" and self.separatesample:
            self.write_variant_sample_separately = True
        else:
            self.write_variant_sample_separately = False
        datarows_iter = await self.cf.get_level_data_iterator(
            level, page=page, pagesize=pagesize, uid=self.ftable_uid
        )
        if not datarows_iter:
            return
        row_count = 0
        c = 0
        for datarow in datarows_iter:
            datarow = dict(datarow)
            c += 1
            if datarow is None:
                continue
            if level == "gene" and add_summary:
                await self.add_gene_summary_data_to_gene_level(datarow)
            if level == "variant":
                await self.add_gene_level_data_to_variant_level(datarow)
            datarow = self.substitute_val(level, datarow)
            self.stringify_all_mapping(level, datarow)
            self.escape_characters(datarow)
            self.write_row_with_samples_separate_or_not(datarow)
            row_count += 1
            if pagesize and row_count == pagesize:
                break

    def write_row_with_samples_separate_or_not(self, datarow):
        if self.legacy_samples_col:
            col_name = "base__samples"
        else:
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

    def escape_characters(self, datarow):
        for k, v in datarow.items():
            if isinstance(v, str) and "\n" in v:
                datarow[k] = v.replace("\n", "%0A")

    def stringify_all_mapping(self, level, datarow):
        from json import loads

        if hasattr(self, "keep_json_all_mapping") == True or level != "variant":
            return
        col_name = "base__all_mappings"
        all_map = loads(datarow[col_name])
        newvals = []
        for hugo in all_map:
            for maprow in all_map[hugo]:
                if len(maprow) == 5:
                    # TODO: remove this after a while. Now is 10/22/2022.
                    [protid, protchange, so, transcript, rnachange] = maprow
                    exonno = ""
                else:
                    [protid, protchange, so, transcript, rnachange, exonno] = maprow
                if protid == None:
                    protid = "(na)"
                if protchange == None:
                    protchange = "(na)"
                if rnachange == None:
                    rnachange = "(na)"
                newval = f"{transcript}:{hugo}:{protid}:{so}:{protchange}:{rnachange}:{exonno}"
                newvals.append(newval)
        newvals.sort()
        newcell = "; ".join(newvals)
        datarow[col_name] = newcell

    async def add_gene_summary_data_to_gene_level(self, datarow):
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

    async def add_gene_level_data_to_variant_level(self, datarow):
        if self.nogenelevelonvariantlevel or self.hugo_colno is None or not self.cf:
            return
        generow = await self.cf.exec_db(self.cf.get_gene_row, datarow["base__hugo"])
        if generow is None:
            datarow.update({col: None for col in self.var_added_cols})
        else:
            datarow.update({col: generow[col] for col in self.var_added_cols})

    async def get_variant_colinfo(self, add_summary=True):
        try:
            await self.prep()
            if self.setup() == False:
                await self.close_db()
                return None
            self.levels = await self.get_levels_to_run("all")
            await self.make_col_infos(add_summary=add_summary)
            return self.colinfo
        except Exception as _:
            import traceback

            traceback.print_exc()
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
        if self.dictrow:
            filtered_row = {col: row[col] for col in self.cols_to_display[self.level]}
        else:
            filtered_row = [row[col] for col in self.colnames_to_display[self.level]]
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
        if incl and col_name not in self.colnames_to_display[level]:
            self.colnames_to_display[level].append(col_name)

    async def make_sorted_column_groups(self, level, conn=Any):
        cursor = await conn.cursor()
        self.columngroups[level] = []
        sql = f"select name, displayname from {level}_annotator order by name"
        await cursor.execute(sql)
        rows = await cursor.fetchall()
        for row in rows:
            (name, displayname) = row
            if name == "base":
                self.columngroups[level].append(
                    {"name": name, "displayname": displayname, "count": 0}
                )
                break
        for row in rows:
            (name, displayname) = row
            if name in self.modules_to_add_to_base:
                self.columngroups[level].append(
                    {"name": name, "displayname": displayname, "count": 0}
                )
        for row in rows:
            (name, displayname) = row
            if name != "base" and name not in self.modules_to_add_to_base:
                self.columngroups[level].append(
                    {"name": name, "displayname": displayname, "count": 0}
                )

    async def make_coldefs(self, level, conn=Any, group_name=None):
        from ..util.inout import ColumnDefinition

        if not conn:
            return
        cursor = await conn.cursor()
        header_table = f"{level}_header"
        coldefs = []
        group_names = []
        if group_name:
            group_names.append(group_name)
            sql = f"select col_name, col_def from {header_table} where col_name like '{group_name}__%'"
        else:
            group_names = [d.get("name") for d in self.columngroups[level]]
        for group_name in group_names:
            sql = f"select col_def from {header_table} where col_name like '{group_name}__%'"
            await cursor.execute(sql)
            rows = await cursor.fetchall()
            for row in rows:
                coljson = row[0]
                # group_name = col_name.split("__")[0]
                if group_name == "base" or group_name in self.modules_to_add_to_base:
                    coldef = ColumnDefinition({})
                    coldef.from_json(coljson)
                    coldef.level = level
                    coldef = await self.gather_col_categories(level, coldef, conn)
                    coldefs.append(coldef)
            for row in rows:
                coljson = row[0]
                # group_name = col_name.split("__")[0]
                if group_name == "base" or group_name in self.modules_to_add_to_base:
                    continue
                coldef = ColumnDefinition({})
                coldef.from_json(coljson)
                coldef.level = level
                coldef = await self.gather_col_categories(level, coldef, conn)
                coldefs.append(coldef)
        return coldefs

    async def gather_col_categories(self, level, coldef, conn):
        cursor = await conn.cursor()
        if not coldef.category in ["single", "multi"] or len(coldef.categories) > 0:
            return coldef
        sql = f"select distinct {coldef.name} from {level}"
        await cursor.execute(sql)
        rs = await cursor.fetchall()
        for r in rs:
            coldef.categories.append(r[0])
        return coldef

    async def make_columns_colnos_colnamestodisplay_columngroup(self, level, coldefs):
        self.columns[level] = []
        self.colnos[level] = {}
        self.colcount[level] = 0
        for coldef in coldefs:
            self.colnos[level][coldef.name] = self.colcount[level]
            self.colcount[level] += 1
            [colgrpname, _] = self.get_group_field_names(coldef.name)
            column = coldef.get_colinfo()
            self.columns[level].append(column)
            self.add_to_colnames_to_display(level, column)
            for columngroup in self.columngroups[level]:
                if columngroup["name"] == colgrpname:
                    columngroup["count"] += 1

    async def get_gene_level_modules_to_add_to_variant_level(self, conn):
        cursor = await conn.cursor()
        q = "select name from gene_annotator"
        await cursor.execute(q)
        gene_annotators = [v[0] for v in await cursor.fetchall()]
        modules_to_add = [m for m in gene_annotators if m != "base"]
        return modules_to_add

    async def add_gene_level_displayname_to_variant_level_columngroups(
        self, module_name, coldefs, conn
    ):
        cursor = await conn.cursor()
        q = "select displayname from gene_annotator where name=?"
        await cursor.execute(q, (module_name,))
        r = await cursor.fetchone()
        displayname = r[0]
        self.columngroups["variant"].append(
            {"name": module_name, "displayname": displayname, "count": len(coldefs)}
        )

    async def add_gene_level_columns_to_variant_level(self, conn):
        if not await self.exec_db(self.table_exists, "gene"):
            return
        modules_to_add = await self.get_gene_level_modules_to_add_to_variant_level(conn)
        for module_name in modules_to_add:
            gene_coldefs = await self.make_coldefs(
                "gene", conn=conn, group_name=module_name
            )
            if not gene_coldefs:
                continue
            await self.add_gene_level_displayname_to_variant_level_columngroups(
                module_name, gene_coldefs, conn
            )
            for gene_coldef in gene_coldefs:
                self.colnos["variant"][gene_coldef.name] = self.colcount["variant"]
                self.colcount["variant"] += 1
                gene_column = gene_coldef.get_colinfo()
                self.columns["variant"].append(gene_column)
                self.add_to_colnames_to_display("variant", gene_column)
                self.var_added_cols.append(gene_coldef.name)

    async def add_gene_level_summary_columns(
        self, add_summary=True, conn=Any, cursor=Any
    ):
        from os.path import dirname
        import sys
        from ..exceptions import ModuleLoadingError
        from ..module.local import get_local_module_infos_of_type
        from ..module.local import get_local_module_info
        from ..util.util import load_class
        from ..util.inout import ColumnDefinition

        _ = conn
        if not add_summary:
            return
        q = "select name from variant_annotator"
        await cursor.execute(q)
        done_var_annotators = [v[0] for v in await cursor.fetchall()]
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
                        f"Skipping gene level summarization with {module_name} as it does not exist in the system."
                    )
                continue
            module = local_modules[module_name]
            if "can_summarize_by_gene" in module.conf:
                summarizer_module_names.append(module_name)
        local_modules[self.mapper_name] = get_local_module_info(self.mapper_name)
        summarizer_module_names = [self.mapper_name] + summarizer_module_names
        for module_name in summarizer_module_names:
            if not module_name:
                continue
            mi = local_modules[module_name]
            if not mi:
                continue
            sys.path = sys.path + [dirname(mi.script_path)]
            annot_cls = None
            if mi.name in done_var_annotators or mi.name == self.mapper_name:
                annot_cls = load_class(mi.script_path)
            if not annot_cls:
                raise ModuleLoadingError(module_name=mi.name)
            cmd = {
                "script_path": mi.script_path,
                "input_file": "__dummy__",
                "output_dir": self.output_dir,
                "serveradmindb": self.serveradmindb,
            }
            annot = annot_cls(cmd)
            cols = mi.conf["gene_summary_output_columns"]
            columngroup = {
                "name": mi.name,
                "displayname": mi.title,
                "count": len(cols),
            }
            level = "gene"
            self.columngroups[level].append(columngroup)
            for col in cols:
                coldef = ColumnDefinition(col)
                if self.should_be_in_base(mi.name):
                    coldef.name = f"base__{coldef.name}"
                else:
                    coldef.name = f"{mi.name}__{coldef.name}"
                coldef.genesummary = True
                column = coldef.get_colinfo()
                self.columns[level].append(column)
                self.add_to_colnames_to_display(level, column)
                self.colnos[level][coldef.name] = len(self.colnos[level])
            self.summarizing_modules.append([mi, annot, cols])

    def should_be_in_base(self, name):
        if "__" in name:
            name = self.get_group_name(name)
        return name in self.modules_to_add_to_base

    def get_group_field_names(self, col_name):
        return col_name.split("__")

    def get_group_name(self, col_name):
        return self.get_group_field_names(col_name)[0]

    async def make_report_sub(self, level, conn):
        from json import loads
        from types import SimpleNamespace

        if not level in ["variant", "gene"]:
            return
        reportsubtable = f"{level}_reportsub"
        if not await self.exec_db(self.table_exists, reportsubtable):
            return
        cursor = await conn.cursor()
        q = f"select * from {reportsubtable}"
        await cursor.execute(q)
        reportsub = {r[0]: loads(r[1]) for r in await cursor.fetchall()}
        self.column_subs[level] = []
        for i, column in enumerate(self.columns[level]):
            module_name, field_name = self.get_group_field_names(column["col_name"])
            if module_name == self.mapper_name:
                module_name = "base"
            if module_name in reportsub and field_name in reportsub[module_name]:
                self.column_subs[level].append(
                    SimpleNamespace(
                        module=module_name,
                        col=field_name,
                        index=i,
                        subs=reportsub[module_name][field_name],
                    )
                )
                self.columns[level][i]["reportsub"] = reportsub[module_name][field_name]

    def set_display_select_columns(self, level):
        if self.extract_columns_multilevel.get(level, {}):
            self.display_select_columns[level] = True
        else:
            self.display_select_columns[level] = False

    def set_cols_to_display(self, level):
        self.cols_to_display[level] = []
        self.colnos_to_display[level] = []
        colno = 0
        for col in self.columns[level]:
            col_name = col["col_name"]
            if col_name in self.colnames_to_display[level]:
                self.cols_to_display[level].append(col_name)
                self.colnos_to_display[level].append(colno)
            colno += 1

    async def make_col_infos(self, add_summary=True):
        prev_level = self.level
        for level in self.levels:
            self.level = level
            await self.exec_db(self.make_col_info, level, add_summary=add_summary)
        self.level = prev_level

    def add_column_number_stat_to_col_groups(self, level: str):
        last_columngroup_pos = 0
        for columngroup in self.columngroups.get(level, []):
            columngroup["start_column_number"] = last_columngroup_pos
            new_last_columngroup_pos = last_columngroup_pos + columngroup["count"]
            columngroup["end_colunm_number"] = new_last_columngroup_pos
            last_columngroup_pos = new_last_columngroup_pos

    async def make_col_info(self, level: str, add_summary=True, conn=Any, cursor=Any):
        _ = cursor
        if not level or not await self.exec_db(self.table_exists, level):
            return
        await self.exec_db(self.store_mapper)
        self.colnames_to_display[level] = []
        self.modules_to_add_to_base = [self.mapper_name, "tagsampler"]
        await self.make_sorted_column_groups(level, conn=conn)
        coldefs = await self.make_coldefs(level, conn=conn)
        if not coldefs:
            return
        await self.make_columns_colnos_colnamestodisplay_columngroup(level, coldefs)
        if not self.nogenelevelonvariantlevel and self.level == "variant":
            await self.add_gene_level_columns_to_variant_level(conn)
        if self.level == "gene" and level == "gene" and add_summary:
            await self.exec_db(self.add_gene_level_summary_columns, level)
        self.set_display_select_columns(level)
        self.set_cols_to_display(level)
        self.add_column_number_stat_to_col_groups(level)
        self.colinfo[level] = {
            "colgroups": self.columngroups[level],
            "columns": self.columns[level],
        }
        await self.make_report_sub(level, conn)

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

    async def set_dbpath(self, dbpath=None):
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
        import sqlite3

        for conn in self.conns:
            if type(conn) == sqlite3.Connection:
                conn.close()
            else:
                await conn.close()
        self.conns = []
        if self.cf is not None:
            await self.cf.close_db()
            self.cf = None

    async def load_filter(self, user=None):
        from ... import ReportFilter
        from ..system.consts import DEFAULT_SERVER_DEFAULT_USERNAME

        if user is None:
            user = DEFAULT_SERVER_DEFAULT_USERNAME
        self.cf = await ReportFilter.create(dbpath=self.dbpath, user=user, strict=False)
        await self.cf.exec_db(
            self.cf.loadfilter,
            filter=self.filter,
            filterpath=self.filterpath,
            filtername=self.filtername,
            filterstring=self.filterstring,
            filtersql=self.filtersql,
            includesample=self.includesample,
            excludesample=self.excludesample,
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


CravatReport = BaseReporter
