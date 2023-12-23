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

from . import cli_entry
from . import cli_func


@cli_entry
def cli_report(args):
    return report(args)


@cli_func
def report(args, __name__="report"):
    from pathlib import Path
    from ..api import report
    from ..lib.util.run import get_module_options
    from ..lib.consts import MODULE_OPTIONS_KEY

    if MODULE_OPTIONS_KEY in args:
        module_options = get_module_options(args.get(MODULE_OPTIONS_KEY))
        args["module_options"] = module_options
    else:
        args["module_options"] = {}
    if args["output_path"]:
        args["output_path"] = Path(args["output_path"])
    if args["output_dir"]:
        args["output_dir"] = Path(args["output_dir"])
    ret = report(**args)
    return ret


def get_parser_fn_report():
    from argparse import ArgumentParser, SUPPRESS
    from ..lib.system.consts import DEFAULT_SERVER_DEFAULT_USERNAME

    parser_ov_report = ArgumentParser(
        prog="ov report dbpath ...",
        description="Generate reports from result SQLite files",
        epilog="dbpath must be the first argument.",
    )
    parser_ov_report.add_argument("dbpath", help="Path to aggregator output")
    parser_ov_report.add_argument(
        "-t",
        dest="report_types",
        nargs="*",
        default=None,
        help="report types",
    )
    parser_ov_report.add_argument(
        "-f", dest="filter_path", default=None, help="Path to filter file"
    )
    parser_ov_report.add_argument("--filter", default=None, help=SUPPRESS)
    parser_ov_report.add_argument("--filter-sql", default=None, help="Filter SQL")
    parser_ov_report.add_argument(
        "-s", dest="output_path", default=None, help="Path to save file"
    )
    parser_ov_report.add_argument(
        "--reporter-paths",
        dest="module_paths",
        nargs="*",
        default=None,
        help="report module name",
    )
    parser_ov_report.add_argument(
        "-d", dest="output_dir", default=None, help="directory for output files"
    )
    parser_ov_report.add_argument(
        "--quiet",
        action="store_true",
        default=None,
        help="Suppress output to STDOUT",
    )
    parser_ov_report.add_argument(
        "--module-options",
        dest="module_options",
        nargs="*",
        help="Module-specific option in module_name.key=value syntax. For example, --module-options vcfreporter.type=separate",
    )
    parser_ov_report.add_argument(
        "--samples-to-include",
        nargs="+",
        default=None,
        help="Sample IDs to include",
    )
    parser_ov_report.add_argument(
        "--samples-to-exclude",
        nargs="+",
        default=None,
        help="Sample IDs to exclude",
    )
    parser_ov_report.add_argument(
        "--package", help="Use filters and report types in a package"
    )
    parser_ov_report.add_argument(
        "--columns-to-include",
        nargs="+",
        default=None,
        help="columns to include in reports",
    )
    parser_ov_report.add_argument(
        "--user",
        default=DEFAULT_SERVER_DEFAULT_USERNAME,
        help=f"User who is creating this report. Default is {DEFAULT_SERVER_DEFAULT_USERNAME}.",
    )
    parser_ov_report.add_argument(
        "--skip-gene-summary",
        action="store_true",
        default=False,
        help="Skip gene level summarization. This saves time.",
    )
    parser_ov_report.add_argument(
        "--logtofile",
        action="store_true",
        help="Use this option to prevent gene level result from being added to variant level result.",
    )
    parser_ov_report.add_argument(
        "--head",
        dest="head_n",
        default=None,
        type=int,
        help="Make reports with the first n number of variants."
    )
    parser_ov_report.set_defaults(func=cli_report)
    return parser_ov_report
