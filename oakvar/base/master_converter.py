STDIN = "stdin"


class VTracker:
    """This helper class is used to identify the unique variants from the input
    so the crv file will not contain multiple copies of the same variant.
    """

    def __init__(self, deduplicate=True):
        from collections import defaultdict

        self.var_by_chrom = defaultdict(dict)
        self.current_UID = 1
        self.deduplicate = deduplicate

    # Add a variant - Returns true if the variant is a new unique variant, false
    # if it is a duplicate.  Also returns the UID.
    def addVar(self, chrom, pos, ref, alt):
        if not self.deduplicate:
            self.current_UID += 1
            return True, self.current_UID - 1

        change = ref + ":" + alt

        chr_dict = self.var_by_chrom[chrom]
        if pos not in chr_dict:
            # we have not seen this position before, add the position and change
            chr_dict[pos] = {}
            chr_dict[pos][change] = self.current_UID
            self.current_UID += 1
            return True, chr_dict[pos][change]
        else:
            variants = chr_dict[pos]
            if change not in variants:
                # we have the position but not this base change, add it.
                chr_dict[pos][change] = self.current_UID
                self.current_UID = self.current_UID + 1
                return True, chr_dict[pos][change]
            else:
                # this variant has been seen before.
                return False, chr_dict[pos][change]


