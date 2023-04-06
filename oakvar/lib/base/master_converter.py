from typing import Any
from typing import Optional
from typing import Union
from typing import List
from typing import Dict
from typing import Tuple
from typing import TextIO
from .converter import BaseConverter
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

class LinesData:
    def __init__(self, lines_data: Dict[int, List[Tuple[int, Dict[str, Any]]]]):
        self.lines_data = lines_data

def handle_genotype(variant):
    if "genotype" in variant and "." in variant["genotype"]:
        variant["genotype"] = variant["genotype"].replace(".", variant["ref_base"])

def flush_err_holder(err_holder: list, error_logger, force: bool=False):
    if len(err_holder) > 1000 or force:
        for err_line in err_holder:
            error_logger.error(err_line)
        err_holder.clear()

def _log_conversion_error(logger, error_logger, input_path: str, line_no: int, e, unique_excs: dict, err_holder: list):
    from traceback import format_exc
    from oakvar.lib.exceptions import ExpectedException
    from oakvar.lib.exceptions import NoAlternateAllele

    if isinstance(e, NoAlternateAllele):
        return
    if isinstance(e, ExpectedException):
        err_str = str(e)
    else:
        err_str = format_exc().rstrip()
    if err_str not in unique_excs:
        err_no = len(unique_excs)
        unique_excs[err_str] = err_no
        logger.error(f"Error [{err_no}]: {input_path}: {err_str}")
        err_holder.append(f"{err_no}:{line_no}\t{str(e)}")
    else:
        err_no = unique_excs[err_str]
        err_holder.append(f"{err_no}:{line_no}\t{str(e)}")
    flush_err_holder(err_holder, error_logger)

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
        raise IgnoredVariant(f"Invalid reference base {variant['ref_base']}")
    if not base_re.fullmatch(variant["alt_base"]):
        raise IgnoredVariant(f"Invalid alternate base {variant['alt_base']}")

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
    return variant["var_no"] not in unique_vars

def handle_variant(
        variant: dict, unique_vars: dict, do_liftover: bool, do_liftover_chrM: bool, lifter, wgs_reader, line_no: int, num_valid_error_lines: Dict[str, int]
) -> Optional[Dict[str, Any]]:
    from oakvar.lib.exceptions import NoVariantError

    if variant["ref_base"] == variant["alt_base"]:
        raise NoVariantError()
    tags = variant.get("tags")
    unique = is_unique_variant(variant, unique_vars)
    if unique:
        variant["unique"] = True
        unique_vars[variant["var_no"]] = True
        handle_chrom(variant)
        handle_ref_base(variant, wgs_reader)
        check_invalid_base(variant)
        normalize_variant(variant)
        add_end_pos_if_absent(variant)
        crl_data = perform_liftover_if_needed(variant, do_liftover, do_liftover_chrM, lifter, wgs_reader)
        num_valid_error_lines["valid"] += 1
    else:
        variant["unique"] = False
        crl_data = None
    handle_genotype(variant)
    if unique:
        variant["original_line"] = line_no
        variant["tags"] = tags
    return crl_data

def handle_converted_variants(
        variants: List[Dict[str, Any]], do_liftover: bool, do_liftover_chrM: bool, lifter, wgs_reader, logger, error_logger, input_path: str, input_fname: str, unique_excs: dict, err_holder: list, line_no: int, num_valid_error_lines: Dict[str, int]
):
    from oakvar.lib.exceptions import IgnoredVariant

    if variants is BaseConverter.IGNORE:
        return None, None
    if not variants:
        raise IgnoredVariant("No valid alternate allele was found in any samples.")
    unique_vars = {}
    variant_l: List[Dict[str, Any]] = []
    crl_l: List[Dict[str, Any]] = []
    for variant in variants:
        try:
            crl_data = handle_variant(variant, unique_vars, do_liftover, do_liftover_chrM, lifter, wgs_reader, line_no, num_valid_error_lines)
        except Exception as e:
            _log_conversion_error(logger, error_logger, input_path, line_no, e, unique_excs, err_holder)
            continue
        variant_l.append(variant)
        if crl_data:
            crl_l.append(crl_data)
    return variant_l, crl_l

