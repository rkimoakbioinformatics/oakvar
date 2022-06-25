from ..decorators import cli_func
from ..decorators import cli_entry


"""
@cli_func
def ov_util_updateresult(args):
    import sqlite3
    from os import listdir
    from os.path import join, isdir, exists
    from shutil import copy
    from distutils.version import LooseVersion
    migrate_functions = {}
    migrate_checkpoints = [
        LooseVersion(v) for v in list(migrate_functions.keys())
    ]
    migrate_checkpoints.sort()

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
            print("  [{}] is not OakVar result DB or too old for migration.".
                  format(dbpath))
            continue
        if oc_ver >= max(migrate_checkpoints):
            print(f"  OakVar version of {oc_ver} does not need migration.")
            continue
        elif oc_ver < LooseVersion("1.4.4"):
            print(
                f"  OakVar version of {oc_ver} is not supported for migration."
            )
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
                        (target_ver, ),
                    )
        except:
            from traceback import print_exc
            print_exc()
            print("  converting [{}] was not successful.".format(dbpath))
"""


@cli_entry
def cli_util_addjob(args):
    return addjob(args)


@cli_func
def addjob(args, __name__="util addjob"):
    from json import dump
    from shutil import copyfile
    from time import sleep
    from pathlib import Path
    from datetime import datetime
    from ..system import get_jobs_dir

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
    return True


def variant_id(chrom, pos, ref, alt):
    return chrom + str(pos) + ref + alt


def get_sqliteinfo(args):
    import sqlite3
    from json import loads
    from oyaml import dump

    fmt = args["fmt"]
    to = args["to"]
    dbpaths = args["paths"]
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
        input_paths = loads(c.fetchone()[0].replace("'", '"'))
        if fmt == "text":
            s = f"\n# Input files:"
            ret_list.append(s)
            for p in input_paths.values():
                s = f"{p}"
                ret_list.append(s)
        elif fmt in ["json", "yaml"]:
            ret_dict["inputs"] = list(input_paths.values())
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
        if to == "stdout":
            if fmt == "text":
                print("\n".join(ret_list))
            elif fmt == "json":
                print(ret_dict)
            elif fmt == "yaml":
                print(dump(ret_dict, default_flow_style=False))
        else:
            if fmt == "text":
                return ret_list
            elif fmt == "json":
                return ret_dict
            elif fmt == "yaml":
                return dump(ret_dict, default_flow_style=False)


@cli_entry
def cli_util_sqliteinfo(args):
    sqliteinfo(args)


@cli_func
def sqliteinfo(args, __name__="util sqliteinfo"):
    return get_sqliteinfo(args)


@cli_entry
def cli_util_mergesqlite(args):
    mergesqlite(args)


# For now, only jobs with same annotators are allowed.


@cli_entry
@cli_func
def mergesqlite(args, __name__="util mergesqlite"):
    import sqlite3
    from json import loads, dumps
    from shutil import copy

    dbpaths = args.path
    if len(dbpaths) < 2:
        exit("Multiple sqlite file paths should be given")
    outpath = args.outpath
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


@cli_entry
def cli_util_filtersqlite(args):
    return filtersqlite(args)


@cli_func
def filtersqlite(args, __name__="util filtersqlite"):
    from asyncio import get_event_loop

    loop = get_event_loop()
    return loop.run_until_complete(filtersqlite_async(args))


def filtersqlite_async_drop_copy_table(c, table_name):
    print(f"- {table_name}")
    c.execute(f"drop table if exists main.{table_name}")
    c.execute(f"create table main.{table_name} as select * from old_db.{table_name}")


async def filtersqlite_async(args):
    import sqlite3
    from os import remove
    from os.path import exists
    from ..base.cravat_filter import CravatFilter

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
            if (
                hasattr(cf, "filter") == False
                or cf.filter is None
                or type(cf.filter) is not dict
            ):
                from ..exceptions import FilterLoadingError

                raise FilterLoadingError()
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
    from datetime import date

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
        d["submission_time"] = date.fromtimestamp(dbpath.stat().st_ctime).isoformat()
        d["viewable"] = True
    except:
        raise
    finally:
        c.close()
        db.close()
    return d


