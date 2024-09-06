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

from typing import Optional
from typing import Dict


class BasePreparer(object):
    def __init__(
        self,
        script_path: str,
        input_file: Optional[str] = None,
        name: Optional[str] = None,
        output_dir: Optional[str] = None,
        module_options: Dict = {},
        conf: Dict = {},
        serveradmindb=None,
        outer=None,
    ):
        import sys
        from pathlib import Path
        from os.path import split
        from os import makedirs
        from ..module.local import get_module_conf
        from ..exceptions import ModuleLoadingError
        from ..exceptions import NoInput

        self.serveradmindb = serveradmindb
        self.outer = outer
        self.cmd_parser = None
        self.input_path = None
        self.input_dir = None
        self.reader = None
        self.output_dir: Optional[str] = None
        self.output_base_fname = None
        self.input_fname = None
        self.module_options = None
        self.logger = None
        self.error_logger = None
        self.unique_excs = []
        self.uid = 0
        fp = sys.modules[self.__module__].__file__
        if not fp:
            raise ModuleLoadingError(module_name=self.__module__)
        self.main_fpath = Path(fp).resolve()
        self.module_name = self.main_fpath.stem
        self.input_path = Path(input_file).absolute() if input_file else None
        if not self.input_path:
            raise NoInput()
        self.output_path = f"{self.input_path}.{self.module_name}.prep.crv"
        self.input_dir, self.input_fname = split(self.input_path)
        if output_dir:
            self.output_dir = output_dir
        else:
            self.output_dir = self.input_dir
        if not Path(self.output_dir).exists():
            makedirs(self.output_dir)
        self.output_base_fname = name
        if not self.output_base_fname:
            self.output_base_fname = self.input_fname
        self.module_options = {}
        self.module_options.update(module_options)
        self.module_options.update(conf or {})
        main_fpath = script_path
        main_basename = Path(main_fpath).name
        if "." in main_basename:
            self.module_name = Path(main_fpath).stem
        else:
            self.module_name = main_basename
        self.module_dir = Path(main_fpath).parent
        self._setup_logger()
        self.conf = get_module_conf(self.module_name, module_type="preparer")

    def run_setups(self):
        self.setup()
        self.setup_io()
        self.open_output_files()

    def setup(self):
        pass

    def end(self):
        pass

    def _setup_logger(self):
        import logging

        self.logger = logging.getLogger(f"oakvar.{self.module_name}")
        self.error_logger = logging.getLogger("err." + self.module_name)

    def setup_io(self):
        from ..util.inout import FileReader
        from ..util.inout import FileWriter
        from ..exceptions import SetupError

        if (
            self.output_base_fname is None
            or self.conf is None
            or self.output_dir is None
        ):
            raise SetupError()
        self.reader = FileReader(self.input_path)
        self.writer = FileWriter(self.output_path)

    def open_output_files(self):
        from ..exceptions import SetupError

        if self.output_base_fname is None or self.output_dir is None:
            raise SetupError()
        from ..util.util import get_crv_def
        from ..consts import crv_idx

        self.writer.add_columns(get_crv_def())
        self.writer.write_definition()
        for index_columns in crv_idx:
            self.writer.add_index(index_columns)

    def run(self):
        from time import time, asctime, localtime
        from ..exceptions import SetupError
        from ..util.run import update_status

        self.run_setups()
        start_time = time()
        if (
            self.logger is None
            or self.conf is None
            or self.reader is None
            or not hasattr(self, "prepare")
        ):
            raise SetupError()
        self.logger.info("started: %s" % asctime(localtime(start_time)))
        status = f"started {self.conf['title']} ({self.module_name})"
        update_status(status, logger=self.logger, serveradmindb=self.serveradmindb)
        count = 0
        last_status_update_time = time()
        output = {}
        for ln, line, crv_data in self.reader.loop_data():
            out_data = None
            try:
                count += 1
                cur_time = time()
                if count % 100000 == 0 or cur_time - last_status_update_time > 10:
                    status = f"Running {self.module_name}: line {count}"
                    update_status(
                        status, logger=self.logger, serveradmindb=self.serveradmindb
                    )
                    last_status_update_time = cur_time
                uid = crv_data.get("uid")
                if not uid:
                    continue
                if uid > self.uid:
                    self.uid = uid
                out_data = self.prepare(crv_data)  # type: ignore
            except Exception as e:
                self._log_runtime_error(ln, line, e, fn=self.reader.path)
                continue
            if out_data:
                self.writer.write_data(out_data)  # type: ignore
        self.postloop()
        stop_time = time()
        self.logger.info("finished: %s" % asctime(localtime(stop_time)))
        runtime = stop_time - start_time
        self.logger.info("runtime: %6.3f" % runtime)
        status = f"finished {self.module_name}"
        update_status(status, logger=self.logger, serveradmindb=self.serveradmindb)
        self.replace_crv()
        self.end()
        return output

    def prepare(self, input_data: dict):
        _ = input_data
        pass

    def postloop(self):
        pass

    def _log_runtime_error(self, ln, line, e, fn=None):
        import traceback

        _ = line
        err_str = traceback.format_exc().rstrip()
        if (
            self.logger is not None
            and self.unique_excs is not None
            and err_str not in self.unique_excs
        ):
            self.unique_excs.append(err_str)
            self.logger.error(err_str)
        if self.error_logger is not None:
            self.error_logger.error(f"{fn}:{ln}\t{str(e)}")

    def get_new_uid(self):
        self.uid += 1
        return self.uid

    def replace_crv(self):
        from os import replace

        if self.output_path and self.input_path:
            replace(self.output_path, self.input_path)


if __name__ == "__main__":
    import argparse

    cmd_parser = argparse.ArgumentParser()
    cmd_parser.add_argument("input_file", help="Input crv file")
    cmd_parser.add_argument(
        "-n", dest="name", help="Name of job. " + "Default is input file name."
    )
    cmd_parser.add_argument(
        "-d",
        dest="output_dir",
        help="Output directory. " + "Default is input file directory.",
    )
