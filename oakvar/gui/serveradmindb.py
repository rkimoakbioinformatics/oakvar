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

from logging import getLogger
from typing import Any
from typing import Optional
from typing import Union

admindb_path = None
serveradmindb = None


async def get_serveradmindb(new_setup: bool = False):
    from .serveradmindb import ServerAdminDb

    global serveradmindb
    if not serveradmindb:
        serveradmindb = ServerAdminDb(new_setup=new_setup)
    return serveradmindb


def db_func(func):
    async def outer_func(*args, **kwargs):
        from aiosqlite import Row

        admindb = await get_serveradmindb()
        conn = await admindb.get_db_conn()
        if not conn:
            return
        conn.row_factory = Row
        cursor = await conn.cursor()
        ret = await func(*args, conn=conn, cursor=cursor, **kwargs)
        await cursor.close()
        await conn.close()
        return ret

    return outer_func


def get_admindb_path():
    from ..lib.system import get_conf_dir
    from ..lib.system import get_default_conf_dir
    from ..lib.system.consts import ADMIN_DB_FN

    global admindb_path
    if not admindb_path:
        conf_dir = get_conf_dir()
        if not conf_dir:
            conf_dir = get_default_conf_dir()
        if not conf_dir.exists():
            conf_dir.mkdir(parents=True)
        admindb_path = conf_dir / ADMIN_DB_FN
    return admindb_path