def get_parser_fn_util():
    from argparse import ArgumentParser

    parser_fn_util = ArgumentParser()
    _subparsers = parser_fn_util.add_subparsers(title="Commands")
    # test
    from .test import get_parser_cli_util_test

    parser_cli_util_test = _subparsers.add_parser(
        "test",
        parents=[get_parser_cli_util_test()],
        add_help=False,
        description="Test modules",
        help="Test installed modules",
    )
    parser_cli_util_test.r_return = "A named list. Field result is a named list showing the test result for each module. Fields num_passed and num_failed show the number of passed and failed modules."  # type: ignore
    parser_cli_util_test.r_examples = [  # type: ignore
        "# Test the ClinVar module",
        '#roakvar::util.test(modules="clinvar")',
        "# Test the ClinVar and the COSMIC modules",
        '#roakvar::util.test(modules=list("clinvar", "cosmic"))',
    ]

    # converts db coordinate to hg38
    """
    parser_fn_util_convert = _subparsers.add_parser(
        "converttohg38",
        help="converts hg19 coordinates in SQLite3 database to hg38 ones.")
    parser_fn_util_convert.add_argument("--db",
                                        nargs="?",
                                        required=True,
                                        help="path to SQLite3 database file")
    parser_fn_util_convert.add_argument(
        "--sourcegenome",
        required=True,
        help="genome assembly of source database")
    parser_fn_util_convert.add_argument("--cols",
                                        nargs="+",
                                        default=["base__pos"],
                                        help="names of the columns to convert")
    parser_fn_util_convert.add_argument(
        "--tables",
        nargs="*",
        default=["variant"],
        help=
        "table(s) to convert. If omitted, table name will be used as chromosome name.",
    )
    parser_fn_util_convert.add_argument(
        "--chromcol",
        required=False,
        help=
        "chromosome column. If omitted, all tables will be tried to be converted.",
    )
    parser_fn_util_convert.set_defaults(func=converttohg38)
    parser_fn_util_convert.r_return = "A boolean. TRUE if successful, FALSE if not"
    parser_fn_util_convert.r_examples = [
        "# Convert the hg19 coordinates in \"base__pos\" column of an OakVar result database into hg38",
        "#roakvar::util.convert(db=\"example.sqlite\", cols=\"base__pos\", tables=\"variant\")"
    ]
    """

    # migrate old result db
    """
    parser_fn_util_updateresult = _subparsers.add_parser(
        "updateresult",
        help="migrates result db made with older versions of oakvar")
    parser_fn_util_updateresult.add_argument(
        "dbpath", help="path to a result db file or a directory")
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
    parser_fn_util_updateresult.r_return = "A boolean. TRUE if successful, FALSE if not"
    """

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
    parser_fn_util_addjob.set_defaults(func=addjob)
    parser_fn_util_addjob.r_return = "A boolean. TRUE if successful, FALSE if not"  # type: ignore
    parser_fn_util_addjob.r_examples = [  # type: ignore
        "# Add a result file to the job list of a user",
        '#roakvar::util.addjob(path="example.sqlite", user="user1")',
    ]

    # Merge SQLite files
    parser_fn_util_mergesqlite = _subparsers.add_parser(
        "mergesqlite", help="Merge SQLite result files"
    )
    parser_fn_util_mergesqlite.add_argument(
        "path", nargs="+", help="Path to result database"
    )
    parser_fn_util_mergesqlite.add_argument(
        "-o", dest="outpath", required=True, help="Output SQLite file path"
    )
    parser_fn_util_mergesqlite.set_defaults(func=mergesqlite)
    parser_fn_util_mergesqlite.r_return = "A boolean. TRUE if successful, FALSE if not"  # type: ignore
    parser_fn_util_mergesqlite.r_examples = [  # type: ignore
        "# Merge two OakVar analysis result files into one SQLite file",
        '#roakvar::util.mergesqlite(path=list("example1.sqlite", "example2.sqlite"), outpath="merged.sqlite")',
    ]

    # Show SQLite info
    parser_fn_util_showsqliteinfo = _subparsers.add_parser(
        "sqliteinfo", help="Show SQLite result file information"
    )
    parser_fn_util_showsqliteinfo.add_argument(
        "paths", nargs="+", help="SQLite result file paths"
    )
    parser_fn_util_showsqliteinfo.add_argument(
        "--fmt", default="json", help="Output format. text / json / yaml"
    )
    parser_fn_util_showsqliteinfo.add_argument(
        "--to", default="return", help="Output to. stdout / return"
    )
    parser_fn_util_showsqliteinfo.set_defaults(func=sqliteinfo)
    parser_fn_util_showsqliteinfo.r_return = "A named list. Information of a job SQLite file"  # type: ignore
    parser_fn_util_showsqliteinfo.r_examples = [  # type: ignore
        "# Get the named list of the information of an analysis result file",
        '#roakvar::util.sqliteinfo(paths="example.sqlite")',
    ]

    # Filter SQLite
    parser_fn_util_filtersqlite = _subparsers.add_parser(
        "filtersqlite",
        help="Filter SQLite result files to produce filtered SQLite result files",
    )
    parser_fn_util_filtersqlite.add_argument(
        "paths", nargs="+", help="Path to result database"
    )
    parser_fn_util_filtersqlite.add_argument(
        "-o", dest="out", default=".", help="Output SQLite file folder"
    )
    parser_fn_util_filtersqlite.add_argument(
        "-s", dest="suffix", default="filtered", help="Suffix for output SQLite files"
    )
    parser_fn_util_filtersqlite.add_argument(
        "-f", dest="filterpath", default=None, help="Path to a filter JSON file"
    )
    parser_fn_util_filtersqlite.add_argument(
        "--filtersql", default=None, help="Filter SQL"
    )
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
    parser_fn_util_filtersqlite.set_defaults(func=filtersqlite)
    parser_fn_util_filtersqlite.r_return = "A boolean. TRUE if successful, FALSE if not"  # type: ignore
    parser_fn_util_filtersqlite.r_examples = [  # type: ignore
        "# Filter an analysis result file with an SQL filter set",
        '#roakvar::util.filtersqlite(paths="example.sqlite", ',
        "#  filtersql='base__so==\"MIS\" and gnomad__af>0.01')",
        "# Filter two analysis result files with a filter definition file",
        '#roakvar::util.filtersqlite(paths=list("example1.sqlite", ',
        '#  "example2.sqlite"), filterpath="filter.json")',
    ]
    return parser_fn_util


def main():
    pass


if __name__ == "__main__":
    main()
