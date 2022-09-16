#!/usr/bin/env python3
from typing import Any
from typing import List
import sys

if sys.platform == "win32" and sys.version_info >= (3, 8):
    from asyncio import set_event_loop_policy, WindowsSelectorEventLoopPolicy # ignore: type

    set_event_loop_policy(WindowsSelectorEventLoopPolicy())

report_filter_db_name = "report_filter"
report_filter_db_dirname = "report_filters"
report_filter_registry_name = "registry"
default_user_name = "default"
default_filter_name = "default"
sample_to_filter_table_name = "fsamplegiven"
gene_to_filter_table_name = "fgenegiven"
report_filter_in_progress = "in_progress"
report_filter_ready = "ready"
report_filter_not_needed = "not_needed"
ref_col_names = {
    "variant": "base__uid",
    "gene": "base__hugo",
    "sample": "base__uid",
    "mapping": "base__uid"
}

class FilterColumn(object):

    test2sql = {
        "equals": "==",
        "lessThanEq": "<=",
        "lessThan": "<",
        "greaterThanEq": ">=",
        "greaterThan": ">",
        "hasData": "is not null",
        "noData": "is null",
        "stringContains": "like",
        "stringStarts": "like",  # Deprecated. Eliminate later
        "stringEnds": "like",  # Deprecated. Eliminate later
        "between": "between",
        "in": "in",
        "select": "in",
    }

    def __init__(self, d, parent_operator):
        self.column = d["column"]
        if self.column == "base__numsample":
            self.column = "tagsampler__numsample"
        self.test = d["test"]
        self.value = d.get("value")
        self.negate = d.get("negate", False)
        self.parent_operator = parent_operator

    def __repr__(self):
        return f"{self.column} {self.test} {self.value}"

    def get_sql(self):
        s = ""
        # TODO unify this to a single if/else on self.test
        if self.test == "multicategory":
            s = '{} like "%{}%"'.format(self.column, self.value[0])
            for v in self.value[1:]:
                s += ' or {} like "%{}%"'.format(self.column, v)
        elif self.test in ("select", "in"):
            ss = []
            for val in self.value:
                if type(val) == str:
                    val = '"{}"'.format(val)
                else:
                    val = str(val)
                ss.append(f"({self.column} = {val})")
            if ss:
                s = "(" + f" or ".join(ss) + ")"
            else:
                s = ""
        else:
            s = "{col} {opr}".format(col=self.column, opr=self.test2sql[self.test])
            sql_val = None
            if self.test == "equals":
                if type(self.value) is list:
                    v = self.value[0]
                    if type(v) is str:
                        sql_val = '"' + v + '"'
                    else:
                        sql_val = str(v)
                    for v in self.value[1:]:
                        if type(v) is str:
                            v = '"' + v + '"'
                        else:
                            v = str(v)
                        sql_val += " OR {} == {}".format(self.column, v)
                else:
                    if type(self.value) is str:
                        sql_val = '"{}"'.format(self.value)
                    else:
                        sql_val = str(self.value)
            elif self.test == "stringContains":
                sql_val = '"%{}%"'.format(self.value)
            elif self.test == "stringStarts":
                sql_val = '"{}%"'.format(self.value)
            elif self.test == "stringEnds":
                sql_val = '"%{}"'.format(self.value)
            elif self.test == "between":
                sql_val = "{} and {}".format(self.value[0], self.value[1])
            elif self.test in (
                "lessThan",
                "lessThanEq",
                "greaterThan",
                "greaterThanEq",
            ):
                sql_val = str(self.value)
            if sql_val:
                s += " (" + sql_val + ")"
        if self.negate:
            s = "not(" + s + ")"
        return s


class FilterGroup(object):
    def __init__(self, d):
        self.operator = d.get("operator", "and")
        self.negate = d.get("negate", False)
        self.rules = []
        for rule in d.get("rules", []):
            if "operator" in rule:
                self.rules.append(FilterGroup(rule))
            else:
                self.rules.append(FilterColumn(rule, self.operator))
        # Backwards compatability, may remove later
        self.rules += [FilterGroup(x) for x in d.get("groups", [])]
        self.rules += [FilterColumn(x, self.operator) for x in d.get("columns", [])]
        self.column_prefixes = {}

    def add_prefixes(self, prefixes):
        self.column_prefixes.update(prefixes)
        for rule in self.rules:
            if isinstance(rule, FilterGroup):
                rule.add_prefixes(prefixes)
            elif isinstance(rule, FilterColumn):
                prefix = self.column_prefixes.get(rule.column)
                if prefix is not None:
                    rule.column = prefix + "." + rule.column

    def get_sql(self):
        clauses = []
        for operand in self.rules:
            clause = operand.get_sql()
            if clause:
                clauses.append(clause)
        s = ""
        if clauses:
            s += "("
            sql_operator = " " + self.operator + " "
            s += sql_operator.join(clauses)
            s += ")"
            if self.negate:
                s = "not" + s
        return s


