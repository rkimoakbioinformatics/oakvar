from typing import Any
from typing import Optional
from typing import Union
from typing import List
from typing import Dict
from typing import Tuple
from typing import TextIO
from oakvar import BaseConverter
from pyliftover import LiftOver
from io import BufferedReader
from re import compile

STDIN = "stdin"
chromdict = {
    "chrx": "chrX",
    "chry": "chrY",
    "chrMT": "chrM",
    "chrMt": "chrM",
    "chr23": "chrX",
    "chr24": "chrY",
}
base_re = compile("^[ATGC]+|[-]+$")

def handle_genotype(variant):
    if "genotype" in variant and "." in variant["genotype"]:
        variant["genotype"] = variant["genotype"].replace(".", variant["ref_base"])

def _log_conversion_error(logger, error_logger, serveradmindb, input_path: str, input_fname: str, line_no: int, e, unique_excs: dict, err_holder: list, full_line_error=True):
    from traceback import format_exc
    from oakvar.lib.exceptions import ExpectedException
    from oakvar.lib.exceptions import NoAlternateAllele
    from oakvar.lib.util.run import update_status

    if isinstance(e, NoAlternateAllele):
        if line_no % 10000 == 0:
            status = f"Running Converter ({input_fname}): line {line_no}"
            update_status(
                status, logger=logger, serveradmindb=serveradmindb
            )
        return
    #if full_line_error:
    #    self.file_error_lines += 1
    #    self.total_error_lines += 1
    if isinstance(e, ExpectedException):
        err_str = str(e)
    else:
        err_str = format_exc().rstrip()
    if err_str not in unique_excs:
        err_no = len(unique_excs)
        unique_excs[err_str] = err_no
        if hasattr(e, "traceback") and e.traceback is False:
            pass
        else:
            logger.error(f"Error [{err_no}]: {input_path}: {err_str}")
        err_holder.append(f"{err_no}:{line_no}\t{str(e)}")
    else:
        err_no = unique_excs[err_str]
        err_holder.append(f"{err_no}:{line_no}\t{str(e)}")
    #if err_holder and t - time_error_written > 60:
    #    for s in err_holder:
    #        error_logger.error(s)
    #    err_holder = []
    if line_no % 10000 == 0:
        status = f"Running Converter ({input_fname}): line {line_no}"
        update_status(status, logger=logger, serveradmindb=serveradmindb)

def is_chrM(wdict):
    return wdict["chrom"] == "chrM"

def perform_liftover_if_needed(variant, do_liftover: bool, do_liftover_chrM: bool, lifter, wgs_reader) -> Optional[Dict[str, Any]]:
    from copy import copy
    from oakvar.lib.util.seq import liftover_one_pos
    from oakvar.lib.util.seq import liftover

    if is_chrM(variant):
        needed = do_liftover_chrM
    else:
        needed = do_liftover
    if needed:
        prelift_wdict = copy(variant)
        #prelift_wdict["uid"] = self.uid
        #self.crl_writer.write_data(prelift_wdict)
        crl_data = prelift_wdict
        (
            variant["chrom"],
            variant["pos"],
            variant["ref_base"],
            variant["alt_base"],
        ) = liftover(
            variant["chrom"],
            int(variant["pos"]),
            variant["ref_base"],
            variant["alt_base"],
            lifter=lifter,
            wgs_reader=wgs_reader,
        )
        converted_end = liftover_one_pos(
            variant["chrom"], variant["pos_end"], lifter=lifter
        )
        if converted_end is None:
            pos_end = ""
        else:
            pos_end = converted_end[1]
        variant["pos_end"] = pos_end
    else:
        crl_data = None
    return crl_data

def add_end_pos_if_absent(variant: dict):
    col_name = "pos_end"
    if col_name not in variant:
        ref_base = variant["ref_base"]
        ref_len = len(ref_base)
        if ref_len == 1:
            variant[col_name] = variant["pos"]
        else:
            variant[col_name] = variant["pos"] + ref_len - 1

def normalize_variant(variant):
    from oakvar.lib.util.seq import normalize_variant_left

    p, r, a = (
        int(variant["pos"]),
        variant["ref_base"],
        variant["alt_base"],
    )
    (
        new_pos,
        new_ref,
        new_alt,
    ) = normalize_variant_left("+", p, r, a)
    variant["pos"] = new_pos
    variant["ref_base"] = new_ref
    variant["alt_base"] = new_alt

