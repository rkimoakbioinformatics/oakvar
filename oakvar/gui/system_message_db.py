# OakVar Dual License
# 
# Copyright (c) 2023 Oak Bioinformatics, LLC
# 
# This program is dual licensed under the Affero GPL-3.0 or later for 
# non-commercial and open source use, and under a commercial license, 
# which is available for purchase, for closed-source or commercial use.
# 
# For the commercial use, please contact Oak Bioinformatics, LLC 
# for obtaining such a license. OakVar commercial license does not impose 
# the Affero GPL open-source licensing terms, conditions, and limitations. 
# To obtain a commercial-use license of OakVar, please visit our website at
# https://oakbioinformatics.com or contact us at info@oakbioinformatics.com 
# for more information.
# 
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
