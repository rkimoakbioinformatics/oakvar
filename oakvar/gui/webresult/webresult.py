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

import os
import aiosqlite
import json
import sys
from typing import Optional
from ... import ReportFilter
from aiohttp import web
import time

wu = None
logger = None
default_gui_result_pagesize = 100
gui_result_pagesize_key = "gui_result_pagesize"
servermode = False


async def get_nowg_annot_modules(_):
    # disabling this until required_annotator is included in the remote manifest.
    return web.json_response({})


async def get_filter_save_names(request):
    from aiohttp.web import Response

    _ = request.rel_url.query
    dbpath = await get_dbpath(request)
    conn = None
    cursor = None
    content = []
    try:
        conn = await get_db_conn(dbpath)
        if not conn:
            return Response(status=500)
        cursor = await conn.cursor()
        table = "viewersetup"
        r = await table_exists(cursor, table)
        if r is False:
            pass
        else:
            q = "select distinct name from " + table + ' where datatype="filter"'
            await cursor.execute(q)
            rs = await cursor.fetchall()
            for r in rs:
                content.append(r[0])
        await cursor.close()
        await conn.close()
    except:
        if cursor is not None:
            await cursor.close()
        if conn is not None:
            await conn.close()
        raise
    return web.json_response(content)


async def get_layout_save_names(request):
    from aiohttp.web import Response

    _ = request.rel_url.query
    dbpath = await get_dbpath(request)
    content = []
    conn = await get_db_conn(dbpath)
    if not conn:
        return Response(status=500)
    cursor = await conn.cursor()
    table = "viewersetup"
    r = await table_exists(cursor, table)
    if r:
        q = "select distinct name from " + table + ' where datatype="layout"'
        await cursor.execute(q)
        rs = await cursor.fetchall()
        for r in rs:
            content.append(r[0])
    await cursor.close()
    await conn.close()
    return web.json_response(content)


async def rename_layout_setting(request):
    from aiohttp.web import Response

    queries = request.rel_url.query
    dbpath = await get_dbpath(request)
    content = {}
    name = queries["name"]
    new_name = queries["newname"]
    conn = await get_db_conn(dbpath)
    if not conn:
        return Response(status=500)
    cursor = await conn.cursor()
    table = "viewersetup"
    r = await table_exists(cursor, table)
    if r is True:
        q = (
            "update "
            + table
            + ' set name="'
            + new_name
            + '" where datatype="layout" and name="'
            + name
            + '"'
        )
        await cursor.execute(q)
    await conn.commit()
    await cursor.close()
    await conn.close()
    return web.json_response(content)


async def get_db_conn(dbpath):
    if dbpath is None:
        return None
    conn = await aiosqlite.connect(dbpath)
    return conn


async def delete_layout_setting(request):
    from aiohttp.web import Response

    queries = request.rel_url.query
    dbpath = await get_dbpath(request)
    name = queries["name"]
    content = {}
    conn = await get_db_conn(dbpath)
    if not conn:
        return Response(status=500)
    cursor = await conn.cursor()
    table = "viewersetup"
    r = await table_exists(cursor, table)
    if r is True:
        q = "DELETE FROM " + table + ' WHERE datatype="layout" and name="' + name + '"'
        await cursor.execute(q)
    await conn.commit()
    await cursor.close()
    await conn.close()
    return web.json_response(content)


async def load_layout_setting(request):
    from aiohttp.web import Response

    queries = request.rel_url.query
    dbpath = await get_dbpath(request)
    name = queries["name"]
    conn = await get_db_conn(dbpath)
    content = {"widgetSettings": {}}
    if not conn:
        return Response(status=500)
    cursor = await conn.cursor()
    table = "viewersetup"
    r = await table_exists(cursor, table)
    if r is True:
        q = (
            "select viewersetup from "
            + table
            + ' where datatype="layout" and name="'
            + name
            + '"'
        )
        await cursor.execute(q)
        r = await cursor.fetchone()
        if r is not None:
            data = r[0]
            content = json.loads(data)
        else:
            content = {"widgetSettings": {}}
    await cursor.close()
    await conn.close()
    return web.json_response(content)


