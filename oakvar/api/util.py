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
from typing import List
from typing import Union
from pathlib import Path


def job_to_gui(args, __name__="util to-gui"):
    from shutil import copyfile
    from pathlib import Path
    import sqlite3
    import json
    import copy
    from types import SimpleNamespace
    from ..lib.system import get_jobs_dir
    from ..lib.consts import LOG_SUFFIX
    from ..gui.serveradmindb import setup_serveradmindb
    from ..lib.util.admin_util import oakvar_version

    dbpath = Path(args.path)
    run_name = dbpath.stem
    user = args.user
    jobs_dir = get_jobs_dir()
    user_dir = jobs_dir / user
    if not user_dir.is_dir():
        exit(f"User {user} not found")
    conn = sqlite3.connect(dbpath)
    c = conn.cursor()
    c.execute("select * from info")
    info = {
        "db_path": str(dbpath.absolute()),
        "runtime": 0,
        "note": "",
        "status": "finished",
        "postaggregators": [],
        "viewable": True,
        "report_types": [],
        "package_version": oakvar_version(),
        "run_name": run_name,
    }
    modules = []
    job = SimpleNamespace()
    for row in c.fetchall():
        colkey = row[0]
        colval = row[1]
        if colkey == "inputs":
            inputs = json.loads(colval)
            orig_input_fname = []
            orig_input_path = []
            for p in inputs:
                pt = Path(p)
                orig_input_fname.append(pt.name)
                orig_input_path.append(str(pt.absolute()))
            info["orig_input_fname"] = orig_input_fname
            info["orig_input_path"] = orig_input_path
        elif colkey == "job_name":
            job.job_name = colval
            info["job_name"] = [colval]
            job_id = colval
            job_dir: Path = user_dir / job_id
            num: int = 0
            while job_dir.exists():
                num += 1
                job_dir = job_dir.with_name(f"{job_id}_{num}")
            info["dir"] = str(job_dir)
            info["job_dir"] = [str(job_dir)]
            job.dir = str(job_dir)
            job_dir.mkdir()
            new_dbpath = job_dir / dbpath.name
            copyfile(dbpath, new_dbpath)
            log_path = dbpath.with_suffix(LOG_SUFFIX)
            if log_path.exists():
                copyfile(log_path, job_dir / log_path.name)
            err_path = dbpath.with_suffix(".err")
            if err_path.exists():
                copyfile(err_path, job_dir / err_path.name)
        elif colkey == "created_at":
            info["submission_time"] = colval
        elif colkey == "num_variants":
            info["numinput"] = int(colval)
        elif colkey == "annotators":
            annotators = [
                v.split("==")[0]
                for v in json.loads(colval)
                if not v.startswith("original_input")
            ]
            info["annotators"] = annotators
            modules.extend(annotators)
        elif colkey == "postaggregators":
            postaggregators = [v.split("==")[0] for v in json.loads(colval)]
            info["annotators"] = postaggregators
            modules.extend(postaggregators)
        elif colkey == "genome_assemblies":
            info["assembly"] = json.loads(colval)[0]
    info["info_json"] = copy.deepcopy(info)
    job.info = info
    job.status = "Finished"
    serveradmindb = setup_serveradmindb()
    serveradmindb.add_job_info_sync(user, job)
    return True


def variant_id(chrom, pos, ref, alt):
    """variant_id.

    Args:
        chrom:
        pos:
        ref:
        alt:
    """
    return chrom + str(pos) + ref + alt


def sqliteinfo(dbpath: Union[Path, str], fmt: str = "json", outer=None):
    """sqliteinfo.

    Args:
        dbpath (str): Path to a result SQLite file
        fmt (str): json or yaml
        outer: Deprecated
    """
    from oyaml import dump
    from ..lib.util.db import get_sqliteinfo

    _ = outer
    out = get_sqliteinfo(dbpath)
    if fmt == "json":
        return out
    elif fmt == "yaml":
        return str(dump(out, default_flow_style=False))
    else:
        return out


