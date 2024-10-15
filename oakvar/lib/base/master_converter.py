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

from typing import Any
from typing import Optional
from typing import List
from typing import Set
from typing import Dict
from typing import Tuple
from re import compile
from pathlib import Path
from liftover import ChainFile
from oakvar.lib.base.converter import BaseConverter

chromdict = {
    "chrx": "chrX",
    "chry": "chrY",
    "chrMT": "chrM",
    "chrMt": "chrM",
    "chr23": "chrX",
    "chr24": "chrY",
}
base_re = compile("^[ATGC]+|[-]+$")
VALID: str = "valid"
ERROR: str = "error"
IGNORED: str = "ignored"


class LinesData:
    def __init__(self, lines_data: Dict[int, List[Tuple[int, Dict[str, Any]]]]):
        self.lines_data = lines_data


def handle_genotype(variant):
    genotype = variant.get("genotype")
    if genotype and "." in genotype:
        variant["genotype"] = variant["genotype"].replace(".", variant["ref_base"])


def flush_err_holder(
    err_holders: List[List[str]], core_num: int, error_logger, force: bool = False
):
    err_holder: List[str] = err_holders[core_num]
    if len(err_holder) > 1000 or force:
        for err_line in err_holder:
            error_logger.error(err_line)
        err_holder.clear()


def _log_conversion_error(
    logger,
    error_logger,
    input_path: str,
    line_no: int,
    e,
    unique_excs: dict,
    err_holders: List[List[str]],
    unique_err_in_line: Set[str],
    core_num=None,
):
    from traceback import format_exc
    from oakvar.lib.exceptions import ExpectedException
    from oakvar.lib.exceptions import NoAlternateAllele
    from oakvar.lib.exceptions import IgnoredVariant

    if core_num is None:
        raise Exception(f"core_num is None.")
    if isinstance(e, NoAlternateAllele):
        err_str = str(e)
    if isinstance(e, ExpectedException):
        err_str = str(e)
    if getattr(e, "traceback", True) is not True:
        err_str = str(e)
    else:
        err_str = format_exc().rstrip()
    if err_str not in unique_excs:
        err_no = len(unique_excs)
        unique_excs[err_str] = err_no
        if isinstance(e, IgnoredVariant):
            header = "Ignored"
        else:
            header = "Error"
        logger.error(f"{header} [{err_no}]: {input_path}: {err_str}")
        err_holders[core_num].append(f"{err_no}:{line_no}\t{str(e)}")
        unique_err_in_line.add(err_str)
    else:
        if err_str not in unique_err_in_line:
            err_no = unique_excs[err_str]
            err_holders[core_num].append(f"{err_no}:{line_no}\t{str(e)}")
            unique_err_in_line.add(err_str)
    flush_err_holder(err_holders, core_num, error_logger)


def is_chrM(wdict):
    return wdict["chrom"] == "chrM"


def perform_liftover_if_needed(
    variant,
    do_liftover: bool,
    do_liftover_chrM: bool,
    lifter,
    wgs_reader,
    keep_liftover_failed: bool,
) -> Optional[Dict[str, Any]]:
    from copy import copy
    from oakvar.lib.util.seq import liftover_one_pos
    from oakvar.lib.util.seq import liftover

    if is_chrM(variant):
        needed = do_liftover_chrM
    else:
        needed = do_liftover
    if needed:
        prelift_wdict = copy(variant)
        orig_chrom = variant["chrom"]
        crl_data = prelift_wdict
        try:
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
        except Exception as e:
            if keep_liftover_failed:
                variant["pos"] = 0
                variant["pos_end"] = 0
                variant["ref_base"] = ""
                variant["alt_base"] = ""
                return crl_data
            else:
                raise e
        converted_end = liftover_one_pos(orig_chrom, variant["pos_end"], lifter=lifter)
        if converted_end is None:
            pos_end = ""
        else:
            pos_end = converted_end[1]
        variant["pos_end"] = pos_end
    else:
        crl_data = variant.get("crl")
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


def handle_alt_base(variant):
    from oakvar.lib.exceptions import IgnoredVariant

    if variant["alt_base"] is None:
        raise IgnoredVariant("No alternate allele")