async def load_filter_setting(request):
    from aiohttp.web import Response

    queries = request.rel_url.query
    dbpath = await get_dbpath(request)
    name = queries["name"]
    conn = await get_db_conn(dbpath)
    content = {"filterSet": []}
    if not conn:
        return Response(status=500)
    cursor = await conn.cursor()
    table = "viewersetup"
    r = await table_exists(cursor, table)
    if r is True:
        q = (
            "select viewersetup from "
            + table
            + ' where datatype="filter" and name="'
            + name
            + '"'
        )
        await cursor.execute(q)
        r = await cursor.fetchone()
        if r is not None:
            data = r[0]
            content = json.loads(data)
        else:
            content = {"filterSet": []}
    await cursor.close()
    await conn.close()
    return web.json_response(content)


async def save_layout_setting(request):
    from aiohttp.web import Response
    from urllib.parse import unquote
    from json import loads

    text_data = await request.text()
    text_data = unquote(text_data)
    queries = loads(text_data)
    dbpath = await get_dbpath(request)
    name = queries["name"]
    savedata = queries["savedata"]
    conn = await get_db_conn(dbpath)
    content = "fail"
    if not conn:
        return Response(status=500)
    cursor = await conn.cursor()
    table = "viewersetup"
    r = await table_exists(cursor, table)
    if r is False:
        q = (
            "create table "
            + table
            + " (datatype text, name text, viewersetup text, unique (datatype, name))"
        )
        await cursor.execute(q)
    q = (
        "replace into "
        + table
        + ' values ("layout", "'
        + name
        + "\", '"
        + savedata
        + "')"
    )
    await cursor.execute(q)
    await conn.commit()
    await cursor.close()
    await conn.close()
    content = "saved"
    return web.json_response(content)


async def get_status(request):
    from aiohttp.web import Response

    global logger
    dbpath = await get_dbpath(request)
    conn = await get_db_conn(dbpath)
    if not conn:
        if logger:
            logger.error(f"db connection could not be made for {dbpath}.")
        return Response(status=500)
    content = {}
    cursor = await conn.cursor()
    q = r"select * from info where colkey not like '\_%' escape '\'"
    await cursor.execute(q)
    for row in await cursor.fetchall():
        content[row[0]] = row[1]
    if "dbpath" not in content:
        content["dbpath"] = dbpath
    await cursor.close()
    await conn.close()
    return web.json_response(content)


def get_widgetlist(_):
    from ...lib.module.local import get_local_module_infos_of_type

    content = []
    modules = get_local_module_infos_of_type("webviewerwidget")
    for module_name in modules:
        if module_name in ["wgcasecontrols"]:
            continue
        module = modules[module_name]
        conf = module.conf
        if "required_annotator" in conf:
            req = conf["required_annotator"]
        else:
            # Removes wg.
            req = module_name[2:]
        content.append(
            {
                "name": module_name,
                "title": module.title,
                "required_annotator": req,
                "helphtml_exists": module.helphtml_exists,
            }
        )
    return web.json_response(content)


async def get_count(request):
    from ...lib.exceptions import DatabaseConnectionError

    global logger
    dbpath = await get_dbpath(request)
    if dbpath is None:
        raise DatabaseConnectionError("result database")
    queries = await request.json()
    tab = queries["tab"]
    if "filter" in queries:
        filterstring = queries["filter"]
    else:
        filterstring = None
    cf = await ReportFilter.create(dbpath=dbpath, mode="sub", filterstring=filterstring)
    dbbasename = os.path.basename(dbpath)
    _ = dbbasename
    if logger:
        logger.info(f"calling count for {dbbasename}. filterstring={filterstring}")
    t = time.time()
    n = await cf.getcount(level=tab)
    await cf.close_db()
    if logger:
        t = round(time.time() - t, 3)
        logger.info(f"count obtained from {dbbasename} in {t}s")
    content = {"n": n}
    return web.json_response(content)


