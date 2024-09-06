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
    parser_cli_new_exampleinput.r_return = (
        "A string. Location of the example input file"  # type: ignore
    )
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
    parser_cli_new_annotator.add_argument(
        "-n", dest="name", required=True, help="Module name"
    )
    parser_cli_new_annotator.add_argument(
        "-t", dest="type", required=True, help="Module type"
    )
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