def check_invalid_base(variant: dict):
    from oakvar.lib.exceptions import IgnoredVariant

    if not base_re.fullmatch(variant["ref_base"]):
        raise IgnoredVariant("Invalid reference base")
    if not base_re.fullmatch(variant["alt_base"]):
        raise IgnoredVariant("Invalid alternate base")

def handle_ref_base(variant, wgs_reader):
    from oakvar.lib.exceptions import IgnoredVariant

    if "ref_base" not in variant or variant["ref_base"] in [
        "",
        ".",
    ]:
        variant["ref_base"] = wgs_reader.get_bases(
            variant.get("chrom"), int(variant["pos"])
        ).upper()
    else:
        ref_base = variant["ref_base"]
        if ref_base == "" and variant["alt_base"] not in [
            "A",
            "T",
            "C",
            "G",
        ]:
            raise IgnoredVariant("Reference base required for non SNV")
        elif ref_base is None or ref_base == "":
            variant["ref_base"] = wgs_reader.get_bases(
                variant.get("chrom"), int(variant.get("pos"))
            )

def handle_chrom(variant):
    from oakvar.lib.exceptions import IgnoredVariant

    if not variant.get("chrom"):
        raise IgnoredVariant("No chromosome")
    if not variant.get("chrom").startswith("chr"):
        variant["chrom"] = "chr" + variant.get("chrom")
    variant["chrom"] = chromdict.get(
        variant.get("chrom"), variant.get("chrom")
    )

def is_unique_variant(variant: dict, unique_vars: dict) -> bool:
    chrom = variant["chrom"]
    pos = variant["pos"]
    ref_base = variant["ref_base"]
    alt_base = variant["alt_base"]
    if chrom not in unique_vars:
        unique_vars[chrom] = {pos: {ref_base: {alt_base: 1}}}
        return True
    if pos not in unique_vars[chrom]:
        unique_vars[chrom][pos] = {ref_base: {alt_base: 1}}
        return True
    if ref_base not in unique_vars[chrom][pos]:
        unique_vars[chrom][pos][ref_base] = {alt_base: 1}
        return True
    if alt_base not in unique_vars[chrom][pos][ref_base]:
        unique_vars[chrom][pos][ref_base][alt_base] = 1
        return True
    return False

def handle_variant(
        variant: dict, var_no: int, converter, unique_vars: dict, do_liftover: bool, do_liftover_chrM: bool, lifter, wgs_reader, logger, error_logger, serveradmindb, input_path, input_fname, unique_excs, err_holder
) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]], bool]:
    from oakvar.lib.exceptions import NoVariantError

    print(f"@ check 1")
    if variant["ref_base"] == variant["alt_base"]:
        raise NoVariantError()
    tags = variant.get("tags")
    unique = is_unique_variant(variant, unique_vars)
    print(f"@ check 2. unique={unique}. unique_vars={unique_vars}")
    if unique:
        #self.uid += 1
        #variant["uid"] = self.uid
        variant["unique"] = True
        handle_chrom(variant)
        print(f"@ check")
        handle_ref_base(variant, wgs_reader)
        print(f"@ check")
        check_invalid_base(variant)
        print(f"@ check")
        normalize_variant(variant)
        add_end_pos_if_absent(variant)
        crl_data = perform_liftover_if_needed(variant, do_liftover, do_liftover_chrM, lifter, wgs_reader)
        #self.crv_writer.write_data(variant)
        try:
            converter.addl_operation_for_unique_variant(variant, var_no)
        except Exception as e:
            print(f"@!!!!!! e={e}")
            _log_conversion_error(logger, error_logger, serveradmindb, input_path, input_fname, variant["read_lnum"], e, unique_excs, err_holder, full_line_error=False)
    else:
        variant["unique"] = False
        crl_data = None
    handle_genotype(variant)
    #fileno = input_path_dict2[input_path]
    if unique:
        #self.crm_writer.write_data(
        crm_data = {
            "original_line": variant["read_lnum"],
            "tags": tags,
            #"uid": self.uid,
            #"fileno": fileno,
        }
    else:
        crm_data = None
    return crl_data, crm_data, unique