def handle_chrom(variant, genome: str):
    from oakvar.lib.exceptions import IgnoredVariant
    from oakvar.lib.util.seq import get_grch37_to_hg19
    from oakvar.lib.util.seq import get_grch38_to_hg38

    chrom = variant.get("chrom")
    if not chrom:
        raise IgnoredVariant("No chromosome")
    if len(chrom) > 8:
        if genome == "hg19":
            new_chrom = get_grch37_to_hg19(chrom)
            if not new_chrom:
                raise IgnoredVariant(f"Unsupported chromosome {chrom}")
            variant["chrom"] = new_chrom
        elif genome == "hg38":
            new_chrom = get_grch38_to_hg38(chrom)
            if not new_chrom:
                raise IgnoredVariant(f"Unsupported chromosome {chrom}")
            variant["chrom"] = new_chrom
    if not chrom[0].startswith("c"):
        chrom = "chr" + chrom
    variant["chrom"] = chromdict.get(chrom, chrom)


def handle_variant(
    variant: dict,
    do_liftover: bool,
    do_liftover_chrM: bool,
    lifter,
    wgs_reader,
    line_no: int,
    genome: str,
    keep_liftover_failed: bool,
):
    from oakvar.lib.exceptions import NoVariantError

    if variant["ref_base"] == variant["alt_base"]:
        raise NoVariantError()
    tags = variant.get("tags")
    handle_chrom(variant, genome)
    handle_ref_base(variant, wgs_reader)
    handle_alt_base(variant)
    check_invalid_base(variant)
    normalize_variant(variant)
    add_end_pos_if_absent(variant)
    crl_data = perform_liftover_if_needed(
        variant, do_liftover, do_liftover_chrM, lifter, wgs_reader, keep_liftover_failed
    )
    handle_genotype(variant)
    variant["original_line"] = line_no
    variant["tags"] = tags
    variant["crl"] = crl_data


def handle_converted_variants(
    variants: List[Dict[str, Any]],
    do_liftover: bool,
    do_liftover_chrM: bool,
    lifter,
    wgs_reader,
    logger,
    error_logger,
    input_path: str,
    unique_excs: dict,
    err_holders: List[List[str]],
    line_no: int,
    core_num: int,
    genome: str,
    unique_err_in_line: Set[str],
    keep_liftover_failed: bool,
) -> Tuple[List[Dict[str, Any]], bool]:
    if variants is BaseConverter.IGNORE:
        return [], False
    if not variants:
        return [], False
    variant_l: List[Dict[str, Any]] = []
    error_occurred: bool = False
    for variant in variants:
        try:
            handle_variant(
                variant,
                do_liftover,
                do_liftover_chrM,
                lifter,
                wgs_reader,
                line_no,
                genome,
                keep_liftover_failed,
            )
            variant_l.append(variant)
        except Exception as e:
            _log_conversion_error(
                logger,
                error_logger,
                input_path,
                line_no,
                e,
                unique_excs,
                err_holders,
                unique_err_in_line,
                core_num=core_num,
            )
            error_occurred = True
            continue
    return variant_l, error_occurred


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
    unique_excs: dict,
    err_holders: List[List[str]],
    num_valid_error_lines: Dict[str, int],
    genome: str,
    keep_liftover_failed: bool,
) -> List[List[Dict[str, Any]]]:
    from oakvar.lib.exceptions import IgnoredInput

    variants_l: List[List[Dict[str, Any]]] = []
    line_data = lines_data[core_num]
    for line_no, line in line_data:
        unique_err_in_line: Set[str] = set()
        try:
            variants = converter.convert_line(line)
            variants_datas, error_occurred = handle_converted_variants(
                variants,
                do_liftover,
                do_liftover_chrM,
                lifter,
                wgs_reader,
                logger,
                error_logger,
                input_path,
                unique_excs,
                err_holders,
                line_no,
                core_num,
                genome,
                unique_err_in_line,
                keep_liftover_failed,
            )
            if error_occurred:
                num_valid_error_lines[ERROR] += 1
            else:
                num_valid_error_lines[VALID] += 1
            if not variants_datas:
                continue
            variants_l.append(variants_datas)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            _log_conversion_error(
                logger,
                error_logger,
                input_path,
                line_no,
                e,
                unique_excs,
                err_holders,
                unique_err_in_line,
                core_num=core_num,
            )
            if isinstance(e, IgnoredInput):
                num_valid_error_lines[IGNORED] += 1
            else:
                num_valid_error_lines[ERROR] += 1
    return variants_l


def gather_variantss_wrapper(args):
    return gather_variantss(*args)