def mergesqlite(dbpaths: List[str] = [], outpath: str = ""):
    """mergesqlite.

    Args:
        dbpaths (List[str]): dbpaths
        outpath (str): outpath
    """
    import sqlite3
    from json import loads, dumps
    from shutil import copy

    if len(dbpaths) < 2:
        exit("Multiple sqlite file paths should be given")
    if outpath.endswith(".sqlite") is False:
        outpath = outpath + ".sqlite"
    # Checks columns being the same.
    conn = sqlite3.connect(dbpaths[0])
    c = conn.cursor()
    c.execute("select col_name from variant_header")
    v_cols = sorted([r[0] for r in c.fetchall()])
    c.execute("select col_name from gene_header")
    g_cols = sorted([r[0] for r in c.fetchall()])
    c.close()
    conn.close()
    for dbpath in dbpaths[1:]:
        conn = sqlite3.connect(dbpath)
        c = conn.cursor()
        c.execute("select col_name from variant_header")
        if v_cols != sorted([r[0] for r in c.fetchall()]):
            exit("Annotation columns mismatch (variant table)")
        c.execute("select col_name from gene_header")
        if g_cols != sorted([r[0] for r in c.fetchall()]):
            exit("Annotation columns mismatch (gene table)")
    # Copies the first db.
    print(f"Copying {dbpaths[0]} to {outpath}...")
    copy(dbpaths[0], outpath)
    outconn = sqlite3.connect(outpath)
    outc = outconn.cursor()
    # Gets key column numbers.
    outc.execute("select col_name from variant_header order by rowid")
    cols = [r[0] for r in outc.fetchall()]
    v_chrom_colno = cols.index("base__chrom")
    v_pos_colno = cols.index("base__pos")
    v_ref_colno = cols.index("base__ref_base")
    v_alt_colno = cols.index("base__alt_base")
    outc.execute("select col_name from gene_header order by rowid")
    cols = [r[0] for r in outc.fetchall()]
    g_hugo_colno = cols.index("base__hugo")
    outc.execute("select col_name from sample_header order by rowid")
    cols = [r[0] for r in outc.fetchall()]
    s_uid_colno = cols.index("base__uid")
    outc.execute("select col_name from mapping_header order by rowid")
    cols = [r[0] for r in outc.fetchall()]
    m_uid_colno = cols.index("base__uid")
    m_fileno_colno = cols.index("base__fileno")
    outc.execute("select max(base__uid) from variant")
    new_uid = outc.fetchone()[0] + 1
    # Input paths
    outc.execute('select colkey, colval from info where colkey="_input_paths"')
    input_paths = loads(outc.fetchone()[1].replace("'", '"'))
    new_fileno = max([int(v) for v in input_paths.keys()]) + 1
    rev_input_paths = {}
    for fileno, filepath in input_paths.items():
        rev_input_paths[filepath] = fileno
    # Makes initial hugo and variant id lists.
    outc.execute("select base__hugo from gene")
    genes = {r[0] for r in outc.fetchall()}
    outc.execute(
        "select base__chrom, base__pos, base__ref_base, base__alt_base from variant"
    )
    variants = {variant_id(r[0], r[1], r[2], r[3]) for r in outc.fetchall()}
    for dbpath in dbpaths[1:]:
        print(f"Merging {dbpath}...")
        conn = sqlite3.connect(dbpath)
        c = conn.cursor()
        # Gene
        c.execute("select * from gene order by rowid")
        for r in c.fetchall():
            hugo = r[g_hugo_colno]
            if hugo in genes:
                continue
            q = f'insert into gene values ({",".join(["?" for _ in range(len(r))])})'
            outc.execute(q, r)
            genes.add(hugo)
        # Variant
        uid_dic = {}
        c.execute("select * from variant order by rowid")
        for r in c.fetchall():
            vid = variant_id(
                r[v_chrom_colno], r[v_pos_colno], r[v_ref_colno], r[v_alt_colno]
            )
            if vid in variants:
                continue
            old_uid = r[0]
            r = list(r)
            r[0] = new_uid
            uid_dic[old_uid] = new_uid
            new_uid += 1
            q = f'insert into variant values ({",".join(["?" for _ in range(len(r))])})'
            outc.execute(q, r)
            variants.add(vid)
        # Sample
        c.execute("select * from sample order by rowid")
        for r in c.fetchall():
            uid = r[s_uid_colno]
            if uid in uid_dic:
                new_uid = uid_dic[uid]
                r = list(r)
                r[s_uid_colno] = new_uid
                q = f'insert into sample values ({",".join(["?" for _ in range(len(r))])})'
                outc.execute(q, r)
        # File numbers
        c.execute('select colkey, colval from info where colkey="_input_paths"')
        ips = loads(c.fetchone()[1].replace("'", '"'))
        fileno_dic = {}
        for fileno, filepath in ips.items():
            if filepath not in rev_input_paths:
                input_paths[str(new_fileno)] = filepath
                rev_input_paths[filepath] = str(new_fileno)
                fileno_dic[int(fileno)] = new_fileno
                new_fileno += 1
        # Mapping
        c.execute("select * from mapping order by rowid")
        for r in c.fetchall():
            uid = r[m_uid_colno]
            if uid in uid_dic:
                new_uid = uid_dic[uid]
                r = list(r)
                r[m_uid_colno] = new_uid
                r[m_fileno_colno] = fileno_dic[r[m_fileno_colno]]
                q = f'insert into mapping values ({",".join(["?" for _ in range(len(r))])})'
                outc.execute(q, r)
    q = 'update info set colval=? where colkey="_input_paths"'
    outc.execute(q, [dumps(input_paths)])
    q = 'update info set colval=? where colkey="Input file name"'
    v = ";".join(
        [input_paths[str(v)] for v in sorted(input_paths.keys(), key=lambda v: int(v))]
    )
    outc.execute(q, [v])
    outconn.commit()
    return True


