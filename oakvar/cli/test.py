# OakVar Dual License
# 
# Copyright (c) 2023 Oak Bioinformatics, LLC
# 
# This program is dual licensed under the Affero GPL-3.0 or later for non-commercial, 
# open source use, and a commercial license, which is available for purchase, 
# for commercial use.
# 
# For commercial use, please contact Oak Bioinformatics, LLC for obtaining a
# commercial license. OakVar commercial license does not impose the Affero GPL
# open-source licensing terms, conditions, and limitations. To obtain a
# commercial-use license of OakVar, please visit our website at
# https://oakbioinformatics.com or contact us at info@oakbioinformatics.com for
# more information.
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
def cli_util_test(args):
    return test(args)


@cli_func
def test(args, __name__="util test"):
    from ..api.test import test

    ret = test(**args)
    if ret:
        num_failed: int = ret.get("num_failed", 0)
        if num_failed > 0:
            return False
        else:
            return True
    return True


def get_parser_cli_util_test():
    from argparse import ArgumentParser

    parser_cli_util_test = ArgumentParser()
    parser_cli_util_test.add_argument("-d", "--rundir", help="Directory for output")
    parser_cli_util_test.add_argument(
        "-m", "--modules", nargs="+", help="Name of module(s) to test. (e.g. gnomad)"
    )
    parser_cli_util_test.add_argument(
        "--quiet", action="store_true", default=None, help="run quietly"
    )
    parser_cli_util_test.set_defaults(func=cli_util_test)
    return parser_cli_util_test


def main():
    args = get_parser_cli_util_test().parse_args()
    cli_util_test(args)


if __name__ == "__main__":
    main()
