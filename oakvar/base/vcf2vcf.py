class VCF2VCF:

    OV_PREFIX: str = "OV_"

    def __init__(self, *inargs, **inkwargs):
        import sys
        from oakvar.exceptions import ModuleLoadingError

        fp = sys.modules[self.__module__].__file__
        if fp is None:
            raise ModuleLoadingError(self.__module__)
        self.primary_input_path = None
        self.output_dir = ""
        self.job_conf_path = None
        self.logger = None
        self.error_logger = None
        self.cmd_arg_parser = None
        self.module_options = None
        self.output_path = None
        self.last_status_update_time = None
        self.output_columns = None
        self.log_path = None
        self.log_handler = None
        self.unique_excs = []
        self.conf = {}
        self.lifter = None
        self.module_name = "vcf2vcf"
        self.define_cmd_parser()
        self.parse_cmd_args(inargs, inkwargs)
        self.setup_logger()
        self.setup_liftover()
        self.serveradmindb = self.args.get("serveradmindb")
        if self.logger and "logging_level" in self.conf:
            self.logger.setLevel(self.conf["logging_level"].upper())

    def setup_liftover(self):
        from pyliftover import LiftOver
        from oakvar.util.admin_util import get_liftover_chain_paths
        from oakvar import get_wgs_reader

        if self.args.get("genome"):
            liftover_chain_paths = get_liftover_chain_paths()
            self.lifter = LiftOver(liftover_chain_paths[self.args.get("genome")])
            self.do_liftover = True
        else:
            self.lifter = None
            self.do_liftover = False
        self.wgsreader = get_wgs_reader(assembly="hg38")

    def liftover(self, chrom, pos, ref, alt):
        from oakvar.exceptions import LiftoverFailure
        from oakvar.util.seq import reverse_complement

        if not self.lifter or not self.wgsreader:
            return None
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

    def liftover_one_pos(self, chrom, pos):
        if not self.lifter:
            return None
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

    def load_col_infos(self, module_names: list, mapper: str):
        col_infos = {}
        col_infos[mapper] = self.get_col_info(mapper, mapper, module_type="mapper")
        for module_name in module_names:
            col_infos[module_name] = self.get_col_info(
                module_name, mapper, module_type="annotator"
            )
        return col_infos

    def get_all_col_names(self, col_infos, mapper: str):
        all_col_names = [
            "uid",
            "chrom",
            "pos",
            "strand",
            "ref_base",
            "alt_base",
            "sample_id",
            "tags",
            "note",
        ]
        all_col_names += [
            v["name"] for v in col_infos[mapper] if v["name"] not in all_col_names
        ]
        for module_name, col_info in col_infos.items():
            if module_name == mapper:
                continue
            all_col_names += [module_name + "__" + v["name"] for v in col_info]
        return all_col_names

    def get_col_info(self, module_name, mapper: str, module_type=None):
        from oakvar.util.util import get_crx_def
        from oakvar.module.local import get_module_conf

        if module_name == mapper:
            mc = get_crx_def()
        else:
            mc = get_module_conf(module_name, module_type=module_type)
            if mc:
                mc = mc["output_columns"]
            else:
                mc = []
        return mc

    def escape_vcf_value(self, v):
        if "%" in v:
            v = v.replace("%", "%25")
        if " " in v:
            v = v.replace(" ", "%20")
        if ":" in v:
            v = v.replace(":", "%3A")
        if ";" in v:
            v = v.replace(";", "%3B")
        if "=" in v:
            v = v.replace("=", "%3D")
        if "," in v:
            v = v.replace(",", "%2C")
        if "\n" in v:
            v = v.replace("\n", "%0A")
        if "\t" in v:
            v = v.replace("\t", "%09")
        if "\r" in v:
            v = v.replace("\r", "%0D")
        if " " in v:
            v = v.replace(" ", "%20")
        return v

    def trim_variant(self, pos, ref, alt):
        if alt is None:
            return pos, ref, alt
        if len(ref) == 1 and len(alt) == 1:
            return pos, ref, alt
        ref = list(ref)
        alt = list(alt)
        adj = 0
        while ref and alt and ref[0] == alt[0]:
            adj += 1
            ref.pop(0)
            alt.pop(0)
        while ref and alt and ref[-1] == alt[-1]:
            ref.pop()
            alt.pop()
        ref = "".join(ref) if ref else "-"
        alt = "".join(alt) if alt else "-"
        return pos + adj, ref, alt

    def _log_exception(self, e, halt=True):
        if self.logger:
            self.logger.exception(e)
        if halt:
            return False
        else:
            return True

    def define_cmd_parser(self):
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument("inputs", help="Input file to be annotated.")
        parser.add_argument(
            "-n", dest="run_name", help="Name of job. Default is input file name."
        )
        parser.add_argument(
            "-d",
            dest="output_dir",
            help="Output directory. " + "Default is input file directory.",
        )
        parser.add_argument("-c", dest="conf", help="Path to optional run conf file.")
        parser.add_argument(
            "--module-options", dest="module-options", default="{}", help="Configuration string"
        )
        parser.add_argument(
            "-a",
            dest="annotator_names",
            nargs="*",
            help="annotator module names",
        )
        parser.add_argument(
            "-l",
            "--liftover",
            dest="genome",
            default=None,
            help="reference genome of input. OakVar will lift over to hg38 if needed.",
        )
        parser.add_argument(
            "-m",
            dest="mapper_name",
            nargs=1,
            help="mapper module name",
        )
        parser.add_argument(
            "--quiet",
            action="store_true",
            dest="quiet",
            default=None,
            help="Silent operation",
        )
        self.cmd_arg_parser = parser

    # Parse the command line arguments
    def parse_cmd_args(self, inargs, inkwargs):
        import os
        from oakvar.util.util import get_args
        from oakvar.util.run import get_module_options

        args = get_args(self.cmd_arg_parser, inargs, inkwargs)
        self.inputs = [os.path.abspath(v) for v in args.get("inputs")]
        self.primary_input_path = os.path.abspath(args.get("inputs")[0])
        self.output_dir = os.path.dirname(self.primary_input_path)
        if args["output_dir"]:
            self.output_dir = args["output_dir"]
        self.job_conf_path = args.get("conf")
        self.module_options = get_module_options(args)
        self.annotator_names = args.get("annotator_names", [])
        self.mapper_name = args.get("mapper_name")
        self.run_name = args.get("run_name")
        self.args = args

    def log_progress(self, lnum):
        from time import time
        from ..util.run import update_status

        if self.last_status_update_time is None:
            return
        if self.conf is None:
            return
        cur_time = time()
        if lnum % 10000 == 0 or cur_time - self.last_status_update_time > 3:
            status = "Running {self.conf['title']} ({self.module_name}): line {lnum}"
            update_status(status, logger=self.logger, serveradmindb=self.serveradmindb)
            self.last_status_update_time = cur_time

    def run(self):
        from oakvar.util.seq import normalize_variant_dict_left
        from oakvar.module.local import load_modules
        from oakvar.util.util import quiet_print
        from oakvar.util.run import log_variant_exception
        from oakvar.exceptions import IgnoredVariant
        from os.path import join
        from re import compile

        if not self.mapper_name or not self.inputs:
            return False
        base_re = compile("^[*]|[ATGC]+|[-]+$")
        modules = load_modules(annotators=self.annotator_names, mapper=self.mapper_name)
        col_infos = self.load_col_infos(self.annotator_names, self.mapper_name)
        all_col_names = self.get_all_col_names(col_infos, self.mapper_name)
        mapper = modules[self.mapper_name]
        output_suffix = ".vcf"
        for p in self.inputs:
            quiet_print(f"processing {p}", args=self.args)
            if self.run_name:
                if len(self.inputs) == 1:
                    outpath = join(self.output_dir, self.run_name + output_suffix)
                else:
                    outpath = join(
                        self.output_dir, p + "." + self.run_name + output_suffix
                    )
            else:
                outpath = p + output_suffix
            f = open(p)
            wf = open(outpath, "w", 1024 * 128)
            f.seek(0)
            for line in f:
                if line.startswith("##"):
                    wf.write(line)
                else:
                    break
            for module_name in [self.mapper_name] + self.annotator_names:
                prefix = "base" if module_name == self.mapper_name else module_name
                col_info = col_infos[module_name]
                for col in col_info:
                    wf.write(
                        f"##INFO=<ID={self.OV_PREFIX}{prefix}__{col['name']},Number=A,Type={col['type'].capitalize()},Description=\"{col['title']}\">\n"
                    )
            f.seek(0)
            for line in f:
                if line.startswith("#CHROM"):
                    wf.write(line)
                    break
            read_lnum = 0
            uid = 0
            for l in f:
                try:
                    read_lnum += 1
                    vcf_toks = l[:-1].split("\t")
                    chrom = vcf_toks[0]
                    if not chrom.startswith("chr"):
                        chrom = "chr" + chrom
                    pos = int(vcf_toks[1])
                    ref = vcf_toks[3]
                    alts = vcf_toks[4].split(",")
                    if read_lnum % 10000 == 0:
                        quiet_print(
                            f"{read_lnum}: {chrom} {pos} {ref} {vcf_toks[4]}",
                            args=self.args,
                        )
                    variants = []
                    for alt in alts:
                        if "<" in alt:
                            continue
                        pos, ref, alt = self.trim_variant(pos, ref, alt)
                        if self.do_liftover:
                            _, pos, ref, alt = self.liftover(chrom, pos, ref, alt)
                        uid += 1
                        variant = {"uid": uid}
                        if ref == alt:
                            pass
                        elif alt == "*":
                            pass
                        else:
                            if not base_re.fullmatch(alt):
                                log_variant_exception(
                                    lnum=read_lnum,
                                    line=l,
                                    unique_excs=self.unique_excs,
                                    logger=self.logger,
                                    error_logger=self.error_logger,
                                    e=IgnoredVariant("Invalid alternate base"),
                                )
                            else:
                                variant = {
                                    "uid": uid,
                                    "chrom": chrom,
                                    "pos": pos,
                                    "strand": "+",
                                    "ref_base": ref,
                                    "alt_base": alt,
                                }
                                variant = normalize_variant_dict_left(variant)
                                res = mapper.map(variant)
                                res = mapper.live_report_substitute(res)
                                if res:
                                    variant.update(res)
                                for module_name in self.annotator_names:
                                    res = modules[module_name].annotate(variant)
                                    if res:
                                        variant.update(
                                            {
                                                module_name + "__" + k: v
                                                for k, v in res.items()
                                            }
                                        )
                        variants.append(variant)
                    wf.write("\t".join(vcf_toks[:7]))
                    if vcf_toks[7] == ".":
                        wf.write("\t")
                    else:
                        wf.write("\t")
                        wf.write(vcf_toks[7])
                        wf.write(";")
                    for col_name in all_col_names:
                        if col_name in [
                            "chrom",
                            "pos",
                            "strand",
                            "ref_base",
                            "alt_base",
                            "sample_id",
                        ]:
                            continue
                        values = []
                        has_value: bool = False
                        for variant in variants:
                            value = variant.get(col_name)
                            if value is None:
                                value = ""
                            else:
                                vt = type(value)
                                if vt == int or vt == float:
                                    value = str(value)
                                else:
                                    if vt != str:
                                        value = str(value)
                                    value = self.escape_vcf_value(value)
                            values.append(value)
                            if value and value != "{}":
                                has_value = True
                        if not has_value:
                            continue
                        if "__" not in col_name:
                            col_name = "base__" + col_name
                        wf.write(self.OV_PREFIX + col_name + "=" + ",".join(values))
                        if col_name != all_col_names[-1]:
                            wf.write(";")
                    wf.write("\t" + "\t".join(vcf_toks[8:]) + "\n")
                except Exception as e:
                    print(e)
                    log_variant_exception(
                        lnum=read_lnum,
                        line=l,
                        unique_excs=self.unique_excs,
                        logger=self.logger,
                        error_logger=self.error_logger,
                        e=e,
                    )
                    if hasattr(e, "halt") and getattr(e, "halt"):
                        break
            f.close()
            wf.close()

    def setup_logger(self):
        import logging
        from oakvar.exceptions import LoggerError

        self.logger = logging.getLogger(f"oakvar.{self.module_name}")
        self.error_logger = logging.getLogger("err." + self.module_name)
        self.unique_excs = []
        if not self.logger:
            raise LoggerError(module_name=self.module_name)