class ReportFilter:

    @classmethod
    async def create(
        cls,
        dbpath=None,
        filterpath=None,
        filtername=None,
        filterstring=None,
        filter=None,
        mode="sub",
        filtersql=None,
        includesample=None,
        excludesample=None,
        strict=True,
        user=default_user_name
    ):
        self = ReportFilter(
            dbpath=dbpath,
            filterpath=filterpath,
            filtername=filtername,
            filterstring=filterstring,
            filter=filter,
            mode=mode,
            filtersql=filtersql,
            includesample=includesample,
            excludesample=excludesample,
            strict=strict,
            user=user
        )
        await self.second_init()
        return self

    def __init__(
        self,
        dbpath=None,
        filterpath=None,
        filtername=None,
        filterstring=None,
        filter=None,
        filtersql=None,
        includesample=None,
        excludesample=None,
        mode="sub",
        strict=True,
        user=default_user_name
    ):
        from os.path import abspath
        self.mode = mode
        if self.mode == "main":
            self.stdout = True
        else:
            self.stdout = False
        if not dbpath:
            return
        self.dbpath = abspath(dbpath)
        self.conn = None
        self.filterpath = filterpath
        self.cmd = None
        self.level = None
        self.filter = filter
        self.savefiltername = None
        self.filtername = None
        self.filterstring = filterstring
        self.filtersql = filtersql
        self.includesample = includesample
        self.excludesample = excludesample
        self.strict = strict
        if filter != None:
            self.filter = filter
        else:
            if filterstring != None:
                self.filterstring = filterstring
            elif filtername != None:
                self.filtername = filtername
            elif filterpath != None:
                self.filterpath = filterpath
        self.filtertable = "filter"
        self.generows = {}
        self.table_aliases = None
        self.column_prefixes = {}
        self.conn_read = None
        self.conn_write = None
        self.uid = None
        self.user = self.escape_user(user)

    async def get_module_version_in_job(self, module_name, cursor_read=Any, cursor_write=Any):
        _ = cursor_write
        q = 'select colval from info where colkey="_annotators"'
        await cursor_read.execute(q)
        anno_vers = await cursor_read.fetchone()
        if anno_vers is None:
            return None
        version = None
        for anno_ver in anno_vers[0].split(","):
            [mname, ver] = anno_ver.split(":")
            if mname == module_name:
                version = ver
                break
        return version

    async def exec_db(self, func, *args, **kwargs):
        if not self.conn_read or not self.conn_write:
            return None
        cursor_read = await self.conn_read.cursor()
        cursor_write = await self.conn_write.cursor()
        ret = await func(*args, cursor_read=cursor_read, cursor_write=cursor_write, **kwargs)
        return ret

    async def second_init(self):
        if self.mode == "sub":
            if self.dbpath != None:
                await self.connect_dbs()
            await self.exec_db(self.loadfilter)

    #async def run_level_based_func(self, cmd):
    #    ret = {}
    #    if self.level != None:
    #        ret[self.level] = await cmd(level=self.level)
    #    else:
    #        levels = ["variant", "gene"]
    #        ret = {}
    #        for level in levels:
    #            ret_onelevel = await cmd(level=level)
    #            ret[level] = ret_onelevel
    #    return ret

    def parse_args(self, args):
        from argparse import ArgumentParser
        from os.path import abspath

        parser = ArgumentParser()
        parser.add_argument(
            "-d",
            dest="dbpath",
            required=True,
            help="Path of a result database file (.sqlite)",
        )
        parser.add_argument(
            "-f", dest="filterpath", help="Path of a filtering criteria file"
        )
        parser.add_argument(
            "-F",
            dest="filtername",
            help="Name of the filter to apply (saved in the database)",
        )
        parser.add_argument(
            "--filterstring", dest="filterstring", default=None, help="Filter in JSON"
        )
        parser.add_argument(
            "-l",
            dest="level",
            default=None,
            choices=["variant", "gene"],
            help="Analysis level to filter",
        )
        parser.add_argument(
            "-s",
            dest="savefiltername",
            help="Name to save the filter as (in the database)",
        )
        parser.add_argument(
            "--filtersql", dest="filtersql", default=None, help="Filter SQL"
        )
        parser.add_argument(
            "--includesample",
            dest="includesample",
            nargs="+",
            default=None,
            help="Sample IDs to include",
        )
        parser.add_argument(
            "--excludesample",
            dest="excludesample",
            nargs="+",
            default=None,
            help="Sample IDs to exclude",
        )
        if self.mode == "main":
            parser.add_argument(
                "command",
                choices=["uidpipe", "count", "rows", "pipe", "save", "list"],
                help="Command",
            )

        parsed_args = parser.parse_args(args)
        self.dbpath = abspath(parsed_args.dbpath)
        self.filterpath = parsed_args.filterpath
        self.level = parsed_args.level
        if self.mode == "main":
            self.cmd = parsed_args.command
        self.savefiltername = parsed_args.savefiltername
        self.filtername = parsed_args.filtername
        self.filterstring = parsed_args.filterstring
        self.filtersql = parsed_args.filtersql

    def get_report_filter_db_dir(self):
        from ..system import get_user_conf_dir
        from os.path import join
        user_conf_dir = get_user_conf_dir()
        return join(user_conf_dir, report_filter_db_dirname)

    def escape_user(self, user):
        return "".join([c if c.isalnum() else "_" for c in user])

    def get_report_filter_db_fn(self):
        report_filter_db_fn = f"report_filter.{self.user}.sqlite"
        return report_filter_db_fn

    def get_report_filter_db_path(self):
        from os.path import join
        report_filter_db_dir = self.get_report_filter_db_dir()
        report_filter_db_fn = self.get_report_filter_db_fn()
        return join(report_filter_db_dir, report_filter_db_fn)

    def get_report_filter_registry_table_name(self):
        return f"{report_filter_db_name}.{report_filter_registry_name}"

    async def create_report_filter_registry_table_if_not_exists(self, conn):
        cursor = await conn.cursor()
        q = f"create table if not exists {report_filter_db_name}.{report_filter_registry_name} ( uid int, user text, dbpath text, filterjson text, status text )"
        await cursor.execute(q)
        await conn.commit()
        await cursor.close()

    async def create_and_attach_filter_database(self, conn):
        from os.path import exists
        from os import mkdir
        if not conn:
            return
        cursor = await conn.cursor()
        report_filter_db_dir = self.get_report_filter_db_dir()
        if not exists(report_filter_db_dir):
            mkdir(report_filter_db_dir)
        report_filter_db_path = self.get_report_filter_db_path()
        q = f"attach database '{report_filter_db_path}' as {report_filter_db_name}"
        await cursor.execute(q)
        await cursor.close()
        await self.create_report_filter_registry_table_if_not_exists(conn)

    async def make_db_conns(self):
        from aiosqlite import connect
        from aiosqlite import Row
        if not self.dbpath:
            return None
        if not self.conn_read:
            self.conn_read = await connect(self.dbpath)
            self.conn_read.row_factory = Row
            await self.conn_read.execute("pragma journal_mode=wal")
            await self.create_and_attach_filter_database(self.conn_read)
        if not self.conn_write:
            self.conn_write = await connect(self.dbpath)
            await self.conn_write.execute("pragma journal_mode=wal")
            await self.create_and_attach_filter_database(self.conn_write)

    async def connect_dbs(self, dbpath=None):
        from os.path import abspath
        if dbpath != None:
            self.dbpath = abspath(dbpath)
        await self.make_db_conns()
        #if conn is not None:
        #    await conn.create_function("regexp", 2, regexp)
        #    await self.exec_db(self.set_aliases)

    #async def set_aliases(self, conn=None, cursor=None):
    #    if conn is None:
    #        pass
    #    self.table_aliases = {"variant": "v", "gene": "g"}
    #    self.column_prefixes = {}
    #    q = "pragma table_info(variant)"
    #    if cursor is not None:
    #        await cursor.execute(q)
    #        self.column_prefixes.update(
    #            {
    #                row[1]: self.table_aliases["variant"]
    #                for row in await cursor.fetchall()
    #            }
    #        )
    #        q = "pragma table_info(gene)"
    #        await cursor.execute(q)
    #        self.column_prefixes.update(
    #            {row[1]: self.table_aliases["gene"] for row in await cursor.fetchall()}
    #        )

    async def close_db(self):
        if self.conn_read:
            await self.conn_read.close()
            self.conn_read = None
        if self.conn_write:
            await self.conn_write.close()
            self.conn_write = None

    async def create_filtertable(self, cursor_read=Any, cursor_write=Any):
        if not self.conn_write:
            return
        _ = cursor_read
        sql = "create table " + self.filtertable + " (name text, criteria text)"
        await cursor_write.execute(sql)
        await self.conn_write.commit()

    async def filtertable_exists(self, cursor_read=Any, cursor_write=Any):
        _ = cursor_write
        sql = f'select * from viewersetup where datatype="filter" and name="{self.filtername}"'
        await cursor_read.execute(sql)
        row = await cursor_read.fetchone()
        if row == None:
            ret = False
        else:
            ret = True
        return ret

    async def loadfilter(
        self,
        filterpath=None,
        filtername=None,
        filterstring=None,
        filtersql=None,
        filter=None,
        includesample=None,
        excludesample=None,
        cursor_read=Any,
        cursor_write=Any,
        strict=None
    ):
        from os.path import exists
        from oyaml import safe_load
        from json import load, loads

        _ = cursor_write
        if strict:
            self.strict = strict
        if filterpath != None:
            self.filterpath = filterpath
        if filtername != None:
            self.filtername = filtername
        if filterstring != None:
            self.filterstring = filterstring
        if filtersql != None:
            self.filtersql = filtersql
        if filter != None:
            self.filter = filter
        if includesample is not None:
            self.includesample = includesample
        if excludesample is not None:
            self.excludesample = excludesample
        filter_table_present = await self.exec_db(self.filtertable_exists)
        if self.filter:
            pass
        elif self.filtersql is not None:
            if exists(self.filtersql):  # a file can be used.
                with open(self.filtersql) as f:
                    self.filtersql = "".join(f.readlines())
            self.filter = {}
        elif self.filterstring is not None:
            self.filterstring = self.filterstring.replace("'", '"')
            self.filter = loads(self.filterstring)
        elif self.filtername is not None and filter_table_present:
            await cursor_read.execute(
                "select viewersetup from viewersetup"
                + ' where datatype="filter" and name="'
                + self.filtername
                + '"'
            )
            criteria = await cursor_read.fetchone()
            if criteria != None:
                self.filter = loads(criteria[0])["filterSet"]
        elif self.filterpath is not None and exists(self.filterpath):
            with open(self.filterpath) as f:
                ftype = self.filterpath.split(".")[-1]
                if ftype in ["yml", "yaml"]:
                    self.filter = safe_load(f)
                elif ftype in ["json"]:
                    self.filter = load(f)
        if self.filter is None:
            self.filter = {}
        await self.exec_db(self.verify_filter)

    async def verify_filter(self, cursor_read=Any, cursor_write=Any):
        from oakvar.exceptions import InvalidFilter

        _ = cursor_write
        wrong_samples = await self.verify_filter_sample(cursor_read)
        wrong_colnames = await self.verify_filter_module(cursor_read)
        if self.strict and (len(wrong_samples) > 0 or len(wrong_colnames) > 0):
            raise InvalidFilter(wrong_samples, wrong_colnames)

    async def check_sample_name(self, sample_id, cursor):
        await cursor.execute(
            'select base__sample_id from sample where base__sample_id="'
            + sample_id
            + '" limit 1'
        )
        ret = await cursor.fetchone()
        return ret is not None

    async def verify_filter_sample(self, cursor):
        if not self.filter or "sample" not in self.filter:
            return []
        ft = self.filter["sample"]
        wrong_samples = set()
        if "require" in ft:
            for rq in ft["require"]:
                if await self.check_sample_name(rq, cursor) == False:
                    wrong_samples.add(rq)
        if not self.strict:
            for s in wrong_samples:
                if s in ft["require"]:
                    ft["require"].remove(s)
        if "reject" in ft:
            for rq in ft["reject"]:
                if await self.check_sample_name(rq, cursor) == False:
                    wrong_samples.add(rq)
        if not self.strict:
            for s in wrong_samples:
                if s in ft["reject"]:
                    ft["reject"].remove(s)
        return wrong_samples

    async def col_name_exists(self, colname, cursor):
        await cursor.execute(
            'select col_def from variant_header where col_name="'
            + colname
            + '" limit 1'
        )
        ret = await cursor.fetchone()
        if ret is None:
            await cursor.execute(
                'select col_def from gene_header where col_name="'
                + colname
                + '" limit 1'
            )
            ret = await cursor.fetchone()
        return ret is not None

    async def extract_filter_columns(self, rules, colset, cursor):
        rules_to_delete = []
        for rule in rules:
            if "column" in rule:
                if await self.col_name_exists(rule["column"], cursor) == False:
                    colset.add(rule["column"])
                    rules_to_delete.append(rule)
            elif "rules" in rule:
                await self.extract_filter_columns(rule["rules"], colset, cursor)
        if not self.strict:
            for rule in rules_to_delete:
                rules.remove(rule)

    async def verify_filter_module(self, cursor):
        if "variant" not in self.filter:
            return []
        wrong_modules = set()
        if "rules" in self.filter["variant"]:
            await self.extract_filter_columns(
                self.filter["variant"]["rules"], wrong_modules, cursor
            )
        return wrong_modules

    def getwhere(self, level):
        where = ""
        if self.filter and level in self.filter:
            criteria = self.filter[level]
            main_group = FilterGroup(criteria)
            main_group.add_prefixes(self.column_prefixes)
            sql = main_group.get_sql()
            if sql:
                where = "where " + sql
        return where

    def get_sample_to_filter(self):
        if not self.filter:
            return None
        req = []
        rej = []
        if "sample" in self.filter:
            if "require" in self.filter["sample"]:
                req = self.filter["sample"]["require"]
            if "reject" in self.filter["sample"]:
                rej = self.filter["sample"]["reject"]
        if self.includesample:
            req = self.includesample
        if self.excludesample:
            rej = self.excludesample
        if len(req) == 0 and len(rej) == 0:
            return None
        return [req, rej]

    def get_sample_to_filter_table_name(self, uid=None):
        if not uid:
            return None
        return f"{report_filter_db_name}.{sample_to_filter_table_name}_{uid}"

    async def remove_temporary_tables(self, uid=None, cursor_read=Any, cursor_write=Any, gene_to_filter=None, sample_to_filter=None):
        if not self.conn_write:
            return
        _ = cursor_read
        if sample_to_filter:
            table_name = self.get_sample_to_filter_table_name(uid=uid)
            if not table_name:
                return
            q = f"drop table if exists {table_name}"
            await cursor_write.execute(q)
        if gene_to_filter:
            table_name = self.get_gene_to_filter_table_name(uid=uid)
            if not table_name:
                return
            q = f"drop table if exists {table_name}"
            await cursor_write.execute(q)
        await self.conn_write.commit()

    async def make_sample_to_filter_table(self, uid=None, req=None, rej=None, cursor_read=Any, cursor_write=Any):
        if not self.conn_write:
            return
        _ = cursor_read
        if not uid or (not req and not rej):
            return
        table_name = self.get_sample_to_filter_table_name(uid=uid)
        if not table_name:
            return
        q = f"drop table if exists {table_name}"
        await cursor_write.execute(q)
        await self.conn_write.commit()
        q = f"create table {table_name} as select distinct base__uid from main.sample"
        if req:
            req_s = ", ".join([f'"{sid}"' for sid in req])
            q += f" where base__sample_id in ({req_s})"
        if rej:
            rej_s = ", ".join([f'"{sid}"' for sid in rej])
            q += f" except select base__uid from main.sample where base__sample_id in ({rej_s})"
        await cursor_write.execute(q)
        await self.conn_write.commit()

    async def get_existing_report_filter_status(self, cursor_read=Any, cursor_write=Any):
        from json import dumps
        from asyncio import sleep
        _ = cursor_write
        if not self.filter or not self.dbpath or not cursor_read:
            return None
        filterjson = dumps(self.filter)
        q = f"select uid, status from {report_filter_db_name}.{report_filter_registry_name} where user=? and dbpath=? and filterjson=?"
        while True:
            await cursor_read.execute(q, (self.user, self.dbpath, filterjson))
            ret = await cursor_read.fetchone()
            if not ret:
                return None
            [uid, status] = ret
            if status == report_filter_in_progress:
                print(f"waiting for report filter {uid} to be made...")
                await sleep(1)
                continue
            return {"uid": uid, "status": status}

    async def get_new_report_filter_uid(self, cursor_read=Any, cursor_write=Any):
        _ = cursor_write
        q = f"select uid from {report_filter_db_name}.{report_filter_registry_name}"
        await cursor_read.execute(q)
        rets = await cursor_read.fetchall()
        if len(rets) == 0:
            return 1
        prev_uid = 0
        for ret in rets:
            uid = int(ret[0])
            if uid > prev_uid + 1:
                return prev_uid + 1
            prev_uid = uid
        return prev_uid + 1

    def get_filtered_variant_table_name(self, uid):
        return f"filtered_variant_{uid}"

    async def get_filtered_hugo_list(self, cursor_read=Any, cursor_write=Any):
        _ = cursor_write
        if self.should_bypass_filter():
            table_name = "main.gene"
        else:
            table_name = self.get_ftable_name(uid=self.uid, ftype="gene")
        q = f"select base__hugo from {table_name}"
        await cursor_read.execute(q)
        rets = [v[0] for v in await cursor_read.fetchall()]
        return rets

    async def register_new_report_filter(self, uid: int, cursor_read=Any, cursor_write=Any):
        from json import dumps
        if not self.conn_write:
            return
        _ = cursor_read
        filterjson = dumps(self.filter)
        q = f"insert into {report_filter_db_name}.{report_filter_registry_name} ( uid, user, dbpath, filterjson, status) values (?, ?, ?, ?, ?)"
        await cursor_write.execute(q, (uid, self.user, self.dbpath, filterjson, report_filter_in_progress))
        await self.conn_write.commit()

    def should_bypass_filter(self):
        return not self.filter and not self.filtersql and not self.includesample and not self.excludesample

    def get_ftable_name(self, uid=None, ftype=None):
        if not uid or not ftype:
            return None
        return f"{report_filter_db_name}.f{ftype}_{uid}"

    async def drop_ftable(self, uid=None, ftype=None, cursor_read=Any, cursor_write=Any):
        if not self.conn_write or not ftype or not uid:
            return
        _ = cursor_read
        table_name = self.get_ftable_name(uid=uid, ftype=ftype)
        q = f"drop table if exists {table_name}"
        await cursor_write.execute(q)
        await self.conn_write.commit()

    def get_fvariant_sql(self, uid=None, gene_to_filter=None, sample_to_filter=None):
        q = f"select v.base__uid from main.variant as v"
        if not uid:
            return q
        if gene_to_filter:
            gene_to_filter_table_name = self.get_gene_to_filter_table_name(uid=uid)
            q += f" join {gene_to_filter_table_name} as gl on v.base__hugo=gl.base__hugo"
        if sample_to_filter:
            sample_to_filter_table_name = self.get_sample_to_filter_table_name(uid=uid)
            q += f" join {sample_to_filter_table_name} as sl on v.base__uid=sl.base__uid"
        if self.filter:
            where = self.getwhere("variant")
            if "g." in where:
                q += " join gene as g on v.base__hugo=g.base__hugo"
            q += " " + where
        elif self.filtersql:
            if "g." in self.filtersql:
                q += f" join main.gene as g on v.base__hugo=g.base__hugo"
            if "s." in self.filtersql:
                q += f" join main.sample as s on v.base__uid=s.base__uid"
            q += " where " + self.filtersql
        #q += " order by base__uid"
        return q

    async def create_fvariant(self, uid=None, cursor_read=Any, cursor_write=Any):
        if not self.conn_write:
            return
        _ = cursor_read
        table_name = self.get_ftable_name(uid=uid, ftype="variant")
        q = f"create table {table_name} ( base__uid int )"
        await cursor_write.execute(q)
        await self.conn_write.commit()

    async def create_fgene(self, uid=None, cursor_read=Any, cursor_write=Any):
        if not self.conn_write:
            return
        _ = cursor_read
        table_name = self.get_ftable_name(uid=uid, ftype="gene")
        q = f"create table {table_name} ( base__hugo int )"
        await cursor_write.execute(q)
        await self.conn_write.commit()

    async def populate_fvariant(self, uid=None, sample_to_filter=None, gene_to_filter=None, cursor_read=Any, cursor_write=Any):
        if not uid or not self.conn_write:
            return
        q = self.get_fvariant_sql(uid=uid, gene_to_filter=gene_to_filter, sample_to_filter=sample_to_filter)
        await cursor_read.execute(q)
        rets = await cursor_read.fetchall()
        table_name = self.get_ftable_name(uid=uid, ftype="variant")
        q = f"insert into {table_name} (base__uid) values (?)"
        await cursor_write.executemany(q, rets)
        await self.conn_write.commit()

    async def populate_fgene(self, uid=None, cursor_read=Any, cursor_write=Any):
        if not uid or not self.conn_write:
            return
        _ = cursor_read
        table_name = self.get_ftable_name(uid=uid, ftype="gene")
        fvariant = self.get_ftable_name(uid=uid, ftype="variant")
        q = f"create table {table_name} as select distinct v.base__hugo from main.variant as v inner join {fvariant} as vf on vf.base__uid=v.base__uid where v.base__hugo is not null"
        await cursor_write.execute(q)
        await self.conn_write.commit()

    async def make_fvariant(self, uid=None, sample_to_filter=None, gene_to_filter=None):
        if not uid:
            return
        await self.exec_db(self.drop_ftable, uid=uid, ftype="variant")
        await self.exec_db(self.create_fvariant, uid=uid)
        await self.exec_db(self.populate_fvariant, uid=uid, gene_to_filter=gene_to_filter, sample_to_filter=sample_to_filter)

    async def make_fgene(self, uid=None):
        if not uid:
            return
        await self.exec_db(self.drop_ftable, uid=uid, ftype="gene")
        #await self.exec_db(self.create_fgene, uid=uid)
        await self.exec_db(self.populate_fgene, uid=uid)

    async def set_registry_status(self, uid=None, status=None, cursor_read=Any, cursor_write=Any):
        _ = cursor_read
        if not uid or not status or not self.conn_write:
            return
        table_name = self.get_report_filter_registry_table_name()
        q = f"update {table_name} set status=?"
        await cursor_write.execute(q, (status,))
        await self.conn_write.commit()

    async def make_ftables(self):
        if self.should_bypass_filter():
            return None
        if not self.filter:
            return {"uid": None, "status": report_filter_not_needed}
        ret = await self.exec_db(self.get_existing_report_filter_status)
        if ret:
            self.uid = ret["uid"]
            return ret
        uid = await self.exec_db(self.get_new_report_filter_uid)
        self.uid = uid
        # register
        await self.exec_db(self.register_new_report_filter, uid=uid)
        # samples to filter
        sample_to_filter = self.get_sample_to_filter()
        if sample_to_filter:
            [req, rej] = sample_to_filter
            await self.exec_db(self.make_sample_to_filter_table, uid=uid, req=req, rej=rej)
        # genes to filter
        gene_to_filter = self.get_gene_to_filter()
        if gene_to_filter:
            await self.exec_db(self.make_gene_to_filter_table, uid=uid, genes=gene_to_filter)
        await self.make_fvariant(uid=uid, sample_to_filter=sample_to_filter, gene_to_filter=gene_to_filter)
        await self.make_fgene(uid=uid)
        await self.exec_db(self.remove_temporary_tables, uid=uid, gene_to_filter=gene_to_filter, sample_to_filter=sample_to_filter)
        await self.exec_db(self.set_registry_status, uid=uid, status=report_filter_ready)
        return {"uid": uid, "status": report_filter_ready}

    async def get_variant_data_cols(self, cursor_read=Any, cursor_write=Any) -> List[str]:
        _ = cursor_write
        q = f"select * from main.variant limit 1"
        await cursor_read.execute(q)
        return [v[0] for v in cursor_read.description]

    async def get_ftable_num_rows(self, level=None, uid=None, ftype=None, cursor_read=Any, cursor_write=Any):
        _ = cursor_write
        if not level or not ftype:
            return
        table_name = self.get_ftable_name(uid=uid, ftype=ftype)
        if table_name:
            q = f"select count(*) from {table_name}"
        else:
            q = f"select count(*) from main.{level}"
        await cursor_read.execute(q)
        ret = await cursor_read.fetchone()
        return ret[0]

    async def get_level_data_iterator(self, level, page=None, pagesize=None):
        if not level:
            return None
        if not self.conn_read:
            return None
        ref_col_name = ref_col_names.get(level)
        if not ref_col_name:
            return None
        cursor_read = await self.conn_read.cursor()
        filter_uid_status = await self.exec_db(self.get_existing_report_filter_status)
        q = f"select d.* from main.{level} as d"
        if filter_uid_status:
            ftable = self.get_ftable_name(uid=filter_uid_status["uid"], ftype=level)
            q += f" join {ftable} as f on d.{ref_col_name}=f.{ref_col_name}"
        if page and pagesize:
            offset = (page - 1) * pagesize + 1
            q += f" limit {pagesize} offset {offset}"
        await cursor_read.execute(q)
        rows = await cursor_read.fetchall()
        await cursor_read.close()
        return rows

    async def get_gene_row(self, hugo=None, cursor_read=Any, cursor_write=Any):
        _ = cursor_write
        q = f"select * from main.gene where base__hugo=?"
        await cursor_read.execute(q, (hugo,))
        return await cursor_read.fetchone()

    def get_gene_to_filter(self):
        if isinstance(self.filter, dict) and "genes" in self.filter:
            data = [(hugo,) for hugo in self.filter["genes"]]
        else:
            return None
        if len(data) == 0:
            return None
        return data

    def get_gene_to_filter_table_name(self, uid=None):
        if not uid:
            return None
        return f"{report_filter_db_name}.{gene_to_filter_table_name}_{uid}"

    async def make_gene_to_filter_table(self, uid=None, genes=None, cursor_read=Any, cursor_write=Any):
        if not self.conn_write:
            return
        _ = cursor_read
        if not uid or not genes:
            return
        table_name = self.get_gene_to_filter_table_name(uid=uid)
        if not table_name:
            return
        q = f"drop table if exists {table_name}"
        await cursor_write.execute(q)
        q = f"create table {table_name} (base__hugo text)"
        await cursor_write.execute(q)
        q = f"insert into {table_name} (base__hugo) values (?)"
        print(f"q={q}")
        await cursor_write.executemany(q, genes)
        await self.conn_write.commit()

    async def make_filtered_hugo_table(self, conn=None, cursor_read=Any, cursor_write=Any):
        _ = cursor_read
        bypassfilter = (
            not self.filter
            and not self.filtersql
            and not self.includesample
            and not self.excludesample
        )
        if conn and cursor_write and bypassfilter == False:
            gftable = "gene_filtered"
            q = f"drop table if exists {gftable}"
            await cursor_write.execute(q)
            q = f"create table {gftable} as select distinct v.base__hugo from variant as v inner join variant_filtered as vf on vf.base__uid=v.base__uid where v.base__hugo is not null"
            await cursor_write.execute(q)

    async def savefilter(self, name=None, cursor_read=Any, cursor_write=Any):
        from json import dumps

        if not self.conn_write:
            return
        if name == None:
            if self.savefiltername != None:
                name = self.savefiltername
            else:
                name = default_filter_name
        # Creates filter save table if not exists.
        await cursor_read.execute(
            "select name from sqlite_master where "
            + 'type="table" and name="'
            + self.filtertable
            + '"'
        )
        for ret in await cursor_read.fetchone():
            if ret == None:
                await cursor_write.execute(
                    "create table "
                    + self.filtertable
                    + " (name text unique, criteria text)"
                )
        # Saves the filter.
        filterstr = dumps(self.filter)
        sql = (
            "insert or replace into "
            + self.filtertable
            + ' values ("'
            + name
            + "\", '"
            + filterstr
            + "')"
        )
        await cursor_write.execute(sql)
        await self.conn_write.commit()

    async def listfilter(self, name=None, cursor_read=Any, cursor_write=Any):
        from json import loads
        if not self.conn_write:
            return
        ret = {}
        if name == None:
            if self.savefiltername != None:
                name = self.savefiltername
            else:
                name = default_filter_name
        # Creates filter save table if not exists.
        await cursor_read.execute(
            "select name from sqlite_master where "
            + 'type="table" and name="'
            + self.filtertable
            + '"'
        )
        for ret in await cursor_read.fetchone():
            if ret == None:
                await cursor_write.execute(
                    "create table "
                    + self.filtertable
                    + " (name text, criteria text)"
                )
                await self.conn_write.commit()
        sql = "select name, criteria from " + self.filtertable
        await cursor_read.execute(sql)
        for row in await cursor_read.fetchall():
            name = row[0]
            criteria = loads(row[1])
            ret[name] = criteria
            if self.stdout:
                print("#" + name)
                for level in criteria:
                    print("    " + level + ":")
                    for column in criteria[level]:
                        print("        " + column + ": " + criteria[level][column])
        return ret

    def addvariantfilter(self, column, condition):
        self.addfilter(column, condition, "variant")

    def addgenefilter(self, column, condition):
        self.addfilter(column, condition, "gene")

    def addfilter(self, column, condition, level="variant"):
        if self.filter == None:
            self.filter = {}
        if level not in self.filter:
            self.filter[level] = {}
        self.filter[level][column] = condition

    def removevariantfilter(self, column):
        self.removefilter(column, "variant")

    def removegenefilter(self, column):
        self.removefilter(column, "gene")

    def removefilter(self, column, level="variant"):
        if self.filter == None:
            return
        if level in self.filter and column in self.filter[level]:
            del self.filter[level][column]

    async def table_exists(self, table, cursor_read=Any, cursor_write=Any):
        _ = cursor_write
        sql = (
            'select name from sqlite_master where type="table" and '
            + 'name="'
            + table
            + '"'
        )
        await cursor_read.execute(sql)
        row = await cursor_read.fetchone()
        if row:
            return True
        else:
            return False

    async def get_variant_data_for_cols(self, cols, cursor_read=Any, cursor_write=Any):
        _ = cursor_write
        bypassfilter = (
            not self.filter
            and not self.filtersql
            and not self.includesample
            and not self.excludesample
        )
        if cols[0] == "base__uid":
            cols[0] = "v.base__uid"
        q = "select {},base__hugo from variant as v".format(",".join(cols))
        if bypassfilter == False:
            q += " inner join variant_filtered as f on v.base__uid=f.base__uid"
        if cols[0] == "v.base__uid":
            cols[0] = "base__uid"
        await cursor_read.execute(q)
        rows = await cursor_read.fetchall()
        return rows

    async def get_variant_data_for_hugo(self, hugo, cols, cursor_read=Any, cursor_write=Any):
        _ = cursor_write
        bypassfilter = (
            not self.filter
            and not self.filtersql
            and not self.includesample
            and not self.excludesample
        )
        if cols[0] == "base__uid":
            cols[0] = "v.base__uid"
        q = "select {} from variant as v".format(",".join(cols))
        if bypassfilter == False:
            q += ' inner join variant_filtered as f on v.base__uid=f.base__uid and v.base__hugo="{}"'.format(
                hugo
            )
        if cols[0] == "v.base__uid":
            cols[0] = "base__uid"
        await cursor_read.execute(q)
        rows = await cursor_read.fetchall()
        return rows

    async def get_result_levels(self, cursor_read=Any, cursor_write=Any) -> List[str]:
        _ = cursor_write
        table_names = []
        q = 'select name from sqlite_master where type="table" and ' + 'name like "%_header"'
        await cursor_read.execute(q)
        for row in await cursor_read.fetchall():
            table_names.append(row[0].replace("_header", ""))
        return table_names

    async def get_stored_output_columns(self, module_name, cursor_read=Any, cursor_write=Any):
        from json import loads
        _ = cursor_write
        output_columns = []
        q = f'select col_def from variant_header where col_name like "{module_name}\\_\\_%" escape "\\"'
        await cursor_read.execute(q)
        for row in await cursor_read.fetchall():
            d = loads(row[0])
            d["name"] = d["name"].replace(f"{module_name}__", "")
            output_columns.append(d)
        return output_columns


def regexp(y, x, search=None):
    import re

    if search is None:
        search = re.search
    if x is None:
        return 0
    return 1 if search(y, x) else 0


def main():
    #import sys
    from asyncio import new_event_loop

    loop = new_event_loop()
    #cv = loop.run_until_complete(ReportFilter.create(mode="main"))
    #loop.run_until_complete(cv.run(args=sys.argv[1:]))
    loop.close()