class MasterConverter(object):
    DEFAULT_MP: int = 4

    def __init__(
        self,
        inputs: List[str] = [],
        input_format: Optional[str] = None,
        converter_module: Optional[str] = None,
        name: Optional[str] = None,
        output_dir: Optional[str] = None,
        genome: Optional[str] = None,
        serveradmindb=None,
        conf: Dict = {},
        module_options: Dict = {},
        input_encoding=None,
        ignore_sample: bool = False,
        skip_variant_deduplication: bool = False,
        mp: int = DEFAULT_MP,
        keep_liftover_failed: bool = False,
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
        self.converter_paths: Dict[str, Path] = {}
        self.input_paths = None
        self.input_dir = None
        self.input_path_dict = {}
        self.input_path_dict2 = {}
        self.input_file_handles: Dict[str, str] = {}
        self.output_base_fname: Optional[str] = None
        self.error_logger = None
        self.unique_excs: Dict[str, int] = {}
        self.err_holders: List[List[str]] = []
        self.wpath = None
        self.crm_path = None
        self.crs_path = None
        self.crl_path = None
        self.do_liftover = None
        self.do_liftover_chrM = None
        self.lifter = None
        self.converter_name_by_input_path: Dict[str, str] = {}
        self.extra_output_columns = []
        self.file_num_unique_variants: int = 0
        self.file_num_dup_variants: int = 0
        self.file_error_lines: int = 0
        self.total_num_valid_lines: int = 0
        self.total_num_error_lines: int = 0
        self.total_unique_variants: int = 0
        self.total_duplicate_variants: int = 0
        self.fileno: int = 0
        self.ignore_sample = ignore_sample
        self.total_num_unique_variants: int = 0
        self.total_num_duplicate_variants: int = 0
        self.skip_variant_deduplication: bool = skip_variant_deduplication
        self.input_formats: List[str] = []
        self.keep_liftover_failed: bool = keep_liftover_failed
        self.converter_module: Optional[str] = converter_module
        self.genome_assemblies: List[str] = []
        self.base_re = compile("^[ATGC]+|[-]+$")
        self.last_var: str = ""
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
        self.genome: str = genome if genome is not None else ""
        self.parse_inputs()
        self.parse_output_dir()
        self.given_input_assembly: Optional[str] = genome
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
        self.mp = mp or self.DEFAULT_MP

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

    def setup_lifter(self, genome_assembly) -> Optional[ChainFile]:
        from oakvar.lib.util.seq import get_lifter

        self.lifter = get_lifter(source_assembly=genome_assembly)

    def parse_inputs(self):
        from pathlib import Path

        self.input_paths = []
        self.input_paths = [str(Path(x).absolute()) for x in self.inputs if x != "-"]
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
        from pathlib import Path
        from oakvar.lib.util.util import detect_encoding

        suffix = Path(input_path).suffix
        # TODO: Remove the hardcoding.
        if suffix in [".parquet"]:
            encoding = ""
        else:
            if self.input_encoding:
                encoding = self.input_encoding
            else:
                if self.logger:
                    self.logger.info(f"detecting encoding of {input_path}")
                encoding = detect_encoding(input_path)
        if self.logger:
            self.logger.info(f"encoding: {input_path} {encoding}")
        return encoding

    def collect_input_file_handles(self):
        if not self.input_paths:
            raise
        for input_path in self.input_paths:
            encoding = self.get_file_object_for_input_path(input_path)
            self.input_file_handles[input_path] = encoding

    def setup(self, *args, **kwargs):
        _ = args
        _ = kwargs
        self.collect_converter_paths()
        self.collect_input_file_handles()
        self.collect_converter_name_by_input()
        self.collect_extra_output_columns()
        self.open_output_files()

    def setup_logger(self):
        from logging import getLogger

        self.logger = getLogger("oakvar.converter")
        self.error_logger = getLogger("err.converter")

    def get_converter(self, module_name: str) -> Optional[BaseConverter]:
        from oakvar.lib.util.util import load_class
        from oakvar.lib.module.local import get_local_module_info
        from oakvar.lib.exceptions import ModuleLoadingError

        try:
            script_path: Path = self.converter_paths[module_name]
            cls = load_class(script_path)
            if cls is None:
                raise ModuleLoadingError(module_name=module_name)
            module_options = self.module_options.get(module_name, {})
            module_info = get_local_module_info(script_path.parent)
            if not module_info:
                if self.logger:
                    self.logger.error(f"{module_name} yml file is missing or bad.")
                return None
            converter = cls(ignore_sample=self.ignore_sample, module_options=module_options)
            # TODO: backward compatibility
            converter.output_dir = None
            converter.run_name = None
            converter.module_name = module_name
            converter.name = module_info.name
            converter.version = module_info.version
            converter.conf = module_info.conf
            # end of backward compatibility
            if not hasattr(converter, "format_name") or converter.format_name is None:
                format_name = module_info.conf.get("format_name")
                if format_name:
                    converter.format_name = format_name
                else:
                    converter.format_name = module_name.split("-")[0]
            if not converter.format_name:
                if self.logger:
                    self.logger.error(
                        f"{module_name} module code does not have 'format_name' variable."
                    )
                return None
            converter.script_path = script_path
            return converter
        except Exception as e:
            raise e

    def collect_converter_paths(self):
        from pathlib import Path
        from oakvar.lib.module.local import get_local_module_infos_of_type

        if self.converter_module:
            module_path: Path = Path(self.converter_module)
            module_name = module_path.stem
            if module_name in ["cravat-converter", "oldcravat-converter"]:
                if self.logger:
                    self.logger.warn(
                        f"{module_name} is deprecated. Please install and use csv-converter module."
                    )
            script_path: Path = module_path / f"{module_name}.py"
            self.converter_paths[module_name] = script_path
        else:
            for module_name, module_info in get_local_module_infos_of_type(
                "converter"
            ).items():
                module_name = module_info.name
                if module_name in ["cravat-converter", "oldcravat-converter"]:
                    if self.logger:
                        self.logger.warn(
                            f"{module_name} is deprecated. Please install and use csv-converter module."
                        )
                    continue
                self.converter_paths[module_name] = module_info.script_path

    def collect_converter_name_by_input(self):
        if not self.input_paths:
            return
        for input_path in self.input_paths:
            converter_name = self.get_converter_name_for_input_file(input_path)
            self.converter_name_by_input_path[input_path] = converter_name

    def collect_extra_output_columns(self):
        for converter_name in self.converter_name_by_input_path.values():
            if not converter_name:
                continue
            converter = self.get_converter(converter_name)
            if not converter:
                continue
            if converter.conf:
                extra_output_columns = converter.conf.get("extra_output_columns")
                if not extra_output_columns:
                    continue
                for col in extra_output_columns:
                    self.extra_output_columns.append(col)

    def get_converter_name_for_input_file(self, input_path) -> str:
        from pathlib import Path
        from oakvar.lib.exceptions import NoConverterFound

        converter_name: str = ""
        if self.converter_module:
            module_name: str = Path(self.converter_module).name
            converter_name = module_name
        elif self.format:
            converter_name = f"{self.format}-converter"
        else:
            for module_name in self.converter_paths.keys():
                try:
                    converter = self.get_converter(module_name)
                    if not converter:
                        if self.logger:
                            self.logger.exception(f"{module_name} could not be loaded.")
                        continue
                    check_success = converter.check_format(input_path)
                except Exception:
                    import traceback

                    if self.logger:
                        self.logger.error(traceback.format_exc())
                    check_success = False
                if check_success:
                    converter_name = module_name
                    break
        if converter_name:
            if self.logger:
                self.logger.info(f"Using {converter_name} for {input_path}")
        else:
            raise NoConverterFound(input_path)
        return converter_name

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
        from copy import deepcopy
        from oakvar.lib.util.util import get_crs_def
        from oakvar.lib.util.inout import FileWriter
        from oakvar.lib.consts import crs_idx
        from oakvar.lib.consts import SAMPLE_FILE_SUFFIX

        if not self.output_dir or not self.output_base_fname or not self.input_paths:
            raise
        crs_def = deepcopy(get_crs_def())
        added_module_names: Set[str] = set()
        for input_path in self.input_paths:
            module_name = self.converter_name_by_input_path[input_path]
            if module_name in added_module_names:
                continue
            converter = self.get_converter(module_name)
            if converter:
                extra_output_columns = converter.get_extra_output_columns()
                crs_def.extend(extra_output_columns)
                added_module_names.add(module_name)
        self.crs_path = Path(self.output_dir) / (
            self.output_base_fname + SAMPLE_FILE_SUFFIX
        )
        self.crs_writer = FileWriter(self.crs_path)
        self.crs_writer.add_columns(crs_def)
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

    def setup_file(self, input_path: str) -> List[BaseConverter]:
        from logging import getLogger
        from oakvar.lib.util.util import log_module
        from oakvar.lib.exceptions import NoConverterFound

        encoding = self.input_file_handles[input_path]
        converter_name = self.converter_name_by_input_path[input_path]
        if not converter_name:
            raise NoConverterFound(input_path)
        converters: List[BaseConverter] = []
        for _ in range(self.mp):
            converter = self.get_converter(converter_name)
            if not converter:
                raise NoConverterFound(input_path)
            if not converter.module_name or not converter.format_name:
                raise NoConverterFound(input_path)
            if converter.format_name not in self.input_formats:
                self.input_formats.append(converter.format_name)
            self.fileno += 1
            self.set_converter_properties(converter)
            log_module(converter, self.logger)
            self.error_logger = getLogger("err." + converter.module_name)  # type: ignore
            converter.input_path = input_path
            converter.input_paths = self.input_paths
            converter.setup(input_path, encoding=encoding)
            genome_assembly = self.get_genome_assembly(converter)
            self.genome_assemblies.append(genome_assembly)
            self.log_input_and_genome_assembly(input_path, genome_assembly, converter)
            self.genome = genome_assembly
            self.set_do_liftover(genome_assembly, converter, input_path)
            if self.do_liftover or self.do_liftover_chrM:
                self.setup_lifter(genome_assembly)
            converters.append(converter)
        return converters

    def handle_chrom(self, variant):
        from oakvar.lib.exceptions import IgnoredVariant

        if not variant.get("chrom"):
            raise IgnoredVariant("No chromosome")
        chrom = variant.get("chrom")
        if isinstance(chrom, int):
            chrom = f"chr{chrom}"
        elif not chrom.startswith("chr"):
            chrom = f"chr{chrom}"
        variant["chrom"] = chrom
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
        from sys import platform as sysplatform
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
        if (
            sysplatform == "win32"
        ):  # TODO: Remove after releasing Rust-based vcf-converter.
            batch_size: int = 10000
            num_pool = 1
        else:
            batch_size: int = 2500
            num_pool = self.mp
        self.err_holders: List[List[str]] = []
        for _ in range(num_pool):
            self.err_holders.append([])
        pool = ThreadPool(num_pool)
        unique_var_dict: Dict[int, Dict[str, int]] = {}
        uid_var: int = 0
        log_batch_size: int = 100000
        for input_path in self.input_paths:
            self.input_fname = Path(input_path).name
            fileno = self.input_path_dict2[input_path]
            converters = self.setup_file(input_path)
            main_converter = converters[0]
            self.file_num_unique_variants = 0
            self.file_num_dup_variants: int = 0
            self.file_error_lines = 0
            self.num_valid_error_lines = {VALID: 0, ERROR: 0, IGNORED: 0}
            start_line_pos: int = 1
            start_line_no: int = start_line_pos
            round_no: int = 0
            next_batch_log: int = log_batch_size
            while True:
                lines_data, immature_exit = main_converter.get_variant_lines(
                    input_path, num_pool, start_line_no, batch_size
                )
                args = [
                    (
                        converters[core_num],
                        lines_data,
                        core_num,
                        self.do_liftover,
                        self.do_liftover_chrM,
                        self.lifter,
                        self.wgs_reader,
                        self.logger,
                        self.error_logger,
                        input_path,
                        self.unique_excs,
                        self.err_holders,
                        self.num_valid_error_lines,
                        self.genome,
                        self.keep_liftover_failed,
                    )
                    for core_num in range(num_pool)
                ]
                results = pool.map(gather_variantss_wrapper, args)
                for core_num in range(num_pool):
                    flush_err_holder(
                        self.err_holders, core_num, self.error_logger, force=True
                    )
                lines_data = None
                for result in results:
                    variants_l = result
                    for i in range(len(variants_l)):
                        variants = variants_l[i]
                        if len(variants) == 0:
                            continue
                        for variant in variants:
                            if "sample" in variant:
                                sample = variant["sample"]
                            else:
                                sample = variant
                            if "extra_info" in variant:
                                extra_info = variant["extra_info"]
                            else:
                                extra_info = variant
                            crl = variant.get("crl")
                            variant["fileno"] = fileno
                            if self.skip_variant_deduplication:
                                uid_var += 1
                                variant["uid"] = uid_var
                                sample["uid"] = uid_var
                                extra_info["uid"] = uid_var
                                self.crv_writer.write_data(variant)
                                self.crm_writer.write_data(variant)
                                self.crs_writer.write_data(sample)
                                main_converter.write_extra_info(extra_info)
                                if crl:
                                    crl["uid"] = variant["uid"]
                                    self.crl_writer.write_data(crl)
                                self.file_num_unique_variants += 1
                            else:
                                dup_found: bool = False
                                pos: int = variant.get("pos", 0)
                                var_str: str = f'{variant["chrom"]}:{variant["pos"]}:{variant["ref_base"]}:{variant["alt_base"]}'
                                if pos not in unique_var_dict:
                                    unique_var_dict[pos] = {}
                                for comp_var_str in unique_var_dict.get(pos, {}).keys():
                                    if var_str == comp_var_str:
                                        # crs: uid, sample_id, genotype, zygosity, tot_reads, alt_reads, af
                                        comp_uid: int = unique_var_dict[pos][
                                            comp_var_str
                                        ]
                                        sample["uid"] = comp_uid
                                        variant["uid"] = comp_uid
                                        dup_found = True
                                        break
                                if not dup_found:
                                    uid_var += 1
                                    variant["uid"] = uid_var
                                    sample["uid"] = uid_var
                                    extra_info["uid"] = uid_var
                                    if crl:
                                        crl["uid"] = uid_var
                                    self.crv_writer.write_data(variant)
                                    self.file_num_unique_variants += 1
                                    unique_var_dict[pos][var_str] = uid_var
                                    main_converter.write_extra_info(extra_info)
                                    if crl:
                                        self.crl_writer.write_data(crl)
                                else:
                                    self.file_num_dup_variants += 1
                                self.crs_writer.write_data(sample)
                                self.crm_writer.write_data(variant)
                    variants_l = None
                if not immature_exit:
                    break
                start_line_no += batch_size * num_pool
                round_no += 1
                if start_line_no >= next_batch_log:
                    status = f"Running Converter ({self.input_fname}): line {start_line_no - 1}"
                    update_status(
                        status, logger=self.logger, serveradmindb=self.serveradmindb
                    )
                    next_batch_log = start_line_no + log_batch_size
            self.logger.info(
                f"{input_path}: number of lines ignored: {self.num_valid_error_lines[IGNORED]}"
            )
            self.logger.info(
                f"{input_path}: number of lines successfully processed: {self.num_valid_error_lines[VALID]}"
            )
            self.logger.info(
                f"{input_path}: number of lines skipped due to errors: {self.num_valid_error_lines[ERROR]}"
            )
            self.logger.info(
                f"{input_path}: number of unique variants: {self.file_num_unique_variants}"
            )
            self.logger.info(
                f"{input_path}: number of duplicate variants: {self.file_num_dup_variants}"
            )
            self.total_num_unique_variants += self.file_num_unique_variants
            self.total_num_duplicate_variants += self.file_num_dup_variants
            self.total_num_valid_lines += self.num_valid_error_lines[VALID]
            self.total_num_error_lines += self.num_valid_error_lines[ERROR]
        for core_num in range(num_pool):
            flush_err_holder(self.err_holders, core_num, self.error_logger, force=True)
        self.close_output_files()
        self.end()
        self.log_ending()
        ret = {
            "num_unique_variants": self.total_num_unique_variants,
            "num_duplicate_variants": self.total_duplicate_variants,
            "num_valid_lines": self.total_num_valid_lines,
            "num_error_lines": self.total_num_error_lines,
            "input_formats": self.input_formats,
            "assemblies": self.genome_assemblies,
        }
        return ret

    def set_variables_pre_run(self):
        from time import time

        self.start_time = time()
        self.total_num_unique_variants = 0
        self.total_num_duplicate_variants = 0
        self.total_num_valid_lines = 0
        self.total_num_error_lines = 0
        self.uid = 0

    def log_ending(self):
        from time import time, asctime, localtime
        from oakvar.lib.util.run import update_status

        if not self.logger:
            raise
        self.logger.info(
            f"total number of unique variants: {self.total_num_unique_variants}"
        )
        self.logger.info(
            f"total number of duplicate variants: {self.total_num_duplicate_variants}"
        )
        self.logger.info(f"total number of valid lines: {self.total_num_valid_lines}")
        self.logger.info(f"total number of error lines: {self.total_num_error_lines}")
        end_time = time()
        self.logger.info("finished: %s" % asctime(localtime(end_time)))
        runtime = round(end_time - self.start_time, 3)
        self.logger.info("runtime: %s" % runtime)
        status = "finished Converter"
        update_status(status, logger=self.logger, serveradmindb=self.serveradmindb)

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
