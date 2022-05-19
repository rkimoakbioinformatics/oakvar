from argparse import ArgumentParser


def converttohg38(args):
    from subprocess import check_output
    import sqlite3
    from .constants import get_liftover_chain_path_for_src_genome
    from pyliftover import LiftOver
    from os.path import exists
    from os import remove
    if args.sourcegenome not in ["hg18", "hg19"]:
        print("Source genome should be either hg18 or hg19.")
        exit()
    if exists(args.db) == False:
        print(args.db, "does not exist.")
        exit()
    liftover = LiftOver(
        get_liftover_chain_path_for_src_genome(args.sourcegenome)
    )
    print("Extracting table schema from DB...")
    cmd = ["sqlite3", args.db, ".schema"]
    output = check_output(cmd)
    sqlpath = args.db + ".newdb.sql"
    wf = open(sqlpath, "w")
    wf.write(output.decode())
    wf.close()
    newdbpath = ".".join(args.db.split(".")[:-1]) + ".hg38.sqlite"
    if exists(newdbpath):
        print("Deleting existing hg38 DB...")
        remove(newdbpath)
    print("Creating " + newdbpath + "...")
    newdb = sqlite3.connect(newdbpath)
    newc = newdb.cursor()
    print("Creating same table(s) in " + newdbpath + "...")
    cmd = ["sqlite3", newdbpath, ".read " + sqlpath]
    output = check_output(cmd)
    db = sqlite3.connect(args.db)
    c = db.cursor()
    if args.tables == None:
        print("tables not given. All tables will be tried.")
        output = check_output(["sqlite3", args.db, ".table"])
        args.tables = output.decode().split()
        args.tables.sort()
        print("The following tables will be examined:", ", ".join(args.tables))
    tables_toconvert = []
    tables_tocopy = []
    for table in args.tables:
        c.execute("select * from " + table + " limit 1")
        cols = [v[0] for v in c.description]
        hit = False
        if args.chromcol is not None and args.chromcol not in cols:
            tables_tocopy.append(table)
            continue
        for col in args.cols:
            if col in cols:
                hit = True
                break
        if hit:
            tables_toconvert.append(table)
        else:
            tables_tocopy.append(table)
    print(
        "Tables to convert:",
        ", ".join(tables_toconvert) if len(tables_toconvert) > 0 else "none",
    )
    print(
        "Tables to copy:",
        ", ".join(tables_tocopy) if len(tables_tocopy) > 0 else "none",
    )
    wf = open(newdbpath + ".noconversion", "w")
    count_interval = 10000
    for table in tables_toconvert:
        print("Converting " + table + "...")
        c.execute("select * from " + table)
        allcols = [v[0] for v in c.description]
        colnos = []
        for col in args.cols:
            if col in allcols:
                colnos.append(allcols.index(col))
        if args.chromcol is None:
            chromcolno = None
        else:
            chromcolno = allcols.index(args.chromcol)
        count = 0
        for row in c.fetchall():
            row = list(row)
            if chromcolno is not None:
                chrom = row[chromcolno]
            else:
                chrom = table
            if chrom.startswith("chr") == False:
                chrom = "chr" + chrom
            for colno in colnos:
                pos = int(row[colno])
                liftover_out = liftover.convert_coordinate(chrom, pos)
                if liftover_out == None:
                    print("- no liftover mapping:", chrom + ":" + str(pos))
                    continue
                if liftover_out == []:
                    wf.write(table + ":" + ",".join([str(v) for v in row]) + "\n")
                    continue
                newpos = liftover_out[0][1]
                row[colno] = newpos
            q = (
                "insert into "
                + table
                + " values("
                + ",".join(
                    ['"' + v + '"' if type(v) == type("a") else str(v) for v in row]
                )
                + ")"
            )
            newc.execute(q)
            count += 1
            if count % count_interval == 0:
                print("  " + str(count) + "...")
        print("  " + table + ": done.", count, "rows converted")
    wf.close()
    for table in tables_tocopy:
        count = 0
        print("Copying " + table + "...")
        c.execute("select * from " + table)
        for row in c.fetchall():
            row = list(row)
            q = (
                "insert into "
                + table
                + " values("
                + ",".join(
                    ['"' + v + '"' if type(v) == type("a") else str(v) for v in row]
                )
                + ")"
            )
            newc.execute(q)
            count += 1
            if count % count_interval == 0:
                print("  " + str(count) + "...")
        print("  " + table + ": done.", count, "rows converted")
    newdb.commit()




