from typing import List
from typing import Tuple
from typing import Optional
from typing import Union
from pathlib import Path
import sqlite3
import duckdb

REPORT_FILTER_DB_NAME = "report_filter"
REPORT_FILTER_DB_DIRNAME = "report_filters"
REPORT_FILTER_REGISTRY_NAME = "registry"
SAMPLE_TO_FILTER_TABLE_NAME = "fsamplegiven"
GENE_TO_FILTER_TABLE_NAME = "fgenegiven"
REPORT_FILTER_IN_PROGRESS = "in_progress"
REPORT_FILTER_READY = "ready"
REPORT_FILTER_NOT_NEEDED = "not_needed"
REF_COL_NAMES = {
    "variant": "base__uid",
    "gene": "base__hugo",
    "sample": "base__uid",
    "mapping": "base__uid",
}
level_prefixes = {"variant": "v", "gene": "g"}


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
        self.level = d.get("level")

    def __repr__(self):
        return f"{self.column} {self.test} {self.value}"

    def get_sql(self):
        s = ""
        col_name = f"{level_prefixes[self.level]}.{self.column}"
        if self.test == "multicategory":
            s = '{} like "%{}%"'.format(col_name, self.value[0])
            for v in self.value[1:]:
                s += ' or {} like "%{}%"'.format(col_name, v)
        elif self.test in ("select", "in"):
            ss = []
            for val in self.value:
                if type(val) == str:
                    val = '"{}"'.format(val)
                else:
                    val = str(val)
                ss.append(f"({col_name} = {val})")
            if ss:
                s = "(" + " or ".join(ss) + ")"
            else:
                s = ""
        else:
            s = "{col} {opr}".format(col=col_name, opr=self.test2sql[self.test])
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
                        sql_val += " OR {} == {}".format(col_name, v)
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