def filtersqlite(
    dbpaths: List[str] = [],
    suffix: str = "filtered",
    out: str = ".",
    filterpath: Optional[str] = None,
    filtersql: Optional[str] = None,
    includesample: List[str] = [],
    excludesample: List[str] = [],
):
    """filtersqlite.

    Args:
        dbpaths (List[str]): dbpaths
        suffix (str): suffix
        filterpath (Optional[str]): filterpath
        filtersql (Optional[str]): filtersql
        includesample (List[str]): includesample
        excludesample (List[str]): excludesample
    """
    from ..lib.util.asyn import get_event_loop

    loop = get_event_loop()
    return loop.run_until_complete(
        filtersqlite_async(
            dbpaths=dbpaths,
            suffix=suffix,
            out=out,
            filterpath=filterpath,
            filtersql=filtersql,
            includesample=includesample,
            excludesample=excludesample,
        )
    )


async def filtersqlite_async_drop_copy_table(cursor_old, conn_new, table_name):
    """filtersqlite_async_drop_copy_table.

    Args:
        c:
        table_name:
    """
    print(f"- {table_name}")
    await conn_new.execute(f"drop table if exists {table_name}")
    await cursor_old.execute(f"select sql from sqlite_master where name='{table_name}'")
    ret = await cursor_old.fetchone()
    if ret is None:
        raise Exception(f"Table {table_name} not found")
    sql = ret[0]
    await conn_new.execute(sql)
    await cursor_old.execute(f"select * from {table_name}")
    q = f"insert into {table_name} values ({','.join(['?' for _ in cursor_old.description])})"
    ret = await cursor_old.fetchall()
    for row in ret:
        if row is None:
            continue
        await conn_new.execute(q, row)


