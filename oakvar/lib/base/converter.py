from typing import Optional
from typing import Any
from typing import Tuple
from typing import List
from typing import Dict
import polars as pl
from pyliftover import LiftOver


class BaseConverter(object):
    IGNORE = "converter_ignore"
    unique_var_key = "_unique"

    def __init__(
        self,
        inputs: List[str] = [],
        input_format: Optional[str] = None,
        output_dir: Optional[str] = None,
        genome: Optional[str] = None,
        serveradmindb=None,
        module_options: Dict = {},
        input_encoding=None,
        outer=None,
        title: Optional[str] = None,
        conf: Dict[str, Any] = {},
        code_version: Optional[str] = None,
        run_name: Optional[str] = None,
        ignore_sample: bool=False,
        df_mode: bool = False,
        output_columns: List[Dict[str, Any]] = [],
    ):
        from re import compile
        from pathlib import Path
        import inspect
        from oakvar import get_wgs_reader
        from oakvar.lib.module.local import get_module_conf
        from oakvar.lib.util.util import get_crv_def

        self.logger = None
        self.converters = {}
        self.available_input_formats: List[str] = []
        self.input_dir = None
        self.input_path_dict = {}
        self.input_path_dict2 = {}
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
        self.uid: int = 0
        self.read_lnum: int = 0
        self.lifter = None
        self.module_options = None
        self.given_input_assembly: Optional[str] = genome
        self.converter_by_input_path: Dict[str, Optional[BaseConverter]] = {}
        self.file_num_valid_variants = 0
        self.file_error_lines = 0
        self.total_num_valid_variants = 0
        self.total_error_lines = 0
        self.fileno = 0
        self.module_options = module_options
        self.serveradmindb = serveradmindb
        self.input_encoding = input_encoding
        self.outer = outer
        self.extra_output_columns: List[Dict[str, Any]] = []
        self.total_num_converted_variants = 0
        self.input_formats: List[str] = []
        self.genome_assemblies: List[str] = []
        self.df_mode = df_mode
        self.base_re = compile("^[ATGC]+|[-]+$")
        self.chromdict = {
            "chrx": "chrX",
            "chry": "chrY",
            "chrMT": "chrM",
            "chrMt": "chrM",
            "chr23": "chrX",
            "chr24": "chrY",
        }
        #if not inputs:
        #    raise ExpectedException("Input files are not given.")
        self.input_paths = inputs
        self.format = input_format
        self.script_path = Path(inspect.getfile(self.__class__))
        self.module_type = "converter"
        self.ignore_sample: bool = ignore_sample
        self.header_num_line: int = 0
        self.line_no: int = 0
        self.name: str = self.script_path.stem
        self.output_dir = output_dir
        if run_name:
            self.run_name = run_name
        else:
            self.run_name = Path(self.input_paths[0]).name
        self.parse_inputs()
        self.parse_output_dir()
        self.conf: Dict[str, Any] = (
            get_module_conf(self.name, module_type="converter") or {}
        )
        if conf:
            self.conf.update(conf.copy())
        self.setup_logger()
        self.wgs_reader = get_wgs_reader(assembly="hg38")
        self.time_error_written: float = 0

        self.module_type = "converter"
        self.format_name: str = ""
        self.input_path: str = ""
        self.total_num_converted_variants = 0
        self.title = title
        if self.title:
            self.conf["title"] = self.title
        elif "title" in self.conf:
            self.title = self.conf["title"]
        self.version: str = ""
        if code_version:
            self.code_version = code_version
        else:
            if "code_version" in self.conf:
                self.code_version: str = self.conf["version"]
            elif "version" in self.conf:
                self.code_version: str = self.conf["version"]
            else:
                self.code_version: str = ""
        self.output_columns: List[Dict[str, Any]] = get_crv_def()
        self.collect_extra_output_columns()

    def check_format(self, *__args__, **__kwargs__):
        pass

    def get_variants_df(self, input_path, start_line_no, batch_size, num_pool=1):
        return None, None

    def get_variant_lines(
        self, input_path: str, mp: int, start_line_no: int, batch_size: int
    ) -> Tuple[Dict[int, List[Tuple[int, Any]]], bool]:
        import linecache

        immature_exit: bool = False
        line_no: int = start_line_no
        end_line_no = line_no + mp * batch_size - 1
        lines: Dict[int, List[Tuple[int, Any]]] = {i: [] for i in range(mp)}
        chunk_no: int = 0
        chunk_size: int = 0
        while True:
            line = linecache.getline(input_path, line_no)
            if not line:
                break
            line = line[:-1]
            lines[chunk_no].append((line_no, line))
            chunk_size += 1
            if line_no >= end_line_no:
                immature_exit = True
                break
            line_no += 1
            if chunk_size >= batch_size:
                chunk_no += 1
                chunk_size = 0
        return lines, immature_exit

    def write_extra_info(self, _: dict):
        pass

    def convert_line(self, *__args__, **__kwargs__) -> List[Dict[str, Any]]:
        return []

    def addl_operation_for_unique_variant(self, __wdict__, __wdict_no__):
        pass

    def save(self, overwrite: bool = False, interactive: bool = False):
        from ..module.local import create_module_files

        create_module_files(self, overwrite=overwrite, interactive=interactive)

    def get_do_liftover_chrM(self, genome_assembly, input_path: str, do_liftover):
        _ = genome_assembly or input_path 
        return do_liftover

    def set_do_liftover(self, genome_assembly, input_path: str):
        self.do_liftover = genome_assembly != 38
        self.do_liftover_chrM = self.get_do_liftover_chrM(
            genome_assembly, input_path, self.do_liftover
        )
        if self.logger:
            self.logger.info(f"liftover needed: {self.do_liftover}")
            self.logger.info(f"liftover for chrM needed: {self.do_liftover_chrM}")

    def setup_lifter(self, genome_assembly) -> Optional[LiftOver]:
        from oakvar.lib.util.seq import get_lifter

        self.lifter = get_lifter(source_assembly=genome_assembly)

    def parse_inputs(self):
        from pathlib import Path

        self.input_paths = [str(Path(x).resolve()) for x in self.input_paths if x != "-"]
        if not self.input_paths:
            self.input_dir = Path(".").resolve().parent
        else:
            self.input_dir = Path(self.input_paths[0]).parent
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
        self.output_base_fname: Optional[str] = self.run_name
        if not self.output_base_fname:
            #if not self.input_paths:
            #    raise
            if not self.input_paths:
                self.output_base_fname = "oakvar_result"
            else:
                self.output_base_fname = Path(self.input_paths[0]).name

    def get_file_object_for_input_path(self, input_path: str):
        import gzip
        from pathlib import Path
        from oakvar.lib.util.util import detect_encoding

        suffix = Path(input_path).suffix
        # TODO: Remove the hardcoding.
        if suffix in [".parquet"]:
            encoding = None
        else:
            if self.input_encoding:
                encoding = self.input_encoding
            else:
                if self.logger:
                    self.logger.info(f"detecting encoding of {input_path}")
                encoding = detect_encoding(input_path)
        if self.logger:
            self.logger.info(f"encoding: {input_path} {encoding}")
        if input_path.endswith(".gz"):
            f = gzip.open(input_path, mode="rt", encoding=encoding)
        elif suffix in [".parquet"]:
            f = open(input_path, "rb")
        else:
            f = open(input_path, encoding=encoding)
        return f

    def setup_logger(self):
        from logging import getLogger

        self.logger = getLogger("oakvar.converter")
        self.error_logger = getLogger("err.converter")

    def log_input_and_genome_assembly(self, input_path, genome_assembly):
        if not self.logger:
            return
        self.logger.info(f"input file: {input_path}")
        self.logger.info(f"input format: {self.format_name}")
        self.logger.info(f"genome_assembly: {genome_assembly}")

    def setup(self, input_path: str, encoding="utf-8"):
        _ = input_path or encoding
        pass

    def setup_file(self, input_path: str):
        from oakvar.lib.util.util import log_module

        f = self.get_file_object_for_input_path(input_path)
        log_module(self, self.logger)
        self.input_path = input_path
        self.setup(input_path)
        genome_assembly = self.get_genome_assembly()
        self.genome_assemblies.append(genome_assembly)
        self.log_input_and_genome_assembly(input_path, genome_assembly)
        self.set_do_liftover(genome_assembly, input_path)
        if self.do_liftover or self.do_liftover_chrM:
            self.setup_lifter(genome_assembly)

    def get_genome_assembly(self) -> str:
        from oakvar.lib.system.consts import default_assembly_key
        from oakvar.lib.exceptions import NoGenomeException
        from oakvar.lib.system import get_user_conf

        if self.given_input_assembly:
            return self.given_input_assembly
        input_assembly = getattr(self, "input_assembly", None)
        if input_assembly:
            return input_assembly
        user_conf = get_user_conf() or {}
        genome_assembly = user_conf.get(default_assembly_key, None)
        if genome_assembly:
            return genome_assembly
        raise NoGenomeException()

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

    def add_unique_variant(self, variant: dict, unique_variants: set):
        var_str = (
            f"{variant['chrom']}:{variant['pos']}:{variant['ref_base']}"
            + f":{variant['alt_base']}"
        )
        is_unique = var_str not in unique_variants
        if is_unique:
            unique_variants.add(var_str)
        return is_unique

    def add_end_pos_if_absent(self, variant: dict):
        col_name = "pos_end"
        if col_name not in variant:
            ref_base = variant["ref_base"]
            ref_len = len(ref_base)
            if ref_len == 1:
                variant[col_name] = variant["pos"]
            else:
                variant[col_name] = variant["pos"] + ref_len - 1

    def gather_variantss_wrapper(self, args):
        return self.gather_variantss(*args)

    def gather_variantss(self,
            lines_data: Dict[int, List[Tuple[int, Dict[str, Any]]]],
            core_num: int, 
    ) -> Tuple[List[List[Dict[str, Any]]], List[Dict[str, Any]]]:
        variants_l = []
        crl_l = []
        line_data = lines_data[core_num]
        for (line_no, line) in line_data:
            try:
                variants = self.convert_line(line)
                variants_datas, crl_datas = self.handle_converted_variants(variants, line_no)
                if variants_datas is None or crl_datas is None:
                    continue
                variants_l.append(variants_datas)
                crl_l.append(crl_datas)
            except KeyboardInterrupt:
                raise
            except Exception as e:
                self._log_conversion_error(line_no, e)
                self.num_valid_error_lines["error"] += 1
        return variants_l, crl_l

    def is_unique_variant(self, variant: dict, unique_vars: dict) -> bool:
        return variant["var_no"] not in unique_vars

    def handle_converted_variants(self,
            variants: List[Dict[str, Any]], line_no: int
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
                crl_data = self.handle_variant(variant, unique_vars, line_no)
            except Exception as e:
                self._log_conversion_error(line_no, e)
                continue
            variant_l.append(variant)
            if crl_data:
                crl_l.append(crl_data)
        return variant_l, crl_l

    def handle_variant(
        self,
        variant: dict, unique_vars: dict, line_no: int
    ) -> Optional[Dict[str, Any]]:
        from oakvar.lib.exceptions import NoVariantError

        if variant["ref_base"] == variant["alt_base"]:
            raise NoVariantError()
        tags = variant.get("tags")
        unique = self.is_unique_variant(variant, unique_vars)
        if unique:
            variant[self.unique_var_key] = True
            unique_vars[variant["var_no"]] = True
            self.handle_chrom(variant)
            self.handle_ref_base(variant)
            self.check_invalid_base(variant)
            self.normalize_variant(variant)
            self.add_end_pos_if_absent(variant)
            crl_data = self.perform_liftover_if_needed(variant)
            self.num_valid_error_lines["valid"] += 1
        else:
            variant[self.unique_var_key] = False
            crl_data = None
        self.handle_genotype(variant)
        if unique:
            variant["original_line"] = line_no
            variant["tags"] = tags
        return crl_data

    def collect_extra_output_columns(self):
        extra_output_columns = self.conf.get("extra_output_columns")
        if not extra_output_columns:
            return
        for col in extra_output_columns:
            self.extra_output_columns.append(col)

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
        self.set_variables_pre_run()
        batch_size: int = 2500
        uid = 1
        num_pool = 4
        pool = ThreadPool(num_pool)
        for input_path in self.input_paths:
            self.input_fname = Path(input_path).name
            fileno = self.input_path_dict2[input_path]
            self.setup_file(input_path)
            self.file_num_valid_variants = 0
            self.file_error_lines = 0
            self.num_valid_error_lines = {"valid": 0, "error": 0}
            start_line_pos: int = 1
            start_line_no: int = start_line_pos
            round_no: int = 0
            #stime = time.time()
            while True:
                #ctime = time.time()
                lines_data, immature_exit = self.get_variant_lines(input_path, num_pool, start_line_no, batch_size)
                args = [
                    (
                        lines_data,
                        core_num, 
                    ) for core_num in range(num_pool)
                ]
                results = pool.map(self.gather_variantss_wrapper, args)
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
                            if variant[self.unique_var_key]:
                                variant["fileno"] = fileno
                                self.write_extra_info(variant)
                        for crl in crl_data:
                            pass
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
        self.flush_err_holder(force=True)
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

    def get_df_headers(self):
        df_headers = []
        for col in self.output_columns:
            ty = col.get("type")
            if ty in ["str", "string"]:
                ty = pl.Utf8
            elif ty == "int":
                ty = pl.Int64
            elif ty == "float":
                ty = pl.Float64
            else:
                ty = None
            df_headers.append({"name": col.get("name"), "type": ty})
        return df_headers

    def get_intialized_var_ld(self, df_headers: List[Dict[str, Any]]):
        var_ld: Dict[str, List[Any]] = {}
        for header in df_headers:
            var_ld[header["name"]] = []
        return var_ld

    def iter_df_chunk(self, start: int=0, size: int = 10000, ignore_sample: bool=False):
        from pathlib import Path
        from multiprocessing.pool import ThreadPool
        from oakvar.lib.util.run import update_status
        from oakvar.lib.exceptions import LoggerError

        #raise ValueError("No input file was given. Consider giving `inputs` argument when initializing this module or giving `input_path` argument to this method.")
        if not self.logger:
            raise LoggerError(module_name=self.name)
        update_status(
            "started converter", logger=self.logger, serveradmindb=self.serveradmindb
        )
        self.set_variables_pre_run()
        uid = 1
        num_pool = 4
        pool = ThreadPool(num_pool)
        df_headers = self.get_df_headers()
        df_header_names: List[str] = [header["name"] for header in df_headers]
        var_ld = self.get_intialized_var_ld(df_headers)
        df: Optional[pl.DataFrame] = None
        for input_path in self.input_paths:
            self.input_fname = Path(input_path).name
            fileno = self.input_path_dict2[input_path]
            self.setup_file(input_path)
            self.file_num_valid_variants = 0
            self.file_error_lines = 0
            self.num_valid_error_lines = {"valid": 0, "error": 0}
            start_line_pos: int = 1
            start_line_no: int = start_line_pos
            round_no: int = 0
            #stime = time.time()
            while True:
                #ctime = time.time()
                df, immature_exit = self.get_variants_df(input_path, start_line_no, size)
                if not immature_exit is None:
                    yield df
                    if not immature_exit:
                        break
                    start_line_no += size
                else:
                    lines_data, immature_exit = self.get_variant_lines(input_path, num_pool, start_line_no, size)
                    args = [
                        (
                            lines_data,
                            core_num, 
                        ) for core_num in range(num_pool)
                    ]
                    results = pool.map(self.gather_variantss_wrapper, args)
                    lines_data = None
                    for result in results:
                        variants_l, crl_l = result
                        for i in range(len(variants_l)):
                            variants = variants_l[i]
                            crl_data = crl_l[i]
                            if len(variants) == 0:
                                continue
                            for variant in variants:
                                if variant[self.unique_var_key]:
                                    variant["uid"] = uid + variant["var_no"]
                                    if variant[self.unique_var_key]:
                                        variant["fileno"] = fileno
                                    for header_name in df_header_names:
                                        var_ld[header_name].append(variant.get(header_name))
                            uid += max([v["var_no"] for v in variants]) + 1
                    df2 = self.get_df_from_var_ld(var_ld, df_headers)
                    if df is None:
                        df = df2
                    else:
                        df = df.vstack(df2)
                    if df is not None and df.height >= size:
                        while df.height >= size:
                            yield df[:size]
                            df = df[size:]
                    var_ld = self.get_intialized_var_ld(df_headers)
                    if not immature_exit:
                        if df is not None and df.height > 0:
                            yield df
                        break
                    start_line_no += size * num_pool
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
        self.flush_err_holder(force=True)
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

    def initialize_var_ld(self, var_ld):
        var_ld["base__uid"] = []
        var_ld["base__chrom"] = []
        var_ld["base__pos"] = []
        var_ld["base__ref_base"] = []
        var_ld["base__alt_base"] = []

    def get_df_from_var_ld(self, var_ld: Dict[str, List[Any]], headers: List[Dict[str, Any]]) -> pl.DataFrame:
        df: pl.DataFrame = pl.DataFrame(
            [pl.Series(header["name"], var_ld[header["name"]], dtype=header["type"]) for header in headers]
        )
        return df

    def set_variables_pre_run(self):
        from time import time

        self.start_time = time()
        self.total_num_converted_variants = 0
        self.uid = 1

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

    def perform_liftover_if_needed_df(self, df: pl.DataFrame):
        from copy import copy
        from oakvar.lib.util.seq import liftover_one_pos
        from oakvar.lib.util.seq import liftover

        if self.is_chrM(variant):
            needed = self.do_liftover_chrM
        else:
            needed = self.do_liftover
        crl_data = None
        if needed:
            prelift_wdict = copy(variant)
            if crl_to_variant:
                variant["original_chrom"] = variant["chrom"]
                variant["original_pos"] = variant["pos"]
            else:
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
        return crl_data

    def perform_liftover_if_needed(self, variant, crl_to_variant: bool=False):
        from copy import copy
        from oakvar.lib.util.seq import liftover_one_pos
        from oakvar.lib.util.seq import liftover

        if self.is_chrM(variant):
            needed = self.do_liftover_chrM
        else:
            needed = self.do_liftover
        crl_data = None
        if needed:
            prelift_wdict = copy(variant)
            if crl_to_variant:
                variant["original_chrom"] = variant["chrom"]
                variant["original_pos"] = variant["pos"]
            else:
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
        return crl_data

    def is_chrM(self, wdict):
        return wdict["chrom"] == "chrM"

    def flush_err_holder(self, force: bool=False):
        if len(self.err_holder) > 1000 or force:
            if self.error_logger:
                for err_line in self.err_holder:
                    self.error_logger.error(err_line)
            self.err_holder.clear()

    def _log_conversion_error(self, line_no: int, e):
        from traceback import format_exc
        from oakvar.lib.exceptions import ExpectedException
        from oakvar.lib.exceptions import NoAlternateAllele

        if isinstance(e, NoAlternateAllele):
            return
        if isinstance(e, ExpectedException):
            err_str = str(e)
        else:
            err_str = format_exc().rstrip()
        if err_str not in self.unique_excs:
            err_no = len(self.unique_excs)
            self.unique_excs[err_str] = err_no
            if self.logger:
                self.logger.error(f"Error [{err_no}]: {self.input_path}: {err_str}")
            self.err_holder.append(f"{err_no}:{line_no}\t{str(e)}")
        else:
            err_no = self.unique_excs[err_str]
            self.err_holder.append(f"{err_no}:{line_no}\t{str(e)}")
        self.flush_err_holder()

    def end(self):
        pass
