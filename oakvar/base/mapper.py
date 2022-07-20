class BaseMapper(object):
    """
    BaseMapper is the parent class for Cravat Mapper objects.
    It receives a crv file and writes crx and crg files based on it's child
    mapper's map() function.
    It handles command line arguments, option parsing and file io for the
    mapping process.
    """

    def __init__(self, *inargs, **inkwargs):
        import os
        from time import time
        import pkg_resources
        from ..module.local import get_module_conf

        self.cmd_parser = None
        self.input_path = None
        self.input_dir = None
        self.reader = None
        self.output_dir = None
        self.output_base_fname = None
        self.crx_path = None
        self.crg_path = None
        self.crx_writer = None
        self.crg_writer = None
        self.input_fname = None
        self.slavemode = False
        self.confs = None
        self.postfix = None
        self.primary_transcript_paths = None
        self.args = None
        self.logger = None
        self.error_logger = None
        self.unique_excs = None
        self.written_primary_transc = None
        self._define_main_cmd_args()
        self._define_additional_cmd_args()
        self._parse_cmd_args(inargs, inkwargs)
        if self.args is None:
            return
        self.live = self.args["live"]
        self.t = time()
        self.status_writer = self.args["status_writer"]
        main_fpath = self.args["script_path"]
        main_basename = os.path.basename(main_fpath)
        if "." in main_basename:
            self.module_name = ".".join(main_basename.split(".")[:-1])
        else:
            self.module_name = main_basename
        self.module_dir = os.path.dirname(main_fpath)
        self.mapper_dir = os.path.dirname(main_fpath)
        self.gene_sources = []
        # self.primary_gene_source = None
        self.gene_info = {}
        # self.written_primary_transc = set([])
        self._setup_logger()
        self.conf = get_module_conf(self.module_name, module_type="mapper")
        self.cravat_version = pkg_resources.get_distribution("oakvar").version

    def _define_main_cmd_args(self):
        import argparse

        self.cmd_parser = argparse.ArgumentParser()
        self.cmd_parser.add_argument("input_file", help="Input crv file")
        self.cmd_parser.add_argument(
            "-n", dest="name", help="Name of job. " + "Default is input file name."
        )
        self.cmd_parser.add_argument(
            "-d",
            dest="output_dir",
            help="Output directory. " + "Default is input file directory.",
        )
        self.cmd_parser.add_argument(
            "--confs", dest="confs", default="{}", help="Configuration string"
        )
        self.cmd_parser.add_argument(
            "--seekpos", dest="seekpos", default=None, help=argparse.SUPPRESS
        )
        self.cmd_parser.add_argument(
            "--chunksize", dest="chunksize", default=None, help=argparse.SUPPRESS
        )
        self.cmd_parser.add_argument(
            "--slavemode",
            dest="slavemode",
            action="store_true",
            default=False,
            help=argparse.SUPPRESS,
        )
        self.cmd_parser.add_argument(
            "--postfix", dest="postfix", default="", help=argparse.SUPPRESS
        )
        self.cmd_parser.add_argument(
            "--primary-transcript",
            dest="primary_transcript",
            #nargs="*",
            default=["mane"],
            help='"mane" for MANE transcripts as primary transcripts, or a path to a file of primary transcripts. MANE is default.',
        )
        self.cmd_parser.add_argument(
            "--live", action="store_true", default=False, help=argparse.SUPPRESS
        )
        self.cmd_parser.add_argument(
            "--status_writer", default=None, help=argparse.SUPPRESS
        )

    def _define_additional_cmd_args(self):
        """This method allows sub-classes to override and provide addittional command line args"""
        pass

    def _parse_cmd_args(self, inargs, inkwargs):
        from os.path import abspath, split, exists
        from os import makedirs
        from json import loads
        from ..util.util import get_args

        args = get_args(self.cmd_parser, inargs, inkwargs)
        self.input_path = abspath(args["input_file"]) if args["input_file"] else None
        if self.input_path:
            self.input_dir, self.input_fname = split(self.input_path)
            if args["output_dir"]:
                self.output_dir = args["output_dir"]
            else:
                self.output_dir = self.input_dir
            if not (exists(self.output_dir)):
                makedirs(self.output_dir)
        if hasattr(args, "run_name"):
            self.output_base_fname = args["run_name"]
        else:
            self.output_base_fname = self.input_fname
        self.confs = None
        if args["confs"] is not None:
            confs = args["confs"].lstrip("'").rstrip("'").replace("'", '"')
            self.confs = loads(confs)
        self.slavemode = args["slavemode"]
        self.postfix = args["postfix"]
        self.primary_transcript_paths = [v for v in args["primary_transcript"] if v]
        self.args = args

    def base_setup(self):
        self.setup()
        if self.live == False:
            self._setup_io()

    def setup(self):
        raise NotImplementedError("Mapper must have a setup() method.")

    def end(self):
        pass

    def _setup_logger(self):
        import logging

        self.logger = logging.getLogger("oakvar.mapper")
        if self.input_path:
            self.logger.info("input file: %s" % self.input_path)
        self.error_logger = logging.getLogger("error.mapper")
        self.unique_excs = []

    def _setup_io(self):
        """
        Open input and output files
        Open CravatReader for crv input. Open  CravatWriters for crx, and crg
        output. Open plain file for err output.
        """
        import os
        from ..util.inout import CravatReader
        from ..util.inout import CravatWriter
        from ..consts import crx_def, crx_idx, crg_def, crg_idx

        if (
            self.output_base_fname is None
            or self.postfix is None
            or self.conf is None
            or self.output_dir is None
        ):
            from ..exceptions import SetupError

            raise SetupError()
        # Reader
        if (
            self.args is not None
            and self.args["seekpos"] is not None
            and self.args["chunksize"] is not None
        ):
            self.reader = CravatReader(
                self.input_path,
                seekpos=int(self.args["seekpos"]),
                chunksize=int(self.args["chunksize"]),
            )
        else:
            self.reader = CravatReader(self.input_path)
        # Various output files
        output_toks = self.output_base_fname.split(".")
        if output_toks[-1] == "crv":
            output_toks = output_toks[:-1]
        # .crx
        crx_fname = ".".join(output_toks) + ".crx"
        self.crx_path = os.path.join(self.output_dir, crx_fname)
        if self.slavemode:
            self.crx_path += self.postfix
        self.crx_writer = CravatWriter(self.crx_path)
        self.crx_writer.add_columns(crx_def)
        self.crx_writer.write_definition(self.conf)
        for index_columns in crx_idx:
            self.crx_writer.add_index(index_columns)
        self.crx_writer.write_meta_line("title", self.conf["title"])
        self.crx_writer.write_meta_line("version", self.conf["version"])
        self.crx_writer.write_meta_line("modulename", self.module_name)
        if not self.primary_transcript_paths:
            self.crx_writer.write_meta_line("primary_transcript_paths", "")
        else:
            self.crx_writer.write_meta_line(
                "primary_transcript_paths", ",".join(self.primary_transcript_paths)
            )
        # .crg
        crg_fname = ".".join(output_toks) + ".crg"
        self.crg_path = os.path.join(self.output_dir, crg_fname)
        if self.slavemode:
            self.crg_path += self.postfix
        self.crg_writer = CravatWriter(self.crg_path)
        self.crg_writer.add_columns(crg_def)
        self.crg_writer.write_definition(self.conf)
        for index_columns in crg_idx:
            self.crg_writer.add_index(index_columns)

    def run(self):
        """
        Read crv file and use map() function to convert to crx dict. Write the
        crx dict to the crx file and add information in crx dict to gene_info
        """
        from time import time, asctime, localtime

        self.base_setup()
        start_time = time()
        if (
            self.logger is None
            or self.conf is None
            or self.reader is None
            or not hasattr(self, "map")
        ):
            from ..exceptions import SetupError

            raise SetupError()
        self.logger.info("started: %s" % asctime(localtime(start_time)))
        if self.status_writer is not None:
            self.status_writer.queue_status_update(
                "status", "Started {} ({})".format(self.conf["title"], self.module_name)
            )
        count = 0
        last_status_update_time = time()
        crx_data = None
        output = {}
        for ln, line, crv_data in self.reader.loop_data():
            crx_data = None
            try:
                count += 1
                cur_time = time()
                if self.status_writer is not None:
                    if count % 10000 == 0 or cur_time - last_status_update_time > 3:
                        self.status_writer.queue_status_update(
                            "status", "Running gene mapper: line {}".format(count)
                        )
                        last_status_update_time = cur_time
                if crv_data["alt_base"] == "*":
                    crx_data = crv_data
                    crx_data["all_mappings"] = "{}"
                else:
                    crx_data = self.map(crv_data)  # type: ignore
                # Skip cases where there was no change. Can result if ref_base not in original input
                if crx_data["ref_base"] == crx_data["alt_base"]:
                    continue
            except Exception as e:
                self._log_runtime_error(ln, line, e)
                continue
            if crx_data is not None:
                self.crx_writer.write_data(crx_data)  # type: ignore
                self._add_crx_to_gene_info(crx_data)
        self._write_crg()
        stop_time = time()
        self.logger.info("finished: %s" % asctime(localtime(stop_time)))
        runtime = stop_time - start_time
        self.logger.info("runtime: %6.3f" % runtime)
        if self.status_writer is not None:
            self.status_writer.queue_status_update("status", "Finished gene mapper")
        self.end()
        return output

    def run_as_slave(self, __pos_no__):
        """
        Read crv file and use map() function to convert to crx dict. Write the
        crx dict to the crx file and add information in crx dict to gene_info
        """
        from time import time, asctime, localtime

        self.base_setup()
        if (
            self.args is None
            or self.logger is None
            or self.conf is None
            or self.reader is None
            or self.crx_writer is None
        ):
            from ..exceptions import SetupError

            raise SetupError()
        start_time = time()
        tstamp = asctime(localtime(start_time))
        self.logger.info(f"started: {tstamp} | {self.args['seekpos']}")
        if self.status_writer is not None:
            self.status_writer.queue_status_update(
                "status", "Started {} ({})".format(self.conf["title"], self.module_name)
            )
        count = 0
        last_status_update_time = time()
        crx_data = None
        for ln, line, crv_data in self.reader.loop_data():
            try:
                count += 1
                cur_time = time()
                if self.status_writer is not None:
                    if count % 10000 == 0 or cur_time - last_status_update_time > 3:
                        self.status_writer.queue_status_update(
                            "status", "Running gene mapper: line {}".format(count)
                        )
                        last_status_update_time = cur_time
                if crv_data["alt_base"] == "*":
                    crx_data = crv_data
                    crx_data["all_mappings"] = "{}"
                else:
                    crx_data = self.map(crv_data)  # type: ignore
                if crx_data is None:
                    continue
            except Exception as e:
                self._log_runtime_error(ln, line, e)
            if crx_data is not None:
                self.crx_writer.write_data(crx_data)
                self._add_crx_to_gene_info(crx_data)
        self._write_crg()
        stop_time = time()
        tstamp = asctime(localtime(stop_time))
        self.logger.info(f"finished: {tstamp} | {self.args['seekpos']}")
        runtime = stop_time - start_time
        self.logger.info("runtime: %6.3f" % runtime)
        self.end()

    def _add_crx_to_gene_info(self, crx_data):
        """
        Add information in a crx dict to persistent gene_info dict
        """
        from ..util.inout import AllMappingsParser

        tmap_json = crx_data["all_mappings"]
        # Return if no tmap
        if tmap_json == "":
            return
        tmap_parser = AllMappingsParser(tmap_json)
        for hugo in tmap_parser.get_genes():
            self.gene_info[hugo] = True

    def _write_crg(self):
        """
        Convert gene_info to crg dict and write to crg file
        """
        if self.crg_writer is None:
            return
        from ..consts import crg_def

        sorted_hugos = list(self.gene_info.keys())
        sorted_hugos.sort()
        for hugo in sorted_hugos:
            crg_data = {x["name"]: "" for x in crg_def}
            crg_data["hugo"] = hugo
            self.crg_writer.write_data(crg_data)

    def _log_runtime_error(self, ln, line, e):
        import traceback

        err_str = traceback.format_exc().rstrip()
        if (
            self.logger is not None
            and self.unique_excs is not None
            and err_str not in self.unique_excs
        ):
            self.unique_excs.append(err_str)
            self.logger.error(err_str)
        if self.error_logger is not None:
            self.error_logger.error(
                "\nLINE:{:d}\nINPUT:{}\nERROR:{}\n#".format(ln, line[:-1], str(e))
            )

    async def get_gene_summary_data(self, cf):
        from ..consts import crx_def

        hugos = await cf.exec_db(cf.get_filtered_hugo_list)
        # Below is to fix opening oc 1.8.0 jobs with oc 1.8.1.
        # TODO: Remove it after a while and add 1.8.0 to the db update chain in cmd_util.
        cols = [
            "base__" + coldef["name"]
            for coldef in crx_def
            if coldef["name"] != "cchange"
        ]
        cols.extend(["tagsampler__numsample"])
        data = {}
        rows = await cf.exec_db(cf.get_variant_data_for_cols, cols)
        rows_by_hugo = {}
        for row in rows:
            hugo = row[-1]
            if hugo not in rows_by_hugo:
                rows_by_hugo[hugo] = []
            rows_by_hugo[hugo].append(row)
        for hugo in hugos:
            rows = rows_by_hugo[hugo]
            input_data = {}
            for i in range(len(cols)):
                input_data[cols[i].split("__")[1]] = [row[i] for row in rows]
            if hasattr(self, "summarize_by_gene"):
                out = self.summarize_by_gene(hugo, input_data)  # type: ignore
                data[hugo] = out
        return data

    def live_report_substitute(self, d):
        import re

        if self.conf is None or "report_substitution" not in self.conf:
            return
        rs_dic = self.conf["report_substitution"]
        rs_dic_keys = list(rs_dic.keys())
        for colname in d.keys():
            if colname in rs_dic_keys:
                value = d[colname]
                if colname in ["all_mappings", "all_so"]:
                    for target in list(rs_dic[colname].keys()):
                        value = re.sub(
                            "\\b" + target + "\\b", rs_dic[colname][target], value
                        )
                else:
                    if value in rs_dic[colname]:
                        value = rs_dic[colname][value]
                d[colname] = value
        return d
