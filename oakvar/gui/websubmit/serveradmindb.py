from logging import getLogger
from typing import Any
from typing import Optional


def db_func(func):
    async def outer_func(*args, **kwargs):
        from aiosqlite import Row
        from .multiuser import get_admindb
        admindb = await get_admindb()
        conn = await admindb.get_db_conn()
        if not conn:
            return
        conn.row_factory = Row
        cursor = await conn.cursor()
        ret = await func(*args, conn=conn, cursor=cursor, **kwargs)
        return ret
    return outer_func

def get_admindb_path():
    from oakvar.system import get_conf_dir
    from pathlib import Path
    from ...system.consts import ADMIN_DB_FN
    admindb_path = Path(get_conf_dir()) / ADMIN_DB_FN
    return admindb_path

class ServerAdminDb ():
    def __init__ (self, new_setup=False, job_dir=None, job_name=None):
        from ...exceptions import SystemMissingException

        self.job_dir = job_dir
        self.job_name = job_name
        admindb_path = get_admindb_path()
        if not admindb_path.exists() and not new_setup:
            raise SystemMissingException("server admin database is missing.")
        self.admindb_path = str(admindb_path)

    def setup(self, args={}):
        from sqlite3 import connect
        conn = connect(self.admindb_path)
        cursor = conn.cursor()
        if args.get("clean"):
            self.drop_tables(conn, cursor)
        self.create_tables(conn, cursor)
        self.do_backward_compatibility(conn, cursor)
        self.add_admin(conn, cursor)
        self.add_default_user(conn, cursor)
        self.add_secret_key(conn, cursor)
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
        cursor.execute('create table if not exists users (email text primary key, role text, passwordhash text, question text, answerhash text, settings text)')
        cursor.execute('create table if not exists jobs (jobid integer primary key autoincrement, username text, dir text, name text, submit date, runtime integer, numinput integer, modules text, assembly text, note text, statusjson text, status text)')
        cursor.execute('create table if not exists config (key text primary key, value text)')
        cursor.execute('create table if not exists apilog (writetime text primary key, count int)')
        conn.commit()

    def do_backward_compatibility(self, conn, cursor):
        from json import loads

        q = f"select name from pragma_table_info('jobs') as tblinfo"
        cursor.execute(q)
        columns = [v[0] for v in cursor.fetchall()]
        if "status" in columns:
            return
        q = f"alter table jobs add column status text"
        cursor.execute(q)
        conn.commit()
        q = f"select jobid, statusjson from jobs"
        cursor.execute(q)
        rets = cursor.fetchall()
        for ret in rets:
            jobid = ret[0]
            statusjson = ret[1]
            if not statusjson:
                statusjson = {"status": "Error"}
            else:
                statusjson = loads(ret[1])
            status = statusjson.get("status")
            q = f"update jobs set status=? where jobid=?"
            cursor.execute(q, (status, jobid))
        conn.commit()

    def add_admin(self, conn, cursor):
        from ...store.ov.account import get_email_from_token_set
        from ...system.consts import ADMIN_ROLE
        email = get_email_from_token_set()
        q = "insert or replace into users (email, role) values (?, ?)"
        cursor.execute(q, (email, ADMIN_ROLE))
        conn.commit()

    def add_default_user(self, conn, cursor):
        from ...system.consts import USER_ROLE
        from ...system.consts import DEFAULT_SERVER_DEFAULT_USERNAME
        q = "insert or replace into users (email, role) values (?, ?)"
        cursor.execute(q, (DEFAULT_SERVER_DEFAULT_USERNAME, USER_ROLE))
        conn.commit()

    def add_secret_key(self, conn, cursor):
        from cryptography import fernet
        fernet_key = fernet.Fernet.generate_key()
        q = "insert or replace into config (key, value) values (?, ?)"
        cursor.execute(q, ("fernet_key", fernet_key))
        conn.commit()

    def get_pwhash(self, pw):
        from hashlib import sha256
        m = sha256()
        m.update(pw.encode('utf-16be'))
        pwhash = m.hexdigest()
        return pwhash

    async def upgrade_db_if_needed(self):
        pass

    async def get_db_conn (self):
        from aiosqlite import connect
        conn = await connect(str(get_admindb_path()))
        return conn

    def get_sync_db_conn (self):
        from sqlite3 import connect
        conn = connect(str(get_admindb_path()))
        return conn

    async def add_job_info(self, username, job):
        from json import dumps

        conn = await self.get_db_conn()
        if not conn:
            return
        cursor = await conn.cursor()
        annotators = job.info.get("annotators", [])
        postaggregators = job.info.get("postaggregators", [])
        modules = ",".join(annotators + postaggregators)
        q = "insert into jobs (username, dir, name, submit, runtime, numinput, modules, assembly, note, statusjson, status) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        statusjson = dumps(job.info["statusjson"])
        await cursor.execute(q, (username, job.info["dir"], job.info['id'], job.info['submission_time'], -1, -1, modules, job.info['assembly'], job.info["note"], statusjson, job.info["status"]))
        await conn.commit()
        await cursor.close()
        await conn.close()

    async def check_username_presence (self, username):
        conn = await self.get_db_conn()
        if not conn:
            return False
        cursor = await conn.cursor()
        await cursor.execute('select * from users where email="{}"'.format(username))
        r = await cursor.fetchone()
        await cursor.close()
        await conn.close()
        if r is None:
            return False
        else:
            return True

    async def get_user_role_of_email(self, email, servermode=True):
        from ...system.consts import ADMIN_ROLE
        if not servermode:
            return ADMIN_ROLE
        conn = await self.get_db_conn()
        if not conn:
            return
        cursor = await conn.cursor()
        q = f"select role from users where email=?"
        await cursor.execute(q, (email,))
        ret = await cursor.fetchone()
        if ret:
            ret = ret[0]
        await cursor.close()
        await conn.close()
        return ret

    async def add_user_if_not_exist (self, username, passwordhash, question, answerhash):
        from json import dumps
        conn = await self.get_db_conn()
        if not conn:
            return
        cursor = await conn.cursor()
        q = f"select email from users where email=?"
        await cursor.execute(q, (username,))
        ret = await cursor.fetchone()
        if not ret:
            default_settings = {'lastAssembly':None}
            q = f"insert into users (email, role, passwordhash, question, answerhash, settings) values (?, ?, ?, ?, ?, ?)"
            await cursor.execute(q, (username, "user", passwordhash, question, answerhash, dumps(default_settings)))
        await conn.commit()
        await cursor.close()
        await conn.close()

    async def get_password_question (self, email):
        conn = await self.get_db_conn()
        if not conn:
            return None
        cursor = await conn.cursor()
        await cursor.execute('select question from users where email="{}"'.format(email))
        r = await cursor.fetchone()
        await cursor.close()
        await conn.close()
        if r is None:
            return None
        else:
            return r[0]

    async def check_password_answer (self, email, answerhash):
        conn = await self.get_db_conn()
        if not conn:
            return False
        cursor = await conn.cursor()
        await cursor.execute('select * from users where email="{}" and answerhash="{}"'.format(email, answerhash))
        r = await cursor.fetchone()
        await cursor.close()
        await conn.close()
        if r is None:
            return False
        else:
            return True

    async def set_temp_password (self, email):
        from hashlib import sha256
        from random import randint
        temppassword = ''.join([chr(randint(97,122)) for _ in range(8)])
        m = sha256()
        m.update(temppassword.encode('utf-16be'))
        temppasswordhash = m.hexdigest()
        conn = await self.get_db_conn()
        if not conn:
            return None
        cursor = await conn.cursor()
        await cursor.execute('update users set passwordhash="{}" where email="{}"'.format(temppasswordhash, email))
        await conn.commit()
        await cursor.close()
        await conn.close()
        return temppassword

    async def set_username (self, email, newemail):
        from os.path import join
        from os import rename
        from ...system import get_jobs_dir
        conn = await self.get_db_conn()
        if not conn:
            return
        cursor = await conn.cursor()
        await cursor.execute(f'select * from users where email="{newemail}"')
        r = await cursor.fetchone()
        if r is not None:
            await cursor.close()
            await conn.close()
            return 'Duplicate username'
        cursor = await conn.cursor()
        q = f'update users set email="{newemail}" where email="{email}"'
        await cursor.execute(q)
        q = f'update jobs set username="{newemail}" where username="{email}"'
        await cursor.execute(q)
        await conn.commit()
        await cursor.close()
        await conn.close()
        root_jobs_dir = get_jobs_dir()
        old_job_dir = join(root_jobs_dir, email)
        new_job_dir = join(root_jobs_dir, newemail)
        rename(old_job_dir, new_job_dir)
        return ''

    async def set_password (self, email, passwordhash):
        conn = await self.get_db_conn()
        if not conn:
            return
        cursor = await conn.cursor()
        await cursor.execute('update users set passwordhash="{}" where email="{}"'.format(passwordhash, email))
        await conn.commit()
        await cursor.close()
        await conn.close()

    async def get_user_settings (self, username):
        from json import loads
        conn = await self.get_db_conn()
        if not conn:
            return None
        cursor = await conn.cursor()
        q = 'select settings from users where email=?'
        await cursor.execute(q,[username])
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

    async def update_user_settings (self, username, d):
        from json import dumps
        newsettings = await self.get_user_settings(username)
        if not newsettings:
            return
        newsettings.update(d)
        conn = await self.get_db_conn()
        if not conn:
            return
        cursor = await conn.cursor()
        await cursor.execute('update users set settings=? where email=?',[dumps(newsettings), username])
        await cursor.close()
        await conn.close()

    async def delete_user (self, username):
        conn = await self.get_db_conn()
        if not conn:
            return
        cursor = await conn.cursor()
        q = f'delete from users where email="{username}"'
        await cursor.execute(q)
        await conn.commit()
        await cursor.close()
        await conn.close()

    async def open_conn_cursor(self):
        conn = await self.get_db_conn()
        if not conn:
            return None, None
        cursor = await conn.cursor()
        return conn, cursor

    async def close_conn_cursor(self, conn, cursor):
        await cursor.close()
        await conn.close()

    async def write_single_api_access_count_to_db (self, t, count):
        from time import strftime
        from time import localtime
        conn = await self.get_db_conn()
        if not conn:
            return
        cursor = await conn.cursor()
        ts = strftime('%Y-%m-%d %H:%M:%S', localtime(t))
        q = f'insert into apilog values ("{ts}", {count})'
        await cursor.execute(q)
        await conn.commit()
        await cursor.close()
        await conn.close()

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
            stderr.write(f"no job_dir nor job_name for server admin DB")
            return
        cursor.execute(q, values)
        conn.commit()
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

    def get_pagesize(self, in_pagesize: Optional[str]) -> int:
        from ...system import get_sys_conf_value
        from ..consts import job_table_pagesize_key
        from ..consts import DEFAULT_JOB_TABLE_PAGESIZE

        if not in_pagesize:
            in_pagesize = get_sys_conf_value(job_table_pagesize_key)
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
    async def get_jobs_of_email(self, email, pageno=None, pagesize=None, search_text=None, conn=Any, cursor=Any):
        from json import loads
        _ = search_text
        pageno = self.get_pageno(pageno)
        pagesize = self.get_pagesize(pagesize)
        offset = (pageno - 1) * pagesize
        limit = pagesize
        _ = conn
        if not email:
            return
        q = f"select name, statusjson, status from jobs where username=? order by jobid desc limit {limit} offset {offset}"
        await cursor.execute(q, (email,))
        ret = await cursor.fetchall()
        ret = [dict(v) for v in ret]
        for d in ret:
            if not d.get("statusjson"):
                d["statusjson"] = ""
            else:
                d["statusjson"] = loads(d["statusjson"])
        return ret

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
        from ...system import get_user_jobs_dir
        from ...system import get_job_status
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
            job_status = get_job_status(job_dir)
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
            statusjson = dumps(job_status)
            if not job_name or not submit:
                continue
            q = f"select jobid from jobs where dir=?"
            cursor.execute(q, (job_dir,))
            ret = cursor.fetchone()
            if ret:
                continue
            q = "insert into jobs (username, dir, name, submit, runtime, numinput, modules, assembly, note, statusjson, status) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            values = (email, job_dir, job_name, submit, runtime, numinput, modules, assembly, note, statusjson, status)
            cursor.execute(q, values)
        conn.commit()
        cursor.close()
        conn.close()

def setup_serveradmindb(args={}):
    from os import remove
    clean = args.get("clean")
    admindb_path = get_admindb_path()
    if clean:
        remove(admindb_path)
    admindb = ServerAdminDb(new_setup=True)
    admindb.setup()

