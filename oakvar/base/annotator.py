class BaseAnnotator(object):

    from ..consts import crv_def, crx_def, crg_def

    valid_levels = ["variant", "gene"]
    valid_input_formats = ["crv", "crx", "crg"]
    id_col_defs = {"variant": crv_def[0], "gene": crg_def[0]}
    default_input_columns = {
        "crv": [x["name"] for x in crv_def],
        "crx": [x["name"] for x in crx_def],
        "crg": [x["name"] for x in crg_def],
    }
    required_conf_keys = ["level", "output_columns"]

    def __init__(self, *inargs, **inkwargs):
        import os
        import sys
        from ..util.util import get_args
        from ..consts import cannonical_chroms
        from ..module.local import get_module_conf
        from ..exceptions import ModuleLoadingError

        fp = sys.modules[self.__module__].__file__
        if fp is None:
            raise ModuleLoadingError(self.__module__)
        main_fpath = os.path.abspath(fp)
        self.primary_input_path = None
        self.secondary_paths = {}
        self.output_dir = None
        self.output_basename = None
        self.plain_output = None
        self.job_conf_path = None
        self.logger = None
        self.error_logger = None
        self.dbconn = None
        self.cursor = None
        self.cmd_arg_parser = None
        self.update_status_json_flag = None
        self.confs = None
        self.json_colnames = None
        self.primary_input_reader = None
        self.output_path = None
        self.last_status_update_time = None
        self.output_columns = None
        self.secondary_readers = {}
        self.output_writer = None
        self.invalid_path = None
        self.log_path = None
        self.unique_excs = []
        self.log_handler = None
        self._define_cmd_parser()
        self.args = get_args(self.cmd_arg_parser, inargs, inkwargs)
        self.parse_cmd_args(inargs, inkwargs)
        if hasattr(self.args, "status_writer") == False:
            self.status_writer = None
        else:
            self.status_writer = self.args["status_writer"]
        if hasattr(self.args, "live") == False:
            live = False
        else:
            live = self.args["live"]
        self.supported_chroms = set(cannonical_chroms)
        if live:
            return
        main_basename = os.path.basename(main_fpath)
        if "." in main_basename:
            self.module_name = ".".join(main_basename.split(".")[:-1])
        else:
            self.module_name = main_basename
        self.annotator_name = self.module_name
        self.module_dir = os.path.dirname(main_fpath)
        self.annotator_dir = os.path.dirname(main_fpath)
        self.data_dir = os.path.join(self.module_dir, "data")
        # Load command line opts
        self._setup_logger()
        self.conf = get_module_conf(self.module_name, module_type="annotator")
        if self.conf is None:
            from ..exceptions import ModuleLoadingError

            raise ModuleLoadingError(self.module_name)
        self._verify_conf()
        self._id_col_name = self.conf["output_columns"][0]["name"]
        if self.logger is None:
            from ..exceptions import LoggerError

            raise LoggerError(module_name=self.module_name)
        if "logging_level" in self.conf:
            self.logger.setLevel(self.conf["logging_level"].upper())
        if "title" in self.conf:
            self.annotator_display_name = self.conf["title"]
        else:
            self.annotator_display_name = os.path.basename(self.module_dir).upper()
        if "version" in self.conf:
            self.annotator_version = self.conf["version"]
        else:
            self.annotator_version = ""

    def summarize_by_gene(self, __hugo__, __input_data__):
        pass

    def _log_exception(self, e, halt=True):
        if self.logger:
            self.logger.exception(e)
        if halt:
            return False
        else:
            return True

    def _verify_conf(self):
        if self.conf is None:
            from ..exceptions import SetupError

            raise SetupError(self.module_name)
        from ..exceptions import ConfigurationError

        for k in self.required_conf_keys:
            if k not in self.conf:
                err_msg = 'Required key "%s" not found in configuration' % k
                raise ConfigurationError(err_msg)
        if self.conf["level"] in self.valid_levels:
            self.conf["output_columns"] = [
                self.id_col_defs[self.conf["level"]]
            ] + self.conf["output_columns"]
        else:
            err_msg = "%s is not a valid level. Valid levels are %s" % (
                self.conf["level"],
                ", ".join(self.valid_levels),
            )
            raise ConfigurationError(err_msg)
        if "input_format" in self.conf:
            if self.conf["input_format"] not in self.valid_input_formats:
                err_msg = "Invalid input_format %s, select from %s" % (
                    self.conf["input_format"],
                    ", ".join(self.valid_input_formats),
                )
        else:
            if self.conf["level"] == "variant":
                self.conf["input_format"] = "crv"
            elif self.conf["level"] == "gene":
                self.conf["input_format"] = "crg"
        if "input_columns" in self.conf:
            id_col_name = self.id_col_defs[self.conf["level"]]["name"]
            if id_col_name not in self.conf["input_columns"]:
                self.conf["input_columns"].append(id_col_name)
        else:
            self.conf["input_columns"] = self.default_input_columns[
                self.conf["input_format"]
            ]

    def _define_cmd_parser(self):
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument("input_file", help="Input file to be annotated.")
        parser.add_argument(
            "-s",
            action="append",
            dest="secondary_inputs",
            help="Secondary inputs. " + "Format as <module_name>:<path>",
        )
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
            "-p",
            "--plainoutput",
            action="store_true",
            dest="plainoutput",
            help="Skip column definition writing",
        )
        parser.add_argument(
            "--confs", dest="confs", default="{}", help="Configuration string"
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
        import json
        import re
        from ..util.util import get_args

        args = get_args(self.cmd_arg_parser, inargs, inkwargs)
        self.primary_input_path = os.path.abspath(args["input_file"])
        if args["secondary_inputs"]:
            for secondary_def in args["secondary_inputs"]:
                sec_name, sec_path = re.split(r"(?<!\\)=", secondary_def)
                self.secondary_paths[sec_name] = os.path.abspath(sec_path)
        self.output_dir = os.path.dirname(self.primary_input_path)
        if args["output_dir"]:
            self.output_dir = args["output_dir"]
        self.plain_output = args["plainoutput"]
        if "run_name" in args and args["run_name"] is not None:
            self.output_basename = args["run_name"]
        else:
            self.output_basename = os.path.basename(self.primary_input_path)
            if self.output_basename.endswith(".crx"):
                self.output_basename = self.output_basename[:-4]
        if self.output_basename != "__dummy__":
            self.update_status_json_flag = True
        else:
            self.update_status_json_flag = False
        if hasattr(args, "conf"):
            self.job_conf_path = args["conf"]
        self.confs = None
        if hasattr(args, "confs") and args["confs"] is not None:
            confs = args["confs"].lstrip("'").rstrip("'").replace("'", '"')
            self.confs = json.loads(confs)
        self.args = args

    def handle_jsondata(self, output_dict):
        import json

        if self.json_colnames is None:
            return
        for colname in self.json_colnames:
            json_data = output_dict.get(colname, None)
            if json_data is not None:
                json_data = json.dumps(json_data)
            output_dict[colname] = json_data
        return output_dict

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

    def is_star_allele(self, input_data):
        if self.conf is None:
            return
        return self.conf["level"] == "variant" and input_data.get("alt_base", "") == "*"

    def should_skip_chrom(self, input_data):
        if self.conf is None:
            return
        return (
            self.conf["level"] == "variant"
            and not input_data.get("chrom") in self.supported_chroms
        )

    def fill_empty_output(self, output_dict):
        if self.conf is None:
            return
        for output_col in self.conf["output_columns"]:
            col_name = output_col["name"]
            if col_name not in output_dict:
                output_dict[col_name] = ""
        return output_dict

    def make_json_colnames(self):
        if self.output_columns is None:
            return
        self.json_colnames = []
        for col in self.output_columns:
            if "table" in col and col["table"] == True:
                self.json_colnames.append(col["name"])

    # Runs the annotator.
    def run(self):
        if self.conf is None:
            return
        if self.logger is None:
            return
        from time import time, asctime, localtime
        from ..util.util import quiet_print

        if self.update_status_json_flag and self.status_writer is not None:
            self.status_writer.queue_status_update(
                "status", "Started {} ({})".format(self.conf["title"], self.module_name)
            )
        try:
            start_time = time()
            self.logger.info("started: %s" % asctime(localtime(start_time)))
            quiet_print(
                "        {}: started at {}".format(
                    self.module_name, asctime(localtime(start_time))
                ),
                self.args,
            )
            self.base_setup()
            self.last_status_update_time = time()
            self.output_columns = self.conf["output_columns"]
            self.make_json_colnames()
            for lnum, line, input_data, secondary_data in self._get_input():
                try:
                    self.log_progress(lnum)
                    # * allele and undefined non-canonical chroms are skipped.
                    if self.is_star_allele(input_data) or self.should_skip_chrom(
                        input_data
                    ):
                        continue
                    output_dict = None
                    if secondary_data == {}:
                        output_dict = self.annotate(input_data)
                    else:
                        output_dict = self.annotate(
                            input_data, secondary_data=secondary_data
                        )
                    # This enables summarizing without writing for now.
                    if output_dict is None:
                        continue
                    # Handles empty table-format column data.
                    output_dict = self.handle_jsondata(output_dict)
                    # Preserves the first column
                    if output_dict:
                        output_dict[self._id_col_name] = input_data[self._id_col_name]
                    # Fill absent columns with empty strings
                    output_dict = self.fill_empty_output(output_dict)
                    # Writes output.
                    if self.output_writer:
                        self.output_writer.write_data(output_dict)
                except Exception as e:
                    self._log_runtime_exception(lnum, line, input_data, e)
            # This does summarizing.
            self.postprocess()
            self.base_cleanup()
            end_time = time()
            self.logger.info("finished: {0}".format(asctime(localtime(end_time))))
            quiet_print(
                "        {}: finished at {}".format(
                    self.module_name, asctime(localtime(end_time))
                ),
                self.args,
            )
            run_time = end_time - start_time
            self.logger.info("runtime: {0:0.3f}s".format(run_time))
            quiet_print(
                "        {}: runtime {:0.3f}s".format(self.module_name, run_time),
                self.args,
            )
            if self.update_status_json_flag and self.status_writer is not None:
                self.status_writer.queue_status_update(
                    "status",
                    "Finished {} ({})".format(self.conf["title"], self.module_name),
                )
        except Exception as e:
            self._log_exception(e)
        if hasattr(self, "log_handler") and self.log_handler:
            self.log_handler.close()

    def postprocess(self):
        pass

    async def get_gene_summary_data(self, cf):
        hugos = await cf.exec_db(cf.get_filtered_hugo_list)
        output_columns = await cf.exec_db(
            cf.get_stored_output_columns, self.module_name
        )
        cols = [
            self.module_name + "__" + coldef["name"]
            for coldef in output_columns
            if coldef["name"] != "uid"
        ]
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
            out = self.summarize_by_gene(hugo, input_data)
            data[hugo] = out
        return data

    def _log_runtime_exception(self, lnum, line, __input_data__, e):
        import traceback

        err_str = traceback.format_exc().rstrip()
        lines = err_str.split("\n")
        last_line = lines[-1]
        err_str_log = "\n".join(lines[:-1]) + "\n" + ":".join(last_line.split(":")[:2])
        if err_str_log not in self.unique_excs:
            self.unique_excs.append(err_str_log)
            if self.logger:
                self.logger.error(err_str_log)
        if self.error_logger:
            self.error_logger.error(
                "\n[{:d}]{}\n({})\n#".format(lnum, line.rstrip(), str(e))
            )

    # Setup function for the base_annotator, different from self.setup()
    # which is intended to be for the derived annotator.
    def base_setup(self):
        self._setup_primary_input()
        self._setup_secondary_inputs()
        self._setup_outputs()
        self._open_db_connection()
        self.setup()
        if not hasattr(self, "supported_chroms"):
            self.supported_chroms = set(
                ["chr" + str(n) for n in range(1, 23)] + ["chrX", "chrY"]
            )

    def _setup_primary_input(self):
        if self.conf is None:
            from ..exceptions import SetupError

            raise SetupError(module_name=self.module_name)
        from ..exceptions import ConfigurationError
        from ..util.inout import CravatReader

        self.primary_input_reader = CravatReader(self.primary_input_path)
        requested_input_columns = self.conf["input_columns"]
        defined_columns = self.primary_input_reader.get_column_names()
        missing_columns = set(requested_input_columns) - set(defined_columns)
        if missing_columns:
            if len(defined_columns) > 0:
                err_msg = "Columns not defined in input: %s" % ", ".join(
                    missing_columns
                )
                raise ConfigurationError(err_msg)
            else:
                default_columns = self.default_input_columns[self.conf["input_format"]]
                for col_name in requested_input_columns:
                    try:
                        col_index = default_columns.index(col_name)
                    except ValueError:
                        err_msg = "Column %s not defined for %s format input" % (
                            col_name,
                            self.conf["input_format"],
                        )
                        raise ConfigurationError(err_msg)
                    if col_name == "pos":
                        data_type = "int"
                    else:
                        data_type = "string"
                    self.primary_input_reader.override_column(
                        col_index, col_name, data_type=data_type
                    )

    def _setup_secondary_inputs(self):
        if self.conf is None:
            from ..exceptions import SetupError

            raise SetupError(module_name=self.module_name)
        self.secondary_readers = {}
        try:
            num_expected = len(self.conf["secondary_inputs"])
        except KeyError:
            num_expected = 0
        num_provided = len(self.secondary_paths)
        if num_expected > num_provided:
            raise Exception(
                f"Too few secondary inputs. {num_expected} expected, {num_provided} provided"
            )
        elif num_expected < num_provided:
            raise Exception(
                "Too many secondary inputs. %d expected, %d provided"
                % (num_expected, num_provided)
            )
        for sec_name, sec_input_path in self.secondary_paths.items():
            key_col = (
                self.conf["secondary_inputs"][sec_name]
                .get("match_columns", {})
                .get("secondary", "uid")
            )
            use_columns = self.conf["secondary_inputs"][sec_name].get("use_columns", [])
            fetcher = SecondaryInputFetcher(
                sec_input_path, key_col, fetch_cols=use_columns
            )
            self.secondary_readers[sec_name] = fetcher

    # Open the output files (.var, .gen, .ncd) that are needed
    def _setup_outputs(self):
        if self.conf is None or self.output_dir is None or self.output_basename is None:
            from ..exceptions import SetupError

            raise SetupError(module_name=self.module_name)
        import os
        from ..util.inout import CravatWriter

        level = self.conf["level"]
        if level == "variant":
            output_suffix = "var"
        elif level == "gene":
            output_suffix = "gen"
        elif level == "summary":
            output_suffix = "sum"
        else:
            output_suffix = "out"
        if not (os.path.exists(self.output_dir)):
            os.makedirs(self.output_dir)
        self.output_path = os.path.join(
            self.output_dir,
            ".".join([self.output_basename, self.module_name, output_suffix]),
        )
        self.invalid_path = os.path.join(
            self.output_dir,
            ".".join([self.output_basename, self.module_name, "err"]),
        )
        if self.plain_output:
            self.output_writer = CravatWriter(
                self.output_path,
                include_definition=False,
                include_titles=True,
                titles_prefix="",
            )
        else:
            self.output_writer = CravatWriter(self.output_path)
            self.output_writer.write_meta_line("name", self.module_name)
            self.output_writer.write_meta_line(
                "displayname", self.annotator_display_name
            )
            self.output_writer.write_meta_line("version", self.annotator_version)
        skip_aggregation = []
        for col_index, col_def in enumerate(self.conf["output_columns"]):
            self.output_writer.add_column(col_index, col_def)
            if not (col_def.get("aggregate", True)):
                skip_aggregation.append(col_def["name"])
        if not (self.plain_output):
            self.output_writer.write_definition(self.conf)
            self.output_writer.write_meta_line(
                "no_aggregate", ",".join(skip_aggregation)
            )

    def _open_db_connection(self):
        import os
        import sqlite3

        db_dirs = [self.data_dir, os.path.join("/ext", "resource", "newarch")]
        db_path = None
        for db_dir in db_dirs:
            db_path = os.path.join(db_dir, self.module_name + ".sqlite")
            if os.path.exists(db_path):
                self.dbconn = sqlite3.connect(db_path)
                self.cursor = self.dbconn.cursor()

    def close_db_connection(self):
        if self.cursor is not None:
            self.cursor.close()
        if self.dbconn is not None:
            self.dbconn.close()

    def remove_log(self):
        pass

    def get_uid_col(self):
        if self.conf is None:
            from ..exceptions import SetupError

            raise SetupError(module_name=self.module_name)
        return self.conf["output_columns"][0]["name"]

    # Placeholder, intended to be overridded in derived class
    def setup(self):
        pass

    def base_cleanup(self):
        if self.output_writer:
            self.output_writer.close()
        # self.invalid_file.close()
        if self.dbconn != None:
            self.close_db_connection()
        self.cleanup()

    # Placeholder, intended to be overridden in derived class
    def cleanup(self):
        pass

    def remove_log_file(self):
        import os

        if self.logger and self.log_handler:
            self.logger.removeHandler(self.log_handler)
            self.log_handler.flush()
            self.log_handler.close()
        if self.log_path:
            os.remove(self.log_path)

    # Setup the logging utility
    def _setup_logger(self):
        if self.output_basename is None or self.output_dir is None:
            from ..exceptions import SetupError

            raise SetupError(self.module_name)
        import logging
        import os

        self.logger = logging.getLogger("oakvar." + self.module_name)
        if self.output_basename != "__dummy__":
            self.log_path = os.path.join(self.output_dir, self.output_basename + ".log")
            log_handler = logging.FileHandler(self.log_path, "a")
        else:
            log_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s %(name)-20s %(message)s", "%Y/%m/%d %H:%M:%S"
        )
        log_handler.setFormatter(formatter)
        self.logger.addHandler(log_handler)
        self.error_logger = logging.getLogger("error." + self.module_name)
        if self.output_basename != "__dummy__":
            error_log_path = os.path.join(
                self.output_dir, self.output_basename + ".err"
            )
            error_log_handler = logging.FileHandler(error_log_path, "a")
        else:
            error_log_handler = logging.StreamHandler()
        formatter = logging.Formatter("SOURCE:%(name)-20s %(message)s")
        error_log_handler.setFormatter(formatter)
        self.error_logger.addHandler(error_log_handler)
        self.unique_excs = []

    # Gets the input dict from both the input file, and
    # any depended annotators depended annotator feature not complete.
    def _get_input(self):
        from ..util.inout import AllMappingsParser
        from ..consts import all_mappings_col_name
        from ..consts import mapping_parser_name
        from ..exceptions import SetupError

        if self.conf is None or self.primary_input_reader is None:
            raise SetupError(self.module_name)
        for lnum, line, reader_data in self.primary_input_reader.loop_data():
            try:
                input_data = {}
                for col_name in self.conf["input_columns"]:
                    input_data[col_name] = reader_data[col_name]
                if all_mappings_col_name in input_data:
                    input_data[mapping_parser_name] = AllMappingsParser(
                        input_data[all_mappings_col_name]
                    )
                secondary_data = {}
                for module_name, fetcher in self.secondary_readers.items():
                    input_key_col = (
                        self.conf["secondary_inputs"][module_name]
                        .get("match_columns", {})
                        .get("primary", "uid")
                    )
                    input_key_data = input_data[input_key_col]
                    secondary_data[module_name] = fetcher.get(input_key_data)
                yield lnum, line, input_data, secondary_data
            except Exception as e:
                self._log_runtime_exception(lnum, line, reader_data, e)
                continue

    def annotate(self, input_data, secondary_data=None):
        return {
            "default__annotation": "no annotate has been defined",
            "input_data": input_data,
            "secondary_data": secondary_data,
        }

    def live_report_substitute(self, d):
        if self.conf is None:
            from ..exceptions import SetupError

            raise SetupError(self.module_name)
        import re

        if "report_substitution" not in self.conf:
            return d
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


