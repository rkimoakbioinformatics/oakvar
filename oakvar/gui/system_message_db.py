from typing import Optional
from pathlib import Path


def get_system_message_db_conn():
    import sqlite3
    from .consts import SYSTEM_MESSAGE_DB_FNAME
    from .consts import SYSTEM_MESSAGE_TABLE
    from ..lib.system import get_conf_dir
    from ..lib.system import get_default_conf_dir
    from ..lib.exceptions import SystemMissingException

    conf_dir: Optional[Path] = get_conf_dir()
    if not conf_dir:
        conf_dir = get_default_conf_dir()
    if not conf_dir:
        raise SystemMissingException(
            msg="Configuration directory does not exist. Please run "
            + "`ov system setup` to setup OakVar."
        )
    if not Path(conf_dir).exists():
        conf_dir.mkdir(parents=True)
    db_path = conf_dir / SYSTEM_MESSAGE_DB_FNAME
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(
        "select * from sqlite_master where type='table' and "
        + f"name='{SYSTEM_MESSAGE_TABLE}'"
    )
    ret = c.fetchone()
    if not ret:
        create_system_message_db(conn)
    return conn


def create_system_message_db(conn):
    from .consts import SYSTEM_MESSAGE_TABLE
    from .consts import SYSTEM_ERROR_TABLE

    c = conn.cursor()
    c.execute(f"drop table if exists {SYSTEM_MESSAGE_TABLE}")
    c.execute(
        f"create table {SYSTEM_MESSAGE_TABLE} (uid integer primary key, "
        + "kind text, msg text, dt float)"
    )
    c.execute(f"drop table if exists {SYSTEM_ERROR_TABLE}")
    c.execute(
        f"create table {SYSTEM_ERROR_TABLE} (uid integer primary key, "
        + "kind text, msg text, dt float)"
    )
    conn.commit()


def clear_system_message_db(conn):
    from .consts import SYSTEM_MESSAGE_TABLE
    from .consts import SYSTEM_ERROR_TABLE

    c = conn.cursor()
    c.execute(f"delete from {SYSTEM_MESSAGE_TABLE}")
    c.execute(f"delete from {SYSTEM_ERROR_TABLE}")
    conn.commit()


def get_last_msg_id(conn):
    from .consts import SYSTEM_MESSAGE_TABLE

    c = conn.cursor()
    c.execute(f"select max(uid) from {SYSTEM_MESSAGE_TABLE}")
    ret = c.fetchone()
    if ret and ret[0]:
        return ret[0]
    else:
        return 0
