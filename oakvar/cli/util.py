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

from . import cli_entry
from . import cli_func


@cli_entry
def cli_util_sqliteinfo(args):
    sqliteinfo(args)


@cli_func
def sqliteinfo(args, __name__="util sqliteinfo"):
    import json
    from rich import print_json
    from rich.console import Console
    from rich.syntax import Syntax
    from ..api.util import sqliteinfo

    fmt = args.get("fmt", "json")
    out = sqliteinfo(**args)
    if not out:
        return
    console = Console()
    if isinstance(out, str):
        if fmt == "yaml":
            syntax = Syntax(out, "yaml")
            console.print(syntax)
    elif isinstance(out, dict):
        if fmt == "json":
            print_json(json.dumps(out))


@cli_entry
def cli_util_movejob(args):
    movejob(args)


@cli_func
def movejob(args, __name__="util move-job"):
    from rich.console import Console
    from ..api.util import move_job

    out = move_job(**args)
    if not out:
        return
    console = Console()
    console.print(out)


# @cli_entry
# def cli_util_mergesqlite(args):
# mergesqlite(args)
#
#
# @cli_func
# def mergesqlite(args, __name__="util mergesqlite"):
# from ..api.util import mergesqlite
#
# return mergesqlite(**args)


# @cli_entry
# def cli_util_filtersqlite(args):
#    return filtersqlite(args)
#
#
# @cli_func
# def filtersqlite(args, __name__="util filtersqlite"):
#    from ..api.util import filtersqlite
#
#    dbpaths = args.get("dbpaths")
#    suffix = args.get("suffix")
#    filterpath = args.get("filterpath")
#    filtersql = args.get("filtersql")
#    includesample = args.get("includesample")
#    excludesample = args.get("excludesample")
#    return filtersqlite(dbpaths=dbpaths, suffix=suffix, filterpath=filterpath, filtersql=filtersql, includesample=includesample, excludesample=excludesample)


def get_parser_fn_util():
    from argparse import ArgumentParser
    from .test import get_parser_cli_util_test
    from ..api.util import job_to_gui

    parser_fn_util = ArgumentParser()
    _subparsers = parser_fn_util.add_subparsers(title="Commands")
    # test

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

    # Make job accessible through the gui
    parser_fn_util_addjob = _subparsers.add_parser(
        "to-gui", help="Make a command line job by `ov run` to be accessible by GUI."
    )
    parser_fn_util_addjob.add_argument(
        "path", help="Path to result .sqlite database file"
    )
    parser_fn_util_addjob.add_argument(
        "-u",
        "--user",
        help="User who will own the job. Defaults to `default` user.",
        type=str,
        default="default",
    )
    parser_fn_util_addjob.set_defaults(func=job_to_gui)
    parser_fn_util_addjob.r_return = "A boolean. TRUE if successful, FALSE if not"  # type: ignore
    parser_fn_util_addjob.r_examples = [  # type: ignore
        "# Add a result file to the job list of a user",
        '#roakvar::util.to_gui(path="example.sqlite", user="user1")',
    ]

    # Merge SQLite files
    # parser_fn_util_mergesqlite = _subparsers.add_parser(
    #    "mergesqlite", help="Merge SQLite result files"
    # )
    # parser_fn_util_mergesqlite.add_argument(
    #    "path", nargs="+", help="Path to result database"
    # )
    # parser_fn_util_mergesqlite.add_argument(
    #    "-o", dest="outpath", required=True, help="Output SQLite file path"
    # )
    # parser_fn_util_mergesqlite.set_defaults(func=cli_util_mergesqlite)
    # parser_fn_util_mergesqlite.r_return = "A boolean. TRUE if successful, FALSE if not"  # type: ignore
    # parser_fn_util_mergesqlite.r_examples = [  # type: ignore
    #    "# Merge two OakVar analysis result files into one SQLite file",
    #    '#roakvar::util.mergesqlite(path=list("example1.sqlite",
    #          "example2.sqlite"), outpath="merged.sqlite")',
    # ]

    # Show SQLite info
    parser_fn_util_showsqliteinfo = _subparsers.add_parser(
        "sqliteinfo", help="Show SQLite result file information"
    )
    parser_fn_util_showsqliteinfo.add_argument("dbpath", help="SQLite result file path")
    parser_fn_util_showsqliteinfo.add_argument(
        "--fmt", default="json", help="Output format. text / json / yaml"
    )
    parser_fn_util_showsqliteinfo.set_defaults(func=cli_util_sqliteinfo)
    parser_fn_util_showsqliteinfo.r_return = (
        "A named list. Information of a job SQLite file"  # type: ignore
    )
    parser_fn_util_showsqliteinfo.r_examples = [  # type: ignore
        "# Get the named list of the information of an analysis result file",
        '#roakvar::util.sqliteinfo(paths="example.sqlite")',
    ]

    # Move a job to an account
    parser_fn_util_movejob = _subparsers.add_parser(
        "move-job", help="Move a job to another account"
    )
    parser_fn_util_movejob.add_argument("--job-dir", help="Job directory")
    parser_fn_util_movejob.add_argument("--new-account", help="New account")
    parser_fn_util_movejob.set_defaults(func=cli_util_movejob)

    # Filter SQLite
    # parser_fn_util_filtersqlite = _subparsers.add_parser(
    #    "filtersqlite",
    #    help="Filter SQLite result files to produce filtered SQLite result files",
    # )
    # parser_fn_util_filtersqlite.add_argument(
    #    "paths", nargs="+", help="Path to result database"
    # )
    # parser_fn_util_filtersqlite.add_argument(
    #    "-o", dest="out", default=".", help="Output SQLite file folder"
    # )
    # parser_fn_util_filtersqlite.add_argument(
    #    "-s", dest="suffix", default="filtered", help="Suffix for output SQLite files"
    # )
    # parser_fn_util_filtersqlite.add_argument(
    #    "-f", dest="filterpath", default=None, help="Path to a filter JSON file"
    # )
    # parser_fn_util_filtersqlite.add_argument(
    #    "--filtersql", default=None, help="Filter SQL"
    # )
    # parser_fn_util_filtersqlite.add_argument(
    #    "--includesample",
    #    dest="includesample",
    #    nargs="+",
    #    default=None,
    #    help="Sample IDs to include",
    # )
    # parser_fn_util_filtersqlite.add_argument(
    #    "--excludesample",
    #    dest="excludesample",
    #    nargs="+",
    #    default=None,
    #    help="Sample IDs to exclude",
    # )
    # parser_fn_util_filtersqlite.set_defaults(func=filtersqlite)
    # parser_fn_util_filtersqlite.r_return = "A boolean. TRUE if " +\
    #        "successful, FALSE if not"  # type: ignore
    # parser_fn_util_filtersqlite.r_examples = [  # type: ignore
    #    "# Filter an analysis result file with an SQL filter set",
    #    '#roakvar::util.filtersqlite(paths="example.sqlite", ',
    #    "#  filtersql='base__so==\"MIS\" and gnomad__af>0.01')",
    #    "# Filter two analysis result files with a filter definition file",
    #    '#roakvar::util.filtersqlite(paths=list("example1.sqlite", ',
    #    '#  "example2.sqlite"), filterpath="filter.json")',
    # ]
    return parser_fn_util