async def get_result(request):
    import importlib
    import importlib.util
    from pathlib import Path
    from ...lib.exceptions import DatabaseConnectionError

    global logger
    queries = await request.json()
    dbpath = await get_dbpath(request)
    if dbpath is None:
        raise DatabaseConnectionError("result database")
    dbname = os.path.basename(dbpath)
    tab = queries["tab"]
    page = queries.get("page")
    make_filtered_table = queries.get("makefilteredtable")
    if not page:
        page = 1
    else:
        page = int(page)
    pagesize = await get_pagesize(request, valueonly=True)
    if logger is not None:
        logger.info("(Getting result of [{}]:[{}]...)".format(dbname, tab))
    start_time = time.time()
    if "filter" in queries:
        filterstring = queries["filter"]
    else:
        filterstring = None
    if "confpath" in queries:
        confpath = queries["confpath"]
    else:
        confpath = None
    reporter_name = "jsonreporter"
    this_file_dir = Path(__file__).parent
    reporter_path = this_file_dir / f"{reporter_name}.py"
    spec = importlib.util.spec_from_file_location(reporter_name, reporter_path)
    if spec is None:
        raise Exception(f"Could not load {reporter_name}.")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)  # type: ignore
    if "separatesample" in queries:
        separatesample = queries["separatesample"]
        if separatesample == "true":
            separatesample = True
        else:
            separatesample = False
    else:
        separatesample = False
    no_summary = queries.get("no_summary")
    add_summary = not no_summary
    reporter = m.Reporter(
        dbpath=dbpath,
        module_name=reporter_name,
        nogenelevelonvariantlevel=True,
        confpath=confpath,
        filterstring=filterstring,
        separatesample=separatesample,
        report_types=["text"],
        no_summary=no_summary,
        make_col_categories=True,
    )
    data = await reporter.run(
        tab=tab,
        pagesize=pagesize,
        page=page,
        add_summary=add_summary,
        make_filtered_table=make_filtered_table,
        make_col_categories=True,
    )
    data["modules_info"] = await get_modules_info(request)
    content = {}
    content["stat"] = {
        "rowsreturned": True,
        "wherestr": "",
        "filtered": True,
        "filteredresultmessage": "",
        "norows": data["info"]["norows"],
    }
    content["columns"] = get_colmodel(tab, data["colinfo"])
    content["data"] = get_datamodel(data[tab])
    content["status"] = "normal"
    content["modules_info"] = data["modules_info"]
    content["warning_msgs"] = data["warning_msgs"]
    content["total_norows"] = data["total_norows"]
    content["ftable_uid"] = reporter.ftable_uid
    t = round(time.time() - start_time, 3)
    if logger is not None:
        logger.info("Done getting result of [{}][{}] in {}s".format(dbname, tab, t))
    return web.json_response(content)


async def get_pagesize(request, valueonly=False):
    from ...lib.system import get_user_conf
    from ...lib.system import get_system_conf

    user_conf = get_user_conf()
    sys_conf = get_system_conf()
    try:
        queries = await request.json()
    except Exception:
        queries = {}
    gui_result_pagesize = queries.get(
        "pagesize",
        user_conf.get(
            gui_result_pagesize_key,
            sys_conf.get(gui_result_pagesize_key, default_gui_result_pagesize),
        ),
    )
    if gui_result_pagesize:
        gui_result_pagesize = int(gui_result_pagesize)
    if valueonly:
        return gui_result_pagesize
    else:
        content = {"gui_result_pagesize": gui_result_pagesize}
        return web.json_response(content)


async def get_num_var_limit_for_summary_widget(_):
    from ...lib.system import get_system_conf
    from ..consts import DEFAULT_RESULT_VIEWER_NUM_VAR_LIMIT_FOR_SUMMARY_WIDGET
    from ..consts import result_viewer_num_var_limit_for_summary_widget_key

    sys_conf = get_system_conf()
    num_var_limit = sys_conf.get(
        result_viewer_num_var_limit_for_summary_widget_key,
        DEFAULT_RESULT_VIEWER_NUM_VAR_LIMIT_FOR_SUMMARY_WIDGET,
    )
    num_var_limit = int(num_var_limit)
    return web.json_response({"num_var_limit": num_var_limit})


