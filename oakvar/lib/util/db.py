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


from typing import Union
from typing import Dict
from typing import Any
from pathlib import Path


def get_table_info_sqlite(dbpath: Path, level: str):
    import sqlite3
    from json import loads

    conn = sqlite3.connect(dbpath)
    c = conn.cursor()
    out = {}
    out[level] = {
        "name": level,
        "description": f"{level} level annotation data",
    }
    c.execute(f"select col_name, col_def from {level}_header")
    rs = c.fetchall()
    output_columns = []
    for r in rs:
        col_name, col_def = r
        col_def = loads(col_def)
        output_columns.append(
            {
                "name": col_name,
                "title": col_def["title"],
                "type": col_def["type"],
            }
        )
    out[level]["output_columns"] = output_columns
    table_name = f"{level}_annotator"
    out[table_name] = {
        "name": table_name,
        "description": f"Modules used to generate annotation data for {level} level",
        "output_columns": [
            {"name": "name", "description": "Module name", "type": "string"},
            {
                "name": "display",
                "description": "Human-readable module name",
                "type": "string",
            },
            {"name": "version", "description": "Version", "type": "string"},
        ],
    }
    table_name = f"{level}_header"
    out[table_name] = {
        "name": table_name,
        "description": f"Columns in the {level} table",
        "output_columns": [
            {"name": "col_name", "description": "Column name", "type": "string"},
            {
                "name": "col_def",
                "description": "Column definition in JSON",
                "type": "string",
            },
        ],
    }
    table_name = f"{level}_reportsub"
    out[table_name] = {
        "name": table_name,
        "description": f"Code to human-readable text substitution table for the {level} table",
        "output_columns": [
            {"name": "module", "description": "Module name", "type": "string"},
            {
                "name": "subdict",
                "description": "JSON string of the dictionary of internal code and human-readable text pairs.",
                "type": "string",
            },
        ],
    }
    c.close()
    conn.close()
    return out


def get_sqliteinfo(dbpath: Union[Path, str] = "") -> Dict[str, Any]:
    """get_sqliteinfo.

    Args:
        fmt (str): fmt
        outer:
        dbpaths (List[str]): dbpaths
    """
    import sqlite3
    from json import loads
    from pathlib import Path
    from ..exceptions import ExpectedException

    if not dbpath:
        raise ExpectedException("SQLite result file should be given as dbpath.")
    dbpath = Path(dbpath)
    out = {}
    out["dbpath"] = str(dbpath)
    conn = sqlite3.connect(dbpath)
    c = conn.cursor()
    c.execute('select colval from info where colkey="_input_paths"')
    ret = c.fetchone()
    if not ret:
        c.execute('select colval from info where colkey="inputs"')
        ret = c.fetchone()
    if not ret:
        raise ExpectedException(
            f"{dbpath} does not seem to be a proper OakVar result database file. Exiting."
        )
    input_paths = loads(ret[0].replace("'", '"'))
    if isinstance(input_paths, dict):
        out["inputs"] = list(input_paths.values())
    elif isinstance(input_paths, list):
        out["inputs"] = input_paths
    out["tables"] = {}
    out["tables"]["info"] = {
        "name": "info",
        "description": "General information on the ov run job",
        "output_columns": [
            {"name": "colkey", "description": "Information key", "type": "string"},
            {"name": "colval", "description": "Information value", "type": "string"},
        ],
    }
    for level in ["variant", "gene", "sample", "mapping"]:
        out["tables"].update(get_table_info_sqlite(dbpath, level))
    out["tables"]["viewersetup"] = {"name": "viewersetup", "description": "Deprecated"}
    return out


def move_job_to_account(job_dir: Union[Path, str], new_username: str):
    from sqlite3 import connect
    import json
    from ..system import get_user_jobs_dir
    from ...gui.serveradmindb import get_admindb_path

    if isinstance(job_dir, str):
        job_dir = Path(job_dir)
    job_dir = job_dir.resolve()
    if not job_dir.exists():
        print(f"{job_dir} does not exist. Exiting.")
    # Retrieve db
    conn = connect(get_admindb_path())
    cursor = conn.cursor()
    q = "select uid, username, info_json from jobs where dir=?"
    cursor.execute(q, (str(job_dir),))
    ret = cursor.fetchone()
    if not ret:
        print(f"Job dir {job_dir} not found in the jobs table. Exiting.")
        cursor.close()
        conn.close()
        return
    uid = ret[0]
    old_username = ret[1]
    info_json = ret[2]
    info_json = json.loads(info_json)
    new_user_jobs_dir = get_user_jobs_dir(new_username)
    if new_user_jobs_dir is None or not new_user_jobs_dir.exists():
        print(f"Job directory for user {new_username} does not exist. Exiting.")
        cursor.close()
        conn.close()
        return
    new_user_jobs_dir = new_user_jobs_dir.resolve()
    # New job dir
    new_job_dir_parts = []
    for part in list(job_dir.parts):
        if part == old_username:
            part = new_username
        new_job_dir_parts.append(part)
    new_job_dir = Path(*new_job_dir_parts)
    # New input_path
    new_input_fname = info_json["orig_input_fname"]
    # New db_path
    db_path = Path(info_json["db_path"])
    new_db_path = new_job_dir / db_path.relative_to(job_dir)
    # New info_json
    info_json["db_path"] = str(new_db_path)
    info_json["job_dir"] = str(new_job_dir)
    info_json["orig_input_fname"] = new_input_fname
    # Update jobs table
    q = "update jobs set username=?, dir=?, info_json=? where uid=?"
    cursor.execute(q, (new_username, str(new_job_dir), json.dumps(info_json), uid))
    conn.commit()
    cursor.close()
    conn.close()
    # Move job dir
    job_dir.rename(new_job_dir)
    print(f"Job {job_dir} moved to {new_job_dir} for {new_username}.")
