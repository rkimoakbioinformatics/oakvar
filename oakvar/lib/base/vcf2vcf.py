from typing import Optional
from typing import List


class VCF2VCF:

    OV_PREFIX: str = "OV_"

    def __init__(
        self,
        inputs: List[str] = [],
        run_name: Optional[str] = None,
        output_dir: Optional[str] = None,
        module_options: Optional[str] = None,
        annotator_names: List[str] = [],
        genome: Optional[str] = None,
        mapper_name: Optional[str] = None,
        serveradmindb=None,
        outer=None,
    ):
        import sys
        import os
        from ..exceptions import ModuleLoadingError

        fp = sys.modules[self.__module__].__file__
        if fp is None:
            raise ModuleLoadingError(module_name=self.__module__)
        self.primary_input_path = None
        self.output_dir = ""
        self.logger = None
        self.error_logger = None
        self.cmd_arg_parser = None
        self.module_options = module_options
        self.output_path = None
        self.last_status_update_time = None
        self.output_columns = None
        self.log_path = None
        self.log_handler = None
        self.unique_excs = []
        self.conf = {}
        self.lifter = None
        self.genome = genome
        self.module_name = "vcf2vcf"
        self.inputs = [os.path.abspath(v) for v in inputs]
        self.primary_input_path = os.path.abspath(inputs[0])
        self.output_dir = os.path.dirname(self.primary_input_path)
        if output_dir:
            self.output_dir = output_dir
        self.annotator_names = annotator_names
        self.mapper_name = mapper_name
        self.run_name = run_name
        self.setup_logger()
        self.setup_liftover()
        self.serveradmindb = serveradmindb
        self.outer = outer
        if self.logger and "logging_level" in self.conf:
            self.logger.setLevel(self.conf["logging_level"].upper())

    def setup_liftover(self):
        from ..util.seq import get_lifter
        from ..util.seq import get_wgs_reader

        if self.genome:
            self.lifter = get_lifter(source_assembly=self.genome)
            self.do_liftover = True
        else:
            self.lifter = None
            self.do_liftover = False
        self.wgsreader = get_wgs_reader(assembly="hg38")

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

    def get_col_info(self, module_name, mapper: str, module_type: str = ""):
        from ..util.util import get_crx_def
        from ..module.local import get_module_conf

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
        from os.path import join
        from re import compile
        from ..util.seq import normalize_variant_dict_left
        from ..util.seq import liftover
        from ..module.local import load_modules
        from ..util.run import log_variant_exception
        from ..exceptions import IgnoredVariant

        if not self.mapper_name or not self.inputs:
            return False
        base_re = compile("^[*]|[ATGC]+|[-]+$")
        modules = load_modules(annotators=self.annotator_names, mapper=self.mapper_name)
        col_infos = self.load_col_infos(self.annotator_names, self.mapper_name)
        all_col_names = self.get_all_col_names(col_infos, self.mapper_name)
        mapper = modules[self.mapper_name]
        output_suffix = ".vcf"
        for p in self.inputs:
            if self.outer:
                self.outer.write(f"processing {p}")
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
                        if self.outer:
                            self.outer.write(
                                f"{read_lnum}: {chrom} {pos} {ref} {vcf_toks[4]}\n"
                            )
                    variants = []
                    for alt in alts:
                        if "<" in alt:
                            continue
                        pos, ref, alt = self.trim_variant(pos, ref, alt)
                        if self.do_liftover:
                            _, pos, ref, alt = liftover(
                                chrom, pos, ref, alt, lifter=self.lifter
                            )
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
        from ..exceptions import LoggerError

        self.logger = logging.getLogger(f"oakvar.{self.module_name}")
        self.error_logger = logging.getLogger("err." + self.module_name)
        self.unique_excs = []
        if not self.logger:
            raise LoggerError(module_name=self.module_name)


if __name__ == "__main__":
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
        "--module-options",
        dest="module-options",
        default="{}",
        help="Configuration string",
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