async def get_result_levels(request):
    from aiohttp.web import Response
    from ...lib.system import get_system_conf

    sys_conf = get_system_conf()
    gui_result_pagesize = sys_conf.get(
        "gui_result_pagesize", default_gui_result_pagesize
    )
    content = {"gui_result_pagesize": gui_result_pagesize}
    dbpath = await get_dbpath(request)
    content = {}
    if not dbpath:
        content["levels"] = ["NODB"]
    else:
        conn = await get_db_conn(dbpath)
        if not conn:
            return Response(status=500)
        cursor = await conn.cursor()
        sql = (
            'select name from sqlite_master where type="table" and '
            + 'name like "%_header"'
        )
        await cursor.execute(sql)
        ret = await cursor.fetchall()
        if len(ret) > 0:  # type: ignore
            levels = [v[0].split("_")[0] for v in ret]
            levels.insert(0, "info")
            levels.insert(1, "filter")
        else:
            levels = []
        levels.remove("sample")
        levels.remove("mapping")
        content["levels"] = levels
        await cursor.close()
        await conn.close()
    return web.json_response(content)


async def get_request_json_from_post(request) -> dict:
    try:
        queries = await request.json()
    except Exception:
        t = await request.text()
        rep_d = {
            "%2F": "/",
            "%40": "@",
            "%7B": "{",
            "%22": '"',
            "%3A": ":",
            "%5B": "[",
            "%2C": ",",
            "%5D": "]",
            "%7D": "}",
        }
        for k, v in rep_d.items():
            t = t.replace(k, v)
        parts = t.split("&")
        d = {}
        for part in parts:
            kv = part.split("=")
            k = kv[0]
            v = kv[1]
            if v == "":
                d[k] = None
            else:
                v0 = v[0]
                if v0 not in ["{", "["] and not (v0 >= "0" and v0 <= "9"):
                    v = f'"{v}"'
                d[k] = json.loads(v)
        queries = d
    return queries


async def get_dbpath(request) -> Optional[str]:
    from ..util import get_email_from_request
    from ..serveradmindb import get_serveradmindb

    global servermode
    global wu
    method = request.method
    queries = None
    if method == "GET":
        queries = request.rel_url.query
    elif method == "POST":
        queries = await get_request_json_from_post(request)
    if not queries:
        return None
    dbpath = queries.get("dbpath")
    if dbpath:
        return dbpath
    username = get_email_from_request(request, servermode)
    uid = queries.get("uid")
    if uid and username:
        serveradmindb = await get_serveradmindb()
        dbpath = await serveradmindb.get_dbpath_by_eud(
            eud={"uid": uid, "username": username}
        )
    return dbpath


async def get_variant_cols(request):
    queries = request.rel_url.query
    dbpath = await get_dbpath(request)
    confpath = queries.get("confpath")
    filterstring = queries.get("filter")
    add_summary = queries.get("add_summary", True)
    data = {}
    data["data"] = {}
    data["stat"] = {}
    data["status"] = {}
    colinfo = await get_colinfo(
        dbpath, confpath=confpath, filterstring=filterstring, add_summary=add_summary
    )
    data["columns"] = {}
    if "variant" in colinfo:
        data["columns"]["variant"] = get_colmodel("variant", colinfo)
    if "gene" in colinfo:
        data["columns"]["gene"] = get_colmodel("gene", colinfo)
    content = data
    return web.json_response(content)


def get_datamodel(data):
    ret = []
    for row in data:
        ret.append(list(row))
    return ret


