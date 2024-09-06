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
