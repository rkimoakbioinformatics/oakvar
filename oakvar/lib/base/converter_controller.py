from typing import Any
from typing import Optional
from typing import List
from typing import Dict
from typing import Tuple
from oakvar.lib.base.converter import BaseConverter
from re import compile
from liftover import ChainFile # type: ignore

chromdict = {
    "chrx": "chrX",
    "chry": "chrY",
    "chrMT": "chrM",
    "chrMt": "chrM",
    "chr23": "chrX",
    "chr24": "chrY",
}
base_re = compile("^[ATGC]+|[-]+$")

class ConverterController(object):
    def __init__(
        self,
        converter_name: Optional[str] = None,
        input_format: Optional[str] = None,
        run_name: Optional[str] = None,
        output_dir: Optional[str] = None,
        genome: Optional[str] = None,
        serveradmindb=None,
        conf: Dict = {},
        module_options: Dict = {},
        input_encoding=None,
        ignore_sample: bool=False,
        fill_in_missing_ref: bool=False,
        mp: int=1,
        outer=None,
    ):
        from re import compile
        from oakvar import get_wgs_reader
        from oakvar.lib.base.commonmodule import BaseCommonModule

        self.logger = None
        self.converters = {}
        self.input_file_encodings: Dict[str, str] = {}
        self.output_base_fname: Optional[str] = None
        self.error_logger = None
        self.unique_excs: Dict[str, int] = {}
        self.err_holder = []
        self.wpath = None
        self.crm_path = None
        self.crs_path = None
        self.crl_path = None
        self.do_liftover = None
        self.do_liftover_chrM = None
        self.lifter = None
        self.module_options = None
        self.given_input_assembly: Optional[str] = None
        self.converter_by_input_path: Dict[str, Optional[BaseConverter]] = {}
        self.extra_output_columns: List[Dict[str, Any]] = []
        self.file_num_valid_variants = 0
        self.file_error_lines = 0
        self.total_num_valid_variants = 0
        self.total_error_lines = 0
        self.fileno = 0
        self.ignore_sample = ignore_sample
        self.total_num_converted_variants = 0
        self.input_formats: List[str] = []
        self.genome_assemblies: List[str] = []
        self.base_re = compile("^[ATGC]+|[-]+$")
        self.last_var: str = ""
        self.unique_vars: dict = {}
        self.chromdict = {
            "chrx": "chrX",
            "chry": "chrY",
            "chrMT": "chrM",
            "chrMt": "chrM",
            "chr23": "chrX",
            "chr24": "chrY",
        }
        self.converter_name: Optional[str] = converter_name
        self.input_format = input_format
        self.run_name = run_name
        self.output_dir = output_dir
        self.genome = genome
        self.given_input_assembly = genome
        self.conf: Dict = {}
        self.module_options = module_options
        if conf:
            self.conf.update(conf)
        self.serveradmindb = serveradmindb
        self.input_encoding = input_encoding
        self.outer = outer
        self.setup_logger()
        self.wgs_reader: Optional[BaseCommonModule] = None
        if fill_in_missing_ref:
            self.wgs_reader = get_wgs_reader(assembly="hg38")
        self.time_error_written: float = 0
        self.mp = mp

    def setup_logger(self):
        from logging import getLogger

        self.logger = getLogger("oakvar.converter")
        self.error_logger = getLogger("err.converter")

    def choose_converter(self, input_paths: List[str]) -> Optional[BaseConverter]:
        from oakvar.lib.module.local import get_local_module_infos_of_type
        from oakvar.lib.module.local import get_local_module_info
        from oakvar.lib.module.local import LocalModule
        from ..util.module import get_converter_class
        import traceback


        chosen_converter: Optional[BaseConverter] = None
        module_infos: List[LocalModule] = []
        if self.converter_name:
            module_info = get_local_module_info(self.converter_name)
            if module_info is None:
                raise Exception(f" {self.converter_name} does not exist. Please check --converter-name option was given correctly, or consider installing {self.converter_name} module with \"ov module install {self.converter_name}\" command, if the module is in the OakVar store.")
            module_infos.append(module_info)
        elif self.input_format:
            module_name = self.input_format + "-converter"
            module_info = get_local_module_info(module_name)
            if module_info is None:
                raise Exception(module_name + f" does not exist. Please check --input-format option was given correctly, or consider installing {module_name} module with \"ov module install {module_name}\" command, if the module is in the OakVar store.")
            module_infos.append(module_info)
        else:
            module_infos = list(get_local_module_infos_of_type("converter").values())
        for module_info in module_infos:
            try:
                cls = get_converter_class(module_info.name)
                converter = cls(wgs_reader=self.wgs_reader)
            except Exception as e:
                if self.logger:
                    self.logger.error(f"{traceback.format_exc()}\nSkipping {module_info.name} as it could not be loaded. ({e})")
                continue
            try:
                check_success = converter.check_format(input_paths[0])
            except Exception:
                if self.error_logger:
                    self.error_logger.error(traceback.format_exc())
                check_success = False
            if check_success:
                chosen_converter = converter
                break
        if chosen_converter:
            if self.logger:
                self.logger.info(f"Using {chosen_converter.name} for {' '.join(input_paths)}")
            return chosen_converter

    #def collect_extra_output_columns(self):
    #    for converter in self.converter_by_input_path.values():
    #        if not converter:
    #            continue
    #        if converter.conf:
    #            extra_output_columns = converter.conf.get("extra_output_columns")
    #            if not extra_output_columns:
    #                continue
    #            for col in extra_output_columns:
    #                self.extra_output_columns.append(col)

    def iter_df_chunk(self, input_paths: List[str], size: int=10000):
        converter = self.choose_converter(input_paths)
        if not converter:
            if self.logger:
                self.logger.warn("No converter was found for input files.")
            return
        self.set_variables_pre_run()
        for df in converter.iter_df_chunk(input_paths=input_paths, size=size, ignore_sample=self.ignore_sample):
            print(f"@ df from converter={df}")
            yield df
        self.log_ending()
        ret = {
            "total_lnum": self.total_num_converted_variants,
            "write_lnum": self.total_num_valid_variants,
            "error_lnum": self.total_error_lines,
            "input_formats": self.input_formats,
            "assemblies": self.genome_assemblies,
        }
        return ret

    def set_variables_pre_run(self):
        from time import time

        self.start_time = time()
        self.total_num_converted_variants = 0
        self.uid = 0

    def log_ending(self):
        from time import time, asctime, localtime
        from oakvar.lib.util.run import update_status

        if not self.logger:
            raise
        self.logger.info(
            "total number of valid variants: {}".format(
                self.total_num_converted_variants
            )
        )
        self.logger.info("total number of lines skipped due to errors: %d" % self.total_error_lines)
        end_time = time()
        self.logger.info("finished: %s" % asctime(localtime(end_time)))
        runtime = round(end_time - self.start_time, 3)
        self.logger.info("runtime: %s" % runtime)
        status = "finished Converter"
        update_status(status, logger=self.logger, serveradmindb=self.serveradmindb)

    def end(self):
        pass