def fn_util_updateresult(args):
    import sqlite3
    from os import listdir
    from os.path import join, isdir
    from shutil import copy
    from distutils.version import LooseVersion
    from .util import get_dict_from_namespace
    migrate_functions = {}
    migrate_checkpoints = [LooseVersion(v) for v in list(migrate_functions.keys())]
    migrate_checkpoints.sort()
    args = get_dict_from_namespace(args)
    def get_dbpaths(dbpaths, path):
        for fn in listdir(path):
            p = join(path, fn)
            if isdir(p) and args["recursive"]:
                get_dbpaths(dbpaths, p)
            else:
                if fn.endswith(".sqlite"):
                    dbpaths.append(p)
    dbpath = args["dbpath"]
    if exists(dbpath) == False:
        print("[{}] does not exist.".format(dbpath))
        return
    if isdir(dbpath):
        dbpaths = []
        get_dbpaths(dbpaths, dbpath)
    else:
        dbpaths = [dbpath]
    print("Result database files to convert are:")
    for dbpath in dbpaths:
        print("  " + dbpath)
    for dbpath in dbpaths:
        print("converting [{}]...".format(dbpath))
        try:
            db = sqlite3.connect(dbpath)
            cursor = db.cursor()
        except:
            print("  [{}] is not OakVar result DB.".format(dbpath))
            continue
        try:
            q = 'select colval from info where colkey="oakvar"'
            cursor.execute(q)
            r = cursor.fetchone()
            if r is None:
                print("  Result DB is too old for migration.")
                continue
            else:
                oc_ver = LooseVersion(r[0])
        except:
            print(
                "  [{}] is not OakVar result DB or too old for migration.".format(
                    dbpath
                )
            )
            continue
        if oc_ver >= max(migrate_checkpoints):
            print(f"  OakVar version of {oc_ver} does not need migration.")
            continue
        elif oc_ver < LooseVersion("1.4.4"):
            print(f"  OakVar version of {oc_ver} is not supported for migration.")
            continue
        try:
            if args["backup"]:
                bak_path = dbpath + ".bak"
                print("  making backup copy [{}]...".format(bak_path))
                copy(dbpath, bak_path)
            ver_idx = None
            for i, target_ver in enumerate(migrate_checkpoints):
                if oc_ver < target_ver:
                    ver_idx = i
                    break
            if ver_idx is None:
                continue
            for target_ver in migrate_checkpoints[ver_idx:]:
                target_ver = str(target_ver)
                print(f"  converting OakVar version to {target_ver}...")
                migrate_functions[target_ver](dbpath)
                with sqlite3.connect(dbpath) as db:
                    db.execute(
                        'update info set colval=? where colkey="oakvar"',
                        (target_ver,),
                    )
        except:
            from traceback import print_exc
            print_exc()
            print("  converting [{}] was not successful.".format(dbpath))


def fn_util_addjob(args):
    from json import dump
    from shutil import copyfile
    from time import sleep
    from pathlib import Path
    from datetime import datetime
    from .admin_util import get_jobs_dir
    dbpath = args.path
    user = args.user
    jobs_dir = Path(get_jobs_dir())
    user_dir = jobs_dir / user
    if not user_dir.is_dir():
        exit(f"User {user} not found")
    attempts = 0
    while (
        True
    ):  # TODO this will currently overwrite if called in parallel. is_dir check and creation is not atomic
        job_id = datetime.now().strftime(r"%y%m%d-%H%M%S")
        job_dir = user_dir / job_id
        if not job_dir.is_dir():
            break
        else:
            attempts += 1
            sleep(1)
        if attempts >= 5:
            exit(
                "Could not acquire a job id. Too many concurrent job submissions. Wait, or reduce submission frequency."
            )
    job_dir.mkdir()
    new_dbpath = job_dir / dbpath.name
    copyfile(dbpath, new_dbpath)
    log_path = dbpath.with_suffix(".log")
    if log_path.exists():
        copyfile(log_path, job_dir / log_path.name)
    err_path = dbpath.with_suffix(".err")
    if err_path.exists():
        copyfile(err_path, job_dir / err_path.name)
    status_path = dbpath.with_suffix(".status.json")
    if status_path.exists():
        copyfile(status_path, job_dir / status_path.name)
    else:
        statusd = status_from_db(new_dbpath)
        new_status_path = job_dir / status_path.name
        with new_status_path.open("w") as wf:
            dump(statusd, wf, indent=2, sort_keys=True)


def variant_id(chrom, pos, ref, alt):
    return chrom + str(pos) + ref + alt


