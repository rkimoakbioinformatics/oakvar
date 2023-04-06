from typing import Optional
from typing import Any
from typing import Tuple
from typing import List
from typing import Dict
from typing import Iterator
from typing import TextIO
import polars as pl
from pyliftover import LiftOver


class BaseConverter(object):
    IGNORE = "converter_ignore"

    def __init__(
        self,
        inputs: List[str] = [],
        input_format: Optional[str] = None,
        name: Optional[str] = None,
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
    ):
        from re import compile
        from pathlib import Path
        import inspect
        from oakvar import get_wgs_reader
        from oakvar.lib.exceptions import ExpectedException
        from oakvar.lib.module.local import get_module_conf

        self.logger = None
        self.crv_writer = None
        self.crs_writer = None
        self.crm_writer = None
        self.crl_writer = None
        self.converters = {}
        self.available_input_formats: List[str] = []
        self.pipeinput = False
        self.input_dir = None
        self.input_path_dict = {}
        self.input_path_dict2 = {}
        self.input_file_handles: Dict[str, TextIO] = {}
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
        if not inputs:
            raise ExpectedException("Input files are not given.")
        self.input_paths = inputs
        self.format = input_format
        self.script_path = Path(inspect.getfile(self.__class__))
        self.ignore_sample: bool = ignore_sample
        self.header_num_line: int = 0
        self.line_no: int = 0
        if name:
            self.name: str = name
        else:
            self.name = self.script_path.stem.split("-")[0]
        self.output_dir = output_dir
        self.parse_inputs()
        self.parse_output_dir()
        self.conf: Dict[str, Any] = (
            get_module_conf(self.name, module_type="converter") or {}
        )
        if conf:
            self.conf.update(conf.copy())
        self.module_options = module_options
        self.serveradmindb = serveradmindb
        self.input_encoding = input_encoding
        self.outer = outer
        self.setup_logger()
        self.wgs_reader = get_wgs_reader(assembly="hg38")
        self.time_error_written: float = 0

        self.module_type = "converter"
        self.format_name: str = ""
        self.run_name = run_name
        self.input_path = ""
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

    def check_format(self, *__args__, **__kwargs__):
        pass

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

    def prepare_for_mp(self):
        pass

    def write_extra_info(self, _: dict):
        pass

    def convert_line(self, *__args__, **__kwargs__) -> List[Dict[str, Any]]:
        return []

    def addl_operation_for_unique_variant(self, __wdict__, __wdict_no__):
        pass

    def save(self, overwrite: bool = False, interactive: bool = False):
        from ..module.local import create_module_files

        create_module_files(self, overwrite=overwrite, interactive=interactive)

    def convert_file(
            self, file, *__args__, line_no: int=0, file_pos: int=0, exc_handler=None, input_path=None, **__kwargs__
    ) -> Iterator[Tuple[int, List[dict]]]:
        import linecache

        line_no = 0
        for line in file:
            line_no += 1
            try:
                yield line_no, self.convert_line(line)
            except Exception as e:
                if exc_handler:
                    exc_handler(line_no, e)
                else:
                    raise e
        return None

    def get_do_liftover_chrM(self, genome_assembly, f, do_liftover):
        _ = genome_assembly or f
        return do_liftover

    def set_do_liftover(self, genome_assembly, f):
        self.do_liftover = genome_assembly != "hg38"
        self.do_liftover_chrM = self.get_do_liftover_chrM(
            genome_assembly, f, self.do_liftover
        )
        if self.logger:
            self.logger.info(f"liftover needed: {self.do_liftover}")
            self.logger.info(f"liftover for chrM needed: {self.do_liftover_chrM}")

    def setup_lifter(self, genome_assembly) -> Optional[LiftOver]:
        from oakvar.lib.util.seq import get_lifter

        self.lifter = get_lifter(source_assembly=genome_assembly)

    def parse_inputs(self):
        from pathlib import Path

        self.pipeinput = False
        if self.input_paths and len(self.input_paths) == 1 and self.input_paths[0] == "-":
            self.pipeinput = True
            self.input_paths = [STDIN]
        else:
            self.input_paths = [str(Path(x).resolve()) for x in self.input_paths if x != "-"]
        self.input_dir = str(Path(self.input_paths[0]).parent)
        if self.pipeinput is False:
            for i in range(len(self.input_paths)):
                self.input_path_dict[i] = self.input_paths[i]
                self.input_path_dict2[self.input_paths[i]] = i
        else:
            self.input_path_dict[0] = self.input_paths[0]
            self.input_path_dict2[STDIN] = 0

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
        from oakvar.lib.util.util import detect_encoding

        if input_path == STDIN:
            encoding = "utf-8"
        else:
            if self.logger:
                self.logger.info(f"detecting encoding of {input_path}")
        if self.input_encoding:
            encoding = self.input_encoding
        else:
            encoding = detect_encoding(input_path)
        if self.logger:
            self.logger.info(f"encoding: {input_path} {encoding}")
        if input_path == STDIN:
            f = sys.stdin
        elif input_path.endswith(".gz"):
            f = gzip.open(input_path, mode="rt", encoding=encoding)
        else:
            f = open(input_path, encoding=encoding)
        return f

    def setup_logger(self):
        from logging import getLogger

        self.logger = getLogger("oakvar.converter")
        self.error_logger = getLogger("err.converter")

    def check_input_format(self):
        from oakvar.lib.exceptions import InvalidInputFormat

        if self.pipeinput and not self.format:
            raise InvalidInputFormat("input_format should be given with pipe input")

    def log_input_and_genome_assembly(self, input_path, genome_assembly):
        if not self.logger:
            return
        if self.pipeinput:
            self.logger.info(f"input file: {STDIN}")
        else:
            self.logger.info(f"input file: {input_path}")
        self.logger.info("input format: %s" % self.format_name)
        self.logger.info(f"genome_assembly: {genome_assembly}")

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

    def setup(self, _):
        raise NotImplementedError("setup method should be implemented.")

    def setup_file(self, input_path: str) -> TextIO:
        from sys import stdin
        from oakvar.lib.util.util import log_module

        if self.pipeinput:
            f = stdin
        else:
            f = self.input_file_handles[input_path]
        log_module(self, self.logger)
        self.input_path = input_path
        self.setup(f)
        genome_assembly = self.get_genome_assembly()
        self.genome_assemblies.append(genome_assembly)
        self.log_input_and_genome_assembly(input_path, genome_assembly)
        self.set_do_liftover(genome_assembly, f)
        if self.do_liftover or self.do_liftover_chrM:
            self.setup_lifter(genome_assembly)
        if self.pipeinput is False:
            f.seek(0)
        return f

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

    def handle_variant(
        self,
        variant: Dict[str, Any],
        var_no: int,
        unique_variants: set,
        var_ld: Dict[str, List[Any]],
    ):
        from oakvar.lib.exceptions import NoVariantError

        if variant["ref_base"] == variant["alt_base"]:
            raise NoVariantError()
        variant["uid"] = self.uid
        self.handle_chrom(variant)
        self.handle_ref_base(variant)
        self.check_invalid_base(variant)
        self.normalize_variant(variant)
        self.add_end_pos_if_absent(variant)
        self.perform_liftover_if_needed(variant)
        self.file_num_valid_variants += 1
        self.total_num_valid_variants += 1
        try:
            self.addl_operation_for_unique_variant(variant, var_no)
        except Exception as e:
            self._log_conversion_error(self.read_lnum, e, full_line_error=False)
        self.handle_genotype(variant)
        var_ld["base__uid"].append(variant["uid"])
        var_ld["base__chrom"].append(variant["chrom"])
        var_ld["base__pos"].append(variant["pos"])
        var_ld["base__ref_base"].append(variant["ref_base"])
        var_ld["base__alt_base"].append(variant["alt_base"])
        self.uid += 1

    def handle_converted_variants(
        self, variants: List[Dict[str, Any]], var_ld: Dict[str, List[Any]]
    ) -> int:
        from oakvar.lib.exceptions import IgnoredVariant

        if variants is BaseConverter.IGNORE:
            return 0
        self.total_num_converted_variants += 1
        if not variants:
            raise IgnoredVariant("No valid alternate allele was found in any samples.")
        unique_variants = set()
        num_handled_variant: int = 0
        for var_no, variant in enumerate(variants):
            self.handle_variant(variant, var_no, unique_variants, var_ld)
            num_handled_variant += 1
        return num_handled_variant

    def get_df(self, input_path: str, line_no: int=0, file_pos: int=0, ignore_sample: bool=False):
        from pathlib import Path

        input_fname = (
            Path(input_path).name if not self.pipeinput else STDIN
        )
        f = self.setup_file(self.input_path)
        for self.read_lnum, variants in self.convert_file(
            f, input_path=input_path, line_no=line_no, file_pos=file_pos, exc_handler=self._log_conversion_error, ignore_sample=ignore_sample
        ):
            num_handled_variant: int = 0
            try:
                num_handled_variant = self.handle_converted_variants(variants, var_ld)
            except KeyboardInterrupt:
                raise
            except Exception as e:
                self._log_conversion_error(self.read_lnum, e)
            len_variants: int = num_handled_variant
            len_chunk += len_variants
            len_df += len_variants
            if len_chunk >= chunk_size:
                df = self.get_df_from_var_ld(var_ld)
                if total_df is None:
                    total_df = df
                else:
                    total_df.extend(df)
                self.initialize_var_ld(var_ld)
                len_chunk = 0
            if df_size > 0 and len_df >= df_size:
                total_dfs[df_no] = total_df
                df_no += 1
                if df_no == list_size:
                    yield total_dfs
                    total_dfs = [None] * list_size
                    df_no = 0
                total_df = None
                len_df = 0
            if self.read_lnum % 10000 == 0:
                status = (
                    f"Running Converter ({self.input_fname}): line {self.read_lnum}"
                )
                update_status(
                    status, logger=self.logger, serveradmindb=self.serveradmindb
                )
        if len_chunk:
            df = self.get_df_from_var_ld(var_ld)
            if total_df is None:
                total_df = df
            else:
                total_df.extend(df)
            self.initialize_var_ld(var_ld)
            len_chunk = 0
            total_dfs[df_no] = total_df
            yield total_dfs
            total_df = None
            len_df = 0
            df_no = 0

    def run_df(self, input_path: str="", chunk_size: int=1000, start: int=0, df_size: int = 0, ignore_sample: bool=False):
        from pathlib import Path
        from oakvar.lib.util.run import update_status

        if not self.input_paths or not self.logger:
            raise
        update_status(
            "started converter", logger=self.logger, serveradmindb=self.serveradmindb
        )
        self.collect_input_file_handles()
        self.set_variables_pre_run()
        if df_size > 0 and chunk_size > df_size:
            chunk_size = df_size
        total_df: Optional[pl.DataFrame] = None
        len_df: int = 0
        for self.input_path in self.input_paths:
            self.input_fname = (
                Path(self.input_path).name if not self.pipeinput else STDIN
            )
            f = self.setup_file(self.input_path)
            self.file_num_valid_variants = 0
            self.file_error_lines = 0
            var_ld: Dict[str, List[Any]] = {}
            self.initialize_var_ld(var_ld)
            len_chunk: int = 0
            total_dfs: List[Optional[pl.DataFrame]] = [None] * list_size
            df_no = 0
            pool = Pool(list_size)
            for self.read_lnum, variants in self.convert_file(
                f, input_path=self.input_path, exc_handler=self._log_conversion_error, ignore_sample=ignore_sample
            ):
                num_handled_variant: int = 0
                try:
                    num_handled_variant = self.handle_converted_variants(variants, var_ld)
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    self._log_conversion_error(self.read_lnum, e)
                len_variants: int = num_handled_variant
                len_chunk += len_variants
                len_df += len_variants
                if len_chunk >= chunk_size:
                    df = self.get_df_from_var_ld(var_ld)
                    if total_df is None:
                        total_df = df
                    else:
                        total_df.extend(df)
                    self.initialize_var_ld(var_ld)
                    len_chunk = 0
                if df_size > 0 and len_df >= df_size:
                    total_dfs[df_no] = total_df
                    df_no += 1
                    if df_no == list_size:
                        yield total_dfs
                        total_dfs = [None] * list_size
                        df_no = 0
                    total_df = None
                    len_df = 0
                if self.read_lnum % 10000 == 0:
                    status = (
                        f"Running Converter ({self.input_fname}): line {self.read_lnum}"
                    )
                    update_status(
                        status, logger=self.logger, serveradmindb=self.serveradmindb
                    )
            if len_chunk:
                df = self.get_df_from_var_ld(var_ld)
                if total_df is None:
                    total_df = df
                else:
                    total_df.extend(df)
                self.initialize_var_ld(var_ld)
                len_chunk = 0
                total_dfs[df_no] = total_df
                yield total_dfs
                total_df = None
                len_df = 0
                df_no = 0
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

    def initialize_var_ld(self, var_ld):
        var_ld["base__uid"] = []
        var_ld["base__chrom"] = []
        var_ld["base__pos"] = []
        var_ld["base__ref_base"] = []
        var_ld["base__alt_base"] = []

    def get_df_from_var_ld(self, var_ld: Dict[str, List[Any]]) -> pl.DataFrame:
        df: pl.DataFrame = pl.DataFrame(
            [
                pl.Series("uid", var_ld["base__uid"]),
                pl.Series("chrom", var_ld["base__chrom"]),
                pl.Series("pos", var_ld["base__pos"]),
                pl.Series("ref_base", var_ld["base__ref_base"]),
                pl.Series("alt_base", var_ld["base__alt_base"]),
            ]
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

    def perform_liftover_if_needed(self, variant):
        from copy import copy
        from oakvar.lib.util.seq import liftover_one_pos
        from oakvar.lib.util.seq import liftover

        # assert self.crl_writer is not None
        if self.is_chrM(variant):
            needed = self.do_liftover_chrM
        else:
            needed = self.do_liftover
        if needed:
            prelift_wdict = copy(variant)
            prelift_wdict["uid"] = self.uid
            # self.crl_writer.write_data(prelift_wdict)
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
