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
            {
                "name": "name",
                "description": "Module name",
                "type": "string"
            },
            {
                "name": "display",
                "description": "Human-readable module name",
                "type": "string"
            },
            {
                "name": "version",
                "description": "Version",
                "type": "string"
            }
        ]
    }
    table_name = f"{level}_header"
    out[table_name] = {
        "name": table_name,
        "description": f"Columns in the {level} table",
        "output_columns": [
            {
                "name": "col_name",
                "description": "Column name",
                "type": "string"
            },
            {
                "name": "col_def",
                "description": "Column definition in JSON",
                "type": "string"
            }
        ]
    }
    table_name = f"{level}_reportsub"
    out[table_name] = {
        "name": table_name,
        "description": f"Code to human-readable text substitution table for the {level} table",
        "output_columns": [
            {
                "name": "module",
                "description": "Module name",
                "type": "string"
            },
            {
                "name": "subdict",
                "description": "JSON string of the dictionary of internal code and human-readable text pairs.",
                "type": "string"
            }
        ]
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
        raise ExpectedException(f"{dbpath} does not seem to be a proper OakVar result database file. Exiting.")
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
            {
                "name": "colkey",
                "description": "Information key",
                "type": "string"
            },
            {
                "name": "colval",
                "description": "Information value",
                "type": "string"
            }
        ]
    }
    for level in ["variant", "gene", "sample", "mapping"]:
        out["tables"].update(get_table_info_sqlite(dbpath, level))
    out["tables"]["viewersetup"] = {
        "name": "viewersetup",
        "description": "Deprecated"
    }
    return out

