class VCF2VCF:
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
        self.update_status_json_flag = None
        self.confs = None
        self.output_path = None
        self.last_status_update_time = None
        self.output_columns = None
        self.log_path = None
        self.log_handler = None
        self.unique_excs = []
        self.conf = {}
        self.module_name = "vcf2vcf"
        self.define_cmd_parser()
        self.parse_cmd_args(inargs, inkwargs)
        self.setup_logger()
        if self.logger and "logging_level" in self.conf:
            self.logger.setLevel(self.conf["logging_level"].upper())

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
        from oakvar.consts import crx_def
        from oakvar.module.local import get_module_conf

        if module_name == mapper:
            mc = crx_def
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
            "--confs", dest="confs", default="{}", help="Configuration string"
        )
        parser.add_argument(
            "-a",
            dest="annotator_names",
            nargs="*",
            help="annotator module names",
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
        from json import loads
        from oakvar.util.util import get_args
        from types import SimpleNamespace

        args = get_args(self.cmd_arg_parser, inargs, inkwargs)
        self.inputs = [os.path.abspath(v) for v in args.get("inputs")]
        self.primary_input_path = os.path.abspath(args.get("inputs")[0])
        self.output_dir = os.path.dirname(self.primary_input_path)
        if args["output_dir"]:
            self.output_dir = args["output_dir"]
        self.update_status_json_flag = True
        self.job_conf_path = args.get("conf")
        self.confs = loads(
            args.get("confs", "{}").lstrip("'").rstrip("'").replace("'", '"')
        )
        self.annotator_names = args.get("annotator_names", [])
        self.mapper_name = args.get("mapper_name")
        self.status_writer = args.get("status_writer")
        self.run_name = args.get("run_name")
        self.args = SimpleNamespace(**args)

    def log_progress(self, lnum):
        if self.last_status_update_time is None:
            return
        if self.conf is None:
            return
        from time import time

        if self.update_status_json_flag and self.status_writer is not None:
            cur_time = time()
            if lnum % 10000 == 0 or cur_time - self.last_status_update_time > 3:
                self.status_writer.queue_status_update(
                    "status",
                    "Running {} ({}): line {}".format(
                        self.conf["title"], self.module_name, lnum
                    ),
                )
                self.last_status_update_time = cur_time

    def run(self):
        from oakvar.util.util import normalize_variant
        from oakvar.module.local import load_modules
        from oakvar.util.util import quiet_print
        from oakvar.util.util import log_variant_exception
        from oakvar.exceptions import BadFormatError
        from os.path import join
        from re import compile

        if not self.mapper_name or not self.inputs:
            return False
        base_re = compile("^[*]|[ATGC]+|[-]+$")
        modules = load_modules(annotators=self.annotator_names, mapper=self.mapper_name)
        col_infos = self.load_col_infos(self.annotator_names, self.mapper_name)
        all_col_names = self.get_all_col_names(col_infos, self.mapper_name)
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
                        f"##INFO=<ID={prefix + '__' + col['name']},Number=A,Type={col['type'].capitalize()},Description=\"{col['title']}\">\n"
                    )
            f.seek(0)
            for line in f:
                if line.startswith("#CHROM"):
                    wf.write(line)
                    break
            read_lnum = 0
            uid = 0
            for l in f:
                read_lnum += 1
                vcf_toks = l[:-1].split("\t")
                chrom = vcf_toks[0]
                pos = int(vcf_toks[1])
                ref = vcf_toks[3]
                alts = vcf_toks[4].split(",")
                if read_lnum % 10000 == 0:
                    quiet_print(
                        f"{read_lnum}: {chrom} {pos} {ref} {vcf_toks[4]}",
                        args=self.args,
                    )
                try:
                    variants = []
                    for alt in alts:
                        if "<" in alt:
                            continue
                        pos, ref, alt = self.trim_variant(pos, ref, alt)
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
                                    e=BadFormatError("Invalid alternate base"),
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
                                variant = normalize_variant(variant)
                                res = modules[self.mapper_name].map(variant)
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
                        if "__" not in col_name:
                            col_name = "base__" + col_name
                        wf.write(col_name + "=" + ",".join(values))
                        if col_name != all_col_names[-1]:
                            wf.write(";")
                    wf.write("\t" + "\t".join(vcf_toks[8:]) + "\n")
                except Exception as e:
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

        self.logger = logging.getLogger("oakvar." + self.module_name)
        # self.log_path = join(self.output_dir, self.run_name + ".log")
        # log_handler = logging.FileHandler(self.log_path, "a")
        # formatter = logging.Formatter(
        #    "%(asctime)s %(name)-20s %(message)s", "%Y/%m/%d %H:%M:%S"
        # )
        # log_handler.setFormatter(formatter)
        # self.logger.addHandler(log_handler)
        self.error_logger = logging.getLogger("error." + self.module_name)
        # if self.run_name != "__dummy__":
        #    error_log_path = join(self.output_dir, self.run_name + ".err")
        #    error_log_handler = logging.FileHandler(error_log_path, "a")
        # else:
        #    error_log_handler = logging.StreamHandler()
        # formatter = logging.Formatter("SOURCE:%(name)-20s %(message)s")
        # error_log_handler.setFormatter(formatter)
        # self.error_logger.addHandler(error_log_handler)
        self.unique_excs = []
        if not self.logger:
            raise LoggerError(module_name=self.module_name)