class MasterConverter(object):

    ALREADYCRV = 2

    def __init__(self, *inargs, **inkwargs):
        from oakvar.consts import crs_def
        from oakvar import get_wgs_reader

        self.logger = None
        self.crv_writer = None
        self.crs_writer = None
        self.crm_writer = None
        self.crl_writer = None
        self.primary_converter = None
        self.converters = {}
        self.possible_formats = []
        self.ready_to_convert = False
        self.input_format = None
        self.pipeinput = False
        self.input_paths = None
        self.input_dir = None
        self.input_path_dict = None
        self.input_path_dict2 = None
        self.output_dir = None
        self.output_base_fname = None
        self.status_fpath = None
        self.conf = None
        self.unique_variants = None
        self.status_writer = None
        self.error_logger = None
        self.unique_excs = []
        self.wpath = None
        self.err_path = None
        self.crm_path = None
        self.crs_path = None
        self.crl_path = None
        self.cur_file = None
        self.do_liftover = None
        self.do_liftover_chrM = None
        self.lifter = None
        self.file_error_lines = 0
        self.total_error_lines = 0
        self.chromdict = {
            "chrx": "chrX",
            "chry": "chrY",
            "chrMT": "chrM",
            "chrMt": "chrM",
            "chr23": "chrX",
            "chr24": "chrY",
        }
        self._parse_cmd_args(inargs, inkwargs)
        self._setup_logger()
        self.vtracker = VTracker(deduplicate=not (self.unique_variants))
        self.wgsreader = get_wgs_reader(assembly="hg38")
        self.crs_def = crs_def.copy()

    def get_genome_assembly(self, converter):
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
            self.do_liftover_chrM = converter.get_do_liftover_chrM(genome_assembly, f, self.do_liftover)
        else:
            self.do_liftover_chrM = self.do_liftover

    def setup_lifter(self, genome_assembly):
        from oakvar.util.admin_util import get_liftover_chain_paths
        from oakvar.exceptions import InvalidGenomeAssembly
        from pyliftover import LiftOver
        liftover_chain_paths = get_liftover_chain_paths()
        if genome_assembly not in liftover_chain_paths:
            raise InvalidGenomeAssembly(genome_assembly)
        self.lifter = LiftOver(liftover_chain_paths[genome_assembly])

    def _parse_cmd_args(self, inargs, inkwargs):
        """Parse the arguments in sys.argv"""
        import sys
        from json import loads
        from argparse import ArgumentParser, SUPPRESS
        from os.path import abspath, dirname, exists, basename, join
        from os import makedirs
        from oakvar.exceptions import ExpectedException
        from oakvar.util.util import get_args
        from oakvar.exceptions import SetupError

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
        if len(sys.argv) > 1 and len(inargs) == 0:
            inargs = [sys.argv]
        parsed_args = get_args(parser, inargs, inkwargs)
        self.input_format = None
        if parsed_args["format"]:
            self.input_format = parsed_args["format"]
        if parsed_args["inputs"] is None:
            raise ExpectedException("Input files are not given.")
        self.pipeinput = False
        if (
            parsed_args["inputs"] is not None
            and len(parsed_args["inputs"]) == 1
            and parsed_args["inputs"][0] == "-"
        ):
            self.pipeinput = True
        self.input_paths = []
        if self.pipeinput == False:
            self.input_paths = [abspath(x) for x in parsed_args["inputs"] if x != "-"]
        else:
            self.input_paths = [f"./{STDIN}"]
        self.input_dir = dirname(self.input_paths[0])
        self.input_path_dict = {}
        self.input_path_dict2 = {}
        if self.pipeinput == False:
            for i in range(len(self.input_paths)):
                self.input_path_dict[i] = self.input_paths[i]
                self.input_path_dict2[self.input_paths[i]] = i
        else:
            self.input_path_dict[0] = self.input_paths[0]
            self.input_path_dict2[STDIN] = 0
        self.output_dir = None
        if parsed_args["output_dir"]:
            self.output_dir = parsed_args["output_dir"]
        else:
            self.output_dir = self.input_dir
        if self.output_dir is None:
            raise SetupError("output directory")
        if not (exists(self.output_dir)):
            makedirs(self.output_dir)
        self.output_base_fname = None
        if parsed_args["name"]:
            self.output_base_fname = parsed_args["name"]
        else:
            self.output_base_fname = basename(self.input_paths[0])
        self.given_input_assembly = parsed_args["genome"]
        self.status_fpath = join(
            self.output_dir, self.output_base_fname + ".status.json"
        )
        self.conf = {}
        if parsed_args["confs"] is not None:
            confs = parsed_args["confs"].lstrip("'").rstrip("'").replace("'", '"')
            self.conf = loads(confs)
        if "conf" in parsed_args:
            self.conf.update(parsed_args["conf"])
        self.unique_variants = parsed_args["unique_variants"]
        if "status_writer" in parsed_args:
            self.status_writer = parsed_args["status_writer"]
        self.args = parsed_args

    def open_input_file(self, input_path):
        import gzip
        from oakvar.util.util import detect_encoding

        encoding = detect_encoding(input_path)
        if input_path.endswith(".gz"):
            f = gzip.open(input_path, mode="rt", encoding=encoding)
        else:
            f = open(input_path, encoding=encoding)
        return f

    def first_input_file(self):
        import gzip
        from sys import stdin
        from oakvar.util.util import detect_encoding
        from oakvar.exceptions import NoInput

        if self.input_paths is None:
            raise NoInput()
        if self.pipeinput == False:
            input_path = self.input_paths[0]
            encoding = detect_encoding(input_path)
            if input_path.endswith(".gz"):
                f = gzip.open(input_path, mode="rt", encoding=encoding)
            else:
                f = open(input_path, encoding=encoding)
        else:
            f = stdin
        return f

    def setup(self):
        """Do necesarry pre-run tasks"""
        if self.ready_to_convert:
            return
        # Read in the available converters
        self._initialize_converters()
        # Select the converter that matches the input format
        self._select_primary_converter()
        # Open the output files
        self._open_output_files()
        self.ready_to_convert = True

    def _setup_logger(self):
        """Open a log file and set up log handler"""
        from logging import getLogger
        from time import asctime

        self.logger = getLogger("oakvar.converter")
        self.logger.info("started: %s" % asctime())
        self.error_logger = getLogger("err.converter")
        self.unique_excs = []

    def _initialize_converters(self):
        from oakvar.exceptions import ExpectedException
        from oakvar.module.local import get_local_module_infos_of_type
        from oakvar.exceptions import InvalidModule
        from oakvar.util.util import load_class

        for module_info in get_local_module_infos_of_type("converter").values():
            cls = load_class(module_info.script_path)
            converter = cls()
            converter.script_path = module_info.script_path
            if not hasattr(converter, "format_name"):
                raise InvalidModule(module_info.name)
            converter.module_name = module_info.name
            if converter.format_name not in self.converters:
                self.converters[converter.format_name] = converter
            else:
                err_msg = (
                    "Cannot load two converters for format %s" % converter.format_name
                )
                raise ExpectedException(err_msg)
        self.possible_formats = list(self.converters.keys())

    def _select_primary_converter(self):
        from oakvar.exceptions import InvalidInputFormat
        from oakvar.exceptions import LoggerError
        from oakvar.exceptions import NoInput
        from logging import getLogger

        if self.logger is None:
            raise LoggerError()
        if self.input_format is not None:
            if self.input_format not in self.possible_formats:
                raise InvalidInputFormat(self.input_format)
        else:
            if self.pipeinput == False:
                valid_formats = []
                first_file = self.first_input_file()
                first_file.seek(0)
                for converter_name, converter in self.converters.items():
                    try:
                        check_success = converter.check_format(first_file)
                    except:
                        check_success = False
                    first_file.seek(0)
                    if check_success:
                        valid_formats.append(converter_name)
                if len(valid_formats) == 0:
                    raise InvalidInputFormat(f"no converter for input found")
                elif len(valid_formats) > 1:
                    raise InvalidInputFormat(f"ambiguous {','.join(valid_formats)}")
                else:
                    self.input_format = valid_formats[0]
            else:
                if self.input_format is None:
                    raise InvalidInputFormat(
                        f"--input-format should be given with pipe input"
                    )
        self.primary_converter = self.converters[self.input_format]
        self.set_converter_properties(self.primary_converter)
        if self.input_paths is None:
            raise NoInput()
        if self.pipeinput == False:
            if len(self.input_paths) > 1:
                for fn in self.input_paths[1:]:
                    f = self.open_input_file(fn)
                    if not self.primary_converter.check_format(f):
                        raise InvalidInputFormat("inconsistent input formats")
        self.logger.info(
            f"version: {self.primary_converter.module_name}=={self.primary_converter.version} {self.primary_converter.script_path}"
        )
        self.error_logger = getLogger("err." + self.primary_converter.module_name)

    def set_converter_properties(self, converter):
        from oakvar.exceptions import SetupError
        from oakvar.module.local import get_module_code_version

        if self.primary_converter is None or self.conf is None:
            raise SetupError()
        converter.output_dir = self.output_dir
        converter.run_name = self.output_base_fname
        module_name = self.primary_converter.format_name + "-converter"
        converter.module_name = module_name
        converter.version = get_module_code_version(converter.module_name)
        if module_name in self.conf:
            if hasattr(converter, "conf") == False:
                converter.conf = {}
            converter.conf.update(self.conf[module_name])

    def _open_output_files(self):
        from oakvar.exceptions import SetupError

        if (
            self.output_base_fname is None
            or self.primary_converter is None
            or self.output_dir is None
        ):
            raise SetupError()
        from oakvar.consts import (
            crv_def,
            crv_idx,
            crm_def,
            crm_idx,
            crs_idx,
            crl_def,
        )
        from oakvar.util.inout import FileWriter
        from os.path import join

        # Setup writer
        self.wpath = join(self.output_dir, self.output_base_fname + ".crv")
        self.crv_writer = FileWriter(self.wpath)
        self.crv_writer.add_columns(crv_def)
        self.crv_writer.write_definition()
        for index_columns in crv_idx:
            self.crv_writer.add_index(index_columns)
        self.crv_writer.wf.write(
            "#input_format={}\n".format(self.primary_converter.format_name)
        )
        # Setup err file
        self.err_path = join(self.output_dir, self.output_base_fname + ".converter.err")
        # Setup crm line mappings file
        self.crm_path = join(self.output_dir, self.output_base_fname + ".crm")
        self.crm_writer = FileWriter(self.crm_path)
        self.crm_writer.add_columns(crm_def)
        self.crm_writer.write_definition()
        for index_columns in crm_idx:
            self.crm_writer.add_index(index_columns)
        self.crm_writer.write_input_paths(self.input_path_dict)
        # Setup crs sample file
        self.crs_path = join(self.output_dir, self.output_base_fname + ".crs")
        self.crs_writer = FileWriter(self.crs_path)
        self.crs_writer.add_columns(self.crs_def)
        if hasattr(self.primary_converter, "addl_cols"):
            self.crs_writer.add_columns(self.primary_converter.addl_cols, append=True)
            self.crs_def.extend(self.primary_converter.addl_cols)
        self.crs_writer.write_definition()
        for index_columns in crs_idx:
            self.crs_writer.add_index(index_columns)
        self.crl_path = join(
            self.output_dir,
            ".".join([self.output_base_fname, "original_input", "var"]),
        )
        self.crl_writer = FileWriter(self.crl_path)
        self.crl_writer.add_columns(crl_def)
        self.crl_writer.write_definition()
        self.crl_writer.write_names("original_input", "Original Input", "")

    def log_input_and_genome_assembly(self, input_path, genome_assembly):
        if not self.logger:
            return
        if self.pipeinput:
            self.logger.info(f"input file: {STDIN}")
        else:
            self.logger.info(f"input file: {input_path}")
        self.logger.info("input format: %s" % self.input_format)
        self.logger.info(f"genome_assembly: {genome_assembly}")

    def run(self):
        """Convert input file to a .crv file using the primary converter."""
        from sys import stdin
        from os.path import basename
        from time import time, asctime, localtime
        from copy import copy
        from re import compile
        from oakvar.exceptions import IgnoredVariant, NoVariantError
        from oakvar.base.converter import BaseConverter
        from oakvar.exceptions import SetupError
        from oakvar.exceptions import LoggerError
        from oakvar.exceptions import InvalidModule
        from oakvar.util.seq import normalize_variant_left

        self.setup()
        if (
            self.wgsreader is None
            or self.crv_writer is None
            or self.crl_writer is None
            or self.crm_writer is None
            or self.crs_writer is None
            or self.input_path_dict2 is None
            or self.primary_converter is None
        ):
            raise SetupError()
        if self.logger is None:
            raise LoggerError()
        if not hasattr(self.primary_converter, "format_name"):
            if hasattr(self.primary_converter, "module_name"):
                raise InvalidModule(self.primary_converter.module_name)
            else:
                raise InvalidModule("unknown module")
        start_time = time()
        if self.status_writer is not None:
            self.status_writer.queue_status_update(
                "status",
                "Started {} ({})".format(
                    "Converter", self.primary_converter.format_name
                ),  # type: ignore
            )
        last_status_update_time = time()
        if self.input_paths is None:
            raise SetupError()
        multiple_files = len(self.input_paths) > 1
        fileno = 0
        total_lnum = 0
        base_re = compile("^[ATGC]+|[-]+$")
        write_lnum = 0
        genome_assemblies = set()
        for fn in self.input_paths:
            self.cur_file = fn
            if self.pipeinput:
                f = stdin
            else:
                f = self.open_input_file(fn)
            if self.pipeinput == True:
                fname = STDIN
            else:
                fname = f.name
            fileno += 1
            converter = self.primary_converter.__class__()
            if converter is None:
                raise SetupError()
            self.set_converter_properties(converter)
            converter.setup(f)  # type: ignore
            genome_assembly = self.get_genome_assembly(converter)
            genome_assemblies.add(genome_assembly)
            self.log_input_and_genome_assembly(fn, genome_assembly)
            self.set_do_liftover(genome_assembly, converter, f)
            if self.do_liftover or self.do_liftover_chrM:
                self.setup_lifter(genome_assembly)
            if self.pipeinput == False:
                f.seek(0)
            if self.pipeinput:
                cur_fname = STDIN
            else:
                cur_fname = basename(f.name)
            last_read_lnum = None
            self.file_error_lines = 0
            for read_lnum, l, all_wdicts in converter.convert_file(  # type: ignore
                f, exc_handler=self._log_conversion_error
            ):
                samp_prefix = cur_fname
                last_read_lnum = read_lnum
                try:
                    # all_wdicts is a list, since one input line can become
                    # multiple output lines. False is returned if converter
                    # decides line is not an input line.
                    if all_wdicts is BaseConverter.IGNORE:
                        continue
                    total_lnum += 1
                    if all_wdicts:
                        UIDMap = []
                        no_unique_var = 0
                        for wdict in all_wdicts:
                            chrom = wdict["chrom"]
                            pos = wdict["pos"]
                            if not chrom:
                                e = IgnoredVariant("No chromosome")
                                e.traceback = False
                                raise e
                            if not chrom.startswith("chr"):
                                chrom = "chr" + chrom
                            wdict["chrom"] = self.chromdict.get(chrom, chrom)
                            if multiple_files:
                                if wdict["sample_id"]:
                                    wdict["sample_id"] = "__".join(
                                        [samp_prefix, wdict["sample_id"]]
                                    )
                                else:
                                    wdict["sample_id"] = samp_prefix
                            if "ref_base" not in wdict or wdict["ref_base"] in ["", "."]:
                                wdict["ref_base"] = self.wgsreader.get_bases(
                                    chrom, int(wdict["pos"])
                                ).upper()
                            else:
                                ref_base = wdict["ref_base"]
                                if ref_base == "" and wdict["alt_base"] not in [
                                    "A",
                                    "T",
                                    "C",
                                    "G",
                                ]:
                                    e = IgnoredVariant(
                                        "Reference base required for non SNV"
                                    )
                                    e.traceback = False
                                    raise e
                                elif ref_base is None or ref_base == "":
                                    wdict["ref_base"] = self.wgsreader.get_bases(
                                        chrom, int(pos)
                                    )
                            if "genotype" in wdict and "." in wdict["genotype"]:
                                wdict["genotype"] = wdict["genotype"].replace(".", wdict["ref_base"])
                            prelift_wdict = copy(wdict)
                            self.perform_liftover_if_needed(wdict)
                            if not base_re.fullmatch(wdict["ref_base"]):
                                raise IgnoredVariant("Invalid reference base")
                            if not base_re.fullmatch(wdict["alt_base"]):
                                raise IgnoredVariant("Invalid alternate base")
                            p, r, a = (
                                int(wdict["pos"]),
                                wdict["ref_base"],
                                wdict["alt_base"],
                            )
                            (
                                new_pos,
                                new_ref,
                                new_alt,
                            ) = normalize_variant_left("+", p, r, a)
                            wdict["pos"] = new_pos
                            wdict["ref_base"] = new_ref
                            wdict["alt_base"] = new_alt
                            unique, UID = self.vtracker.addVar(
                                wdict["chrom"], new_pos, new_ref, new_alt
                            )
                            wdict["uid"] = UID
                            if wdict["ref_base"] == wdict["alt_base"]:
                                raise NoVariantError()
                            if unique:
                                write_lnum += 1
                                self.crv_writer.write_data(wdict)
                                prelift_wdict["uid"] = UID
                                self.crl_writer.write_data(prelift_wdict)
                                # addl_operation errors shouldnt prevent variant from writing
                                try:
                                    converter.addl_operation_for_unique_variant(  # type: ignore
                                        wdict, no_unique_var
                                    )
                                except Exception as e:
                                    self._log_conversion_error(
                                        read_lnum, l, e, full_line_error=False
                                    )
                                no_unique_var += 1
                            if UID not in UIDMap:
                                # For this input line, only write to the .crm if the UID has not yet been written to the map file.
                                self.crm_writer.write_data(
                                    {
                                        "original_line": read_lnum,
                                        "tags": wdict["tags"],
                                        "uid": UID,
                                        "fileno": f"{self.input_path_dict2[fname]}",
                                    }
                                )
                                UIDMap.append(UID)
                            self.crs_writer.write_data(wdict)
                    else:
                        raise IgnoredVariant("No valid alternate allele was found in any samples.")
                except Exception as e:
                    self._log_conversion_error(read_lnum, l, e)
                    continue
            f.close()
            cur_time = time()
            if total_lnum % 10000 == 0 or cur_time - last_status_update_time > 3:
                if self.status_writer is not None:
                    self.status_writer.queue_status_update(
                        "status",
                        "Running {} ({}): line {}".format(
                            "Converter", cur_fname, last_read_lnum
                        ),
                    )
                last_status_update_time = cur_time
            self.logger.info("error lines: %d" % self.file_error_lines)
        self._close_files()
        self.end()
        self.logger.info("total error lines: %d" % self.total_error_lines)
        if self.status_writer is not None:
            self.status_writer.queue_status_update("num_input_var", total_lnum)
            self.status_writer.queue_status_update("num_unique_var", write_lnum)
            self.status_writer.queue_status_update("num_error_input", self.total_error_lines)
        end_time = time()
        self.logger.info("finished: %s" % asctime(localtime(end_time)))
        runtime = round(end_time - start_time, 3)
        self.logger.info("num input lines: {}".format(total_lnum))
        self.logger.info("runtime: %s" % runtime)
        if self.status_writer is not None:
            self.status_writer.queue_status_update(
                "status",
                "Finished {} ({})".format(
                    "Converter", self.primary_converter.format_name
                ),
            )
        return total_lnum, self.primary_converter.format_name, genome_assemblies

    def perform_liftover_if_needed(self, wdict):
        if self.is_chrM(wdict):
            needed = self.do_liftover_chrM
        else:
            needed = self.do_liftover
        if needed:
            (
                wdict["chrom"],
                wdict["pos"],
                wdict["ref_base"],
                wdict["alt_base"],
            ) = self.liftover(
                wdict["chrom"],
                int(wdict["pos"]),
                wdict["ref_base"],
                wdict["alt_base"],
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

    def _log_conversion_error(self, ln, line, e, full_line_error=True):
        """Log exceptions thrown by primary converter.
        All exceptions are written to the .err file with the exception type
        and message. Exceptions are also written to the log file once, with the
        traceback.
        """
        from oakvar.exceptions import IgnoredVariant
        _ = line
        if not self.logger or not self.error_logger:
            from oakvar.exceptions import LoggerError

            raise LoggerError()
        from traceback import format_exc

        if full_line_error:
            self.file_error_lines += 1
            self.total_error_lines += 1
        err_str = format_exc().rstrip()
        if err_str not in self.unique_excs:
            self.unique_excs.append(err_str)
            if isinstance(e, IgnoredVariant) or (hasattr(e, "traceback") and e.traceback == False):
                pass
            else:
                self.logger.error(err_str)
        self.error_logger.error(f"{self.cur_file}:{ln}\t{str(e)}")
        # self.error_logger.error(
        #    "\nLINE:{:d}\nINPUT:{}\nERROR:{}\n#".format(ln, line[:-1], str(e))
        # )

    def _close_files(self):
        """Close the input and output files."""
        if self.crv_writer is not None:
            self.crv_writer.close()
        if self.crm_writer is not None:
            self.crm_writer.close()
        if self.crs_writer is not None:
            self.crs_writer.close()

    def end(self):
        pass


def main():
    master_converter = MasterConverter()
    master_converter.run()


if __name__ == "__main__":
    master_converter = MasterConverter()
    master_converter.run()