async def filtersqlite_async(
    dbpaths: List[str] = [],
    suffix: str = "filtered",
    out: str=".",
    filterpath: Optional[str] = None,
    filtersql: Optional[str] = None,
    includesample: List[str] = [],
    excludesample: List[str] = [],
):
    """filtersqlite_async.

    Args:
        dbpaths (List[str]): dbpaths
        suffix (str): suffix
        filterpath (Optional[str]): filterpath
        filtersql (Optional[str]): filtersql
        includesample (List[str]): includesample
        excludesample (List[str]): excludesample
    """
    from os import remove
    from os.path import exists
    import aiosqlite
    from .. import ReportFilter

    for dbpath in dbpaths:
        if not dbpath.endswith(".sqlite"):
            print("  Skipping")
            continue
        opath = Path(out) / f"{dbpath[:-7]}.{suffix}.sqlite"
        print(f"{opath}")
        if exists(opath):
            remove(opath)
        try:
            cf = await ReportFilter.create(
                dbpath=dbpath,
                filterpath=filterpath,
                filtersql=filtersql,
                includesample=includesample,
                excludesample=excludesample,
            )
            await cf.exec_db(cf.loadfilter)
            if (
                hasattr(cf, "filter") is False
                or cf.filter is None
                or type(cf.filter) is not dict
            ):
                from ..lib.exceptions import FilterLoadingError
                raise FilterLoadingError()
            conn_read, conn_write = await cf.get_db_conns()
            if conn_read is None or conn_write is None:
                from ..lib.exceptions import FilterLoadingError
                raise FilterLoadingError()
            cursor_read = await conn_read.cursor()
            conn_new = await aiosqlite.connect(opath)
            for table_name in [
                "info",
                "viewersetup",
                "variant_annotator",
                "variant_header",
                "variant_reportsub",
                "gene_annotator",
                "gene_header",
                "gene_reportsub",
                "sample_annotator",
                "sample_header",
                "mapping_annotator",
                "mapping_header",
            ]:
                await filtersqlite_async_drop_copy_table(cursor_read, conn_new, table_name)
            await conn_new.commit()
            # Pragma
            #c.execute("pragma journal_mode=off")
            #c.execute("pragma synchronous=off")
            ftable_uid = await cf.make_ftables_and_ftable_uid()
            # Variant
            await cursor_read.execute("select sql from sqlite_master where name='variant'")
            sql = await cursor_read.fetchone()
            if sql is None:
                raise Exception("variant table not found")
            sql = sql[0]
            print("- variant")
            await conn_new.execute("drop table if exists variant")
            await conn_new.execute(sql)
            await cf.get_level_data_iterator("variant", uid=ftable_uid, cursor_read=cursor_read)
            q = f"insert into variant values ({','.join(['?' for _ in cursor_read.description])})"
            num_vars = 0
            for row in await cursor_read.fetchall():
                await conn_new.execute(q, row)
                num_vars += 1
            await conn_new.commit()
            # Gene
            print("- gene")
            await cursor_read.execute("select sql from sqlite_master where name='gene'")
            sql = await cursor_read.fetchone()
            if sql is None:
                raise Exception("gene table not found")
            sql = sql[0]
            await conn_new.execute("drop table if exists gene")
            await conn_new.execute(sql)
            await cf.get_level_data_iterator("gene", uid=ftable_uid, cursor_read=cursor_read)
            q = f"insert into main.gene values ({",".join(['?' for _ in cursor_read.description])})"
            for row in await cursor_read.fetchall():
                await conn_new.execute(q, row)
            await conn_new.commit()
            # Sample
            print("- sample")
            await cursor_read.execute("select sql from sqlite_master where name='sample'")
            sql = await cursor_read.fetchone()
            if sql is None:
                raise Exception("sample table not found")
            sql = sql[0]
            await conn_new.execute("drop table if exists sample")
            await conn_new.execute(sql)
            await cf.get_level_data_iterator("sample", uid=ftable_uid, cursor_read=cursor_read)
            q = f"insert into sample values ({','.join(['?' for _ in cursor_read.description])})"
            for row in await cursor_read.fetchall():
                await conn_new.execute(q, row)
            await conn_new.commit()
            # Mapping
            await cursor_read.execute("select sql from sqlite_master where name='mapping'")
            sql = await cursor_read.fetchone()
            if sql is None:
                raise Exception("mapping table not found")
            sql = sql[0]
            await conn_new.execute("drop table if exists mapping")
            await conn_new.execute(sql)
            await cf.get_level_data_iterator("mapping", uid=ftable_uid, cursor_read=cursor_read)
            q = f"insert into mapping values ({','.join(['?' for _ in cursor_read.description])})"
            for row in await cursor_read.fetchall():
                if row is None:
                    continue
                await conn_new.execute(q, row)
            # Indices
            await cursor_read.execute("select name, sql from sqlite_master where type='index'")
            for r in await cursor_read.fetchall():
                index_name = r[0]
                sql = r[1]
                if sql is not None:
                    print(f"- {index_name}")
                    await conn_new.execute(sql)
            await conn_new.commit()
            # Info
            print("- info")
            await conn_new.execute(
                f'update info set colval={num_vars} where colkey="num_variants"'
            )
            await conn_new.commit()
            await cf.close_db()
            await cursor_read.close()
            await conn_read.close()
            await conn_write.close()
            await conn_new.close()
            print(f"{opath} generated")
        except Exception as e:
            raise e


def move_job(job_dir="", new_account="", outer=None):
    """move_job_to_account.

    Args:
        job_dir:
        new_account:
    """
    from ..lib.util.db import move_job_to_account

    if not job_dir:
        msg = "Job directory (--job-dir) should be given"
        if outer:
            outer.error(msg)
            return
        else:
            return msg
    if not new_account:
        msg = "New account (--new-account) should be given"
        if outer:
            outer.error(msg)
            return
        else:
            return msg
    return move_job_to_account(job_dir, new_account)