def fn_util_showsqliteinfo(args):
    import sqlite3
    from json import loads
    from .util import get_dict_from_namespace
    from oyaml import dump
    args = get_dict_from_namespace(args)
    fmt = args["fmt"]
    to = args["to"]
    if fmt == "text":
        ret = []
    elif fmt in ["json", "yaml"]:
        ret = {}
    dbpaths = args["paths"]
    width_colname = 30
    width_coltitle = 40
    for dbpath in dbpaths:
        if fmt == "text":
            s = f"# SQLite file:\n{dbpath}"
            ret.append(s)
        elif fmt in ["json", "yaml"]:
            ret["dbpath"] = dbpath
        conn = sqlite3.connect(dbpath)
        c = conn.cursor()
        c.execute('select colval from info where colkey="_input_paths"')
        input_paths = loads(c.fetchone()[0].replace("'", '"'))
        if fmt == "text":
            s = f"\n# Input files:"
            ret.append(s)
            for p in input_paths.values():
                s = f"{p}"
                ret.append(s)
        elif fmt in ["json", "yaml"]:
            ret["inputs"] = list(input_paths.values())
        if fmt == "text":
            s = f"\n# Output columns"
            ret.append(s)
            s = f'{"# Name".ljust(width_colname)} {"Title".ljust(width_coltitle)} Type'
            ret.append(s)
        else:
            ret["output_columns"] = {}
        c.execute("select col_name, col_def from variant_header")
        rs = c.fetchall()
        if fmt in ["json", "yaml"]:
            ret["output_columns"] = {}
            ret["output_columns"]["variant"] = []
            ret["output_columns"]["gene"] = []
        for r in rs:
            col_name, col_def = r
            col_def = loads(col_def)
            if fmt == "text":
                s = f"{col_name.ljust(width_colname)} {col_def['title'].ljust(width_coltitle)} {col_def['type']}"
                ret.append(s)
            elif fmt in ["json", "yaml"]:
                ret["output_columns"]["variant"].append({"name": col_name, "title": col_def["title"], "type": col_def["type"]})
        c.execute("select col_name, col_def from gene_header")
        rs = c.fetchall()
        for r in rs:
            col_name, col_def = r
            col_def = loads(col_def)
            if fmt == "text":
                s = f"{col_name.ljust(width_colname)} {col_def['title'].ljust(width_coltitle)} {col_def['type']}"
                ret.append(s)
            elif fmt in ["json", "yaml"]:
                ret["output_columns"]["gene"].append({"name": col_name, "title": col_def["title"], "type": col_def["type"]})
        c.close()
        conn.close()
        if to == "stdout":
            if fmt == "text":
                print("\n".join(ret))
            elif fmt == "json":
                print(ret)
            elif fmt == "yaml":
                print(dump(ret, default_flow_style=False))
        else:
            if fmt in ["text", "json"]:
                return ret
            elif fmt == "yaml":
                return dump(ret, default_flow_style=False)


# For now, only jobs with same annotators are allowed.
def fn_util_mergesqlite(args):
    import sqlite3
    from json import loads, dumps
    from shutil import copy
    from .util import get_dict_from_namespace
    args = get_dict_from_namespace(args)
    dbpaths = args["path"]
    if len(dbpaths) < 2:
        exit("Multiple sqlite file paths should be given")
    outpath = args["outpath"]
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
            q = f'insert into gene values ({",".join(["?" for v in range(len(r))])})'
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
            q = f'insert into variant values ({",".join(["?" for v in range(len(r))])})'
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
                q = f'insert into sample values ({",".join(["?" for v in range(len(r))])})'
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
                q = f'insert into mapping values ({",".join(["?" for v in range(len(r))])})'
                outc.execute(q, r)
    q = 'update info set colval=? where colkey="_input_paths"'
    outc.execute(q, [dumps(input_paths)])
    q = 'update info set colval=? where colkey="Input file name"'
    v = ";".join(
        [input_paths[str(v)] for v in sorted(input_paths.keys(), key=lambda v: int(v))]
    )
    outc.execute(q, [v])
    outconn.commit()


def fn_util_filtersqlite(args):
    from asyncio import get_event_loop
    from .util import get_dict_from_namespace
    args = get_dict_from_namespace(args)
    loop = get_event_loop()
    loop.run_until_complete(filtersqlite_async(args))


def filtersqlite_async_drop_copy_table(c, table_name):
    print(f"- {table_name}")
    c.execute(f"drop table if exists main.{table_name}")
    c.execute(f"create table main.{table_name} as select * from old_db.{table_name}")


