from typing import Optional
from typing import List

# def addjob(args, __name__="util addjob"):
#    from shutil import copyfile
#    from time import sleep
#    from datetime import datetime
#    from ..lib.system import get_jobs_dir
#    from ..lib.consts import LOG_SUFFIX
#
#    dbpath = args.path
#    user = args.user
#    jobs_dir = get_jobs_dir()
#    user_dir = jobs_dir / user
#    if not user_dir.is_dir():
#        exit(f"User {user} not found")
#    attempts = 0
#    while (
#        True
#    ):  # TODO this will currently overwrite if called in parallel. is_dir check and creation is not atomic
#        job_id = datetime.now().strftime(r"%y%m%d-%H%M%S")
#        job_dir = user_dir / job_id
#        if not job_dir.is_dir():
#            break
#        else:
#            attempts += 1
#            sleep(1)
#        if attempts >= 5:
#            exit(
#                "Could not acquire a job id. Too many concurrent job submissions. Wait, or reduce submission frequency."
#            )
#    job_dir.mkdir()
#    new_dbpath = job_dir / dbpath.name
#    copyfile(dbpath, new_dbpath)
#    log_path = dbpath.with_suffix(LOG_SUFFIX)
#    if log_path.exists():
#        copyfile(log_path, job_dir / log_path.name)
#    err_path = dbpath.with_suffix(".err")
#    if err_path.exists():
#        copyfile(err_path, job_dir / err_path.name)
#    return True


def variant_id(chrom, pos, ref, alt):
    """variant_id.

    Args:
        chrom:
        pos:
        ref:
        alt:
    """
    return chrom + str(pos) + ref + alt


def get_sqliteinfo(fmt: str = "json", outer=None, dbpaths: List[str] = []):
    """get_sqliteinfo.

    Args:
        fmt (str): fmt
        outer:
        dbpaths (List[str]): dbpaths
    """
    import sqlite3
    from json import loads
    from oyaml import dump

    width_colname = 30
    width_coltitle = 40
    ret_list = []
    ret_dict = {}
    for dbpath in dbpaths:
        if fmt == "text":
            s = f"# SQLite file:\n{dbpath}"
            ret_list.append(s)
        elif fmt in ["json", "yaml"]:
            ret_dict["dbpath"] = dbpath
        conn = sqlite3.connect(dbpath)
        c = conn.cursor()
        c.execute('select colval from info where colkey="_input_paths"')
        ret = c.fetchone()
        if not ret:
            c.execute('select colval from info where colkey="inputs"')
            ret = c.fetchone()
        input_paths = loads(ret[0].replace("'", '"'))
        if fmt == "text":
            s = f"\n# Input files:"
            ret_list.append(s)
            if isinstance(input_paths, dict):
                for p in input_paths.values():
                    s = f"{p}"
                    ret_list.append(s)
            elif isinstance(input_paths, list):
                ret_list.extend(input_paths)
        elif fmt in ["json", "yaml"]:
            if isinstance(input_paths, dict):
                ret_dict["inputs"] = list(input_paths.values())
            elif isinstance(input_paths, list):
                ret_dict["inputs"] = input_paths
        if fmt == "text":
            s = f"\n# Output columns"
            ret_list.append(s)
            s = f'{"# Name".ljust(width_colname)} {"Title".ljust(width_coltitle)} Type'
            ret_list.append(s)
        else:
            ret_dict["output_columns"] = {}
        c.execute("select col_name, col_def from variant_header")
        rs = c.fetchall()
        if fmt in ["json", "yaml"]:
            ret_dict["output_columns"] = {}
            ret_dict["output_columns"]["variant"] = []
            ret_dict["output_columns"]["gene"] = []
        for r in rs:
            col_name, col_def = r
            col_def = loads(col_def)
            if fmt == "text":
                s = f"{col_name.ljust(width_colname)} {col_def['title'].ljust(width_coltitle)} {col_def['type']}"
                ret_list.append(s)
            elif fmt in ["json", "yaml"]:
                ret_dict["output_columns"]["variant"].append(
                    {
                        "name": col_name,
                        "title": col_def["title"],
                        "type": col_def["type"],
                    }
                )
        c.execute("select col_name, col_def from gene_header")
        rs = c.fetchall()
        for r in rs:
            col_name, col_def = r
            col_def = loads(col_def)
            if fmt == "text":
                s = f"{col_name.ljust(width_colname)} {col_def['title'].ljust(width_coltitle)} {col_def['type']}"
                ret_list.append(s)
            elif fmt in ["json", "yaml"]:
                ret_dict["output_columns"]["gene"].append(
                    {
                        "name": col_name,
                        "title": col_def["title"],
                        "type": col_def["type"],
                    }
                )
        c.close()
        conn.close()
        if outer:
            if fmt == "text":
                outer.write("\n".join(ret_list))
            elif fmt == "json":
                outer.write(ret_dict)
            elif fmt == "yaml":
                outer.write(dump(ret_dict, default_flow_style=False))
        else:
            if fmt == "text":
                return ret_list
            elif fmt == "json":
                return ret_dict
            elif fmt == "yaml":
                return dump(ret_dict, default_flow_style=False)


