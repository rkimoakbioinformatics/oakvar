class AdminDb:
    @classmethod
    def get_admindb(cls, admindb=None):
        if admindb is None:
            admindb_obj = None
        else:
            if admindb.endswith(".sqlite"):
                admindb_obj = AdminDbSqlite(admindb)
            else:
                admindb_obj = None
        if admindb_obj is not None:
            admindb_obj.connect()
            admindb_obj.create_tables_if_needed()
            admindb_obj.setup()
        return admindb_obj

    def setup(self):
        pass

class AdminDbSqlite(AdminDb):
    def __init__(self, admindb):
        self.admindb = admindb

    def connect(self):
        import sqlite3
        self.db = sqlite3.connect(self.admindb)

    def create_tables_if_needed(self):
        self.cursor = self.db.cursor()
        self.cursor.execute("create table if not exists jobs (jobid text, username text, submit date, runtime integer, numinput integer, annotators text, assembly text)")

    def add_job(self, jobid=None, username=None, submit=None, runtime=None,
        numinput=None, annotators=None, assembly=None):
        if jobid and username and submit:
            self.cursor = self.db.cursor()
            self.cursor.execute(
                "insert into jobs (jobid, username, submit, numinput, annotators, assembly) " +
                "values (?, ?, ?, ?, ?, ?)", 
                (jobid, username, submit, numinput, annotators, assembly))
            self.cursor.close()
            self.db.commit()

    def add_numinput(self, jobid=None, numinput=None):
        if jobid and numinput:
            self.cursor = self.db.cursor()
            self.cursor.execute(
                "update jobs set numinput=? where jobid=?",
                (numinput, jobid))
            self.cursor.close()
            self.db.commit()

    def add_runtime(self, jobid=None, runtime=None):
        if jobid and runtime:
            self.cursor = self.db.cursor()
            self.cursor.execute(
                "update jobs set runtime=? where jobid=?",
                (runtime, jobid))
            self.cursor.close()
            self.db.commit()
