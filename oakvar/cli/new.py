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
def cli_new_exampleinput(args):
    exampleinput(args)


@cli_func
def exampleinput(args, __name__="new exampleinput"):
    from ..api.new import exampleinput

    return exampleinput(args.get("directory"))


@cli_entry
def cli_new_module(args):
    return module(args)


@cli_func
def module(args, __name__="new module"):
    from ..api.new import module

    ret = module(args.get("name"), args.get("type"), outer=args.get("outer"))
    if ret:
        print(f"Created {ret}")


def get_parser_fn_new():
    from argparse import ArgumentParser, RawDescriptionHelpFormatter

    parser_fn_new = ArgumentParser(formatter_class=RawDescriptionHelpFormatter)
    _subparsers = parser_fn_new.add_subparsers(title="Commands")

    # test input file
    parser_cli_new_exampleinput = _subparsers.add_parser(
        "exampleinput", help="makes a file with example input variants."
    )
    parser_cli_new_exampleinput.add_argument(
        "-d",
        dest="directory",
        default=".",
        help="Directory to make the example input file in",
    )
    parser_cli_new_exampleinput.add_argument(
        "--quiet", action="store_true", default=None, help="run quietly"
    )
    parser_cli_new_exampleinput.set_defaults(func=cli_new_exampleinput)
    parser_cli_new_exampleinput.r_return = "A string. Location of the example input file"  # type: ignore
    parser_cli_new_exampleinput.r_examples = [  # type: ignore
        "# Create an example input file in the current working directory",
        "#roakvar::new.exampleinput()",
        "# Create an example input file at /home/user1/",
        '#roakvar::new.exampleinput(directory="/home/user1")',
    ]

    # new-annotator
    parser_cli_new_annotator = _subparsers.add_parser(
        "module", help="creates a new module skeleton."
    )
    parser_cli_new_annotator.add_argument("-n", dest="name", help="Module name")
    parser_cli_new_annotator.add_argument("-t", dest="type", help="Module type")
    parser_cli_new_annotator.add_argument(
        "--quiet", action="store_true", default=None, help="No print to stdout"
    )
    parser_cli_new_annotator.set_defaults(func=cli_new_module)
    parser_cli_new_annotator.r_return = "A string. Location of the new annotator module"  # type: ignore
    parser_cli_new_annotator.r_examples = [  # type: ignore
        "# Create an annotator template at the OakVar modules directory/annotators/annotatortest",
        '#roakvar::new.annotator(annotator_name="annotatortest")',
    ]
    return parser_fn_new