def sqliteinfo(dbpaths: List[str] = [], outer=None, fmt: str = "json"):
    """sqliteinfo.

    Args:
        dbpaths (List[str]): dbpaths
        outer:
        fmt (str): fmt
    """
    return get_sqliteinfo(dbpaths=dbpaths, outer=outer, fmt=fmt)


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
    if outpath.endswith(".sqlite") == False:
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
            filterpath=filterpath,
            filtersql=filtersql,
            includesample=includesample,
            excludesample=excludesample,
        )
    )


def filtersqlite_async_drop_copy_table(c, table_name):
    """filtersqlite_async_drop_copy_table.

    Args:
        c:
        table_name:
    """
    print(f"- {table_name}")
    c.execute(f"drop table if exists main.{table_name}")
    c.execute(f"create table main.{table_name} as select * from old_db.{table_name}")


async def filtersqlite_async(
    dbpaths: List[str] = [],
    suffix: str = "filtered",
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
    import sqlite3
    from os import remove
    from os.path import exists
    from .. import ReportFilter

    for dbpath in dbpaths:
        if not dbpath.endswith(".sqlite"):
            print(f"  Skipping")
            continue
        opath = f"{dbpath[:-7]}.{suffix}.sqlite"
        print(f"{opath}")
        if exists(opath):
            remove(opath)
        conn = sqlite3.connect(opath)
        c = conn.cursor()
        try:
            c.execute("attach database '" + dbpath + "' as old_db")
            cf = await ReportFilter.create(
                dbpath=dbpath,
                filterpath=filterpath,
                filtersql=filtersql,
                includesample=includesample,
                excludesample=excludesample,
            )
            await cf.exec_db(cf.loadfilter)
            if (
                hasattr(cf, "filter") == False
                or cf.filter is None
                or type(cf.filter) is not dict
            ):
                from ..lib.exceptions import FilterLoadingError

                raise FilterLoadingError()
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
                filtersqlite_async_drop_copy_table(c, table_name)
            # Variant
            print(f"- variant")
            if hasattr(cf, "make_filtered_uid_table"):
                await cf.exec_db(getattr(cf, "make_filtered_uid_table"))
            c.execute(
                "create table variant as select v.* from old_db.variant as v, old_db.variant_filtered as f where v.base__uid=f.base__uid"
            )
            # Gene
            print(f"- gene")
            await cf.exec_db(cf.make_filtered_hugo_table)
            c.execute(
                "create table gene as select g.* from old_db.gene as g, old_db.gene_filtered as f where g.base__hugo=f.base__hugo"
            )
            # Sample
            print(f"- sample")
            req = []
            rej = []
            if "sample" in cf.filter:
                if "require" in cf.filter["sample"]:
                    req = cf.filter["sample"]["require"]
                if "reject" in cf.filter["sample"]:
                    rej = cf.filter["sample"]["reject"]
            if cf.includesample is not None:
                req = cf.includesample
            if cf.excludesample is not None:
                rej = cf.excludesample
            if len(req) > 0 or len(rej) > 0:
                q = "create table sample as select s.* from old_db.sample as s, old_db.variant_filtered as v where s.base__uid=v.base__uid"
                if req:
                    q += " and s.base__sample_id in ({})".format(
                        ", ".join(['"{}"'.format(sid) for sid in req])
                    )
                for s in rej:
                    q += ' except select * from sample where base__sample_id="{}"'.format(
                        s
                    )
            else:
                q = "create table sample as select s.* from old_db.sample as s, old_db.variant_filtered as v where s.base__uid=v.base__uid"
            c.execute(q)
            # Mapping
            c.execute(
                "create table mapping as select m.* from old_db.mapping as m, old_db.variant_filtered as v where m.base__uid=v.base__uid"
            )
            # Indices
            c.execute("select name, sql from old_db.sqlite_master where type='index'")
            for r in c.fetchall():
                index_name = r[0]
                sql = r[1]
                if sql is not None:
                    print(f"- {index_name}")
                    c.execute(sql)
            # Info
            print("- info")
            c.execute("select count(*) from variant")
            n = c.fetchone()[0]
            c.execute(
                f'update info set colval={n} where colkey="Number of unique input variants"'
            )
            conn.commit()
            await cf.close_db()
            c.close()
            conn.close()
            print(f"-> {opath}")
        except Exception as e:
            c.close()
            conn.close()
            raise e
