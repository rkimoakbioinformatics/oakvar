from logging import getLogger
from typing import Any


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
    def __init__ (self, new_setup=False):
        from ...exceptions import SystemMissingException
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
        cursor.execute('create table if not exists jobs (jobid integer primary key autoincrement, username text, dir text, name text, submit date, runtime integer, numinput integer, modules text, assembly text, note text, statusjson text)')
        cursor.execute('create table if not exists config (key text primary key, value text)')
        cursor.execute('create table if not exists apilog (writetime text primary key, count int)')
        conn.commit()

    def add_admin(self, conn, cursor):
        from ...store.ov.account import get_email_from_token_set
        from ...system.consts import ADMIN_ROLE
        email = get_email_from_token_set()
        print(f"@ admin={email}")
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

    async def add_job_info(self, username, job):
        conn = await self.get_db_conn()
        if not conn:
            return
        cursor = await conn.cursor()
        annotators = job.info.get("annotators", [])
        postaggregators = job.info.get("postaggregators", [])
        modules = ",".join(annotators + postaggregators)
        q = "insert into jobs (username, dir, name, submit, runtime, numinput, modules, assembly, note) values (?, ?, ?, ?, ?, ?, ?, ?, ?)"
        await cursor.execute(q, (username, job.info["dir"], job.info['id'], job.info['submission_time'], -1, -1, modules, job.info['assembly'], job.info["note"]))
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

    async def get_input_stat (self, start_date, end_date):
        conn = await self.get_db_conn()
        if not conn:
            return None
        cursor = await conn.cursor()
        q = 'select sum(numinput), max(numinput), avg(numinput) from jobs where submit>="{}" and submit<="{}T23:59:59" and numinput!=-1'.format(start_date, end_date)
        await cursor.execute(q)
        row = await cursor.fetchone()
        if row:
            row = row[0]
            s = row[0] if row[0] is not None else 0
            m = row[1] if row[1] is not None else 0
            a = row[2] if row[2] is not None else 0
            response = [s, m, a]
        else:
            response = None
        await cursor.close()
        await conn.close()
        return response

    async def get_user_stat (self, start_date, end_date):
        conn = await self.get_db_conn()
        if not conn:
            return None
        cursor = await conn.cursor()
        q = 'select count(distinct username) from jobs where submit>="{}" and submit<="{}T23:59:59"'.format(start_date, end_date)
        await cursor.execute(q)
        row = await cursor.fetchone()
        if row is None:
            num_unique_users = 0
        else:
            num_unique_users = row[0]
        q = 'select username, count(*) as c from jobs where submit>="{}" and submit<="{}T23:59:59" group by username order by c desc limit 1'.format(start_date, end_date)
        await cursor.execute(q)
        row = await cursor.fetchone()
        if row is None:
            (frequent_user, frequent_user_num_jobs) = (0, 0)
        else:
            (frequent_user, frequent_user_num_jobs) = row
        q = 'select username, sum(numinput) s from jobs where submit>="{}" and submit<="{}T23:59:59" group by username order by s desc limit 1'.format(start_date, end_date)
        await cursor.execute(q)
        row = await cursor.fetchone()
        if row is None:
            (heaviest_user, heaviest_user_num_input) = (0, 0)
        else:
            (heaviest_user, heaviest_user_num_input) = row
        response = {'num_uniq_user': num_unique_users, 'frequent':[frequent_user, frequent_user_num_jobs], 'heaviest':[heaviest_user, heaviest_user_num_input]}
        await cursor.close()
        await conn.close()
        return response

    async def get_job_stat (self, start_date, end_date):
        conn = await self.get_db_conn()
        if not conn:
            return None
        cursor = await conn.cursor()
        q = 'select count(*) from jobs where submit>="{}" and submit<="{}T23:59:59"'.format(start_date, end_date)
        await cursor.execute(q)
        row = await cursor.fetchone()
        if row is None:
            num_jobs = 0
        else:
            num_jobs = row[0]
        q = 'select date(submit) as d, count(*) as c from jobs where submit>="{}" and submit<="{}T23:59:59" group by d order by d asc'.format(start_date, end_date)
        await cursor.execute(q)
        rows = await cursor.fetchall()
        submits = []
        counts = []
        for row in rows:
            submits.append(row[0])
            counts.append(row[1])
        response = {'num_jobs': num_jobs, 'chartdata': [submits, counts]}
        await cursor.close()
        await conn.close()
        return response

    async def get_api_stat (self, start_date, end_date):
        conn = await self.get_db_conn()
        if not conn:
            return None
        cursor = await conn.cursor()
        q = f'select sum(count) from apilog where writetime>="{start_date}" and writetime<="{end_date}T23:59:59"'
        await cursor.execute(q)
        row = await cursor.fetchone()
        if row is None:
            num_api_access = 0
        else:
            num_api_access = row[0]
        response = {'num_api_access': num_api_access}
        await cursor.close()
        await conn.close()
        return response

    async def get_annot_stat (self, start_date, end_date):
        conn = await self.get_db_conn()
        if not conn:
            return
        cursor = await conn.cursor()
        q = 'select annotators from jobs where submit>="{}" and submit<="{}T23:59:59"'.format(start_date, end_date)
        await cursor.execute(q)
        rows = await cursor.fetchall()
        annot_count = {}
        for row in rows:
            annots = row[0].split(',')
            for annot in annots:
                if not annot in annot_count:
                    annot_count[annot] = 0
                annot_count[annot] += 1
        response = {'annot_count': annot_count}
        await cursor.close()
        await conn.close()
        return response

    async def get_assembly_stat (self, start_date, end_date):
        conn = await self.get_db_conn()
        if not conn:
            return None
        cursor = await conn.cursor()
        q = 'select assembly, count(*) as c from jobs where submit>="{}" and submit<="{}T23:59:59" group by assembly order by c desc'.format(start_date, end_date)
        await cursor.execute(q)
        rows = await cursor.fetchall()
        assembly_count = []
        for row in rows:
            (assembly, count) = row
            assembly_count.append([assembly, count])
        response = assembly_count
        await cursor.close()
        await conn.close()
        return response

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

    @db_func
    async def get_jobs_of_email(self, email, pageno=None, pagesize=None, search_text=None, conn=Any, cursor=Any):
        from json import loads
        from ...system import get_sys_conf_value
        from ..consts import job_table_pagesize_key
        from ..consts import DEFAULT_JOB_TABLE_PAGESIZE
        if not pagesize:
            try:
                pagesize = get_sys_conf_value(job_table_pagesize_key)
                if pagesize:
                    pagesize = int(pagesize)
            except Exception as e:
                logger = getLogger()
                logger.exception(e)
        if not pagesize:
            pagesize = DEFAULT_JOB_TABLE_PAGESIZE
        try:
            if pageno:
                pageno = int(pageno)
        except Exception as e:
            logger = getLogger()
            logger.exception(e)
        if not pageno:
            pageno = 1
        offset = (pageno - 1) * pagesize
        limit = pagesize
        _ = conn
        if not email:
            return
        q = f"select name, statusjson from jobs where username=? order by jobid desc limit {limit} offset {offset}"
        await cursor.execute(q, (email,))
        ret = await cursor.fetchall()
        ret = [dict(v) for v in ret]
        for d in ret:
            try:
                d["statusjson"] = loads(d["statusjson"])
            except:
                d["statusjson"] = {"status": "Error"}
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
            print(f"@ job_dir={str(job_dir_p.absolute())}")
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
            modules = ",".join(job_status.get("annotators", []) + job_status.get("postaggregators", []))
            runtime = get_job_runtime_in_job_dir(job_dir, run_name=run_name)
            assembly = job_status.get("assembly")
            note = job_status.get("note")
            statusjson = dumps(job_status)
            if not job_name or not submit:
                print(f"@ skipping. {job_name}. {run_name}. {submit}. {numinput}. {modules}. {assembly}. {note}.")
                continue
            q = "insert into jobs (username, dir, name, submit, runtime, numinput, modules, assembly, note, statusjson) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            values = (email, job_dir, job_name, submit, runtime, numinput, modules, assembly, note, statusjson)
            print(f"@ values={values}")
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

