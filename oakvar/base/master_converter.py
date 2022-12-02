from typing import Any
from typing import Optional
from typing import List
from typing import Dict
from typing import Tuple
from typing import TextIO
from oakvar import BaseConverter

STDIN = "stdin"


class MasterConverter(object):

    ALREADYCRV = 2

    def __init__(self, *inargs, **inkwargs):
        from re import compile
        from oakvar import get_wgs_reader

        self.logger = None
        self.serveradmindb = None
        self.crv_writer = None
        self.crs_writer = None
        self.crm_writer = None
        self.crl_writer = None
        self.converters = {}
        self.available_input_formats = []
        self.pipeinput = False
        self.input_paths = None
        self.input_dir = None
        self.input_path_dict = {}
        self.input_path_dict2 = {}
        self.input_file_handles: Dict[str, TextIO] = {}
        self.output_dir: Optional[str] = None
        self.output_base_fname: Optional[str] = None
        self.conf = None
        self.unique_variants = None
        self.error_logger = None
        self.unique_excs: Dict[str, int] = {}
        self.err_holder = []
        self.wpath = None
        self.err_path = None
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
        self.total_num_converted_variants = 0
        self.input_formats: List[str] = []
        self.genome_assemblies: List[str] = []
        self.base_re = compile("^[ATGC]+|[-]+$")
        self.chromdict = {
            "chrx": "chrX",
            "chry": "chrY",
            "chrMT": "chrM",
            "chrMt": "chrM",
            "chr23": "chrX",
            "chr24": "chrY",
        }
        self.parse_cmd_args(inargs, inkwargs)
        self.setup_logger()
        self.wgsreader = get_wgs_reader(assembly="hg38")

    def get_genome_assembly(self, converter) -> str:
        from oakvar.system.consts import default_assembly_key
        from oakvar.exceptions import NoGenomeException
        from oakvar.system import get_user_conf

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

    def setup_lifter(self, genome_assembly):
        from oakvar.util.admin_util import get_liftover_chain_paths
        from oakvar.exceptions import InvalidGenomeAssembly
        from pyliftover import LiftOver

        liftover_chain_paths = get_liftover_chain_paths()
        if genome_assembly not in liftover_chain_paths:
            raise InvalidGenomeAssembly(genome_assembly)
        self.lifter = LiftOver(liftover_chain_paths[genome_assembly])

    def parse_inputs(self, args):
        from pathlib import Path

        if not args["inputs"]:
            raise
        self.pipeinput = False
        if (
            args["inputs"] is not None
            and len(args["inputs"]) == 1
            and args["inputs"][0] == "-"
        ):
            self.pipeinput = True
        self.input_paths = []
        if self.pipeinput == False:
            self.input_paths = [str(Path(x).absolute()) for x in args["inputs"] if x != "-"]
        else:
            self.input_paths = [f"./{STDIN}"]
        self.input_dir = str(Path(self.input_paths[0]).parent)
        if self.pipeinput == False:
            for i in range(len(self.input_paths)):
                self.input_path_dict[i] = self.input_paths[i]
                self.input_path_dict2[self.input_paths[i]] = i
        else:
            self.input_path_dict[0] = self.input_paths[0]
            self.input_path_dict2[STDIN] = 0

    def parse_output_dir(self, args):
        from pathlib import Path
        from os import makedirs

        self.output_dir = None
        self.output_dir = args.get("output_dir") or None
        if not self.output_dir:
            self.output_dir = self.input_dir
        if not self.output_dir:
            raise
        if not (Path(self.output_dir).exists()):
            makedirs(self.output_dir)
        self.output_base_fname: Optional[str] = args.get("name")
        if not self.output_base_fname:
            if not self.input_paths:
                raise
            self.output_base_fname = Path(self.input_paths[0]).name

    def parse_cmd_args(self, inargs, inkwargs):
        from oakvar.exceptions import ExpectedException
        from oakvar.util.util import get_args
        from oakvar.util.run import get_module_options

        parser = self.get_cmd_args_parser()
        args = get_args(parser, inargs, inkwargs)
        if "serveradmindb" in args:
            self.serveradmindb = args.get("serveradmindb")
        if args["inputs"] is None:
            raise ExpectedException("Input files are not given.")
        self.parse_inputs(args)
        self.parse_output_dir(args)
        self.given_input_assembly = args.get("genome")
        self.conf = {}
        self.module_options = get_module_options(args)
        if "conf" in args:
            self.conf.update(args["conf"])
        self.unique_variants = args["unique_variants"]
        self.args = args

    def get_file_object_for_input_path(self, input_path: str):
        import gzip
        from oakvar.util.util import detect_encoding

        if self.logger:
            self.logger.info(f"detecting encoding of {input_path}")
        encoding = detect_encoding(input_path)
        if self.logger:
            self.logger.info(f"encoding: {input_path} {encoding}")
        if input_path.endswith(".gz"):
            f = gzip.open(input_path, mode="rt", encoding=encoding)
        else:
            f = open(input_path, encoding=encoding)
        return f

    def collect_input_file_handles(self):
        if not self.input_paths:
            raise
        for input_path in self.input_paths:
            f = self.get_file_object_for_input_path(input_path)
            self.input_file_handles[input_path] = f

    def setup(self):
        self.collect_input_file_handles()
        self.collect_converters()
        self.check_input_format()
        self.collect_converter_by_input()
        self.collect_extra_output_columns()
        self.open_output_files()

    def setup_logger(self):
        from logging import getLogger

        self.logger = getLogger("oakvar.converter")
        self.error_logger = getLogger("err.converter")

    def collect_converters(self):
        from oakvar.module.local import get_local_module_infos_of_type
        from oakvar.util.util import load_class
        from oakvar.util.util import quiet_print

        for module_info in get_local_module_infos_of_type("converter").values():
            cls = load_class(module_info.script_path)
            converter = cls()
            # TODO: backward compatibility
            converter.output_dir = None
            converter.run_name = None
            converter.module_name = module_info.name
            converter.name = module_info.name
            converter.version = module_info.version
            converter.conf = module_info.conf
            converter.script_path = module_info.script_path
            # end of backward compatibility
            if not hasattr(converter, "format_name"):
                quiet_print("{module_info.name} does not have format_name defined and thus was skipped.", args=self.args)
                continue
            converter.module_name = module_info.name
            if converter.format_name not in self.converters:
                self.converters[converter.format_name] = converter
            else:
                quiet_print("{moule_info.name} is skipped because {converter.format_name} is already handled by {self.converters[converter.format_name].name}.", args=self.args)
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
        from oakvar.exceptions import InvalidInputFormat

        if self.args.get("input_format") and self.args.get("input_format") not in self.available_input_formats:
            raise InvalidInputFormat(self.args.get("input_format"))
        if self.pipeinput and not self.args.get("input_format"):
            raise InvalidInputFormat(
                f"--input-format should be given with pipe input"
            )

    def get_converter_for_input_file(self, f) -> Optional[BaseConverter]:
        import sys
        from oakvar.exceptions import ArgumentError

        if f == sys.stdin:
            if not self.args.get("input_format"):
                raise ArgumentError(msg="--input-format option should be given if stdin is used for input.")
            if not self.args.get("input_format") in self.converters:
                raise ArgumentError(msg=f"{self.args.get('input_format')} is not found in installed converter modules.")
            return self.converters[self.args.get("input_format")]
        else:
            for converter_name, converter in self.converters.items():
                f.seek(0)
                try:
                    check_success = converter.check_format(f)
                except:
                    import traceback
                    traceback.print_exc()
                    check_success = False
                f.seek(0)
                if check_success:
                    if self.logger:
                        self.logger.info(f"using {converter_name} for {f.name}")
                    return converter
        return None

    def set_converter_properties(self, converter):
        from oakvar.exceptions import SetupError
        from oakvar.module.local import get_module_code_version

        if self.conf is None:
            raise SetupError()
        converter.output_dir = self.output_dir
        converter.run_name = self.output_base_fname
        module_name = converter.format_name + "-converter"
        converter.module_name = module_name
        converter.version = get_module_code_version(converter.module_name)
        if module_name in self.conf:
            if hasattr(converter, "conf") == False:
                converter.conf = {}
            converter.conf.update(self.conf[module_name])

    def setup_crv_writer(self):
        from pathlib import Path
        from oakvar.util.util import get_crv_def
        from oakvar.util.inout import FileWriter
        from oakvar.consts import crv_idx
        from oakvar.consts import STANDARD_INPUT_FILE_SUFFIX

        if not self.output_dir or not self.output_base_fname:
            raise
        crv_def = get_crv_def()
        self.wpath = Path(self.output_dir) / (self.output_base_fname + STANDARD_INPUT_FILE_SUFFIX)
        self.crv_writer = FileWriter(self.wpath)
        self.crv_writer.add_columns(crv_def)
        self.crv_writer.write_definition()
        for index_columns in crv_idx:
            self.crv_writer.add_index(index_columns)

    def setup_crs_writer(self):
        from pathlib import Path
        from oakvar.util.util import get_crs_def
        from oakvar.util.inout import FileWriter
        from oakvar.consts import crs_idx
        from oakvar.consts import SAMPLE_FILE_SUFFIX

        if not self.output_dir or not self.output_base_fname:
            raise
        crs_def = get_crs_def()
        self.crs_path = Path(self.output_dir) / (self.output_base_fname + SAMPLE_FILE_SUFFIX)
        self.crs_writer = FileWriter(self.crs_path)
        self.crs_writer.add_columns(crs_def)
        self.crs_writer.add_columns(self.extra_output_columns)
        self.crs_writer.write_definition()
        for index_columns in crs_idx:
            self.crs_writer.add_index(index_columns)

    def setup_crm_writer(self):
        from pathlib import Path
        from oakvar.util.util import get_crm_def
        from oakvar.util.inout import FileWriter
        from oakvar.consts import crm_idx
        from oakvar.consts import MAPPING_FILE_SUFFIX

        if not self.output_dir or not self.output_base_fname:
            raise
        crm_def = get_crm_def()
        self.crm_path = Path(self.output_dir) / (self.output_base_fname + MAPPING_FILE_SUFFIX)
        self.crm_writer = FileWriter(self.crm_path)
        self.crm_writer.add_columns(crm_def)
        self.crm_writer.write_definition()
        for index_columns in crm_idx:
            self.crm_writer.add_index(index_columns)
        self.crm_writer.write_input_paths(self.input_path_dict)

    def setup_crl_writer(self):
        from pathlib import Path
        from oakvar.util.util import get_crl_def
        from oakvar.util.inout import FileWriter
        from oakvar.consts import VARIANT_LEVEL_OUTPUT_SUFFIX

        if not self.output_dir or not self.output_base_fname:
            raise
        crl_def = get_crl_def()
        self.crl_path = Path(self.output_dir) / f"{self.output_base_fname}.original_input{VARIANT_LEVEL_OUTPUT_SUFFIX}"
        self.crl_writer = FileWriter(self.crl_path)
        self.crl_writer.add_columns(crl_def)
        self.crl_writer.write_definition()
        self.crl_writer.write_names("original_input", "Original Input", "")

    def open_output_files(self):
        from pathlib import Path
        from oakvar.exceptions import SetupError

        if not self.output_base_fname or not self.output_dir:
            raise SetupError()
        self.err_path = Path(self.output_dir) / (self.output_base_fname + ".master_converter.err")
        self.setup_crv_writer()
        self.setup_crs_writer()
        self.setup_crm_writer()
        self.setup_crl_writer()

    def log_input_and_genome_assembly(self, input_path, genome_assembly, converter):
        if not self.logger:
            return
        if self.pipeinput:
            self.logger.info(f"input file: {STDIN}")
        else:
            self.logger.info(f"input file: {input_path}")
        self.logger.info("input format: %s" % converter.format_name)
        self.logger.info(f"genome_assembly: {genome_assembly}")

    def setup_file(self, input_path: str) -> Tuple[TextIO, BaseConverter]:
        from sys import stdin
        from logging import getLogger
        from oakvar.util.util import log_module
        from oakvar.exceptions import NoConverterFound

        if self.pipeinput:
            f = stdin
        else:
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
        if self.pipeinput == False:
            f.seek(0)
        return (f, converter)

    def handle_chrom(self, variant):
        from oakvar.exceptions import IgnoredVariant

        if not variant.get("chrom"):
            raise IgnoredVariant("No chromosome")
        if not variant.get("chrom").startswith("chr"):
            variant["chrom"] = "chr" + variant.get("chrom")
        variant["chrom"] = self.chromdict.get(variant.get("chrom"), variant.get("chrom"))

    def handle_ref_base(self, variant):
        from oakvar.exceptions import IgnoredVariant

        if "ref_base" not in variant or variant["ref_base"] in [
            "",
            ".",
        ]:
            if not self.wgsreader:
                raise
            variant["ref_base"] = self.wgsreader.get_bases(
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
                raise IgnoredVariant(
                    "Reference base required for non SNV"
                )
            elif ref_base is None or ref_base == "":
                if not self.wgsreader:
                    raise
                variant["ref_base"] = self.wgsreader.get_bases(
                    variant.get("chrom"), int(variant.get("pos"))
                )

    def handle_genotype(self, variant):
        if "genotype" in variant and "." in variant["genotype"]:
            variant["genotype"] = variant["genotype"].replace(
                ".", variant["ref_base"]
            )

    def check_invalid_base(self, variant: dict):
        from oakvar.exceptions import IgnoredVariant

        if not self.base_re.fullmatch(variant["ref_base"]):
            raise IgnoredVariant("Invalid reference base")
        if not self.base_re.fullmatch(variant["alt_base"]):
            raise IgnoredVariant("Invalid alternate base")

    def normalize_variant(self, variant):
        from oakvar.util.seq import normalize_variant_left

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
        variant["uid"] = self.uid

    def handle_variant(self, variant: dict, var_no: int, converter):
        from oakvar.exceptions import NoVariantError

        if not self.crv_writer or not self.crm_writer or not self.crs_writer:
            raise
        self.handle_chrom(variant)
        self.handle_ref_base(variant)
        self.handle_genotype(variant)
        self.perform_liftover_if_needed(variant)
        self.check_invalid_base(variant)
        self.normalize_variant(variant)
        if variant["ref_base"] == variant["alt_base"]:
            raise NoVariantError()
        self.file_num_valid_variants += 1
        self.total_num_valid_variants += 1
        self.crv_writer.write_data(variant)
        try:
            converter.addl_operation_for_unique_variant(
                variant, var_no
            )
        except Exception as e:
            self._log_conversion_error(
                self.read_lnum, e, full_line_error=False
            )
        self.crm_writer.write_data(
            {
                "original_line": self.read_lnum,
                "tags": variant["tags"],
                "uid": self.uid,
                "fileno": f"{self.input_path_dict2[self.input_path]}",
            }
        )
        self.crs_writer.write_data(variant)

    def handle_converted_variants(self, variants: List[Dict[str, Any]], converter: BaseConverter):
        from oakvar.exceptions import IgnoredVariant

        if not self.wgsreader or not self.crv_writer or not self.crm_writer or not self.crs_writer:
            raise
        if variants is BaseConverter.IGNORE:
            return
        self.total_num_converted_variants += 1
        if not variants:
            raise IgnoredVariant(
                "No valid alternate allele was found in any samples."
            )
        for var_no, variant in enumerate(variants):
            self.handle_variant(variant, var_no, converter)
            self.uid += 1

    def run(self):
        from pathlib import Path
        from oakvar.util.run import update_status

        if not self.input_paths or not self.logger:
            raise
        update_status(f"started converter", logger=self.logger, serveradmindb=self.serveradmindb)
        self.setup()
        self.set_variables_pre_run()
        for self.input_path in self.input_paths:
            self.input_fname = Path(self.input_path).name if not self.pipeinput else STDIN
            f, converter = self.setup_file(self.input_path)
            self.file_num_valid_variants = 0
            self.file_error_lines = 0
            for self.read_lnum, variants in converter.convert_file(
                f, exc_handler=self._log_conversion_error
            ):
                try:
                    self.handle_converted_variants(variants, converter)
                    if self.read_lnum % 10000 == 0:
                        status = f"Running Converter ({self.input_fname}): line {self.read_lnum}"
                        update_status(
                            status, logger=self.logger, serveradmindb=self.serveradmindb
                        )
                except Exception as e:
                    self._log_conversion_error(self.read_lnum, e)
            f.close()
            self.logger.info(f"number of valid variants: {self.file_num_valid_variants}")
            self.logger.info(f"number of error lines: {self.file_error_lines}")
        self.close_output_files()
        self.end()
        self.log_ending()
        ret = {
            "total_lnum": self.total_num_converted_variants,
            "write_lnum": self.total_num_valid_variants,
            "error_lnum": self.total_error_lines,
            "format": self.input_formats,
            "assemblies": self.genome_assemblies,
        }
        return ret

    def set_variables_pre_run(self):
        from time import time

        self.start_time = time()
        self.total_num_converted_variants = 0
        self.uid = 1

    def log_ending(self):
        from time import time, asctime, localtime
        from oakvar.util.run import update_status

        if not self.logger:
            raise
        self.logger.info("total number of converted variants: {}".format(self.total_num_converted_variants))
        self.logger.info("number of total error lines: %d" % self.total_error_lines)
        end_time = time()
        self.logger.info("finished: %s" % asctime(localtime(end_time)))
        runtime = round(end_time - self.start_time, 3)
        self.logger.info("runtime: %s" % runtime)
        status = f"finished Converter"
        update_status(status, logger=self.logger, serveradmindb=self.serveradmindb)

    def perform_liftover_if_needed(self, variant):
        from copy import copy

        if not self.crl_writer:
            raise
        prelift_wdict = copy(variant)
        prelift_wdict["uid"] = self.uid
        self.crl_writer.write_data(prelift_wdict)
        if self.is_chrM(variant):
            needed = self.do_liftover_chrM
        else:
            needed = self.do_liftover
        if needed:
            (
                variant["chrom"],
                variant["pos"],
                variant["ref_base"],
                variant["alt_base"],
            ) = self.liftover(
                variant["chrom"],
                int(variant["pos"]),
                variant["ref_base"],
                variant["alt_base"],
            )

    def is_chrM(self, wdict):
        return wdict["chrom"] == "chrM"

    def liftover_one_pos(self, chrom, pos):
        from oakvar.exceptions import SetupError

        if not self.lifter:
            raise SetupError("no lifter")
        res = self.lifter.convert_coordinate(chrom, pos - 1)
        if res is None or len(res) == 0:
            res_prev = self.lifter.convert_coordinate(chrom, pos - 2)
            res_next = self.lifter.convert_coordinate(chrom, pos)
            if res_prev is not None and res_next is not None:
                if len(res_prev) == 1 and len(res_next) == 1:
                    pos_prev = res_prev[0][1]
                    pos_next = res_next[0][1]
                    if pos_prev == pos_next - 2:
                        res = [(res_prev[0][0], pos_prev + 1)]
                    elif pos_prev == pos_next + 2:
                        res = [(res_prev[0][0], pos_prev - 1)]
        return res

    def liftover(self, chrom, pos, ref, alt):
        from oakvar.exceptions import LiftoverFailure
        from oakvar.util.seq import reverse_complement
        from oakvar.exceptions import SetupError

        if not self.lifter or not self.wgsreader:
            raise SetupError("no lifter")
        reflen = len(ref)
        altlen = len(alt)
        if reflen == 1 and altlen == 1:
            res = self.liftover_one_pos(chrom, pos)
            if res is None or len(res) == 0:
                raise LiftoverFailure("Liftover failure")
            if len(res) > 1:
                raise LiftoverFailure("Liftover failure")
            try:
                el = res[0]
            except:
                raise LiftoverFailure("Liftover failure")
            newchrom = el[0]
            newpos = el[1] + 1
        elif reflen >= 1 and altlen == 0:  # del
            pos1 = pos
            pos2 = pos + reflen - 1
            res1 = self.lifter.convert_coordinate(chrom, pos1 - 1)
            res2 = self.lifter.convert_coordinate(chrom, pos2 - 1)
            if res1 is None or res2 is None or len(res1) == 0 or len(res2) == 0:
                raise LiftoverFailure("Liftover failure")
            if len(res1) > 1 or len(res2) > 1:
                raise LiftoverFailure("Liftover failure")
            el1 = res1[0]
            el2 = res2[0]
            newchrom1 = el1[0]
            newpos1 = el1[1] + 1
            newpos2 = el2[1] + 1
            newchrom = newchrom1
            newpos = newpos1
            newpos = min(newpos1, newpos2)
        elif reflen == 0 and altlen >= 1:  # ins
            res = self.lifter.convert_coordinate(chrom, pos - 1)
            if res is None or len(res) == 0:
                raise LiftoverFailure("Liftover failure")
            if len(res) > 1:
                raise LiftoverFailure("Liftover failure")
            el = res[0]
            newchrom = el[0]
            newpos = el[1] + 1
        else:
            pos1 = pos
            pos2 = pos + reflen - 1
            res1 = self.lifter.convert_coordinate(chrom, pos1 - 1)
            res2 = self.lifter.convert_coordinate(chrom, pos2 - 1)
            if res1 is None or res2 is None or len(res1) == 0 or len(res2) == 0:
                raise LiftoverFailure("Liftover failure")
            if len(res1) > 1 or len(res2) > 1:
                raise LiftoverFailure("Liftover failure")
            el1 = res1[0]
            el2 = res2[0]
            newchrom1 = el1[0]
            newpos1 = el1[1] + 1
            newpos2 = el2[1] + 1
            newchrom = newchrom1
            newpos = min(newpos1, newpos2)
        hg38_ref = self.wgsreader.get_bases(newchrom, newpos)
        if hg38_ref == reverse_complement(ref):
            newref = hg38_ref
            newalt = reverse_complement(alt)
        else:
            newref = ref
            newalt = alt
        return [newchrom, newpos, newref, newalt]

    def _log_conversion_error(self, line_no: int, e, full_line_error=True):
        from traceback import format_exc
        from oakvar.exceptions import ExpectedException
        from oakvar.exceptions import NoAlternateAllele
        from oakvar.util.run import update_status

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
            if hasattr(e, "traceback") and e.traceback == False:
                pass
            else:
                self.logger.error(f"Error [{err_no}]: {self.input_path}: {err_str}")
            self.err_holder.append(f"{err_no}:{line_no}\t{str(e)}")
        else:
            err_no = self.unique_excs[err_str]
            self.err_holder.append(f"{err_no}:{line_no}\t{str(e)}")
        if len(self.err_holder) % 1000 == 0:
            for s in self.err_holder:
                self.error_logger.error(s)
            self.err_holder = []
        if line_no % 10000 == 0:
            status = f"Running Converter ({self.input_fname}): line {line_no}"
            update_status(
                status, logger=self.logger, serveradmindb=self.serveradmindb
            )

    def close_output_files(self):
        if self.crv_writer is not None:
            self.crv_writer.close()
        if self.crm_writer is not None:
            self.crm_writer.close()
        if self.crs_writer is not None:
            self.crs_writer.close()

    def end(self):
        pass


    def get_cmd_args_parser(self):
        from argparse import ArgumentParser, SUPPRESS

        parser = ArgumentParser()
        parser.add_argument("path", help="Path to this converter's python module")
        parser.add_argument(
            "inputs", nargs="*", default=None, help="Files to be converted to .crv"
        )
        parser.add_argument(
            "-f", dest="format", default=None, help="Specify an input format"
        )
        parser.add_argument(
            "-n", "--name", dest="name", help="Name of job. Default is input file name."
        )
        parser.add_argument(
            "-d",
            "--output-dir",
            dest="output_dir",
            help="Output directory. Default is input file directory.",
        )
        parser.add_argument(
            "-l",
            "--genome",
            dest="genome",
            default=None,
            help="Input gene assembly. Will be lifted over to hg38",
        )
        parser.add_argument(
            "--confs", dest="confs", default="{}", help="Configuration string"
        )
        parser.add_argument(
            "--unique-variants",
            dest="unique_variants",
            default=False,
            action="store_true",
            help=SUPPRESS,
        )
        return parser


def main():
    master_converter = MasterConverter()
    master_converter.run()


if __name__ == "__main__":
    master_converter = MasterConverter()
    master_converter.run()
