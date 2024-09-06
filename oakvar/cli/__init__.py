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


class CliOuter:
    def __init__(self):
        import sys
        from rich.console import Console

        self.out_writer = Console()
        self.err_writer = sys.stderr
        self.fileno = lambda: False

    def write(self, msg):
        self.out_writer.print(msg)

    def error(self, msg):
        self.err_writer.write(f"{msg}\n")
        self.err_writer.flush()

    def flush(self):
        self.err_writer.flush()


def cli_entry(func):
    def change_args_for_cli(args):
        if not hasattr(args, "quiet") or getattr(args, "quiet") is not True:
            args.outer = CliOuter()
        ret = func(args)
        exit(ret)

    return change_args_for_cli


def cli_func(func):
    def run_cli_func(*args, **kwargs):
        from ..__main__ import handle_exception

        args = get_args(*args, **kwargs)
        if "quiet" in args:
            del args["quiet"]
        try:
            ret = func(args, **kwargs)
            if ret is False:
                ret = 1
            else:
                ret = None
            return ret
        except Exception as e:
            handle_exception(e)

    def get_args(*args, **kwargs):
        from ..lib.util.util import get_args
        from inspect import signature

        s = signature(func)
        name = s.parameters["__name__"].default
        parser = get_parser(name)
        args = get_args(parser, args, kwargs)
        return args

    return run_cli_func


def get_parser(parser_name):
    from ..__main__ import get_entry_parser
    from typing import Any

    p_entry = get_entry_parser()
    pp_dict: dict[str, Any] = get_commands(p_entry)
    for pp_cmd, pp_parser in pp_dict.items():
        ppp_dict = get_commands(pp_parser)
        if ppp_dict:
            for ppp_cmd, ppp_parser in ppp_dict.items():
                pppp_dict = get_commands(ppp_parser)
                if pppp_dict:
                    for pppp_cmd, pppp_parser in pppp_dict.items():
                        cmd = f"{pp_cmd} {ppp_cmd} {pppp_cmd}"
                        if cmd == parser_name:
                            return pppp_parser
                else:
                    cmd = f"{pp_cmd} {ppp_cmd}"
                    if cmd == parser_name:
                        return ppp_parser
        else:
            cmd = f"{pp_cmd}"
            if cmd == parser_name:
                return pp_parser
    return None


def get_commands(p):
    from argparse import _SubParsersAction
    from typing import Any

    cmds: dict[str, Any] = {}
    for a in p._actions:
        if type(a) == _SubParsersAction:
            cmds = a.choices
            break
    return cmds