def gather_variantss_wrapper(args):
    return gather_variantss(*args)

def gather_variantss(
        converter: BaseConverter, 
        lines_data: Dict[int, List[Tuple[int, Dict[str, Any]]]],
        core_num: int, 
        do_liftover: bool, 
        do_liftover_chrM: bool, 
        lifter, 
        wgs_reader, 
        logger, 
        error_logger, 
        input_path: str, 
        input_fname: str, 
        unique_excs: dict, 
        err_holder: list,
        num_valid_error_lines: Dict[str, int],
) -> Tuple[List[List[Dict[str, Any]]], List[Dict[str, Any]]]:
    variants_l = []
    crl_l = []
    line_data = lines_data[core_num]
    for (line_no, line) in line_data:
        try:
            variants = converter.convert_line(line)
            variants_datas, crl_datas = handle_converted_variants(variants, do_liftover, do_liftover_chrM, lifter, wgs_reader, logger, error_logger, input_path, input_fname, unique_excs, err_holder, line_no, num_valid_error_lines)
            if variants_datas is None or crl_datas is None:
                continue
            variants_l.append(variants_datas)
            crl_l.append(crl_datas)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            _log_conversion_error(logger, error_logger, input_path, line_no, e, unique_excs, err_holder)
            num_valid_error_lines["error"] += 1
    return variants_l, crl_l


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
        self.input_paths: List[str] = []
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

    def set_do_liftover(self, genome_assembly, converter, input_path):
        self.do_liftover = genome_assembly != "hg38"
        if hasattr(converter, "get_do_liftover_chrM"):
            self.do_liftover_chrM = converter.get_do_liftover_chrM(
                genome_assembly, input_path, self.do_liftover
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
            str(Path(x).resolve()) for x in self.inputs if x != "-"
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
        from ... import get_converter_class

        for module_name, module_info in get_local_module_infos_of_type(
            "converter"
        ).items():
            cls = get_converter_class(module_name)
            converter = cls(name=module_name, code_version=module_info.version)
            # TODO: backward compatibility
            format_name: str = module_info.conf.get("format_name", "")
            # end of backward compatibility
            if format_name:
                converter.format_name = format_name
            elif not hasattr(converter, "format_name"):
                converter.format_name = module_name.split("-")[0]
            if not converter.format_name:
                if self.outer:
                    self.outer.error(
                        f"Skipping {module_info.name} as it does not "
                        + "have format_name defined."
                    )
                continue
            if converter.format_name not in self.converters:
                self.converters[converter.format_name] = converter
            else:
                if self.outer:
                    self.outer.error(
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
                self.logger.info(f"Using {converter.name} for {f.name}")
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

    def setup_file(self, input_path: str) -> BaseConverter:
        from logging import getLogger
        from oakvar.lib.util.util import log_module
        from oakvar.lib.exceptions import NoConverterFound

        f = self.input_file_handles[input_path]
        converter = self.converter_by_input_path[input_path]
        if not converter:
            raise NoConverterFound(input_path)
        if not converter.name or not converter.format_name:
            raise NoConverterFound(input_path)
        self.input_formats.append(converter.format_name)
        self.fileno += 1
        self.set_converter_properties(converter)
        log_module(converter, self.logger)
        self.error_logger = getLogger("err." + converter.name)
        converter.input_path = input_path
        converter.input_paths = self.input_paths
        genome_assembly = self.get_genome_assembly(converter)
        self.genome_assemblies.append(genome_assembly)
        self.log_input_and_genome_assembly(input_path, genome_assembly, converter)
        self.set_do_liftover(genome_assembly, converter, input_path)
        if self.do_liftover or self.do_liftover_chrM:
            self.setup_lifter(genome_assembly)
        f.seek(0)
        return converter

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
            variant["ref_base"] = self.wgs_reader.get_bases( # type: ignore
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
                variant["ref_base"] = self.wgs_reader.get_bases( # type: ignore
                    variant.get("chrom"), int(variant.get("pos"))
                )

    def handle_genotype(self, variant):
        if "genotype" in variant and "." in variant["genotype"]:
            variant["genotype"] = variant["genotype"].replace(".", variant["ref_base"])

    def check_invalid_base(self, variant: dict):
        from oakvar.lib.exceptions import IgnoredVariant

        if not self.base_re.fullmatch(variant["ref_base"]):
            raise IgnoredVariant(f"Invalid reference base {variant['ref_base']}")
        if not self.base_re.fullmatch(variant["alt_base"]):
            raise IgnoredVariant(f"Invalid alternate base {variant['alt_base']}")

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
        from multiprocessing.pool import ThreadPool
        #import time
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
        batch_size: int = 2500
        uid = 1
        num_pool = 4
        pool = ThreadPool(num_pool)
        for input_path in self.input_paths:
            self.input_fname = Path(input_path).name
            fileno = self.input_path_dict2[input_path]
            converter = self.setup_file(input_path)
            self.file_num_valid_variants = 0
            self.file_error_lines = 0
            self.num_valid_error_lines = {"valid": 0, "error": 0}
            start_line_pos: int = 1
            start_line_no: int = start_line_pos
            round_no: int = 0
            #stime = time.time()
            while True:
                #ctime = time.time()
                lines_data, immature_exit = converter.get_variant_lines(input_path, num_pool, start_line_no, batch_size)
                args = [
                    (
                        converter, 
                        lines_data,
                        core_num, 
                        self.do_liftover, 
                        self.do_liftover_chrM, 
                        self.lifter, 
                        self.wgs_reader, 
                        self.logger, 
                        self.error_logger, 
                        input_path, 
                        self.input_fname, 
                        self.unique_excs, 
                        self.err_holder,
                        self.num_valid_error_lines,
                    ) for core_num in range(num_pool)
                ]
                results = pool.map(gather_variantss_wrapper, args)
                lines_data = None
                for result in results:
                    variants_l, crl_l = result
                    for i in range(len(variants_l)):
                        variants = variants_l[i]
                        crl_data = crl_l[i]
                        if len(variants) == 0:
                            continue
                        for variant in variants:
                            variant["uid"] = uid + variant["var_no"]
                            if variant["unique"]:
                                self.crv_writer.write_data(variant)
                                variant["fileno"] = fileno
                                self.crm_writer.write_data(variant)
                                converter.write_extra_info(variant)
                            self.crs_writer.write_data(variant)
                        for crl in crl_data:
                            self.crl_writer.write_data(crl)
                        uid += max([v["var_no"] for v in variants]) + 1
                    variants_l = None
                    crl_l = None
                if not immature_exit:
                    break
                start_line_no += batch_size * num_pool
                round_no += 1
                status = (
                    f"Running Converter ({self.input_fname}): line {start_line_no - 1}"
                )
                update_status(
                    status, logger=self.logger, serveradmindb=self.serveradmindb
                )
            self.logger.info(
                f"{input_path}: number of valid variants: {self.num_valid_error_lines['valid']}"
            )
            self.logger.info(f"{input_path}: number of lines skipped due to errors: {self.num_valid_error_lines['error']}")
            self.total_num_converted_variants += self.num_valid_error_lines["valid"]
            self.total_num_valid_variants += self.num_valid_error_lines["valid"]
            self.total_error_lines += self.num_valid_error_lines["error"]
        flush_err_holder(self.err_holder, self.error_logger, force=True)
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

    def close_output_files(self):
        if self.crv_writer is not None:
            self.crv_writer.close()
        if self.crm_writer is not None:
            self.crm_writer.close()
        if self.crs_writer is not None:
            self.crs_writer.close()

    def end(self):
        pass
