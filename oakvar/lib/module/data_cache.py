from typing import Optional


class ModuleDataCache:
    def __init__(self, module_name: str, module_type: str = ""):
        from pathlib import Path
        from .local import get_cache_conf
        from .local import get_module_dir

        self.conn = None
        self.module_name = module_name
        self.module_type = module_type
        self.module_dir = get_module_dir(module_name, module_type=module_type)
        self.conf = get_cache_conf(module_name, module_type=module_type)
        self.expiration_in_day = self.conf.get("expiration") if self.conf else None
        self.expiration = (
            self.expiration_in_day * 60 * 60 * 24 if self.expiration_in_day else None
        )
        self.dir = Path(self.module_dir) / "cache" if self.module_dir else None
        self.path = self.dir / "cache.sqlite" if self.dir else None
        if self.path:
            self.create_cache_dir_if_needed()
        self.conn = self.get_conn()
        self.create_cache_table_if_needed()

    def create_cache_dir_if_needed(self):
        from pathlib import Path

        if self.dir and not Path(self.dir).exists():
            self.dir.mkdir()

    def get_conn(self):
        from sqlite3 import connect
        from os import remove

        if not self.path:
            return None
        if not self.conn:
            try:
                self.conn = connect(str(self.path))
            except Exception:
                print(
                    f"Could not open module cache for {self.module_name}. Restarting the cache db."
                )
                remove(self.path)
                self.conn = connect(str(self.path))
        return self.conn

    def create_cache_table_if_needed(self):
        if not self.conn:
            return
        q = f"create table if not exists cache (k text primary key, v text, timestamp float)"
        self.conn.execute(q)
        self.conn.commit()

    def commit(self):
        if not self.conn:
            return
        self.conn.commit()

    def add_cache(self, key, value, defer_commit=False):
        import time
        from json import dumps

        if not self.conn:
            return
        key = key
        value = dumps(value)
        q = f"insert or replace into cache (k, v, timestamp) values (?, ?, ?)"
        ts = time.time()
        self.conn.execute(q, (key, value, ts))
        if not defer_commit:
            self.conn.commit()

    def delete_cache(self, key, defer_commit=False):
        if not self.conn:
            return
        q = f"delete from cache where key=?"
        self.conn.execute(q, (key,))
        if not defer_commit:
            self.conn.commit()

    def get_cache(self, key) -> Optional[str]:
        import time
        from json import loads
        from traceback import print_exc

        if not self.conn:
            return
        q = f"select v, timestamp from cache where k=?"
        ret = self.conn.execute(q, (key,)).fetchone()
        if ret:
            v = ret[0]  # type: ignore
            try:
                v = loads(v)
            except:
                print_exc()
            timestamp = float(ret[1])  # type: ignore
            if self.expiration:
                if time.time() - timestamp > self.expiration:
                    self.delete_cache(key)
                    return
                else:
                    return v
            else:
                return v
        else:
            return
