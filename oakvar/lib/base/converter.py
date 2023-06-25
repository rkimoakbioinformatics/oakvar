from typing import Optional
from typing import Any
from typing import Tuple
from typing import List
from typing import Set
from typing import Dict
import polars as pl
from .commonmodule import BaseCommonModule


CHROM = "chrom"
POS = "pos"
END_POS = "end_pos"
REF_BASE = "ref_base"
ALT_BASE = "alt_base"
ORIG_CHROM = "ori_chrom"
ORIG_POS = "ori_pos"
ORIG_END_POS = "ori_end_pos"
ORIG_REF_BASE = "ori_ref_base"
ORIG_ALT_BASE = "ori_alt_base"
VALID = "valid"
ERROR = "error"
NO_ALLELE = "noallele"


class BaseConverter(object):
    IGNORE = "converter_ignore"
    input_assembly_int_dict = {
        "hg18": 18,
        "hg19": 19,
        "hg38": 38,
        "GRCh36": 18,
        "GRCh37": 19,
        "GRCh38": 38,
    }

    def __init__(
        self,
        format_name: str = "",
        genome: Optional[str] = None,
        serveradmindb=None,
        module_options: Dict = {},
        input_encoding: Optional[str] = None,
        outer=None,
        title: Optional[str] = None,
        conf: Dict[str, Any] = {},
        code_version: Optional[str] = None,
        ignore_sample: bool=False,
        wgs_reader: Optional[BaseCommonModule] = None,
        df_mode: Optional[bool] = None,
    ):
        from re import compile
        from pathlib import Path
        import inspect
        from multiprocessing.pool import ThreadPool
        from oakvar.lib.module.local import get_module_conf
        from oakvar.lib.util.util import get_ov_system_output_columns

        self.logger = None
        self.converters = {}
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
        self.input_assembly: Optional[int] = None
        self.uid: int = 0
        self.read_lnum: int = 0
        self.lifter = None
        self.module_options = None
        self.given_input_assembly: Optional[str] = genome
        self.converter_by_input_path: Dict[str, Optional[BaseConverter]] = {}
        self.file_num_valid_variants: Dict[int, int] = {}
        self.file_error_lines: Dict[int, int] = {}
        self.num_valid_error_lines: Dict[str, int] = {}
        self.fileno = 0
        self.module_options = module_options
        self.serveradmindb = serveradmindb
        self.input_encoding = input_encoding
        self.outer = outer
        self.total_num_converted_variants = 0
        self.genome_assemblies: List[int] = []
        self.base_re = compile("^[ATGC]+|[-]+$")
        self.chromdict = {
            "chrx": "chrX",
            "chry": "chrY",
            "chrMT": "chrM",
            "chrMt": "chrM",
            "chr23": "chrX",
            "chr24": "chrY",
        }
        self.chrom_colno: int = -1
        self.pos_colno: int = -1
        self.end_pos_colno: int = -1
        self.ref_base_colno: int = -1
        self.alt_base_colno: int = -1
        self.script_path = Path(inspect.getfile(self.__class__))
        self.module_type = "converter"
        self.ignore_sample: bool = ignore_sample
        self.header_num_line: int = 0
        self.line_no: int = 0
        self.wgs_reader = wgs_reader
        self.name: str = self.script_path.stem
        self.conf: Dict[str, Any] = (
            get_module_conf(self.name, module_type="converter") or {}
        )
        if conf:
            self.conf.update(conf.copy())
        if df_mode is not None:
            self.df_mode = df_mode
        else:
            self.df_mode = self.conf.get("df_mode", False)
        self.setup_logger()
        self.time_error_written: float = 0
        self.module_type = "converter"
        self.input_path: str = ""
        self.pool: Optional[ThreadPool] = None
        self.df_headers: Dict[str, List[Dict[str, Any]]] = {}
        self.c: int = 0
        self.title = title
        if self.title:
            self.conf["title"] = self.title
        elif "title" in self.conf:
            self.title = self.conf["title"]
        # code_version
        if code_version:
            self.code_version = code_version
        else:
            if "code_version" in self.conf:
                self.code_version: str = self.conf["version"]
            elif "version" in self.conf:
                self.code_version: str = self.conf["version"]
            else:
                self.code_version: str = ""
        # format_name
        if not format_name:
            format_name = str(self.conf.get("format_name", ""))
        if not format_name:
            format_name = self.name.split("-")[0]
        self.format_name = format_name
        self.output: Dict[str, Dict[str, Any]] = get_ov_system_output_columns().copy()

    def check_format(self, *__args__, **__kwargs__):
        pass

    def get_variant_lines(
        self, input_path: str, mp: int, start_line_no: int, batch_size: int
    ) -> Tuple[Dict[int, List[Tuple[str, int]]], bool, int]:
        import linecache

        immature_exit: bool = False
        line_no: int = start_line_no
        end_line_no = line_no + mp * batch_size - 1
        lines: Dict[int, List[Tuple[str, int]]] = {i: [] for i in range(mp)}
        chunk_no: int = 0
        chunk_size: int = 0
        while True:
            line = linecache.getline(input_path, line_no)
            if not line:
                immature_exit = False
                break
            line = line[:-1]
            lines[chunk_no].append((line, line_no))
            chunk_size += 1
            if line_no >= end_line_no:
                immature_exit = True
                line_no += 1
                break
            else:
                if chunk_size >= batch_size:
                    chunk_no += 1
                    chunk_size = 0
                line_no += 1
        return lines, immature_exit, line_no

    def write_extra_info(self, _: dict):
        pass

    def convert_line(self, l: str, *__args__, **__kwargs__) -> Dict[str, List[Dict[str, Any]]]:
        _ = l
        return {}

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

    def setup_lifter(self, genome_assembly: Optional[int]):
        from oakvar.lib.util.seq import get_lifter

        self.lifter = get_lifter(source_assembly=genome_assembly)

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

        log_module(self, self.logger)
        self.input_path = input_path
        self.detect_encoding_of_input_path(input_path)
        self.setup(input_path)
        genome_assembly = self.get_genome_assembly()
        self.genome_assemblies.append(genome_assembly)
        self.log_input_and_genome_assembly(input_path, genome_assembly)
        self.set_do_liftover(genome_assembly, input_path)
        if self.do_liftover or self.do_liftover_chrM:
            self.setup_lifter(genome_assembly)

    def get_genome_assembly(self) -> int:
        from oakvar.lib.system.consts import default_assembly_key
        from oakvar.lib.exceptions import NoGenomeException
        from oakvar.lib.system import get_user_conf

        if self.given_input_assembly:
            input_assembly = self.given_input_assembly
        elif self.input_assembly:
            input_assembly = self.input_assembly
        else:
            user_conf = get_user_conf() or {}
            input_assembly = user_conf.get(default_assembly_key, None)
            if not input_assembly:
                raise NoGenomeException()
        if not isinstance(input_assembly, int):
            if input_assembly not in self.input_assembly_int_dict:
                raise NoGenomeException()
            input_assembly = self.input_assembly_int_dict.get(input_assembly, 38)
        return input_assembly

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
        col_name = "end_pos"
        if col_name not in variant:
            ref_base = variant["ref_base"]
            ref_len = len(ref_base)
            if ref_len == 1:
                variant[col_name] = variant["pos"]
            else:
                variant[col_name] = variant["pos"] + ref_len - 1

    def get_dfs(self, fileno: int, lines_data: List[Tuple[str, int]], uid_start: int) -> Dict[str, pl.DataFrame]:
        converted_data, max_idx = self.collect_converted_datas(fileno, lines_data)
        dfs = self.make_dfs_from_converted_datas(converted_data, max_idx, uid_start, fileno)
        return dfs

    def collect_converted_datas(self, fileno: int, lines_data: List[Tuple[str, int]]) -> Tuple[Dict[str, Dict[str, List[Any]]], int]:
        from oakvar.lib.consts import VARIANT_LEVEL
        from oakvar.lib.consts import ERR_LEVEL
        from oakvar.lib.consts import LINE_NO_KEY

        COLLECT_MARGIN: float = 1.2
        size: int = int(len(lines_data) * COLLECT_MARGIN)
        series_data: Dict[str, Dict[str, List[Any]]] = self.get_intialized_series_data(size)
        c: int = 0
        for line, line_no in lines_data:
            try:
                try:
                    converted_data = self.convert_line(line)
                    if not converted_data:
                        continue
                    self.process_converted_data(converted_data, series_data, fileno, line_no)
                except Exception as e:
                    self.log_conversion_error(e, series_data[ERR_LEVEL], fileno=fileno, lineno=line_no)
                    self.num_valid_error_lines[ERROR] += 1
                    continue
                if len(converted_data[VARIANT_LEVEL]) == 0:
                    self.num_valid_error_lines[NO_ALLELE] += 1
                    continue
                if c < size:
                    for table_name, table_data in converted_data.items():
                        for d in table_data: 
                            for col_name, col_value in d.items():
                                series_data[table_name][col_name][c] = col_value
                    series_data[VARIANT_LEVEL][LINE_NO_KEY][c] = line_no
                else:
                    for table_name, table_data in converted_data.items():
                        for d in table_data: 
                            for col_name, col_value in d.items():
                                series_data[table_name][col_name].append(col_value)
                    series_data[VARIANT_LEVEL][LINE_NO_KEY].append(line_no)
                self.num_valid_error_lines[VALID] += 1
                c += 1
            except KeyboardInterrupt:
                raise
            except Exception as e:
                self.log_conversion_error(e, series_data[ERR_LEVEL], fileno=fileno, lineno=line_no)
                self.num_valid_error_lines[ERROR] += 1
        return series_data, c

    def process_converted_data(self,
            converted_data: Dict[str, List[Dict[str, Any]]],
            series_data: Dict[str, Dict[str, List[Any]]],
            fileno: int,
            lineno: int
    ):
        from ..consts import VARIANT_LEVEL
        from ..consts import SAMPLE_LEVEL
        from ..consts import ERR_LEVEL

        ld_var = converted_data[VARIANT_LEVEL]
        ld_spl = converted_data[SAMPLE_LEVEL]
        c: int = 0
        max_c: int = len(ld_var)
        while c < max_c:
            d_var = ld_var[c]
            try:
                self.handle_variant(d_var)
                c += 1
            except Exception as e:
                del ld_var[c]
                del ld_spl[c]
                max_c = max_c - 1
                self.log_conversion_error(e, series_data[ERR_LEVEL], fileno=fileno, lineno=lineno)
                continue

    def handle_variant(
        self,
        d_var: Dict[str, Any]
    ):
        from oakvar.lib.exceptions import NoVariantError

        if d_var["ref_base"] == d_var["alt_base"]:
            raise NoVariantError()
        tags = d_var.get("tags")
        self.handle_chrom(d_var)
        self.handle_ref_base(d_var)
        self.check_invalid_base(d_var)
        self.normalize_variant(d_var)
        self.add_end_pos_if_absent(d_var)
        self.perform_liftover_if_needed(d_var)
        self.handle_genotype(d_var)
        d_var["tags"] = tags

    def get_sample_colname(self, sample: str) -> str:
        return f"in__{sample}"

    def get_df_headers(self) -> Dict[str, List[Dict[str, Any]]]:
        from ..consts import OUTPUT_COLS_KEY

        self.df_headers: Dict[str, List[Dict[str, Any]]] = {}
        for table_name, table_output in self.output.items():
            self.df_headers[table_name] = []
            coldefs = table_output.get(OUTPUT_COLS_KEY, [])
            for col in coldefs:
                ty = col.get("type")
                if ty in ["str", "string"]:
                    ty = pl.Utf8
                elif ty == "int":
                    ty = pl.Int64
                elif ty == "float":
                    ty = pl.Float64
                elif ty == "bool":
                    ty = pl.Boolean
                else:
                    ty = None
                self.df_headers[table_name].append({"name": col.get("name"), "type": ty})
        return self.df_headers

    def get_intialized_series_data(self, size: int) -> Dict[str, Dict[str, List[Any]]]:
        from ..consts import ERR_LEVEL

        series_data: Dict[str, Dict[str, List[Any]]] = {}
        for table_name, headers in self.df_headers.items():
            series_data[table_name] = {}
            if table_name == ERR_LEVEL:
                for header in headers:
                    series_data[table_name][header["name"]] = []
            else:
                for header in headers:
                    series_data[table_name][header["name"]] = [None] * size
        return series_data

    def detect_encoding_of_input_path(self, input_path: str):
        from pathlib import Path
        from oakvar.lib.util.util import detect_encoding

        suffix = Path(input_path).suffix
        if self.input_encoding:
            return
        # TODO: Remove the hardcoding.
        elif suffix in [".parquet"]:
            encoding = ""
        else:
            if self.logger:
                self.logger.info(f"detecting encoding of {input_path}")
            encoding = detect_encoding(input_path)
        if self.logger:
            self.logger.info(f"encoding: {input_path} {encoding}")
        self.input_encoding = encoding

    def make_dfs_from_converted_datas(self, converted_data: Dict[str, Dict[str, List[Any]]], max_idx: int, uid_start: int, fileno: int) -> Dict[str, pl.DataFrame]:
        from oakvar.lib.consts import VARIANT_LEVEL

        series_data: Dict[str, Dict[str, List[Any]]] = {}
        for table_name, table_data in converted_data.items():
            series_data[table_name] = {}
            for col_name, col_data in table_data.items():
                series_data[table_name][col_name] = col_data[:max_idx]
        series_data[VARIANT_LEVEL]["uid"] = [uid_start + i for i in range(max_idx)]
        series_data[VARIANT_LEVEL]["fileno"] = [fileno for _ in range(max_idx)]
        dfs = self.get_dfs_from_series_data(series_data, self.df_headers)
        return dfs

    def get_conversion_stats(self) -> Dict[str, int]:
        return self.num_valid_error_lines

    def log_conversion_stats(self, conversion_stats: Optional[Dict[str, int]] = None):
        from ..util.run import update_status

        if conversion_stats is None:
            conversion_stats = self.num_valid_error_lines
        status: str = f"Lines converted: {conversion_stats[VALID]}"
        update_status(status, logger=self.logger, serveradmindb=self.serveradmindb)
        status: str = f"Lines with conversion error: {conversion_stats[ERROR]}"
        update_status(status, logger=self.logger, serveradmindb=self.serveradmindb)
        status: str = f"Lines with no conversion result: {conversion_stats[NO_ALLELE]}"
        update_status(status, logger=self.logger, serveradmindb=self.serveradmindb)

    def setup_df(self, input_paths: List[str] = [], samples: Optional[List[str]] = None):
        from oakvar.lib.consts import VARIANT_LEVEL

        if samples is None:
            if not self.samples and not self.ignore_sample:
                samples = self.collect_samples(input_paths)
                self.make_sample_output_columns(samples)
        else:
            self.make_sample_output_columns(samples)
        self.set_variables_pre_run()
        df_headers: Dict[str, List[Dict[str, Any]]] = self.get_df_headers()
        df_variant_header_names: List[str] = [header["name"] for header in df_headers[VARIANT_LEVEL]]
        self.chrom_colno = df_variant_header_names.index("chrom") + 1 if "chrom" in df_variant_header_names else -1
        self.pos_colno = df_variant_header_names.index("pos") + 1 if "pos" in df_variant_header_names else -1
        self.end_pos_colno = df_variant_header_names.index("pos") + 1 if "pos" in df_variant_header_names else -1
        self.ref_base_colno = df_variant_header_names.index("ref_base") + 1 if "ref_base" in df_variant_header_names else -1
        self.alt_base_colno = df_variant_header_names.index("alt_base") + 1 if "alt_base" in df_variant_header_names else -1

    def setup_df_file(self, input_path: str, fileno: int):
        from pathlib import Path

        self.current_input_fname = Path(input_path).name
        self.setup_file(input_path)
        self.file_num_valid_variants[fileno] = 0
        self.file_error_lines[fileno] = 0
        self.num_valid_error_lines = {VALID: 0, ERROR: 0, NO_ALLELE: 0}

    def initialize_series_data(self, series_data):
        series_data["base__uid"] = []
        series_data["base__chrom"] = []
        series_data["base__pos"] = []
        series_data["base__ref_base"] = []
        series_data["base__alt_base"] = []

    def get_dfs_from_series_data(self, series_data: Dict[str, Dict[str, List[Any]]], headers: Dict[str, List[Dict[str, Any]]]) -> Dict[str, pl.DataFrame]:
        dfs: Dict[str, pl.DataFrame] = {}
        for table_name, table_data in series_data.items():
            df: pl.DataFrame = pl.DataFrame(
                [pl.Series(header["name"], table_data[header["name"]], dtype=header["type"]) for header in headers[table_name]]
            )
            dfs[table_name] = df
        return dfs

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
        end_time = time()
        self.logger.info("finished: %s" % asctime(localtime(end_time)))
        runtime = round(end_time - self.start_time, 3)
        self.logger.info("runtime: %s" % runtime)
        status = "finished Converter"
        update_status(status, logger=self.logger, serveradmindb=self.serveradmindb)

    def perform_liftover_if_needed_df(self, df: pl.DataFrame):
        from oakvar.lib.util.seq import liftover_one_pos
        from oakvar.lib.util.seq import liftover
        from oakvar.lib.exceptions import LiftoverFailure

        columns = df.columns
        if self.chrom_colno == -1 or self.pos_colno == -1 or self.ref_base_colno == -1 or self.alt_base_colno == -1:
            return df
        df_len = df.shape[0]
        chrom_vals: List[str] = [""] * df_len
        pos_vals: List[int] = [0] * df_len
        end_pos_vals: List[int] = [0] * df_len
        ref_base_vals: List[str] = [""] * df_len
        alt_base_vals: List[str] = [""] * df_len
        row_no: int = 0
        for row in df.iter_rows():
            chrom: str = row[self.chrom_colno]
            pos: int = row[self.pos_colno]
            end_pos: int = row[self.pos_colno]
            ref_base: str = row[self.ref_base_colno]
            alt_base: str = row[self.alt_base_colno]
            if self.is_chrM(chrom):
                needed = self.do_liftover_chrM
            else:
                needed = self.do_liftover
            if needed:
                try:
                    (
                        chrom,
                        pos,
                        ref_base,
                        alt_base,
                    ) = liftover(
                        chrom,
                        pos,
                        ref_base,
                        alt_base,
                        lifter=self.lifter,
                        wgs_reader=self.wgs_reader,
                    )
                    converted_end = liftover_one_pos(
                        chrom, end_pos, lifter=self.lifter
                    )
                    if converted_end is None:
                        end_pos = pos
                    else:
                        end_pos = converted_end[1]
                except LiftoverFailure:
                    chrom = ""
                    pos = 0
                    end_pos = 0
                    ref_base = ""
                    alt_base = ""
            chrom_vals[row_no] = chrom
            pos_vals[row_no] = pos
            end_pos_vals[row_no] = end_pos
            ref_base_vals[row_no] = ref_base
            alt_base_vals[row_no] = alt_base
            row_no += 1
        if ORIG_POS not in columns:
            df.rename({CHROM: ORIG_CHROM, POS: ORIG_POS, REF_BASE: ORIG_REF_BASE, ALT_BASE: ORIG_ALT_BASE})
        else:
            df = df.drop([CHROM, POS, END_POS, REF_BASE, ALT_BASE])
        df = df.with_columns(
            [
                pl.Series(CHROM, chrom_vals, dtype=pl.Utf8), # type: ignore
                pl.Series(POS, pos_vals, dtype=pl.Int32),
                pl.Series(END_POS, end_pos_vals, dtype=pl.Int32),
                pl.Series(REF_BASE, ref_base_vals, dtype=pl.Utf8),
                pl.Series(ALT_BASE, alt_base_vals, dtype=pl.Utf8),
            ]
        )
        return df

    def get_wgs_reader(self):
        pass

    def perform_liftover_if_needed(self, variant):
        from oakvar.lib.util.seq import liftover_one_pos
        from oakvar.lib.util.seq import liftover

        if self.is_chrM(variant):
            needed = self.do_liftover_chrM
        else:
            needed = self.do_liftover
        if needed:
            variant["original_chrom"] = variant["chrom"]
            variant["original_pos"] = variant["pos"]
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
                variant["chrom"], variant["end_pos"], lifter=self.lifter
            )
            if converted_end is None:
                end_pos = ""
            else:
                end_pos = converted_end[1]
            variant["end_pos"] = end_pos

    def is_chrM(self, chrom: str):
        return chrom == "chrM"

    def add_to_err_series(self, err_series: Dict[str, List[Any]], fileno: Optional[int] = None, lineno: Optional[int] = None, uid: Optional[int] = None, err: Optional[str] = None):
        err_series["fileno"].append(fileno)
        err_series["lineno"].append(lineno)
        err_series["uid"].append(uid)
        err_series["err"].append(err)

    def log_conversion_error(self, e, err_series: Dict[str, List[Any]], fileno: Optional[int]=None, lineno: Optional[int]=None):
        from traceback import format_exc
        from oakvar.lib.exceptions import ExpectedException
        from oakvar.lib.exceptions import NoAlternateAllele

        if isinstance(e, NoAlternateAllele):
            self.add_to_err_series(err_series, fileno=fileno, lineno=lineno, err=str(e))
            return
        if isinstance(e, ExpectedException):
            err_str = str(e)
        else:
            err_str = format_exc().rstrip()
        self.add_to_err_series(err_series, fileno=fileno, lineno=lineno, err=err_str)
        if err_str not in self.unique_excs:
            err_no = len(self.unique_excs)
            self.unique_excs[err_str] = err_no
            if self.logger:
                self.logger.error(f"Error [{err_no}]: {self.input_path}: {err_str}")
        else:
            err_no = self.unique_excs[err_str]

    def end(self):
        pass

    def get_standardized_module_option(self, v: Any) -> Any:
        from ..util.run import get_standardized_module_option

        return get_standardized_module_option(v)

    def get_samples_from_line(self, l: str) -> Set[str]:
        _ = l
        samples_line: Set[str] = set()
        return samples_line

    def collect_samples_from_file(self, input_path: str) -> Set[str]:
        import gzip
        from pathlib import Path

        samples: Set[str] = set()
        p = Path(input_path)
        if p.suffix == ".gz":
            f = gzip.open(p, "rt")
        else:
            f = open(p)
        for line in f:
            samples_line = self.get_samples_from_line(line)
            samples = samples.union(samples_line)
        return samples

    def collect_samples(self, input_paths: List[str]) -> List[str]:
        samples: Set[str] = set()
        if self.logger:
            self.logger.info("Detecting samples...")
        for input_path in input_paths:
            samples_file = self.collect_samples_from_file(input_path)
            samples = samples.union(samples_file)
        samples_list = sorted(list(samples))
        self.samples = samples_list
        if self.logger:
            self.logger.info(f"{len(self.samples)} samples detected.")
        return self.samples

    def make_sample_output_columns(self, samples: List[str]):
        from ..consts import SAMPLE_LEVEL
        from ..consts import OUTPUT_COLS_KEY
        from ..util.util import get_ov_system_output_columns

        sample_output_columns: List[Dict[str, Any]] = self.output[SAMPLE_LEVEL][OUTPUT_COLS_KEY]
        self.samples = sorted(samples)
        sample_output_columns = get_ov_system_output_columns().copy()[SAMPLE_LEVEL][OUTPUT_COLS_KEY]
        for sample in self.samples:
            coldef = {"name": self.get_sample_colname(sample), "title": f"Variant present in {sample}", "type": "bool"}
            sample_output_columns.append(coldef)
        self.output[SAMPLE_LEVEL][OUTPUT_COLS_KEY] = sample_output_columns