class DbFilter:
    from ..system.consts import DEFAULT_SERVER_DEFAULT_USERNAME

    @classmethod
    def create(
        cls,
        dbpath: Union[Path, str] = "",
        filter_path: Optional[str] = None,
        filterstring: Optional[str] = None,
        filter=None,
        mode="sub",
        filtersql=None,
        includesample=None,
        excludesample=None,
        strict=True,
        user: str = DEFAULT_SERVER_DEFAULT_USERNAME,
        uid=None,
        use_duckdb: bool = False,
    ):
        self = DbFilter(
            dbpath=dbpath,
            filterpath=filter_path,
            filterstring=filterstring,
            filter=filter,
            mode=mode,
            filtersql=filtersql,
            includesample=includesample,
            excludesample=excludesample,
            strict=strict,
            user=user,
            uid=uid,
            use_duckdb=use_duckdb,
        )
        self.second_init()
        return self

    def __init__(
        self,
        dbpath: Union[Path, str] = "",
        filterpath=None,
        filterstring=None,
        filter=None,
        filtersql=None,
        includesample=None,
        excludesample=None,
        mode="sub",
        strict=True,
        user=DEFAULT_SERVER_DEFAULT_USERNAME,
        uid=None,
        use_duckdb: bool = False,
    ):
        from pathlib import Path
        from ..exceptions import ArgumentError

        self.mode = mode
        if self.mode == "main":
            self.stdout = True
        else:
            self.stdout = False
        if isinstance(dbpath, str):
            dbpath = Path(dbpath)
        if not dbpath.name:
            raise ArgumentError(msg="dbpath should be given.")
        self.dbpath: Path = dbpath.resolve()
        self.filterpath: Optional[str] = filterpath
        self.level = None
        self.filter = filter
        self.filtername = None
        self.filterstring = filterstring
        self.filtersql = filtersql
        self.includesample = includesample
        self.excludesample = excludesample
        self.strict = strict
        if filter is not None:
            self.filter = filter
        else:
            if filterstring is not None:
                self.filterstring = filterstring
            elif filterpath is not None:
                self.filterpath = filterpath
        self.uid = uid
        self.user = self.escape_user(user)
        self.use_duckdb = use_duckdb
        if not use_duckdb:
            if self.dbpath.name.endswith(".duckdb"):
                self.use_duckdb = True
        self.conn_read: Optional[
            Union[sqlite3.Connection, duckdb.DuckDBPyConnection]
        ] = None
        self.conn_write: Optional[
            Union[sqlite3.Connection, duckdb.DuckDBPyConnection]
        ] = None
        if self.mode == "sub":
            self.loadfilter()

    def second_init(self):
        if self.mode == "sub":
            self.loadfilter()

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
        self.filtername = parsed_args.filtername
        self.filterstring = parsed_args.filterstring
        self.filtersql = parsed_args.filtersql

    def get_report_filter_db_dir(self) -> Path:
        from ..system import get_conf_dir
        from ..system import get_system_conf_path
        from ..exceptions import SystemMissingException

        conf_dir = get_conf_dir()
        if not conf_dir:
            sys_conf_path = get_system_conf_path()
            raise SystemMissingException(
                "conf_dir does not exist "
                + f"in the system configuration file at {sys_conf_path}. "
                + "Please consider running `ov system setup`."
            )
        return conf_dir / REPORT_FILTER_DB_DIRNAME

    def escape_user(self, user):
        return "".join([c if c.isalnum() else "_" for c in user])

    def get_report_filter_db_fn(self):
        from ..consts import RESULT_DB_SUFFIX_DUCKDB
        from ..consts import RESULT_DB_SUFFIX_SQLITE

        if self.use_duckdb:
            report_filter_db_fn = f"report_filter.{self.user}{RESULT_DB_SUFFIX_DUCKDB}"
        else:
            report_filter_db_fn = f"report_filter.{self.user}{RESULT_DB_SUFFIX_SQLITE}"
        return report_filter_db_fn

    def get_report_filter_db_path(self) -> Path:
        report_filter_db_dir = self.get_report_filter_db_dir()
        report_filter_db_fn = self.get_report_filter_db_fn()
        return report_filter_db_dir / report_filter_db_fn

    def get_registry_table_name(self):
        return f"{REPORT_FILTER_DB_NAME}.{REPORT_FILTER_REGISTRY_NAME}"

    def create_report_filter_registry_table_if_not_exists(self, conn):
        cursor = conn.cursor()
        q = (
            f"create table if not exists {REPORT_FILTER_DB_NAME}."
            + f"{REPORT_FILTER_REGISTRY_NAME} ( uid int primary key, "
            + "user text, dbpath text, filterjson text, status text )"
        )
        cursor.execute(q)
        conn.commit()
        cursor.close()

    def create_and_attach_filter_database(self, conn):
        from os import mkdir

        if not conn:
            return
        cursor = conn.cursor()
        report_filter_db_dir = self.get_report_filter_db_dir()
        if not report_filter_db_dir.exists():
            mkdir(report_filter_db_dir)
        report_filter_db_path = self.get_report_filter_db_path()
        q = f"attach database '{report_filter_db_path}' as {REPORT_FILTER_DB_NAME}"
        cursor.execute(q)
        cursor.close()
        self.create_report_filter_registry_table_if_not_exists(conn)

    def get_db_conns(
        self,
    ) -> Union[
        Tuple[sqlite3.Connection, sqlite3.Connection],
        Tuple[duckdb.DuckDBPyConnection, duckdb.DuckDBPyConnection],
    ]:
        if isinstance(self.conn_read, sqlite3.Connection) and isinstance(
            self.conn_write, sqlite3.Connection
        ):
            return self.conn_read, self.conn_write
        if isinstance(self.conn_read, duckdb.DuckDBPyConnection) and isinstance(
            self.conn_write, duckdb.DuckDBPyConnection
        ):
            return self.conn_read, self.conn_write
        if self.use_duckdb:
            self.conn_read = duckdb.connect(str(self.dbpath))
            self.create_and_attach_filter_database(self.conn_read)
            self.conn_write = self.conn_read
            return self.conn_read, self.conn_write
        else:
            self.conn_read = sqlite3.connect(self.dbpath)
            self.conn_read.row_factory = sqlite3.Row
            self.conn_read.execute("pragma journal_mode=wal")
            self.create_and_attach_filter_database(self.conn_read)
            self.conn_write = sqlite3.connect(self.dbpath)
            self.conn_write.execute("pragma journal_mode=wal")
            self.create_and_attach_filter_database(self.conn_write)
            return self.conn_read, self.conn_write

    def close_db(self):
        return

    def loadfilter(
        self,
        filterpath=None,
        filtername=None,
        filterstring=None,
        filtersql=None,
        filter=None,
        includesample=None,
        excludesample=None,
        strict=None,
    ):
        from os.path import exists
        from oyaml import safe_load
        from json import load, loads

        if strict:
            self.strict = strict
        if filterpath is not None:
            self.filterpath = filterpath
        if filtername is not None:
            self.filtername = filtername
        if filterstring is not None:
            self.filterstring = filterstring
        if filtersql is not None:
            self.filtersql = filtersql
        if filter is not None:
            self.filter = filter
        if includesample is not None:
            self.includesample = includesample
        if excludesample is not None:
            self.excludesample = excludesample
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
        elif self.filterpath is not None and exists(self.filterpath):
            with open(self.filterpath) as f:
                ftype = self.filterpath.split(".")[-1]
                if ftype in ["yml", "yaml"]:
                    self.filter = safe_load(f)
                elif ftype in ["json"]:
                    self.filter = load(f)
        if self.filter is None:
            self.filter = {}
        self.verify_filter()

    def verify_filter(self):
        from ..exceptions import InvalidFilter

        conn_read, conn_write = self.get_db_conns()
        _ = conn_write
        cursor_read = conn_read.cursor()
        wrong_samples = self.verify_filter_sample(cursor_read)
        wrong_colnames = self.verify_filter_module(cursor_read)
        if self.strict and (len(wrong_samples) > 0 or len(wrong_colnames) > 0):
            raise InvalidFilter(wrong_samples, wrong_colnames)

    def check_sample_name(self, sample_id, cursor):
        cursor.execute(
            'select base__sample_id from sample where base__sample_id="'
            + sample_id
            + '" limit 1'
        )
        ret = cursor.fetchone()
        return ret is not None

    def verify_filter_sample(self, cursor):
        if not self.filter or "sample" not in self.filter:
            return []
        ft = self.filter["sample"]
        wrong_samples = set()
        if "require" in ft:
            for rq in ft["require"]:
                if self.check_sample_name(rq, cursor) is False:
                    wrong_samples.add(rq)
        if not self.strict:
            for s in wrong_samples:
                if s in ft["require"]:
                    ft["require"].remove(s)
        if "reject" in ft:
            for rq in ft["reject"]:
                if self.check_sample_name(rq, cursor) is False:
                    wrong_samples.add(rq)
        if not self.strict:
            for s in wrong_samples:
                if s in ft["reject"]:
                    ft["reject"].remove(s)
        return wrong_samples

    def col_name_exists(self, colname, cursor):
        cursor.execute(
            'select col_def from variant_header where col_name="'
            + colname
            + '" limit 1'
        )
        ret = cursor.fetchone()
        if ret is None:
            cursor.execute(
                'select col_def from gene_header where col_name="'
                + colname
                + '" limit 1'
            )
            ret = cursor.fetchone()
        return ret is not None

    def extract_filter_columns(self, rules, colset, cursor):
        rules_to_delete = []
        for rule in rules:
            if "column" in rule:
                if self.col_name_exists(rule["column"], cursor) is False:
                    colset.add(rule["column"])
                    rules_to_delete.append(rule)
            elif "rules" in rule:
                self.extract_filter_columns(rule["rules"], colset, cursor)
        if not self.strict:
            for rule in rules_to_delete:
                rules.remove(rule)

    def verify_filter_module(self, cursor):
        if not self.filter or "variant" not in self.filter:
            return []
        wrong_modules = set()
        if "rules" in self.filter["variant"]:
            self.extract_filter_columns(
                self.filter["variant"]["rules"], wrong_modules, cursor
            )
        return wrong_modules

    def getwhere(self, level):
        where = ""
        if self.filter and level in self.filter:
            criteria = self.filter[level]
            main_group = FilterGroup(criteria)
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
        if uid is None:
            return None
        return f"{REPORT_FILTER_DB_NAME}.{SAMPLE_TO_FILTER_TABLE_NAME}_{uid}"

    def remove_temporary_tables(
        self,
        uid=None,
        gene_to_filter=None,
        sample_to_filter=None,
    ):
        conn_read, conn_write = self.get_db_conns()
        _ = conn_read
        cursor_write = conn_write.cursor()
        if sample_to_filter:
            table_name = self.get_sample_to_filter_table_name(uid=uid)
            if not table_name:
                return
            q = f"drop table if exists {table_name}"
            cursor_write.execute(q)
        if gene_to_filter:
            table_name = self.get_gene_to_filter_table_name(uid=uid)
            if not table_name:
                return
            q = f"drop table if exists {table_name}"
            cursor_write.execute(q)
        conn_write.commit()

    def make_sample_to_filter_table(self, uid=None, req=None, rej=None):
        conn_read, conn_write = self.get_db_conns()
        cursor_write = conn_write.cursor()
        _ = conn_read
        if uid is None or (not req and not rej):
            return
        table_name = self.get_sample_to_filter_table_name(uid=uid)
        if not table_name:
            return
        q = f"drop table if exists {table_name}"
        cursor_write.execute(q)
        conn_write.commit()
        q = f"create table {table_name} as select distinct base__uid from main.sample"
        if req:
            req_s = ", ".join([f'"{sid}"' for sid in req])
            q += f" where base__sample_id in ({req_s})"
        if rej:
            rej_s = ", ".join([f'"{sid}"' for sid in rej])
            q += (
                " except select base__uid from main.sample where "
                + f"base__sample_id in ({rej_s})"
            )
        cursor_write.execute(q)
        conn_write.commit()

    def get_existing_report_filter_status(self):
        from json import dumps

        conn_read, conn_write = self.get_db_conns()
        _ = conn_write
        cursor_read = conn_read.cursor()
        if not self.filter:
            return None
        filterjson = dumps(self.filter)
        tablename = self.get_registry_table_name()
        q = (
            f"select uid, status from {tablename} where "
            + "user=? and dbpath=? and filterjson=?"
        )
        cursor_read.execute(q, (self.user, self.dbpath, filterjson))
        ret = cursor_read.fetchone()
        if not ret:
            return None
        [uid, status] = ret
        return {"uid": uid, "status": status}

    def get_report_filter_count(
        self, cursor: Union[sqlite3.Cursor, duckdb.DuckDBPyConnection]
    ):
        tablename = self.get_registry_table_name()
        q = f"select count(*) from {tablename}"
        cursor.execute(q)
        ret = cursor.fetchall()
        count = ret[0][0]
        return count

    def get_max_report_filter_uid(
        self, cursor: Union[sqlite3.Cursor, duckdb.DuckDBPyConnection], where=None
    ):
        tablename = self.get_registry_table_name()
        q = f"select max(uid) from {tablename}"
        if where:
            q += f" where {where}"
        cursor.execute(q)
        ret = cursor.fetchall()
        n = ret[0][0]
        return n

    def get_min_report_filter_uid(
        self, cursor: Union[sqlite3.Cursor, duckdb.DuckDBPyConnection], where=None
    ):
        tablename = self.get_registry_table_name()
        q = f"select min(uid) from {tablename}"
        if where:
            q += f" where {where}"
        cursor.execute(q)
        ret = cursor.fetchall()
        n = ret[0][0]
        return n

    def get_report_filter_string(self, uid=None) -> Optional[str]:
        if uid is None:
            return None
        conn_read, conn_write = self.get_db_conns()
        _ = conn_write
        cursor_read = conn_read.cursor()
        tablename = self.get_registry_table_name()
        q = f"select filterjson from {tablename} where uid=?"
        cursor_read.execute(q, (uid,))
        ret = cursor_read.fetchall()
        if ret:
            return ret[0][0]
        else:
            return

    def get_new_report_filter_uid(self):
        from ..system import get_sys_conf_int_value
        from ..system.consts import report_filter_max_num_cache_per_user_key
        from ..system.consts import DEFAULT_REPORT_FILTER_MAX_NUM_CACHE_PER_USER

        conn_read, conn_write = self.get_db_conns()
        _ = conn_write
        cursor_read = conn_read.cursor()
        delete_uids = []
        report_filter_max_num_cache_per_user = get_sys_conf_int_value(
            report_filter_max_num_cache_per_user_key
        )
        if not report_filter_max_num_cache_per_user:
            report_filter_max_num_cache_per_user = (
                DEFAULT_REPORT_FILTER_MAX_NUM_CACHE_PER_USER
            )
        count = self.get_report_filter_count(cursor=cursor_read)
        max_uid = self.get_max_report_filter_uid(cursor=cursor_read)
        min_uid = self.get_min_report_filter_uid(cursor=cursor_read)
        if count < report_filter_max_num_cache_per_user:
            uid = count
        else:
            if max_uid < report_filter_max_num_cache_per_user * 2 - 1:
                delete_uids = [min_uid]
                uid = max_uid + 1
            else:
                delete_uids = [
                    v
                    for v in range(
                        report_filter_max_num_cache_per_user * 2, max_uid + 1
                    )
                ]
                min_over_uid = self.get_min_report_filter_uid(
                    cursor=cursor_read,
                    where=f"uid >= {report_filter_max_num_cache_per_user}",
                )
                delete_uids.append(min_over_uid)
                uid = min_over_uid - report_filter_max_num_cache_per_user
        return [uid, delete_uids]

    def get_filtered_hugo_list(self):
        conn_read, conn_write = self.get_db_conns()
        _ = conn_write
        cursor_read = conn_read.cursor()
        if self.should_bypass_filter():
            table_name = "main.gene"
        else:
            table_name = self.get_ftable_name(uid=self.uid, ftype="gene")
        q = f"select base__hugo from {table_name}"
        cursor_read.execute(q)
        rets = [v[0] for v in cursor_read.fetchall()]
        return rets

    def register_new_report_filter(self, uid: int):
        from json import dumps

        conn_read, conn_write = self.get_db_conns()
        _ = conn_read
        cursor_write = conn_write.cursor()
        filterjson = dumps(self.filter)
        q = (
            f"insert or replace into {REPORT_FILTER_DB_NAME}."
            + f"{REPORT_FILTER_REGISTRY_NAME} ( uid, user, dbpath, "
            + "filterjson, status) values (?, ?, ?, ?, ?)"
        )
        cursor_write.execute(
            q, (uid, self.user, self.dbpath, filterjson, REPORT_FILTER_IN_PROGRESS)
        )
        conn_write.commit()

    def should_bypass_filter(self):
        return (
            not self.filter
            and not self.filtersql
            and not self.includesample
            and not self.excludesample
        )

    def get_ftable_name(self, uid=None, ftype=None):
        if uid is None or not ftype:
            return None
        return f"{REPORT_FILTER_DB_NAME}.f{ftype}_{uid}"

    def get_fvariant_sql(self, uid=None, gene_to_filter=None, sample_to_filter=None):
        q = "select v.base__uid from main.variant as v"
        if uid is None:
            return q
        if gene_to_filter:
            gene_to_filter_table_name = self.get_gene_to_filter_table_name(uid=uid)
            q += (
                f" join {gene_to_filter_table_name} as gl on v.base__hugo=gl.base__hugo"
            )
        if sample_to_filter:
            sample_to_filter_table_name = self.get_sample_to_filter_table_name(uid=uid)
            q += (
                f" join {sample_to_filter_table_name} as sl on v.base__uid=sl.base__uid"
            )
        if self.filter:
            where = self.getwhere("variant")
            if "g." in where:
                q += " join gene as g on v.base__hugo=g.base__hugo"
            q += " " + where
        elif self.filtersql:
            if "g." in self.filtersql:
                q += " join main.gene as g on v.base__hugo=g.base__hugo"
            if "s." in self.filtersql:
                q += " join main.sample as s on v.base__uid=s.base__uid"
            q += " where " + self.filtersql
        # q += " order by base__uid"
        return q

    def populate_fvariant(
        self,
        uid=None,
        sample_to_filter=None,
        gene_to_filter=None,
    ):
        conn_read, conn_write = self.get_db_conns()
        _ = conn_read
        cursor_write = conn_write.cursor()
        if uid is None:
            return
        table_name = self.get_ftable_name(uid=uid, ftype="variant")
        q = self.get_fvariant_sql(
            uid=uid, gene_to_filter=gene_to_filter, sample_to_filter=sample_to_filter
        )
        q = f"create table {table_name} as {q}"
        cursor_write.execute(q)
        conn_write.commit()

    def populate_fgene(self, uid=None):
        if uid is None:
            return
        conn_read, conn_write = self.get_db_conns()
        _ = conn_read
        cursor_write = conn_write.cursor()
        table_name = self.get_ftable_name(uid=uid, ftype="gene")
        fvariant = self.get_ftable_name(uid=uid, ftype="variant")
        q = (
            f"create table {table_name} as select distinct v.base__hugo "
            + f"from main.variant as v inner join {fvariant} as vf on "
            + "vf.base__uid=v.base__uid where v.base__hugo is not null"
        )
        cursor_write.execute(q)
        conn_write.commit()

    def make_fvariant(self, uid=None, sample_to_filter=None, gene_to_filter=None):
        if uid is None:
            return
        self.drop_ftable(uid=uid, ftype="variant")
        self.populate_fvariant(
            uid=uid,
            gene_to_filter=gene_to_filter,
            sample_to_filter=sample_to_filter,
        )

    def make_fgene(self, uid=None):
        if uid is None:
            return
        self.drop_ftable(uid=uid, ftype="gene")
        self.populate_fgene(uid=uid)

    def set_registry_status(self, uid=None, status=None):
        conn_read, conn_write = self.get_db_conns()
        _ = conn_read
        cursor_write = conn_write.cursor()
        if uid is None or not status:
            return
        table_name = self.get_registry_table_name()
        q = f"update {table_name} set status=?"
        cursor_write.execute(q, (status,))
        conn_write.commit()

    def remove_ftables(self, uids):
        conn_read, conn_write = self.get_db_conns()
        _ = conn_read
        cursor_write = conn_write.cursor()
        if type(uids) == int:
            uids = [uids]
        tablename = self.get_registry_table_name()
        for uid in uids:
            for level in ["variant", "gene"]:
                q = f"drop table if exists f{level}_{uid}"
                cursor_write.execute(q)
            q = f"delete from {tablename} where uid=?"
            cursor_write.execute(q, (uid,))
        conn_write.commit()
        conn_read.commit()

    def drop_ftable(self, uid=None, ftype=None):
        conn_read, conn_write = self.get_db_conns()
        if not ftype or uid is None:
            return
        _ = conn_read
        cursor_write = conn_write.cursor()
        table_name = self.get_ftable_name(uid=uid, ftype=ftype)
        q = f"drop table if exists {table_name}"
        cursor_write.execute(q)
        conn_write.commit()

    def make_ftables(self):
        if self.should_bypass_filter():
            return None
        if not self.filter:
            return {"uid": None, "status": REPORT_FILTER_NOT_NEEDED}
        ret = self.get_existing_report_filter_status()
        if ret:
            self.uid = ret["uid"]
            return ret
        ret = self.get_new_report_filter_uid()
        if not ret:
            return None
        [uid, delete_uids] = ret
        if delete_uids:
            for delete_uid in delete_uids:
                self.remove_ftables(delete_uid)
        self.uid = uid
        try:
            # register
            self.register_new_report_filter(uid=uid)
            # samples to filter
            sample_to_filter = self.get_sample_to_filter()
            if sample_to_filter:
                [req, rej] = sample_to_filter
                self.make_sample_to_filter_table(uid=uid, req=req, rej=rej)
            # genes to filter
            gene_to_filter = self.get_gene_to_filter()
            if gene_to_filter:
                self.make_gene_to_filter_table(uid=uid, genes=gene_to_filter)
            self.make_fvariant(
                uid=uid,
                sample_to_filter=sample_to_filter,
                gene_to_filter=gene_to_filter,
            )
            self.make_fgene(uid=uid)
            self.remove_temporary_tables(
                uid=uid,
                gene_to_filter=gene_to_filter,
                sample_to_filter=sample_to_filter,
            )
            self.set_registry_status(uid=uid, status=REPORT_FILTER_READY)
            return {"uid": uid, "status": REPORT_FILTER_READY}
        except Exception as e:
            self.remove_ftables(uid)
            raise e

    def get_variant_data_cols(self) -> List[str]:
        conn_read, conn_write = self.get_db_conns()
        _ = conn_write
        if isinstance(conn_read, sqlite3.Connection):
            cursor_read = conn_read.cursor()
            q = "select * from main.variant limit 1"
            cursor_read.execute(q)
            return [v[0] for v in cursor_read.description]
        elif isinstance(conn_read, duckdb.DuckDBPyConnection):
            q = "describe variant"
            conn_read.execute(q)
            column_names = conn_read.pl()["column_name"]
            return list(column_names)
        else:
            raise

    def get_ftable_num_rows(self, level=None, uid=None, ftype=None):
        conn_read, conn_write = self.get_db_conns()
        if not level or not ftype:
            return
        table_name = self.get_ftable_name(uid=uid, ftype=ftype)
        if table_name:
            q = f"select count(*) from {table_name}"
        else:
            q = f"select count(*) from main.{level}"
        cursor_read = conn_read.cursor()
        _ = conn_write
        cursor_read.execute(q)
        ret = cursor_read.fetchall()
        return ret[0][0]

    def get_level_data_iterator(
        self, level, page=None, pagesize=None, uid=None, var_added_cols=[], cursor=None
    ):
        if not level:
            return None
        if not cursor:
            return None
        ref_col_name = REF_COL_NAMES.get(level)
        if not ref_col_name:
            return None
        if uid is not None:
            filter_uid_status = self.get_existing_report_filter_status()
            if filter_uid_status:
                uid = filter_uid_status.get("uid")
        if level == "variant" and var_added_cols:
            gene_level_cols = [f"g.{col}" for col in var_added_cols]
            q = f"select d.*, {','.join(gene_level_cols)} from main.{level} as d left join main.gene as g on d.base__hugo=g.base__hugo"
        else:
            q = f"select d.* from main.{level} as d"
        if uid is not None:
            ftable = self.get_ftable_name(uid=uid, ftype=level)
            q += f" join {ftable} as f on d.{ref_col_name}=f.{ref_col_name}"
        if page and pagesize:
            offset = (page - 1) * pagesize
            q += f" limit {pagesize} offset {offset}"
        cursor.execute(q)

    def get_gene_row(self, hugo=None):
        conn_read, conn_write = self.get_db_conns()
        _ = conn_write
        cursor_read = conn_read.cursor()
        q = "select * from main.gene where base__hugo=?"
        cursor_read.execute(q, (hugo,))
        return cursor_read.fetchone()

    def get_gene_to_filter(self):
        if isinstance(self.filter, dict) and "genes" in self.filter:
            data = [(hugo,) for hugo in self.filter["genes"]]
        else:
            return None
        if len(data) == 0:
            return None
        return data

    def get_gene_to_filter_table_name(self, uid=None):
        if uid is None:
            return None
        return f"{REPORT_FILTER_DB_NAME}.{GENE_TO_FILTER_TABLE_NAME}_{uid}"

    def make_gene_to_filter_table(self, uid=None, genes=None):
        if uid is None or not genes:
            return
        if not self.dbpath:
            return
        conn_read, conn_write = self.get_db_conns()
        _ = conn_read
        cursor_write = conn_write.cursor()
        q = (
            f"create table if not exists {REPORT_FILTER_DB_NAME}."
            + f"{REPORT_FILTER_REGISTRY_NAME} ( uid int primary key, "
            + "user text, dbpath text, filterjson text, status text )"
        )
        cursor_write.execute(q)
        table_name = self.get_gene_to_filter_table_name(uid=uid)
        if not table_name:
            return
        q = f"drop table if exists {table_name}"
        cursor_write.execute(q)
        q = f"create table {table_name} (base__hugo text)"
        cursor_write.execute(q)
        q = f"insert into {table_name} (base__hugo) values (?)"
        cursor_write.executemany(q, genes)
        conn_write.commit()

    def make_filtered_hugo_table(self):
        conn_read, conn_write = self.get_db_conns()
        _ = conn_read
        bypassfilter = (
            not self.filter
            and not self.filtersql
            and not self.includesample
            and not self.excludesample
        )
        if bypassfilter is False:
            gftable = "gene_filtered"
            q = f"drop table if exists {gftable}"
            conn_write.execute(q)
            q = (
                f"create table {gftable} as select distinct v.base__hugo "
                + "from variant as v inner join variant_filtered as vf on "
                + "vf.base__uid=v.base__uid where v.base__hugo is not null"
            )
            conn_write.execute(q)
            conn_write.commit()

    def table_exists(self, table) -> bool:
        conn_read, conn_write = self.get_db_conns()
        cursor_read = conn_read.cursor()
        _ = conn_write
        sql = (
            'select name from sqlite_master where type="table" and '
            + 'name="'
            + table
            + '"'
        )
        cursor_read.execute(sql)
        row = cursor_read.fetchone()
        if row:
            return True
        else:
            return False

    def get_variant_data_for_cols(self, cols):
        conn_read, conn_write = self.get_db_conns()
        cursor_read = conn_read.cursor()
        _ = conn_write
        bypassfilter = self.should_bypass_filter()
        if cols[0] == "base__uid":
            cols[0] = "v.base__uid"
        q = "select {},base__hugo from variant as v".format(",".join(cols))
        if bypassfilter is False:
            q += " inner join variant_filtered as f on v.base__uid=f.base__uid"
        if cols[0] == "v.base__uid":
            cols[0] = "base__uid"
        cursor_read.execute(q)
        rows = cursor_read.fetchall()
        return rows

    def get_result_levels(self) -> List[str]:
        conn_read, conn_write = self.get_db_conns()
        _ = conn_write
        cursor_read = conn_read.cursor()
        table_names = []
        if self.use_duckdb:
            return ["variant"]
        else:
            q = (
                'select name from sqlite_master where type="table" and '
                + 'name like "%_header"'
            )
            cursor_read.execute(q)
            for row in cursor_read.fetchall():
                table_names.append(row[0].replace("_header", ""))
            return table_names

    def get_stored_output_columns(self, module_name):
        from json import loads

        conn_read, conn_write = self.get_db_conns()
        _ = conn_write
        cursor_read = conn_read.cursor()
        output_columns = []
        q = (
            "select col_def from variant_header where col_name like"
            + ' "{module_name}\\_\\_%" escape "\\"'
        )
        cursor_read.execute(q)
        for row in cursor_read.fetchall():
            d = loads(row[0])
            d["name"] = d["name"].replace(f"{module_name}__", "")
            output_columns.append(d)
        return output_columns

    def make_ftables_and_ftable_uid(self, make_filtered_table=True):
        self.ftable_uid = None
        if not self.should_bypass_filter() or make_filtered_table:
            ret = self.make_ftables()
            if ret:
                ftable_uid = ret["uid"]
                return ftable_uid

    def getcount(self, level="variant", uid=None):
        if self.should_bypass_filter() or uid is not None:
            norows = self.get_ftable_num_rows(level=level, uid=uid, ftype=level)
        else:
            uid = self.make_ftables_and_ftable_uid()
            norows = self.get_ftable_num_rows(level=level, uid=uid, ftype=level)
        return norows
