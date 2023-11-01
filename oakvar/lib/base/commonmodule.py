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

class BaseCommonModule(object):
    def __init__(self):
        self.cmd_arg_parser = None
        self.logger = None
        self.log_path = None
        self.error_logger = None
        self.module_name = None
        self.output_basename = None
        self.output_dir = None
        self.unique_excs = []
        self.args = None

    def _log_exception(self, e, halt=True):
        if halt:
            raise e
        else:
            if self.logger:
                self.logger.exception(e)

    def _define_cmd_parser(self):
        from argparse import ArgumentParser

        try:
            parser = ArgumentParser()
            parser.add_argument(
                "--logtofile",
                action="store_true",
                help="Path to a log file. If given without a path, the "
                + "job's run_name.log will be the log path.",
            )
            self.cmd_arg_parser = parser
        except Exception as e:
            self._log_exception(e)

    def parse_cmd_args(self, cmd_args):
        try:
            self._define_cmd_parser()
            if self.cmd_arg_parser:
                self.args = self.cmd_arg_parser.parse_args(cmd_args[1:])
        except Exception as e:
            self._log_exception(e)

    def setup(self):
        pass

    def _setup_logger(self):
        from logging import getLogger, FileHandler, Formatter, StreamHandler
        from pathlib import Path
        from ..exceptions import SetupError
        from ..consts import LOG_SUFFIX

        if (
            not self.args
            or not self.output_dir
            or not self.output_basename
            or not self.module_name
        ):
            raise SetupError(module_name=self.module_name)
        self.logger = getLogger("oakvar." + self.module_name)
        if self.args and self.args.logtofile:
            self.log_path = Path(self.output_dir) / (self.output_basename + LOG_SUFFIX)
            log_handler = FileHandler(self.log_path, "a")
        else:
            log_handler = StreamHandler()
        formatter = Formatter(
            "%(asctime)s %(name)-20s %(message)s", "%Y/%m/%d %H:%M:%S"
        )
        log_handler.setFormatter(formatter)
        self.logger.addHandler(log_handler)
        self.error_logger = getLogger("err." + self.module_name)
        if self.args.logtofile:
            error_log_path = Path(self.output_dir) / (self.output_basename + ".err")
            error_log_handler = FileHandler(error_log_path, "a")
        else:
            error_log_handler = StreamHandler()
        formatter = Formatter("%(name)s\t%(message)s")
        error_log_handler.setFormatter(formatter)
        self.error_logger.addHandler(error_log_handler)