class SecondaryInputFetcher:
    def __init__(self, input_path, key_col, fetch_cols=[]):
        from ..util.inout import CravatReader
        from ..exceptions import ConfigurationError

        self.key_col = key_col
        self.input_path = input_path
        self.input_reader = CravatReader(self.input_path)
        valid_cols = self.input_reader.get_column_names()
        if key_col not in valid_cols:
            err_msg = "Key column %s not present in secondary input %s" % (
                key_col,
                self.input_path,
            )
            raise ConfigurationError(err_msg)
        if fetch_cols:
            unmatched_cols = list(set(fetch_cols) - set(valid_cols))
            if unmatched_cols:
                err_msg = "Column(s) %s not present in secondary input %s" % (
                    ", ".join(unmatched_cols),
                    self.input_path,
                )
                raise ConfigurationError(err_msg)
            self.fetch_cols = fetch_cols
        else:
            self.fetch_cols = valid_cols
        self.data = {}
        self.load_input()

    def load_input(self):
        for _, _, all_col_data in self.input_reader.loop_data():
            key_data = all_col_data[self.key_col]
            # if key_data not in self.data:
            #    self.data[key_data] = [None] * len(self.fetch_cols)
            # else:
            fetch_col_data = {}
            # row_has_data = False
            for col in self.fetch_cols:
                # if col != self.key_col:# and all_col_data[col] is not None:
                #    row_has_data = True
                fetch_col_data[col] = all_col_data[col]
            # if row_has_data:
            self.data[key_data] = fetch_col_data
            # self.data[key_data].append(fetch_col_data)

    def get(self, key_data):
        if key_data in self.data:
            return self.data[key_data]
        else:
            ret = {}
            for col_name in self.fetch_cols:
                ret[col_name] = None
            return ret

    def get_values(self, key_data, key_column):
        ret = [v[key_column] for v in self.data[key_data]]
        return ret
