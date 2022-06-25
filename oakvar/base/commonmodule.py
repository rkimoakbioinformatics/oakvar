class BaseCommonModule(object):
    def __init__(self):
        self.cmd_arg_parser = None
        self.logger = None
        self.log_path = None
        self.error_logger = None
        self.unique_excs = None
        self.module_name = None
        self.output_basename = None
        self.output_dir = None
        self.parsed_args = None

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
            self.cmd_arg_parser = parser
        except Exception as e:
            self._log_exception(e)

    def parse_cmd_args(self, cmd_args):
        try:
            self._define_cmd_parser()
            if self.cmd_arg_parser is not None:
                self.parsed_args = self.cmd_arg_parser.parse_args(cmd_args[1:])
        except Exception as e:
            self._log_exception(e)

    def setup(self):
        pass

    def _setup_logger(self):
        from logging import getLogger, FileHandler, Formatter, StreamHandler
        from os.path import join

        try:
            if (
                self.module_name is not None
                and self.output_dir is not None
                and self.output_basename is not None
            ):
                self.logger = getLogger("oakvar." + self.module_name)
                if self.output_basename != "__dummy__":
                    self.log_path = join(self.output_dir, self.output_basename + ".log")
                    log_handler = FileHandler(self.log_path, "a")
                else:
                    log_handler = StreamHandler()
                formatter = Formatter(
                    "%(asctime)s %(name)-20s %(message)s", "%Y/%m/%d %H:%M:%S"
                )
                log_handler.setFormatter(formatter)
                self.logger.addHandler(log_handler)
                self.error_logger = getLogger("error." + self.module_name)
                if self.output_basename != "__dummy__":
                    error_log_path = join(
                        self.output_dir, self.output_basename + ".err"
                    )
                    error_log_handler = FileHandler(error_log_path, "a")
                else:
                    error_log_handler = StreamHandler()
                formatter = Formatter("SOURCE:%(name)-20s %(message)s")
                error_log_handler.setFormatter(formatter)
                self.error_logger.addHandler(error_log_handler)
        except Exception as e:
            self._log_exception(e)
        self.unique_excs = []