def get_colmodel(tab, colinfo):
    colModel = []
    groupkeys_ordered = []
    groupnames = {}
    for d in colinfo[tab]["colgroups"]:
        groupnames[d["name"]] = [d["displayname"], d["count"]]
        groupkeys_ordered.append(d["name"])
    dataindx = 0
    for groupkey in groupkeys_ordered:
        [grouptitle, col_count] = groupnames[groupkey]
        columngroupdef = {"name": groupkey, "title": grouptitle, "colModel": []}
        startidx = dataindx
        endidx = startidx + col_count
        genesummary_present = False
        for d in colinfo[tab]["columns"][startidx:endidx]:
            cats = d["col_cats"]
            column = {
                "col": d["col_name"],
                "colgroupkey": groupkey,
                "colgroup": grouptitle,
                "title": d["col_title"],
                "align": "center",
                "dataIndx": dataindx,
                "retfilt": False,
                "retfilttype": "None",
                "multiseloptions": [],
                "reportsub": d["reportsub"] if "reportsub" in d else {},
                "categories": cats,
                "width": d["col_width"],
                "desc": d["col_desc"],
                "type": d["col_type"],
                "hidden": d["col_hidden"],
                "default_hidden": d["col_hidden"],
                "ctg": d["col_ctg"],
                "filterable": d["col_filterable"],
                "hide_from_gui_filter": d["col_hide_from_gui_filter"],
                "link_format": d.get("link_format"),
                "level": d.get("level"),
            }
            if d["col_type"] == "string":
                column["align"] = "left"
                if d["col_ctg"] == "single":
                    column["filter"] = {
                        "type": "select",
                        "attr": "multiple",
                        "condition": "equal",
                        "options": cats,
                        "listeners": ["change"],
                    }
                    column["retfilt"] = True
                    column["retfilttype"] = "select"
                    column["multiseloptions"] = cats
                elif d["col_ctg"] == "multi":
                    column["filter"] = {
                        "type": "select",
                        "attr": "multiple",
                        "condition": "contain",
                        "options": cats,
                        "listeners": ["change"],
                    }
                    column["retfilt"] = True
                    column["retfilttype"] = "select"
                    column["multiseloptions"] = cats
                else:
                    column["filter"] = {
                        "type": "textbox",
                        "condition": "contain",
                        "listeners": ["keyup"],
                    }
                    column["retfilt"] = True
                    column["retfilttype"] = "regexp"
                    column["multiseloptions"] = []
            elif d["col_type"] == "float" or d["col_type"] == "int":
                column["align"] = "right"
                column["filter"] = {
                    "type": "textbox",
                    "condition": "between",
                    "listeners": ["keyup"],
                }
                column["retfilt"] = True
                column["retfilttype"] = "between"
                column["dataType"] = "float"
                column["multiseloptions"] = []
            if "col_genesummary" in d and d["col_genesummary"] is True:
                genesummary_present = True
            columngroupdef["colModel"].append(column)
            dataindx += 1
        if genesummary_present:
            columngroupdef["genesummary"] = True
        colModel.append(columngroupdef)
    return colModel


async def get_colinfo(dbpath, confpath=None, filterstring=None, add_summary=True):
    import importlib
    import importlib.util
    from pathlib import Path

    reporter_name = "jsonreporter"
    this_file_dir = Path(__file__).parent
    reporter_path = this_file_dir / f"{reporter_name}.py"
    spec = importlib.util.spec_from_file_location(reporter_name, reporter_path)
    if spec is None:
        raise Exception(f"Could not load {reporter_name}.")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)  # type: ignore
    reporter = m.Reporter(
        dbpath,
        module_name=reporter_name,
        confpath=confpath,
        filterstring=filterstring,
        report_types=["text"],
    )
    await reporter.prep()
    # reporter_levels = await reporter.get_levels_to_run("all")
    # reporter.levels = reporter_levels
    try:
        colinfo = await reporter.get_variant_colinfo(
            add_summary=add_summary, make_col_categories=True
        )
        await reporter.close_db()
        if reporter.cf is not None:
            await reporter.cf.close_db()
    except:
        await reporter.close_db()
        if reporter.cf is not None:
            await reporter.cf.close_db()
        raise
    return colinfo


async def table_exists(cursor, table):
    q = (
        'select name from sqlite_master where type="table" and '
        + 'name="'
        + table
        + '"'
    )
    await cursor.execute(q)
    r = await cursor.fetchone()
    if r is None:
        return False
    else:
        return True


def serve_widgetfile(request):
    from aiohttp.web import Response
    from ...lib.system import get_modules_dir

    modules_dir = get_modules_dir()
    if not modules_dir:
        return Response(status=404)
    filepath = os.path.join(
        modules_dir,
        "webviewerwidgets",
        request.match_info["module_dir"],
        request.match_info["filename"],
    )
    if os.path.exists(filepath):
        response = web.FileResponse(filepath)
        response.headers["Cache-Control"] = "no-cache"
        return response