class ServerAdminDb:
    def __init__(self, new_setup: bool = False, job_dir=None, job_name=None):
        from ..lib.exceptions import SystemMissingException

        self.job_dir = job_dir
        self.job_name = job_name
        admindb_path = get_admindb_path()
        if (not admindb_path or not admindb_path.exists()) and not new_setup:
            raise SystemMissingException("server admin database is missing.")
        self.admindb_path = admindb_path

    def setup(self, args={}):
        from sqlite3 import connect

        conn = connect(self.admindb_path)
        cursor = conn.cursor()
        if not args.get("clean"):
            need_clean_start = self.do_backward_compatibility(conn, cursor)
        else:
            need_clean_start = False
        if args.get("clean") or need_clean_start:
            self.drop_tables(conn, cursor)
        self.create_tables(conn, cursor)
        self.add_admin(conn, cursor)
        self.add_default_user(conn, cursor)
        self.retrieve_user_jobs_into_db()
        cursor.close()
        conn.close()

    def drop_tables(self, conn, cursor):
        cursor.execute("drop table if exists users")
        cursor.execute("drop table if exists jobs")
        cursor.execute("drop table if exists config")
        cursor.execute("drop table if exists apilog")
        conn.commit()

    def create_tables(self, conn, cursor):
        cursor.execute(
            "create table if not exists users (email text primary key, "
            + "role text, passwordhash text, question text, answerhash text, "
            + "settings text)"
        )
        cursor.execute(
            "create table if not exists jobs (uid integer primary key "
            + "autoincrement, username text, dir text, name text, submit date, "
            + "runtime integer, numinput integer, modules text, assembly text, "
            + "note text, info_json text, status text)"
        )
        cursor.execute(
            "create table if not exists config (key text primary key, value text)"
        )
        cursor.execute(
            "create table if not exists apilog (writetime text primary key, count int)"
        )
        conn.commit()

    def change_statusjson_to_info_json_column(self, conn, cursor):
        q = "alter table jobs rename column statusjson to info_json"  # statusjson Ok
        cursor.execute(q)
        conn.commit()

    def add_status_column(self, conn, cursor):
        from json import loads

        q = "alter table jobs add column status text"
        cursor.execute(q)
        conn.commit()
        q = "select jobid, statusjson from jobs"  # statusjson Ok here.
        cursor.execute(q)
        rets = cursor.fetchall()
        for ret in rets:
            jobid = ret[0]
            legacy_status_json = ret[1]
            if not legacy_status_json:
                legacy_status_json = {"status": "Aborted"}
            else:
                legacy_status_json = loads(ret[1])
            status = legacy_status_json.get("status")
            q = "update jobs set status=? where jobid=?"
            cursor.execute(q, (status, jobid))
        conn.commit()

    def add_uid_column(self, columns, column_types, conn, cursor) -> bool:
        if "jobid" in columns:
            idx = columns.index("jobid")
            ctype = column_types[idx]
            if ctype == "TEXT":
                if "name" in columns:
                    q = "update jobs set name=jobid"
                    cursor.execute(q)
                    conn.commit()
                else:
                    return True
            elif ctype == "INTEGER":
                ex_cols = columns[:idx] + columns[idx + 1 :]
                ex_ctypes = column_types[:idx] + column_types[idx + 1 :]
                q = f"select {','.join(ex_cols)} from jobs"
                cursor.execute(q)
                rows = cursor.fetchall()
                new_cols = ["uid"] + ex_cols
                new_ctypes = ["integer primary key autoincrement"] + ex_ctypes
                cols_def = ",".join(
                    [f"{v[0]} {v[1]}" for v in list(zip(new_cols, new_ctypes))]
                )
                schema = f"create table jobs ({cols_def})"
                q = "drop table jobs"
                cursor.execute(q)
                conn.commit()
                cursor.execute(schema)
                conn.commit()
                for row in rows:
                    col_defs = ",".join(ex_cols)
                    vals = ",".join(["?"] * len(ex_cols))
                    q = f"insert into jobs ({col_defs}) values ({vals})"
                    cursor.execute(q, row)
                conn.commit()
                return False
        return False

    def do_backward_compatibility(self, conn, cursor) -> bool:
        need_clean_start = False
        q = "select name, type, pk from pragma_table_info('jobs') as tblinfo"
        cursor.execute(q)
        columns = []
        column_types = []
        for row in cursor.fetchall():
            columns.append(row[0])
            column_types.append(row[1])
        if not columns:
            return True
        if "status" not in columns:
            self.add_status_column(conn, cursor)
        if "uid" not in columns:
            need_clean_start = self.add_uid_column(columns, column_types, conn, cursor)
        if "statusjson" in columns:  # statusjson Ok here.
            self.change_statusjson_to_info_json_column(conn, cursor)
        return need_clean_start

    def add_admin(self, conn, cursor):
        from ..lib.store.ov.account import get_email_from_token_set
        from ..lib.system.consts import ADMIN_ROLE

        email = get_email_from_token_set()
        q = "insert or replace into users (email, role) values (?, ?)"
        cursor.execute(q, (email, ADMIN_ROLE))
        conn.commit()

    def add_default_user(self, conn, cursor):
        from ..lib.system.consts import USER_ROLE
        from ..lib.system.consts import DEFAULT_SERVER_DEFAULT_USERNAME

        q = "insert or replace into users (email, role) values (?, ?)"
        cursor.execute(q, (DEFAULT_SERVER_DEFAULT_USERNAME, USER_ROLE))
        conn.commit()

    def get_db_conn_sync(self):
        from sqlite3 import connect

        conn = connect(self.admindb_path)
        return conn

    async def get_db_conn(self):
        from aiosqlite import connect

        conn = await connect(self.admindb_path)
        return conn

    def get_sync_db_conn(self):
        from sqlite3 import connect

        conn = connect(self.admindb_path)
        return conn

    def add_job_info_sync(self, username, job):
        from json import dumps

        conn = self.get_db_conn_sync()
        if not conn:
            return
        cursor = conn.cursor()
        annotators = job.info.get("annotators", [])
        postaggregators = job.info.get("postaggregators", [])
        modules = ",".join(annotators + postaggregators)
        q = (
            "insert into jobs (username, dir, name, submit, runtime, "
            + "numinput, modules, assembly, note, info_json, status) values "
            + "(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        )
        info_json = dumps(job.info["info_json"])
        status: str = "Submitted"
        if hasattr(job, "status"):
            status = job.status
        cursor.execute(
            q,
            (
                username,
                job.dir,
                job.job_name,
                job.info["submission_time"],
                -1,
                -1,
                modules,
                job.info["assembly"],
                job.info["note"],
                info_json,
                status,
            ),
        )
        conn.commit()
        q = "select uid from jobs where username=? and dir=? and name=?"
        cursor.execute(q, (username, job.dir, job.job_name))
        ret = cursor.fetchone()
        cursor.close()
        conn.close()
        if ret:
            return ret[0]
        else:
            return None

    async def add_job_info(self, username, job):
        from json import dumps

        conn = await self.get_db_conn()
        if not conn:
            return
        cursor = await conn.cursor()
        annotators = job.info.get("annotators", [])
        postaggregators = job.info.get("postaggregators", [])
        modules = ",".join(annotators + postaggregators)
        q = (
            "insert into jobs (username, dir, name, submit, runtime, "
            + "numinput, modules, assembly, note, info_json, status) values "
            + "(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        )
        info_json = dumps(job.info["info_json"])
        await cursor.execute(
            q,
            (
                username,
                job.info["dir"],
                job.info["job_name"],
                job.info["submission_time"],
                -1,
                -1,
                modules,
                job.info["assembly"],
                job.info["note"],
                info_json,
                "Submitted",
            ),
        )
        await conn.commit()
        q = "select uid from jobs where username=? and dir=? and name=?"
        await cursor.execute(q, (username, job.info["dir"], job.info["job_name"]))
        ret = await cursor.fetchone()
        await cursor.close()
        await conn.close()
        if ret:
            return ret[0]
        else:
            return None

    async def get_user_role_of_email(self, email, servermode=True):
        from ..lib.system.consts import ADMIN_ROLE

        if not servermode:
            return ADMIN_ROLE
        conn = await self.get_db_conn()
        if not conn:
            return
        cursor = await conn.cursor()
        q = "select role from users where email=?"
        await cursor.execute(q, (email,))
        ret = await cursor.fetchone()
        if ret:
            ret = ret[0]
        await cursor.close()
        await conn.close()
        return ret

    async def add_user_if_not_exist(
        self, username: str, passwordhash: str, question: str, answerhash: str
    ):
        from json import dumps

        if not username:
            return
        conn = await self.get_db_conn()
        if not conn:
            return
        cursor = await conn.cursor()
        q = "select email from users where email=?"
        await cursor.execute(q, (username,))
        ret = await cursor.fetchone()
        if not ret:
            default_settings = {"lastAssembly": None}
            q = (
                "insert into users (email, role, passwordhash, question, "
                + "answerhash, settings) values (?, ?, ?, ?, ?, ?)"
            )
            await cursor.execute(
                q,
                (
                    username,
                    "user",
                    passwordhash,
                    question,
                    answerhash,
                    dumps(default_settings),
                ),
            )
        await conn.commit()
        await cursor.close()
        await conn.close()

    async def get_user_settings(self, username):
        from json import loads

        conn = await self.get_db_conn()
        if not conn:
            return None
        cursor = await conn.cursor()
        q = "select settings from users where email=?"
        await cursor.execute(q, [username])
        r = await cursor.fetchone()
        await cursor.close()
        await conn.close()
        if r is None:
            return None
        else:
            settings = r[0]
            if settings is None:
                return {}
            else:
                return loads(settings)

    async def update_user_settings(self, username, d):
        from json import dumps

        newsettings = await self.get_user_settings(username)
        if not newsettings:
            return
        newsettings.update(d)
        conn = await self.get_db_conn()
        if not conn:
            return
        cursor = await conn.cursor()
        await cursor.execute(
            "update users set settings=? where email=?", [dumps(newsettings), username]
        )
        await cursor.close()
        await conn.close()

    def delete_job(self, uid: int):
        conn = self.get_sync_db_conn()
        cursor = conn.cursor()
        q = "delete from jobs where uid=?"
        cursor.execute(q, (uid,))
        conn.commit()
        cursor.close()
        conn.close()

    @db_func
    async def get_job_status(self, uid=None, conn=None, cursor=Any):
        if not uid:
            return None
        _ = conn
        q = "select status from jobs where uid=?"
        await cursor.execute(q, (uid,))  # type: ignore
        ret = await cursor.fetchone()  # type: ignore
        if not ret:
            return None
        return ret[0]

    @db_func
    async def get_job_dir_by_username_uid(
        self, eud={}, conn=Any, cursor=Any
    ) -> Optional[str]:
        if not eud.get("uid") or not eud.get("username"):
            return None
        _ = conn
        q = "select dir from jobs where username=? and uid=?"
        await cursor.execute(q, (eud.get("username"), eud.get("uid")))  # type: ignore
        ret = await cursor.fetchone()  # type: ignore
        if not ret:
            return None
        else:
            return ret[0]

    @db_func
    async def get_dbpath_by_eud(self, eud={}, conn=Any, cursor=Any) -> Optional[str]:
        from json import loads

        if not eud.get("uid") or not eud.get("username"):
            return None
        _ = conn
        q = "select info_json from jobs where username=? and uid=?"
        await cursor.execute(q, (eud.get("username"), eud.get("uid")))  # type: ignore
        ret = await cursor.fetchone()  # type: ignore
        if not ret:
            return None
        info_json = loads(ret[0])
        return info_json.get("db_path")

    def update_job_info(self, info_dict, job_dir=None, job_name=None):
        from sys import stderr

        conn = self.get_sync_db_conn()
        if not conn:
            return
        cursor = conn.cursor()
        columns = list(info_dict.keys())
        values = [info_dict.get(column) for column in columns]
        set_cmds = []
        for k in info_dict.keys():
            set_cmds.append(f"set {k}=?")
        q = f"update jobs {','.join(set_cmds)} where dir=? and name=?"
        if job_dir and job_name:
            values.extend([job_dir, job_name])
        elif self.job_dir and self.job_name:
            values.extend([self.job_dir, self.job_name])
        else:
            stderr.write("no job_dir nor job_name for server admin DB")
            return
        try:
            cursor.execute(q, values)
            conn.commit()
        except Exception:
            pass  # competing job status update can be ignored.
        cursor.close()
        conn.close()

    def get_pageno(self, in_pageno: Optional[str]) -> int:
        if not in_pageno:
            pageno = 1
        else:
            try:
                pageno = int(in_pageno)
            except Exception as e:
                logger = getLogger()
                logger.exception(e)
                pageno = 1
        return pageno

    def get_pagesize(self, in_pagesize: Optional[Union[str, int]]) -> int:
        from ..lib.system import get_sys_conf_value
        from .consts import job_table_pagesize_key
        from .consts import DEFAULT_JOB_TABLE_PAGESIZE

        if not in_pagesize:
            v = get_sys_conf_value(job_table_pagesize_key)
            if v is None or isinstance(v, str) or isinstance(v, int):
                in_pagesize = v
        if not in_pagesize:
            pagesize = DEFAULT_JOB_TABLE_PAGESIZE
        else:
            try:
                pagesize = int(in_pagesize)
            except Exception as e:
                logger = getLogger()
                logger.exception(e)
                pagesize = DEFAULT_JOB_TABLE_PAGESIZE
        return pagesize

    @db_func
    async def get_jobs_of_email(
        self, email, pageno=None, pagesize=None, search_text=None, conn=Any, cursor=Any
    ):
        from json import loads

        _ = search_text
        pageno = self.get_pageno(pageno)
        pagesize = self.get_pagesize(pagesize)
        offset = (pageno - 1) * pagesize
        limit = pagesize
        _ = conn
        if not email:
            return
        q = (
            "select uid, name, info_json, status from jobs where username=? "
            + f"order by uid desc limit {limit} offset {offset}"
        )
        await cursor.execute(q, (email,))  # type: ignore
        ret = await cursor.fetchall()  # type: ignore
        ret = [dict(v) for v in ret]
        if len(ret) == 0:
            q = "select count(*) from jobs where username=?"
            await cursor.execute(q, (email,))  # type: ignore
            total_ret = await cursor.fetchone()  # type: ignore
            total = total_ret[0]
            if offset > total:
                return None
        for d in ret:
            if not d.get("info_json"):
                d["info_json"] = {}
            else:
                d["info_json"] = loads(d["info_json"])
        return ret

    @db_func
    async def get_run_name(
        self, username=None, uid=None, conn=Any, cursor=Any
    ) -> Optional[str]:
        from json import loads

        _ = conn
        if not username or not uid:
            return None
        q = "select info_json from jobs where username=? and uid=?"
        await cursor.execute(q, (username, uid))  # type: ignore
        ret = await cursor.fetchone()  # type: ignore
        if not ret:
            return None
        info_json = loads(ret[0])
        return info_json.get("run_name")

    @db_func
    async def mark_job_as_aborted(self, username=None, uid=None, conn=Any, cursor=Any):
        if not username or not uid:
            return
        q = "update jobs set status=? where username=? and uid=?"
        await cursor.execute(q, ("Aborted", username, uid))  # type: ignore
        await conn.commit()  # type: ignore

    @db_func
    async def get_users(self, conn=Any, cursor=Any):
        _ = conn
        q = "select email, role from users"
        await cursor.execute(q)  # type: ignore
        res = []
        for row in await cursor.fetchall():  # type: ignore
            res.append({"email": row[0], "role": row[1]})
        return res

    @db_func
    async def make_admin(self, email: str, conn=Any, cursor=Any):
        _ = conn
        q = "update users set role=? where email=?"
        await cursor.execute(  # type: ignore
            q,
            (
                "admin",
                email,
            ),
        )
        await conn.commit()  # type: ignore

    @db_func
    async def remove_admin(self, email: str, conn=Any, cursor=Any):
        _ = conn
        q = "update users set role='user' where email=?"
        await cursor.execute(q, (email,))  # type: ignore
        await conn.commit()  # type: ignore

    @db_func
    async def remove_user(self, email: str, conn=Any, cursor=Any):
        _ = conn
        q = "delete from users where email=?"
        await cursor.execute(q, (email,))  # type: ignore
        await conn.commit()  # type: ignore

    def retrieve_user_jobs_into_db(self):
        from pathlib import Path
        from .userjob import get_user_jobs_dir_list

        user_jobs_dir_list = get_user_jobs_dir_list()
        if not user_jobs_dir_list:
            return
        usernames = [Path(v).name for v in user_jobs_dir_list]
        for username in usernames:
            self.retrieve_jobs_of_user_into_db(username)

    def retrieve_jobs_of_user_into_db(self, email):
        from pathlib import Path
        from sqlite3 import connect
        from json import dumps
        from ..lib.system import get_user_jobs_dir
        from ..lib.system import get_legacy_status_json
        from .userjob import get_job_runtime_in_job_dir

        jobs_dir = get_user_jobs_dir(email)
        if not jobs_dir:
            return
        conn = connect(self.admindb_path)
        cursor = conn.cursor()
        jobs_dir_p = Path(jobs_dir)
        jobs_dir_l = list(jobs_dir_p.glob("*"))
        jobs_dir_l.sort(key=lambda p: p.stat().st_ctime)
        for job_dir_p in jobs_dir_l:
            if not job_dir_p.is_dir():
                continue
            job_dir = str(job_dir_p)
            job_status = get_legacy_status_json(job_dir)
            if not job_status:
                continue
            job_name = job_status.get("id")
            run_name = job_status.get("run_name")
            if not run_name:
                continue
            submit = job_status.get("submission_time")
            if not submit:
                continue
            numinput = job_status.get("num_input_var")
            annotators = job_status.get("annotators", [])
            if annotators == "":
                annotators = []
            postaggregators = job_status.get("postaggregators", [])
            if postaggregators == "":
                postaggregators = []
            modules = ",".join(annotators + postaggregators)
            runtime = get_job_runtime_in_job_dir(job_dir, run_name=run_name)
            assembly = job_status.get("assembly")
            note = job_status.get("note")
            status = job_status.get("status")
            info_json = dumps(job_status)
            if not job_name or not submit:
                continue
            q = "select uid from jobs where dir=?"
            cursor.execute(q, (job_dir,))
            ret = cursor.fetchone()
            if ret:
                continue
            q = (
                "insert into jobs (username, dir, name, submit, runtime, "
                + "numinput, modules, assembly, note, info_json, status) values "
                + "(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            )
            values = (
                email,
                job_dir,
                job_name,
                submit,
                runtime,
                numinput,
                modules,
                assembly,
                note,
                info_json,
                status,
            )
            cursor.execute(q, values)
        conn.commit()
        cursor.close()
        conn.close()

    def get_job_info_by_username_uid(self, username: str, uid: int):
        conn = self.get_sync_db_conn()
        cursor = conn.cursor()
        q = "select info_json from jobs where username=? and uid=?"
        cursor.execute(q, (username, uid))
        ret = cursor.fetchone()
        cursor.close()
        conn.close()
        if ret:
            return ret[0]
        return ret


def setup_serveradmindb(clean: bool = False) -> ServerAdminDb:
    from os import remove
    from pathlib import Path

    admindb_path = get_admindb_path()
    if clean and admindb_path and Path(admindb_path).exists():
        remove(admindb_path)
    admindb = ServerAdminDb(new_setup=True)
    admindb.setup()
    return admindb