def handle_converted_variants(
    variants: List[Dict[str, Any]], converter: BaseConverter, do_liftover: bool, do_liftover_chrM: bool, lifter, wgs_reader, logger, error_logger, serveradmindb, input_path: str, input_fname: str, unique_excs: dict, err_holder: list
):
    from oakvar.lib.exceptions import IgnoredVariant

    if variants is BaseConverter.IGNORE:
        return None, None, None, 0
    if not variants:
        raise IgnoredVariant("No valid alternate allele was found in any samples.")
    unique_vars = {}
    variant_l: List[Dict[str, Any]] = []
    crl_l: List[Dict[str, Any]] = []
    crm_l: List[Dict[str, Any]] = []
    var_order = 0
    for var_no, variant in enumerate(variants):
        print(f"@ => variant in handle_converted_variants={variant}")
        try:
            crl_data, crm_data, unique = handle_variant(variant, var_no, converter, unique_vars, do_liftover, do_liftover_chrM, lifter, wgs_reader, logger, error_logger, serveradmindb, input_path, input_fname, unique_excs, err_holder)
            variant["var_order"] = var_order
            if unique:
                var_order += 1
        except Exception as e:
            print(f"@@!! e={e}")
            _log_conversion_error(logger, error_logger, serveradmindb, input_path, input_fname, variant["read_lnum"], e, unique_excs, err_holder)
            continue
        print(f"@@ ==> variant={variant}")
        variant_l.append(variant)
        if crl_data:
            crl_l.append(crl_data)
        if crm_data:
            crm_l.append(crm_data)
    return variant_l, crl_l, crm_l, var_order

def gather_variantss(f, converter: BaseConverter, batch_size: int, core_num: int, start_line: int, do_liftover: bool, do_liftover_chrM: bool, lifter, wgs_reader, logger, error_logger, serveradmindb, input_path: str, input_fname: str, unique_excs: dict, err_holder: list):
    variants_l = []
    for read_lnum, variants in converter.convert_file(
        f, 
        logger,
        error_logger,
        serveradmindb,
        input_path,
        input_fname,
        unique_excs,
        err_holder,
        batch_size=batch_size,
        core_num=core_num,
        start_line=start_line,
        exc_handler=_log_conversion_error
    ):
        for variant in variants:
            variant["read_lnum"] = read_lnum
        variants_l.append(variants)
    variant_nl = []
    crl_nl = []
    crm_nl = []
    max_var_orders = []
    for variants in variants_l:
        print(f"@@@@@ variants={variants}")
        try:
            variants_datas, crl_datas, crm_datas, max_var_order = handle_converted_variants(variants, converter, do_liftover, do_liftover_chrM, lifter, wgs_reader, logger, error_logger, serveradmindb, input_path, input_fname, unique_excs, err_holder)
            print(f"@@@@@@@@@@ variants_datas={variants_datas}")
            variant_nl.append(variants_datas)
            crl_nl.append(crl_datas)
            crm_nl.append(crm_datas)
            max_var_orders.append(max_var_order)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            _log_conversion_error(logger, error_logger, serveradmindb, input_path, input_fname, variants[0]["read_lnum"], e, unique_excs, err_holder)
    return variant_nl, crl_nl, crm_nl, max_var_orders


