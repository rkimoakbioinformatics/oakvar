class BasePreparer(object):

    def __init__(self, *inargs, **inkwargs):
        import os
        import sys
        from pathlib import Path
        from ..module.local import get_module_conf
        from ..exceptions import ModuleLoadingError

        self.cmd_parser = None
        self.input_path = None
        self.input_dir = None
        self.reader = None
        self.output_dir = None
        self.output_base_fname = None
        self.input_fname = None
        self.confs = None
        self.args = None
        self.logger = None
        self.error_logger = None
        self.unique_excs = None
        self.uid = 0
        fp = sys.modules[self.__module__].__file__
        if not fp:
            raise ModuleLoadingError(self.__module__)
        self.main_fpath = Path(fp).resolve()
        self.module_name = self.main_fpath.stem
        self._define_main_cmd_args()
        self._parse_cmd_args(inargs, inkwargs)
        if self.args is None:
            return
        self.status_writer = self.args["status_writer"]
        main_fpath = self.args["script_path"]
        main_basename = os.path.basename(main_fpath)
        if "." in main_basename:
            self.module_name = ".".join(main_basename.split(".")[:-1])
        else:
            self.module_name = main_basename
        self.module_dir = os.path.dirname(main_fpath)
        self._setup_logger()
        self.conf = get_module_conf(self.module_name, module_type="preparer")

    def _define_main_cmd_args(self):
        import argparse

        self.cmd_parser = argparse.ArgumentParser()
        self.cmd_parser.add_argument("input_file", help="Input crv file")
        self.cmd_parser.add_argument(
            "-n", dest="name", help="Name of job. " + "Default is input file name."
        )
        self.cmd_parser.add_argument(
            "-d",
            dest="output_dir",
            help="Output directory. " + "Default is input file directory.",
        )
        self.cmd_parser.add_argument(
            "--confs", dest="confs", default="{}", help="Configuration string"
        )
        self.cmd_parser.add_argument(
            "--status_writer", default=None, help=argparse.SUPPRESS
        )

    def _parse_cmd_args(self, inargs, inkwargs):
        from os.path import abspath, split, exists
        from os import makedirs
        from json import loads
        from ..util.util import get_args
        from ..exceptions import NoInput

        args = get_args(self.cmd_parser, inargs, inkwargs)
        self.input_path = abspath(args["input_file"]) if args["input_file"] else None
        if not self.input_path:
            raise NoInput()
        self.output_path = f"{self.input_path}.{self.module_name}.prep.crv"
        self.input_dir, self.input_fname = split(self.input_path)
        if args["output_dir"]:
            self.output_dir = args["output_dir"]
        else:
            self.output_dir = self.input_dir
        if not (exists(self.output_dir)):
            makedirs(self.output_dir)
        self.output_base_fname = args.get("run_name")
        if not self.output_base_fname:
            self.output_base_fname = self.input_fname
        self.confs = {}
        conf = args.get("conf")
        if conf:
            self.confs.update(conf)
        if args.get("confs"):
            confs = args.get("confs").lstrip("'").rstrip("'").replace("'", '"')
            self.confs.update(loads(confs))
        self.args = args

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
        self.unique_excs = []

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
        from oakvar.exceptions import SetupError

        if (
            self.output_base_fname is None
            or self.output_dir is None
        ):
            raise SetupError()
        from oakvar.consts import crv_def
        from oakvar.consts import crv_idx

        self.writer.add_columns(crv_def)
        self.writer.write_definition()
        for index_columns in crv_idx:
            self.writer.add_index(index_columns)

    def run(self):
        from time import time, asctime, localtime
        from ..exceptions import SetupError

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
        if self.status_writer is not None:
            self.status_writer.queue_status_update(
                "status", "Started {} ({})".format(self.conf["title"], self.module_name)
            )
        count = 0
        last_status_update_time = time()
        output = {}
        for ln, line, crv_data in self.reader.loop_data():
            out_data = None
            try:
                count += 1
                cur_time = time()
                if self.status_writer is not None:
                    if count % 10000 == 0 or cur_time - last_status_update_time > 3:
                        self.status_writer.queue_status_update(
                            "status", "Running gene mapper: line {}".format(count)
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
        if self.status_writer is not None:
            self.status_writer.queue_status_update("status", "Finished gene mapper")
        self.replace_crv()
        self.end()
        return output

    def prepare(self):
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