async def filtersqlite_async(args):
    import sqlite3
    from os import remove
    from os.path import exists
    from .cravat_filter import CravatFilter
    dbpaths = args["paths"]
    for dbpath in dbpaths:
        if not dbpath.endswith(".sqlite"):
            print(f"  Skipping")
            continue
        opath = dbpath[:-7] + "." + args["suffix"] + ".sqlite"
        print(f"{opath}")
        if exists(opath):
            remove(opath)
        conn = sqlite3.connect(opath)
        c = conn.cursor()
        try:
            c.execute("attach database '" + dbpath + "' as old_db")
            cf = await CravatFilter.create(
                dbpath=dbpath,
                filterpath=args["filterpath"],
                filtersql=args["filtersql"],
                includesample=args["includesample"],
                excludesample=args["excludesample"],
            )
            await cf.exec_db(cf.loadfilter)
            for table_name in [
                "info",
                "smartfilters",
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
            await cf.exec_db(cf.make_filtered_uid_table)
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


def status_from_db(dbpath):
    """
    Generate a status json from a result database.
    Currently only works well if the database is in the gui jobs area.
    """
    import sqlite3
    from pathlib import Path
    from datetime import fromtimestamp
    if not isinstance(dbpath, Path):
        dbpath = Path(dbpath)
    d = {}
    db = sqlite3.connect(str(dbpath))
    c = db.cursor()
    c.execute("select colkey, colval from info")
    infod = {r[0]: r[1] for r in c}
    try:
        d["annotators"] = []
        d["annotator_version"] = {}
        c.execute("select name, version from gene_annotator")
        skip_names = {"base", "tagsampler", "vcfinfo", ""}
        for r in c:
            if r[0] in skip_names:
                continue
            d["annotators"].append(r[0])
            d["annotator_version"][r[0]] = r[1]
        c.execute("select name, version from variant_annotator")
        for r in c:
            if r[0] in skip_names:
                continue
            d["annotators"].append(r[0])
            d["annotator_version"][r[0]] = r[1]
        d["annotators"] = sorted(list(set(d["annotators"])))
        c.execute('select colval from info where colkey="Input genome"')
        d["assembly"] = c.fetchone()[0]
        d["db_path"] = str(dbpath)
        d["id"] = str(dbpath.parent)
        d["id"] = str(dbpath.parent.name)
        d["job_dir"] = str(dbpath.parent)
        d["note"] = ""
        d["num_error_input"] = 0
        c.execute(
            'select colval from info where colkey="Number of unique input variants"'
        )
        d["num_unique_var"] = c.fetchone()[0]
        d["num_input_var"] = d["num_unique_var"]
        c.execute('select colval from info where colkey="oakvar"')
        r = c.fetchone()
        ov_ver = "0.0.0"
        if r is not None:
            ov_ver = r[0]
        else:
            c.execute('select colval from info where colkey="open-cravat"')
            r = c.fetchone()
            if r is not None:
                ov_ver = r[0]
            else:
                ov_ver = r[0]
        d["open_cravat_version"] = ov_ver
        if "Input file name" in infod:
            d["orig_input_path"] = infod["Input file name"].split(";")
            d["orig_input_fname"] = [
                Path(p).name for p in infod["Input file name"].split(";")
            ]
        else:
            d["orig_input_fname"] = [str(dbpath.stem)]
            d["orig_input_path"] = [str(dbpath.with_suffix(""))]
        d["reports"] = []
        d["run_name"] = str(dbpath.stem)
        d["status"] = "Finished"
        d["submission_time"] = fromtimestamp(dbpath.stat().st_ctime).isoformat()
        d["viewable"] = True
    except:
        raise
    finally:
        c.close()
        db.close()
    return d


from argparse import ArgumentParser
parser_fn_util = ArgumentParser()
_subparsers = parser_fn_util.add_subparsers(title="Commands")

# test
from .cli_test import fn_util_test
parser_fn_util_test = _subparsers.add_parser("test", help="Test installed modules")
parser_fn_util_test.add_argument("-d", "--rundir", help="Directory for output")
parser_fn_util_test.add_argument(
    "-m", "--modules", nargs="+", help="Name of module(s) to test. (e.g. gnomad)"
)
parser_fn_util_test.add_argument(
    "-t", "--mod_types", nargs="+", help="Type of module(s) to test (e.g. annotators)"
)
parser_fn_util_test.add_argument("--to", default="stdout", help="stdout to print / return to return")
parser_fn_util_test.set_defaults(func=fn_util_test)


# converts db coordinate to hg38
parser_fn_util_convert = _subparsers.add_parser(
    "converttohg38", help="converts hg19 coordinates in SQLite3 database to hg38 ones."
)
parser_fn_util_convert.add_argument(
    "--db", nargs="?", required=True, help="path to SQLite3 database file"
)
parser_fn_util_convert.add_argument(
    "--sourcegenome", required=True, help="genome assembly of source database"
)
parser_fn_util_convert.add_argument(
    "--cols", nargs="+", required=True, help="names of the columns to convert"
)
parser_fn_util_convert.add_argument(
    "--tables",
    nargs="*",
    help="table(s) to convert. If omitted, table name will be used as chromosome name.",
)
parser_fn_util_convert.add_argument(
    "--chromcol",
    required=False,
    help="chromosome column. If omitted, all tables will be tried to be converted.",
)
parser_fn_util_convert.set_defaults(func=converttohg38)

# migrate old result db
parser_fn_util_updateresult = _subparsers.add_parser(
    "migrate-result", help="migrates result db made with older versions of oakvar"
)
parser_fn_util_updateresult.add_argument(
    "dbpath", help="path to a result db file or a directory"
)
parser_fn_util_updateresult.add_argument(
    "-r",
    dest="recursive",
    action="store_true",
    default=False,
    help="recursive operation",
)
parser_fn_util_updateresult.add_argument(
    "-c",
    dest="backup",
    action="store_true",
    default=False,
    help="backup original copy with .bak extension",
)
parser_fn_util_updateresult.set_defaults(func=fn_util_updateresult)

# Make job accessible through the gui
parser_fn_util_addjob = _subparsers.add_parser(
    "addjob", help="Copy a command line job into the GUI submission list"
)
parser_fn_util_addjob.add_argument("path", help="Path to result database")
parser_fn_util_addjob.add_argument(
    "-u",
    "--user",
    help="User who will own the job. Defaults to single user default user.",
    type=str,
    default="default",
)
parser_fn_util_addjob.set_defaults(func=fn_util_addjob)

# Merge SQLite files
parser_fn_util_mergesqlite = _subparsers.add_parser(
    "mergesqlite", help="Merge SQLite result files"
)
parser_fn_util_mergesqlite.add_argument(
    "path", nargs="+", help="Path to result database")
parser_fn_util_mergesqlite.add_argument(
    "-o", dest="outpath", required=True, help="Output SQLite file path"
)
parser_fn_util_mergesqlite.set_defaults(func=fn_util_mergesqlite)

# Show SQLite info
parser_fn_util_showsqliteinfo = _subparsers.add_parser(
    "showsqliteinfo", help="Show SQLite result file information"
)
parser_fn_util_showsqliteinfo.add_argument("paths", nargs="+", help="SQLite result file paths")
parser_fn_util_showsqliteinfo.add_argument("--fmt", default="text", help="Output format. text / json / yaml")
parser_fn_util_showsqliteinfo.add_argument("--to", default="stdout", help="Output to. stdout / return")
parser_fn_util_showsqliteinfo.set_defaults(func=fn_util_showsqliteinfo)
parser_fn_util_filtersqlite = _subparsers.add_parser(
    "filtersqlite",
    help="Filter SQLite result files to produce filtered SQLite result files",
)

# Filter SQLite
parser_fn_util_filtersqlite.add_argument("paths", nargs="+", help="Path to result database")
parser_fn_util_filtersqlite.add_argument(
    "-o", dest="out", default=".", help="Output SQLite file folder"
)
parser_fn_util_filtersqlite.add_argument(
    "-s", dest="suffix", default="filtered", help="Suffix for output SQLite files"
)
parser_fn_util_filtersqlite.add_argument(
    "-f", dest="filterpath", default=None, help="Path to a filter JSON file"
)
parser_fn_util_filtersqlite.add_argument("--filtersql", default=None, help="Filter SQL")
parser_fn_util_filtersqlite.add_argument(
    "--includesample",
    dest="includesample",
    nargs="+",
    default=None,
    help="Sample IDs to include",
)
parser_fn_util_filtersqlite.add_argument(
    "--excludesample",
    dest="excludesample",
    nargs="+",
    default=None,
    help="Sample IDs to exclude",
)
parser_fn_util_filtersqlite.set_defaults(func=fn_util_filtersqlite)


if __name__ == "__main__":
    main()