class MasterConverter(object):
    def __init__(
        self,
        inputs: List[str] = [],
        input_format: Optional[str] = None,
        name: Optional[str] = None,
        output_dir: Optional[str] = None,
        genome: Optional[str] = None,
        serveradmindb=None,
        conf: Dict = {},
        module_options: Dict = {},
        input_encoding=None,
        ignore_sample: bool=False,
        mp: int=1,
        outer=None,
    ):
        from re import compile
        from oakvar import get_wgs_reader
        from oakvar.lib.exceptions import ExpectedException

        self.logger = None
        self.crv_writer = None
        self.crs_writer = None
        self.crm_writer = None
        self.crl_writer = None
        self.converters = {}
        self.available_input_formats = []
        self.input_paths = None
        self.input_dir = None
        self.input_path_dict = {}
        self.input_path_dict2 = {}
        self.input_file_handles: Dict[str, Union[TextIO, BufferedReader]] = {}
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
        self.extra_output_columns = []
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
        if not inputs:
            raise ExpectedException("Input files are not given.")
        self.inputs = inputs
        self.format = input_format
        self.name = name
        self.output_dir = output_dir
        self.genome = genome
        self.parse_inputs()
        self.parse_output_dir()
        self.given_input_assembly = genome
        self.conf: Dict = {}
        self.module_options = module_options
        if conf:
            self.conf.update(conf)
        self.serveradmindb = serveradmindb
        self.input_encoding = input_encoding
        self.outer = outer
        self.setup_logger()
        self.wgs_reader = get_wgs_reader(assembly="hg38")
        self.time_error_written: float = 0
        self.mp = mp

    def get_genome_assembly(self, converter) -> str:
        from oakvar.lib.system.consts import default_assembly_key
        from oakvar.lib.exceptions import NoGenomeException
        from oakvar.lib.system import get_user_conf

        if self.given_input_assembly:
            return self.given_input_assembly
        input_assembly = getattr(converter, "input_assembly", None)
        if input_assembly:
            return input_assembly
        user_conf = get_user_conf() or {}
        genome_assembly = user_conf.get(default_assembly_key, None)
        if genome_assembly:
            return genome_assembly
        raise NoGenomeException()

    def set_do_liftover(self, genome_assembly, converter, f):
        self.do_liftover = genome_assembly != "hg38"
        if hasattr(converter, "get_do_liftover_chrM"):
            self.do_liftover_chrM = converter.get_do_liftover_chrM(
                genome_assembly, f, self.do_liftover
            )
        else:
            self.do_liftover_chrM = self.do_liftover
        if self.logger:
            self.logger.info(f"liftover needed: {self.do_liftover}")
            self.logger.info(f"liftover for chrM needed: {self.do_liftover_chrM}")

    def setup_lifter(self, genome_assembly) -> Optional[LiftOver]:
        from oakvar.lib.util.seq import get_lifter

        self.lifter = get_lifter(source_assembly=genome_assembly)

    def parse_inputs(self):
        from pathlib import Path

        self.input_paths = []
        self.input_paths = [
            str(Path(x).absolute()) for x in self.inputs if x != "-"
        ]
        self.input_dir = str(Path(self.input_paths[0]).parent)
        for i in range(len(self.input_paths)):
            self.input_path_dict[i] = self.input_paths[i]
            self.input_path_dict2[self.input_paths[i]] = i

    def parse_output_dir(self):
        from pathlib import Path
        from os import makedirs

        if not self.output_dir:
            self.output_dir = self.input_dir
        if not self.output_dir:
            raise
        if not (Path(self.output_dir).exists()):
            makedirs(self.output_dir)
        self.output_base_fname: Optional[str] = self.name
        if not self.output_base_fname:
            if not self.input_paths:
                raise
            self.output_base_fname = Path(self.input_paths[0]).name

    def get_file_object_for_input_path(self, input_path: str):
        import gzip
        import sys
        from pathlib import Path
        from oakvar.lib.util.util import detect_encoding

        suffix = Path(input_path).suffix
        # TODO: Remove the hardcoding.
        if suffix in [".parquet"]:
            encoding = None
        else:
            if input_path == STDIN:
                encoding = "utf-8"
            elif self.input_encoding:
                encoding = self.input_encoding
            else:
                if self.logger:
                    self.logger.info(f"detecting encoding of {input_path}")
                encoding = detect_encoding(input_path)
        if self.logger:
            self.logger.info(f"encoding: {input_path} {encoding}")
        if input_path == STDIN:
            f = sys.stdin
        elif input_path.endswith(".gz"):
            f = gzip.open(input_path, mode="rt", encoding=encoding)
        elif suffix in [".parquet"]:
            f = open(input_path, "rb")
        else:
            f = open(input_path, encoding=encoding)
        return f

    def collect_input_file_handles(self):
        from sys import stdin

        if not self.input_paths:
            raise
        for input_path in self.input_paths:
            if input_path in ["./stdin", STDIN]:
                f = stdin
            else:
                f = self.get_file_object_for_input_path(input_path)
            self.input_file_handles[input_path] = f

    def setup(self):
        self.collect_converters()
        self.collect_input_file_handles()
        self.check_input_format()
        self.collect_converter_by_input()
        self.collect_extra_output_columns()
        self.open_output_files()

    def setup_logger(self):
        from logging import getLogger

        self.logger = getLogger("oakvar.converter")
        self.error_logger = getLogger("err.converter")

    def collect_converters(self):
        from oakvar.lib.module.local import get_local_module_infos_of_type
        from oakvar.lib.util.util import load_class

        for module_name, module_info in get_local_module_infos_of_type(
            "converter"
        ).items():
            cls = load_class(module_info.script_path)
            converter = cls(ignore_sample=self.ignore_sample)
            # TODO: backward compatibility
            converter.output_dir = None
            converter.run_name = None
            converter.module_name = module_name
            converter.name = module_info.name
            converter.version = module_info.version
            converter.conf = module_info.conf
            converter.script_path = module_info.script_path
            format_name = module_info.conf.get("format_name")
            # end of backward compatibility
            if format_name:
                converter.format_name = format_name
            elif not hasattr(converter, "format_name"):
                converter.format_name = module_name.split("-")[0]
            if not converter.format_name:
                if self.outer:
                    self.outer.write(
                        f"Skipping {module_info.name} as it does not "
                        + "have format_name defined."
                    )
                continue
            converter.module_name = module_info.name
            if converter.format_name not in self.converters:
                self.converters[converter.format_name] = converter
            else:
                if self.outer:
                    self.outer.write(
                        f"{module_info.name} is skipped because "
                        + f"{converter.format_name} is already handled by "
                        + f"{self.converters[converter.format_name].name}."
                    )
                continue
        self.available_input_formats = list(self.converters.keys())

    def collect_converter_by_input(self):
        if not self.input_paths:
            return
        for input_path in self.input_paths:
            f = self.input_file_handles[input_path]
            converter = self.get_converter_for_input_file(f)
            self.converter_by_input_path[input_path] = converter

    def collect_extra_output_columns(self):
        for converter in self.converter_by_input_path.values():
            if not converter:
                continue
            if converter.conf:
                extra_output_columns = converter.conf.get("extra_output_columns")
                if not extra_output_columns:
                    continue
                for col in extra_output_columns:
                    self.extra_output_columns.append(col)

    def check_input_format(self):
        from oakvar.lib.exceptions import InvalidInputFormat

        if self.format and self.format not in self.available_input_formats:
            raise InvalidInputFormat(self.format)

    def get_converter_for_input_file(self, f) -> Optional[BaseConverter]:
        import sys
        from oakvar.lib.exceptions import ArgumentError

        if f == sys.stdin:
            if not self.format:
                raise ArgumentError(
                    msg="--input-format option should be given if "
                    + "stdin is used for input."
                )
            if self.format not in self.converters:
                raise ArgumentError(
                    msg=f"{self.format} is not found in installed converter modules."
                )
            return self.converters[self.format]
        else:
            converter: Optional[BaseConverter] = None
            if self.format:
                if self.format in self.converters:
                    converter = self.converters[self.format]
            else:
                for check_converter in self.converters.values():
                    f.seek(0)
                    try:
                        check_success = check_converter.check_format(f)
                    except Exception:
                        import traceback

                        if self.error_logger:
                            self.error_logger.error(traceback.format_exc())
                        check_success = False
                    f.seek(0)
                    if check_success:
                        converter = check_converter
                        break
            if converter:
                if self.logger:
                    self.logger.info(f"Using {converter.module_name} for {f.name}")
                return converter
        return None

    def set_converter_properties(self, converter):
        from oakvar.lib.exceptions import SetupError
        from oakvar.lib.module.local import get_module_code_version

        if self.conf is None:
            raise SetupError()
        converter.output_dir = self.output_dir
        converter.run_name = self.output_base_fname
        module_name = converter.module_name
        converter.version = get_module_code_version(converter.module_name)
        if module_name in self.conf:
            if hasattr(converter, "conf") is False:
                converter.conf = {}
            converter.conf.update(self.conf[module_name])

    def setup_crv_writer(self):
        from pathlib import Path
        from oakvar.lib.util.util import get_crv_def
        from oakvar.lib.util.inout import FileWriter
        from oakvar.lib.consts import crv_idx
        from oakvar.lib.consts import STANDARD_INPUT_FILE_SUFFIX

        if not self.output_dir or not self.output_base_fname:
            raise
        crv_def = get_crv_def()
        self.wpath = Path(self.output_dir) / (
            self.output_base_fname + STANDARD_INPUT_FILE_SUFFIX
        )
        self.crv_writer = FileWriter(self.wpath)
        self.crv_writer.add_columns(crv_def)
        self.crv_writer.write_definition()
        for index_columns in crv_idx:
            self.crv_writer.add_index(index_columns)

    def setup_crs_writer(self):
        from pathlib import Path
        from oakvar.lib.util.util import get_crs_def
        from oakvar.lib.util.inout import FileWriter
        from oakvar.lib.consts import crs_idx
        from oakvar.lib.consts import SAMPLE_FILE_SUFFIX

        if not self.output_dir or not self.output_base_fname:
            raise
        crs_def = get_crs_def()
        self.crs_path = Path(self.output_dir) / (
            self.output_base_fname + SAMPLE_FILE_SUFFIX
        )
        self.crs_writer = FileWriter(self.crs_path)
        self.crs_writer.add_columns(crs_def)
        self.crs_writer.add_columns(self.extra_output_columns)
        self.crs_writer.write_definition()
        for index_columns in crs_idx:
            self.crs_writer.add_index(index_columns)

    def setup_crm_writer(self):
        from pathlib import Path
        from oakvar.lib.util.util import get_crm_def
        from oakvar.lib.util.inout import FileWriter
        from oakvar.lib.consts import crm_idx
        from oakvar.lib.consts import MAPPING_FILE_SUFFIX

        if not self.output_dir or not self.output_base_fname:
            raise
        crm_def = get_crm_def()
        self.crm_path = Path(self.output_dir) / (
            self.output_base_fname + MAPPING_FILE_SUFFIX
        )
        self.crm_writer = FileWriter(self.crm_path)
        self.crm_writer.add_columns(crm_def)
        self.crm_writer.write_definition()
        for index_columns in crm_idx:
            self.crm_writer.add_index(index_columns)
        self.crm_writer.write_input_paths(self.input_path_dict)

    def setup_crl_writer(self):
        from pathlib import Path
        from oakvar.lib.util.util import get_crl_def
        from oakvar.lib.util.inout import FileWriter
        from oakvar.lib.consts import VARIANT_LEVEL_OUTPUT_SUFFIX

        if not self.output_dir or not self.output_base_fname:
            raise
        crl_def = get_crl_def()
        self.crl_path = (
            Path(self.output_dir)
            / f"{self.output_base_fname}.original_input{VARIANT_LEVEL_OUTPUT_SUFFIX}"
        )
        self.crl_writer = FileWriter(self.crl_path)
        self.crl_writer.add_columns(crl_def)
        self.crl_writer.write_definition()
        self.crl_writer.write_names("original_input", "Original Input", "")

    def open_output_files(self):
        from oakvar.lib.exceptions import SetupError

        if not self.output_base_fname or not self.output_dir:
            raise SetupError()
        self.setup_crv_writer()
        self.setup_crs_writer()
        self.setup_crm_writer()
        self.setup_crl_writer()

    def log_input_and_genome_assembly(self, input_path, genome_assembly, converter):
        if not self.logger:
            return
        self.logger.info(f"input file: {input_path}")
        self.logger.info("input format: %s" % converter.format_name)
        self.logger.info(f"genome_assembly: {genome_assembly}")

    def setup_file(self, input_path: str) -> Tuple[Union[BufferedReader, TextIO], BaseConverter]:
        from logging import getLogger
        from oakvar.lib.util.util import log_module
        from oakvar.lib.exceptions import NoConverterFound

        f = self.input_file_handles[input_path]
        converter = self.converter_by_input_path[input_path]
        if not converter:
            raise NoConverterFound(input_path)
        if not converter.module_name or not converter.format_name:
            raise NoConverterFound(input_path)
        self.input_formats.append(converter.format_name)
        self.fileno += 1
        self.set_converter_properties(converter)
        log_module(converter, self.logger)
        self.error_logger = getLogger("err." + converter.module_name)
        converter.input_path = input_path
        converter.input_paths = self.input_paths
        converter.setup(f)
        genome_assembly = self.get_genome_assembly(converter)
        self.genome_assemblies.append(genome_assembly)
        self.log_input_and_genome_assembly(input_path, genome_assembly, converter)
        self.set_do_liftover(genome_assembly, converter, f)
        if self.do_liftover or self.do_liftover_chrM:
            self.setup_lifter(genome_assembly)
        f.seek(0)
        return (f, converter)

    def handle_chrom(self, variant):
        from oakvar.lib.exceptions import IgnoredVariant

        if not variant.get("chrom"):
            raise IgnoredVariant("No chromosome")
        if not variant.get("chrom").startswith("chr"):
            variant["chrom"] = "chr" + variant.get("chrom")
        variant["chrom"] = self.chromdict.get(
            variant.get("chrom"), variant.get("chrom")
        )

    def handle_ref_base(self, variant):
        from oakvar.lib.exceptions import IgnoredVariant

        if "ref_base" not in variant or variant["ref_base"] in [
            "",
            ".",
        ]:
            if not self.wgs_reader:
                raise
            variant["ref_base"] = self.wgs_reader.get_bases(
                variant.get("chrom"), int(variant["pos"])
            ).upper()
        else:
            ref_base = variant["ref_base"]
            if ref_base == "" and variant["alt_base"] not in [
                "A",
                "T",
                "C",
                "G",
            ]:
                raise IgnoredVariant("Reference base required for non SNV")
            elif ref_base is None or ref_base == "":
                if not self.wgs_reader:
                    raise
                variant["ref_base"] = self.wgs_reader.get_bases(
                    variant.get("chrom"), int(variant.get("pos"))
                )

    def handle_genotype(self, variant):
        if "genotype" in variant and "." in variant["genotype"]:
            variant["genotype"] = variant["genotype"].replace(".", variant["ref_base"])

    def check_invalid_base(self, variant: dict):
        from oakvar.lib.exceptions import IgnoredVariant

        if not self.base_re.fullmatch(variant["ref_base"]):
            raise IgnoredVariant("Invalid reference base")
        if not self.base_re.fullmatch(variant["alt_base"]):
            raise IgnoredVariant("Invalid alternate base")

    def normalize_variant(self, variant):
        from oakvar.lib.util.seq import normalize_variant_left

        p, r, a = (
            int(variant["pos"]),
            variant["ref_base"],
            variant["alt_base"],
        )
        (
            new_pos,
            new_ref,
            new_alt,
        ) = normalize_variant_left("+", p, r, a)
        variant["pos"] = new_pos
        variant["ref_base"] = new_ref
        variant["alt_base"] = new_alt

    def add_end_pos_if_absent(self, variant: dict):
        col_name = "pos_end"
        if col_name not in variant:
            ref_base = variant["ref_base"]
            ref_len = len(ref_base)
            if ref_len == 1:
                variant[col_name] = variant["pos"]
            else:
                variant[col_name] = variant["pos"] + ref_len - 1

    def run(self):
        from pathlib import Path
        from multiprocess.dummy import Pool
        from oakvar.lib.util.run import update_status

        if not self.input_paths or not self.logger:
            raise
        update_status(
            "started converter", logger=self.logger, serveradmindb=self.serveradmindb
        )
        self.setup()
        self.set_variables_pre_run()
        if not self.crv_writer:
            raise ValueError("No crv_writer")
        if not self.crs_writer:
            raise ValueError("No crs_writer")
        if not self.crm_writer:
            raise ValueError("No crm_writer")
        if not self.crl_writer:
            raise ValueError("No crl_writer")
        batch_size: int = 100
        uid = 1
        pool = Pool(self.mp)
        for self.input_path in self.input_paths:
            self.input_fname = Path(self.input_path).name
            fileno = self.input_path_dict2[self.input_path]
            f, converter = self.setup_file(self.input_path)
            self.file_num_valid_variants = 0
            self.file_error_lines = 0
            start_line: int = 0
            while True:
                results = [pool.apply(gather_variantss, (f, converter, batch_size, core_num, start_line, self.do_liftover, self.do_liftover_chrM, self.lifter, self.wgs_reader, self.logger, self.error_logger, self.serveradmindb, self.input_path, self.input_fname, self.unique_excs, self.err_holder)) for core_num in range(self.mp)]
                has_data = False
                for result in results:
                    variants_l, crl_l, crm_l, max_var_orders = result
                    if len(variants_l) > 0:
                        has_data = True
                    for variants, crl_data, crm_data, max_var_order in zip(variants_l, crl_l, crm_l, max_var_orders):
                        if len(variants) == 0:
                            continue
                        for variant in variants:
                            print(f"@ variant={variant}", flush=True)
                            variant["uid"] = uid + variant["var_order"]
                            if variant["unique"]:
                                self.crv_writer.write_data(variant)
                            self.crs_writer.write_data(variant)
                        for crm in crm_data:
                            crm["fileno"] = fileno
                            self.crm_writer.write_data(crm)
                        for crl in crl_data:
                            self.crl_writer.write_data(crl)
                        uid += max_var_order
                if not has_data:
                    break
                start_line += batch_size * self.mp
            #if self.read_lnum % 10000 == 0:
            status = (
                f"Running Converter ({self.input_fname}): line {uid}"
            )
            update_status(
                status, logger=self.logger, serveradmindb=self.serveradmindb
            )
            f.close()
            self.logger.info(
                f"number of valid variants: {self.file_num_valid_variants}"
            )
            self.logger.info(f"number of error lines: {self.file_error_lines}")
        self.close_output_files()
        self.end()
        self.log_ending()
        ret = {
            "total_lnum": self.total_num_converted_variants,
            "write_lnum": self.total_num_valid_variants,
            "error_lnum": self.total_error_lines,
            "input_format": self.input_formats,
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
            "total number of converted variants: {}".format(
                self.total_num_converted_variants
            )
        )
        self.logger.info("number of total error lines: %d" % self.total_error_lines)
        end_time = time()
        self.logger.info("finished: %s" % asctime(localtime(end_time)))
        runtime = round(end_time - self.start_time, 3)
        self.logger.info("runtime: %s" % runtime)
        status = "finished Converter"
        update_status(status, logger=self.logger, serveradmindb=self.serveradmindb)

    def perform_liftover_if_needed(self, variant) -> Optional[Dict[str, Any]]:
        from copy import copy
        from oakvar.lib.util.seq import liftover_one_pos
        from oakvar.lib.util.seq import liftover

        assert self.crl_writer is not None
        if self.is_chrM(variant):
            needed = self.do_liftover_chrM
        else:
            needed = self.do_liftover
        if needed:
            prelift_wdict = copy(variant)
            #prelift_wdict["uid"] = self.uid
            #self.crl_writer.write_data(prelift_wdict)
            crl_data = prelift_wdict
            (
                variant["chrom"],
                variant["pos"],
                variant["ref_base"],
                variant["alt_base"],
            ) = liftover(
                variant["chrom"],
                int(variant["pos"]),
                variant["ref_base"],
                variant["alt_base"],
                lifter=self.lifter,
                wgs_reader=self.wgs_reader,
            )
            converted_end = liftover_one_pos(
                variant["chrom"], variant["pos_end"], lifter=self.lifter
            )
            if converted_end is None:
                pos_end = ""
            else:
                pos_end = converted_end[1]
            variant["pos_end"] = pos_end
        else:
            crl_data = None
        return crl_data

    def is_chrM(self, wdict):
        return wdict["chrom"] == "chrM"

    def _log_conversion_error(self, line_no: int, e, full_line_error=True):
        from time import time
        from traceback import format_exc
        from oakvar.lib.exceptions import ExpectedException
        from oakvar.lib.exceptions import NoAlternateAllele
        from oakvar.lib.util.run import update_status

        if isinstance(e, NoAlternateAllele):
            if line_no % 10000 == 0:
                status = f"Running Converter ({self.input_fname}): line {line_no}"
                update_status(
                    status, logger=self.logger, serveradmindb=self.serveradmindb
                )
            return
        if not self.logger or not self.error_logger:
            raise
        if full_line_error:
            self.file_error_lines += 1
            self.total_error_lines += 1
        if isinstance(e, ExpectedException):
            err_str = str(e)
        else:
            err_str = format_exc().rstrip()
        if err_str not in self.unique_excs:
            err_no = len(self.unique_excs)
            self.unique_excs[err_str] = err_no
            if hasattr(e, "traceback") and e.traceback is False:
                pass
            else:
                self.logger.error(f"Error [{err_no}]: {self.input_path}: {err_str}")
            self.err_holder.append(f"{err_no}:{line_no}\t{str(e)}")
        else:
            err_no = self.unique_excs[err_str]
            self.err_holder.append(f"{err_no}:{line_no}\t{str(e)}")
        t = time()
        if self.err_holder and t - self.time_error_written > 60:
            for s in self.err_holder:
                self.error_logger.error(s)
            self.err_holder = []
        if line_no % 10000 == 0:
            status = f"Running Converter ({self.input_fname}): line {line_no}"
            update_status(status, logger=self.logger, serveradmindb=self.serveradmindb)

    def close_output_files(self):
        if self.crv_writer is not None:
            self.crv_writer.close()
        if self.crm_writer is not None:
            self.crm_writer.close()
        if self.crs_writer is not None:
            self.crs_writer.close()

    def end(self):
        pass