async def serve_runwidget(request):
    from aiohttp.web import Response
    import importlib
    import importlib.util
    from ...lib.system import get_modules_dir

    modules_dir = get_modules_dir()
    if not modules_dir:
        return Response(status=404)
    module_name = "wg" + request.match_info["module"]
    queries = request.rel_url.query
    dbpath = await get_dbpath(request) or ""
    if ("dbpath" not in queries or queries["dbpath"] == "") and dbpath is not None:
        new_queries = {}
        new_queries["dbpath"] = dbpath
        for key in queries:
            if key != "dbpath":
                new_queries[key] = queries[key]
        queries = new_queries
    module_dir = modules_dir / "webviewerwidgets" / module_name
    module_path = module_dir / f"{module_name}.py"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None:
        raise Exception(f"Could not load {module_name}.")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)  # type: ignore
    cf = await ReportFilter.create(dbpath=dbpath, mode="sub")
    filterstring = await cf.exec_db(
        cf.get_report_filter_string, uid=queries.get("ftable_uid")
    )
    queries_dict = queries.copy()
    queries_dict["filterstring"] = filterstring
    content = await m.get_data(queries_dict)
    return web.json_response(content)


async def serve_webapp_runwidget(request):
    from aiohttp.web import Response
    import importlib
    import importlib.util
    from ...lib.system import get_modules_dir

    modules_dir = get_modules_dir()
    if not modules_dir:
        return Response(status=404)
    module_name = request.match_info["module"]
    widget_name = request.match_info["widget"]
    widget_module_name = "wg" + widget_name
    queries = request.rel_url.query
    tmp_queries = {}
    for key in queries:
        tmp_queries[key] = queries[key]
    queries = tmp_queries
    module_dir = modules_dir / "webapps" / module_name / "widgets" / widget_module_name
    module_path = module_dir / f"{widget_module_name}.py"
    spec = importlib.util.spec_from_file_location(widget_module_name, module_path)
    if spec is None:
        raise Exception(f"Could not load {module_name}.")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)  # type: ignore
    content = await m.get_data(queries)
    return web.json_response(content)


async def serve_runwidget_post(request):
    from aiohttp.web import Response
    import importlib
    import importlib.util
    from ...lib.system import get_modules_dir

    modules_dir = get_modules_dir()
    if not modules_dir:
        return Response(status=404)
    module_name = "wg" + request.match_info["module"]
    dbpath = await get_dbpath(request)
    queries = await get_request_json_from_post(request)
    new_queries = {}
    for k in queries:
        val = queries[k]
        if type(val) is not str:
            pass
        else:
            if val is None:
                val = '""'
            elif val == "":
                val = '""'
            elif val.startswith("{") and val.endswith("}"):
                pass
            elif val.startswith("[") and val.endswith("]"):
                pass
            else:
                val = '"' + val + '"'
            if sys.platform in ["win32"]:
                val = val.replace("\\", "\\\\")
            val = json.loads(val)
        new_queries[k] = val
    queries = new_queries
    if ("dbpath" not in queries or queries["dbpath"] == "") and dbpath is not None:
        new_queries = {}
        new_queries["dbpath"] = dbpath
        for key in queries:
            if key != "dbpath":
                new_queries[key] = queries[key]
        queries = new_queries
    module_dir = modules_dir / "webviewerwidgets" / module_name
    module_path = module_dir / f"{module_name}.py"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None:
        raise Exception(f"Could not load {module_name}.")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)  # type: ignore
    content = await m.get_data(queries)
    return web.json_response(content)


async def get_modules_info(request):
    from aiohttp.web import Response
    from json import loads

    _ = request.rel_url.query
    dbpath = await get_dbpath(request)
    conn = await get_db_conn(dbpath)
    content = {}
    if not conn:
        return Response(status=500)
    cursor = await conn.cursor()
    q = 'select colval from info where colkey="annotator_descs"'
    await cursor.execute(q)
    r = await cursor.fetchone()
    if r is None or r[0] == "{}":
        # TODO: backward-compatibility. Remove after a while. 11/22/2022.
        q = 'select colval from info where colkey="_annotator_desc"'
        await cursor.execute(q)
        r = await cursor.fetchone()
    if not r or r[0] == "{}":
        content = {}
    else:
        try:
            content = loads(r[0])
        except Exception:
            # TODO: backward-compatibility. Remove after a while.
            s = r[0].strip("{").strip("}")
            toks = s.split("', '")
            d = {}
            for tok in toks:
                t2 = tok.split(":")
                k = t2[0].strip().strip("'").replace("'", "'")
                v = t2[1].strip().strip("'").replace("'", "'")
                d[k] = v
            content = d
    await cursor.close()
    await conn.close()
    return content


async def get_samples(request):
    from aiohttp.web import Response

    dbpath = await get_dbpath(request)
    conn = await get_db_conn(dbpath)
    samples = []
    if not conn:
        return Response(status=500)
    cursor = await conn.cursor()
    sample_table = "sample"
    if await table_exists(cursor, sample_table):
        q = f"select distinct base__sample_id from {sample_table};"
        await cursor.execute(q)
        rows = await cursor.fetchall()
        samples = [r[0] for r in rows]
    await cursor.close()
    await conn.close()
    return web.json_response(samples)


async def get_variants_for_hugo(request):
    from aiohttp.web import Response
    from ...lib.exceptions import DatabaseConnectionError

    hugo = request.match_info["hugo"]
    dbpath = await get_dbpath(request)
    if dbpath is None:
        raise DatabaseConnectionError("result database")
    conn = await get_db_conn(dbpath)
    if not conn:
        return Response(status=500)
    cursor = await conn.cursor()
    q = "select * from variant where base__hugo=?"
    await cursor.execute(q, (hugo,))
    rows = await cursor.fetchall()
    out = []
    for row in rows:
        out.append(list(row))
    await cursor.close()
    await conn.close()
    return web.json_response(out)


async def get_variantdbcols(request):
    from aiohttp.web import Response
    from ...lib.exceptions import DatabaseConnectionError

    dbpath = await get_dbpath(request)
    if dbpath is None:
        raise DatabaseConnectionError("result database")
    conn = await get_db_conn(dbpath)
    if not conn:
        return Response(status=500)
    cursor = await conn.cursor()
    q = "select sql from sqlite_master where name='variant'"
    await cursor.execute(q)
    row = await cursor.fetchone()
    if not row:
        return
    out = {}
    coldef = row[0].split("(")[1].split(")")[0]
    for el in coldef.split(", "):
        out[el.split(" ")[0]] = len(out)
    await conn.close()
    return web.json_response(out)


routes = []
routes.append(["GET", "/result/service/variantcols", get_variant_cols])
routes.append(["GET", "/result/service/getresulttablelevels", get_result_levels])
routes.append(["POST", "/result/service/result", get_result])
routes.append(["POST", "/result/service/count", get_count])
routes.append(["GET", "/result/service/widgetlist", get_widgetlist])
routes.append(["GET", "/result/service/status", get_status])
routes.append(["POST", "/result/service/savelayoutsetting", save_layout_setting])
routes.append(["GET", "/result/service/loadfiltersetting", load_filter_setting])
routes.append(["GET", "/result/service/loadlayoutsetting", load_layout_setting])
routes.append(["GET", "/result/service/deletelayoutsetting", delete_layout_setting])
routes.append(["GET", "/result/service/renamelayoutsetting", rename_layout_setting])
routes.append(["GET", "/result/service/getlayoutsavenames", get_layout_save_names])
routes.append(["GET", "/result/service/getfiltersavenames", get_filter_save_names])
routes.append(["GET", "/result/service/getnowgannotmodules", get_nowg_annot_modules])
routes.append(["GET", "/result/widgetfile/{module_dir}/{filename}", serve_widgetfile])
routes.append(["GET", "/result/runwidget/{module}", serve_runwidget])
routes.append(["POST", "/result/runwidget/{module}", serve_runwidget_post])
routes.append(["GET", "/result/service/samples", get_samples])
routes.append(["GET", "/webapps/{module}/widgets/{widget}", serve_webapp_runwidget])
routes.append(["GET", "/result/service/{hugo}/variants", get_variants_for_hugo])
routes.append(["GET", "/result/service/variantdbcols", get_variantdbcols])
routes.append(["GET", "/result/service/pagesize", get_pagesize])
routes.append(
    ["GET", "/result/service/summaryvarlimit", get_num_var_limit_for_summary_widget]
)
