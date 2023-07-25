from typing import Optional
from typing import Any
from typing import List
from typing import Dict
from typing import Union
import polars as pl


class BaseAnnotator(object):
    """BaseAnnotator."""

    def __init__(
        self,
        input_file: Optional[str] = None,
        run_name: Optional[str] = None,
        output_dir: Optional[str] = None,
        plainoutput: bool = False,
        logtofile: bool = False,
        module_options: Dict = {},
        serveradmindb=None,
        name: Optional[str] = None,
        title: Optional[str] = None,
        level: Optional[str] = None,
        output: Union[List[Dict[str, Any]], Dict[str, Dict[str, Any]]] = [],
        module_conf: Dict[str, Any] = {},
        code_version: Optional[str] = None,
        input_level: Optional[str] = None,
        df_mode: Optional[bool] = None,
    ):
        """__init__.

        Args:
            input_file (Optional[str]): input_file
            run_name (Optional[str]): run_name
            output_dir (Optional[str]): output_dir
            plainoutput (bool): plainoutput
            logtofile (bool): logtofile
            module_options (Dict): module_options
            serveradmindb:
            name (Optional[str]): name
            title (Optional[str]): title
            level (Optional[str]): level
            output(Union[Dict[str, Dict[str, Any]], List[Dict]]): output
            module_conf (dict): module_conf
            code_version (Optional[str]): code_version
        """
        import os
        import sys
        from pathlib import Path
        from multiprocessing.pool import ThreadPool
        from ..consts import cannonical_chroms
        from ..module.local import get_module_conf
        from ..module.data_cache import ModuleDataCache
        from ..exceptions import ModuleLoadingError
        from ..exceptions import LoggerError
        from ..consts import VARIANT_LEVEL_PRIMARY_KEY_COLDEF
        from ..consts import GENE_LEVEL_PRIMARY_KEY_COLDEF
        from ..consts import OLD_INPUT_LEVEL_KEY
        from ..consts import OLD_VARIANT_LEVEL_KEY
        from ..consts import OLD_GENE_LEVEL_KEY
        from ..consts import VARIANT_LEVEL
        from ..consts import GENE_LEVEL

        self.valid_levels = ["variant", "gene"]
        self.id_col_defs = {
            "variant": VARIANT_LEVEL_PRIMARY_KEY_COLDEF,
            "gene": GENE_LEVEL_PRIMARY_KEY_COLDEF,
        }
        self.script_path: str = ""
        self.module_options = module_options
        if input_file:
            self.primary_input_path = Path(input_file).resolve()
        else:
            self.primary_input_path = None
        self.run_name = run_name
        self.output_dir = output_dir
        self.plain_output = plainoutput
        self.logtofile = logtofile
        if self.__module__ == "__main__":
            fp = None
            self.main_fpath = None
        else:
            fp = sys.modules[self.__module__].__file__
            if not fp:
                raise ModuleLoadingError(module_name=self.__module__)
            self.main_fpath = Path(fp).resolve()
        self.output_basename = None
        self.logger = None
        self.error_logger = None
        self.dbconn = None
        self.cursor = None
        self.cmd_arg_parser = None
        self.json_colnames = None
        self.primary_input_reader = None
        self.output_path = None
        self.last_status_update_time = None
        self.output_writer = None
        self.log_path = None
        self.unique_excs = []
        self.log_handler = None
        self.pool: Optional[ThreadPool] = None
        self.parse_cmd_args()
        self.serveradmindb = serveradmindb
        self.supported_chroms = set(cannonical_chroms)
        self.module_type = "annotator"
        self.conf = {}
        self.col_names: Dict[str, List[str]] = {}
        self.full_col_names: Dict[str, Dict[str, str]] = {}
        self.df_dtypes: Dict[str, Any] = {}
        self.df_mode: bool
        self.output: Dict[str, Dict[str, Any]] = {}
        if not self.main_fpath:
            if name:
                self.module_name = name
                self.module_dir = Path(os.getcwd()).resolve()
            else:
                raise ModuleLoadingError(msg="name argument should be given.")
            self.conf = module_conf.copy()
        else:
            self.module_name = self.main_fpath.stem
            self.module_dir = self.main_fpath.parent
            self.conf = get_module_conf(
                self.module_name,
                module_type=self.module_type,
                module_dir=self.module_dir,
            )
            if not self.conf:
                self.conf = {}
        if not level and "level" in self.conf:
            level = self.conf.get("level")
        if not level:
            raise ModuleLoadingError(
                msg="level or module_conf with level should be given."
            )
        self.level: str = level
        if "level" not in self.conf:
            self.conf["level"] = self.level
        self.set_output(output)
        self.title = title
        if self.title:
            self.conf["title"] = self.title
        elif "title" in self.conf:
            self.title = self.conf["title"]
        if df_mode is not None:
            self.df_mode: bool = df_mode
        else:
            self.df_mode = self.conf.get("df_mode", False)
        self.annotator_name = self.module_name
        self.data_dir = self.module_dir / "data"
        self._setup_logger()
        if not self.conf:
            raise ModuleLoadingError(module_name=self.module_name)
        self.set_ref_colname()
        if self.logger is None:
            raise LoggerError(module_name=self.module_name)
        if "logging_level" in self.conf:
            self.logger.setLevel(self.conf["logging_level"].upper())
        if "title" in self.conf:
            self.annotator_display_name = self.conf["title"]
        elif self.module_name:
            self.annotator_display_name = self.module_name.capitalize()
        else:
            self.annotator_display_name = os.path.basename(self.module_dir).upper()
        if code_version:
            self.code_version: str = code_version
        else:
            if "code_version" in self.conf:
                self.code_version: str = self.conf["version"]
            elif "version" in self.conf:
                self.code_version: str = self.conf["version"]
            else:
                self.code_version: str = ""
        if input_level is None:
            input_level = self.conf.get("input_level")
            if not input_level:
                input_format = self.conf.get("input_format")
                if input_format:
                    if input_format == OLD_INPUT_LEVEL_KEY:
                        self.input_level = VARIANT_LEVEL
                    elif input_format == OLD_VARIANT_LEVEL_KEY:
                        self.input_level = VARIANT_LEVEL
                    elif input_format == OLD_GENE_LEVEL_KEY:
                        self.input_level = GENE_LEVEL
                    else:
                        raise
                else:
                    self.input_level = VARIANT_LEVEL
            else:
                if input_level not in [VARIANT_LEVEL, GENE_LEVEL]:
                    raise
                self.input_level = input_level
        else:
            if input_level not in [VARIANT_LEVEL, GENE_LEVEL]:
                raise
            self.input_level = input_level
        self.secondary_data_required: bool = False
        if self.conf.get("secondary_inputs"):
            self.secondary_data_required = True
        self.cache = ModuleDataCache(self.module_name, module_type=self.module_type)
        self.setup_df()

    def set_output(
        self, output: Union[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]
    ):
        from ..consts import OUTPUT_COLS_KEY
        from ..consts import OUTPUT_KEY

        if not output:
            output = self.conf.get(
                OUTPUT_KEY, self.conf.get(OUTPUT_COLS_KEY, [])
            ).copy()
        if isinstance(output, dict):
            self.output = output
        else:
            self.output[self.module_name] = {"level": self.level, OUTPUT_COLS_KEY: []}
            coldefs: List[Dict[str, Any]] = []
            for coldef in output:
                if coldef.get("table") is True:
                    table_name = coldef['name']
                    self.output[table_name] = {
                        "level": coldef.get("level", self.level),
                        OUTPUT_COLS_KEY: [],
                    }
                    for table_coldef in coldef.get("table_headers", []):
                        self.output[table_name][OUTPUT_COLS_KEY].append(
                            table_coldef.copy()
                        )
                else:
                    coldefs.append(coldef.copy())
            self.output[self.module_name][OUTPUT_COLS_KEY] = coldefs
        self.conf["output"] = self.output.copy()
        self.col_names = {
            table_name: [
                coldef["name"] for coldef in self.output[table_name][OUTPUT_COLS_KEY]
            ]
            for table_name in self.output.keys()
        }

    def set_ref_colname(self):
        """set_ref_colname."""
        ref_colnames = {
            "variant": "uid",
            "gene": "hugo",
            "sample": "uid",
            "mapping": "uid",
        }
        if self.level:
            self._id_col_name = ref_colnames.get(self.level)
        else:
            self._id_col_name = None

    def summarize_by_gene(self, __hugo__, __input_data__):
        """summarize_by_gene.

        Args:
            __hugo__:
            __input_data__:
        """
        pass

    def _log_exception(self, e, halt=True):
        """_log_exception.

        Args:
            e:
            halt:
        """
        import traceback

        if self.logger:
            self.logger.exception(e)
        else:
            tb = traceback.format_exc()
            print(tb)
        if halt:
            return False
        else:
            return True

    def parse_cmd_args(self):
        """parse_cmd_args."""
        from pathlib import Path

        if not self.output_dir and self.primary_input_path:
            self.output_dir = str(self.primary_input_path.parent)
        if self.run_name is not None:
            self.output_basename = self.run_name
        elif self.primary_input_path:
            self.output_basename = self.primary_input_path.name
            if Path(self.output_basename).suffix in [".crv", ".crg", ".crx"]:
                self.output_basename = self.output_basename[:-4]

    def log_progress(self, lnum):
        """log_progress.

        Args:
            lnum:
        """
        from time import time
        from ..util.run import update_status
        from ..consts import JOB_STATUS_UPDATE_INTERVAL

        if not self.last_status_update_time or not self.conf:
            return
        cur_time = time()
        if (
            lnum % 10000 == 0
            or cur_time - self.last_status_update_time > JOB_STATUS_UPDATE_INTERVAL
        ):
            status = f"Running {self.conf['title']} ({self.module_name}): line {lnum}"
            update_status(status, logger=self.logger, serveradmindb=self.serveradmindb)
            self.last_status_update_time = cur_time

    def is_star_allele(self, input_data):
        """is_star_allele.

        Args:
            input_data:
        """
        if self.conf is None:
            return
        return self.conf["level"] == "variant" and input_data.get("alt_base", "") == "*"

    def should_skip_chrom(self, input_data):
        """should_skip_chrom.

        Args:
            input_data:
        """
        if self.conf is None:
            return
        return (
            self.conf["level"] == "variant"
            and input_data.get("chrom") not in self.supported_chroms
        )

    def annotate_df(self, dfs: Dict[str, pl.DataFrame]) -> Dict[str, pl.DataFrame]:
        """annotate_df.

        Args:
            dfs:
        """
        _ = dfs
        raise NotImplementedError("annotate_df method should be implemented.")

    def setup_df(self):
        from ..consts import OUTPUT_COLS_KEY
        from ..util.run import get_pl_dtype

        self.full_col_names = {
            table_name: {
                col_name: f"{self.module_name}__{col_name}"
                for col_name in self.col_names[table_name]
            }
            for table_name in self.col_names.keys()
        }
        self.df_dtypes = {}
        for table_name, table_output in self.output.items():
            print(f"@@@ annot. {table_name}: {table_output}")
            self.df_dtypes[table_name] = {}
            coldefs: List[Dict[str, Any]] = table_output.get(OUTPUT_COLS_KEY, [])
            for col in coldefs:
                col_name = col.get("name")
                ty = get_pl_dtype(col)
                self.df_dtypes[table_name][col_name] = ty
        self.base_setup()

    def get_series(self, dfs: Dict[str, pl.DataFrame]) -> Dict[str, List[pl.Series]]:
        from ..consts import VARIANT_LEVEL
        from ..consts import VARIANT_LEVEL_PRIMARY_KEY
        from ..consts import GENE_LEVEL
        from ..consts import GENE_LEVEL_PRIMARY_KEY

        keycol: str
        if self.input_level == GENE_LEVEL:
            df = dfs.get(GENE_LEVEL)
            keycol = GENE_LEVEL_PRIMARY_KEY
        else:
            df = dfs.get(VARIANT_LEVEL)
            keycol = VARIANT_LEVEL_PRIMARY_KEY
        if df is None:
            raise
        var_ld: Dict[str, Dict[str, List[Any]]] = {}
        counts: Dict[str, int] = {}
        max_counts: Dict[str, int] = {}
        for table_name, col_names in self.col_names.items():
            counts[table_name] = 0
            if table_name in dfs:
                max_counts[table_name] = dfs[table_name].height
            else:
                max_counts[table_name] = dfs[self.level].height
            var_ld[table_name] = {}
            for col_name in col_names:
                var_ld[table_name][col_name] = [None] * max_counts[table_name]
        for row in df.iter_rows(named=True):
            if self.secondary_data_required:
                keyval: Any = row[keycol]
                secondary_dfs: Dict[str, pl.DataFrame] = {}
                for table_name, s_df in dfs.items():
                    if table_name == self.level:
                        continue
                    if keycol in s_df.columns:
                        secondary_dfs[table_name] = s_df.filter(
                            pl.col(keycol) == keyval
                        )
                output_dict = self.annotate(row, secondary_data=secondary_dfs)
            else:
                output_dict = self.annotate(row)
            if output_dict is not None:
                if self.level in output_dict:
                    for table_name, table_data in output_dict.items():
                        table_ld = var_ld[table_name]
                        table_count = counts[table_name]
                        table_max_count = max_counts[table_name]
                        for table_row in table_data:
                            for col_name, value in table_row.items():
                                table_ld[col_name][table_count] = value
                        if table_name == self.level:
                            counts[table_name] += 1
                        elif table_data:
                            counts[table_name] += 1
                        if counts[table_name] == table_max_count:
                            for col_name, table_col_ld in table_ld.items():
                                table_col_ld.extend([None] * df.height)
                            max_counts[table_name] += df.height
                else:
                    table_name = self.level
                    table_ld = var_ld[table_name]
                    table_count = counts[table_name]
                    table_max_count = max_counts[table_name]
                    for col_name, value in output_dict.items():
                        table_ld[col_name][table_count] = value
                    counts[table_name] += 1
                    if counts[table_name] == table_max_count:
                        for col_name, table_col_ld in table_ld.items():
                            table_col_ld.extend([None] * df.height)
                        max_counts[table_name] += df.height
            else:
                counts[self.module_name] += 1
        for table_name, table_ld in var_ld.items():
            for col_name in table_ld.keys():
                var_ld[table_name][col_name] = var_ld[table_name][col_name][
                    : counts[table_name]
                ]
        seriess: Dict[str, List[pl.Series]] = {}
        for table_name, table_ld in var_ld.items():
            seriess[table_name] = []
            for col_name in self.col_names[table_name]:
                series = pl.Series(
                    self.full_col_names[table_name][col_name],
                    var_ld[table_name][col_name],
                    dtype=self.df_dtypes[table_name][col_name],
                )
                seriess[table_name].append(series)
        return seriess

    def run_df(self, dfs: Dict[str, pl.DataFrame]) -> Dict[str, pl.DataFrame]:
        if self.df_mode:
            dfs = self.annotate_df(dfs)
        else:
            seriess = self.get_series(dfs)
            for table_name, table_seriess in seriess.items():
                if table_name in dfs:
                    dfs[table_name] = dfs[table_name].with_columns(table_seriess)
                else:
                    dfs[table_name] = pl.DataFrame(table_seriess)
        return dfs

    def run(self, dfs: Optional[Dict[str, pl.DataFrame]] = None):
        """run.

        Args:
            df:
        """
        if dfs is not None:
            return self.run_df(dfs)

    def get_gene_summary_data(self, cf):
        """get_gene_summary_data.

        Args:
            cf:
        """
        hugos = cf.get_filtered_hugo_list()
        output_columns = cf.get_stored_output_columns(self.module_name)
        cols = [
            coldef["name"]
            for coldef in output_columns
            if coldef["name"] != "uid"
        ]
        data = {}
        rows = cf.get_variant_data_for_cols(cols)
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

    def _log_runtime_exception(self, lnum, __line__, __input_data__, e, fn=None):
        """_log_runtime_exception.

        Args:
            lnum:
            __line__:
            __input_data__:
            e:
            fn:
        """
        import traceback

        err_str = traceback.format_exc().rstrip()
        lines = err_str.split("\n")
        last_line = lines[-1]
        err_str_log = "\n".join(lines[:-1]) + "\n" + ":".join(last_line.split(":")[:2])
        if err_str_log not in self.unique_excs:
            self.unique_excs.append(err_str_log)
            if self.logger:
                self.logger.error(err_str_log)
            else:
                print(err_str_log)
        err_logger_s = f"{fn}:{lnum}\t{str(e)}"
        if self.error_logger:
            self.error_logger.error(err_logger_s)
        else:
            print(err_logger_s)

    def base_setup(self):
        """base_setup."""
        self.connect_db()
        self.setup()
        if not hasattr(self, "supported_chroms"):
            self.supported_chroms = set(
                ["chr" + str(n) for n in range(1, 23)] + ["chrX", "chrY"]
            )

    def connect_db(self):
        """connect_db."""
        from pathlib import Path
        import sqlite3

        db_path = Path(self.data_dir) / (self.module_name + ".sqlite")
        if db_path.exists():
            self.dbconn = sqlite3.connect(str(db_path))
            self.cursor = self.dbconn.cursor()

    def close_db_connection(self):
        """close_db_connection."""
        if self.cursor is not None:
            self.cursor.close()
        if self.dbconn is not None:
            self.dbconn.close()

    # Placeholder, intended to be overridded in derived class
    def setup(self):
        """setup."""
        pass

    def base_cleanup(self):
        """base_cleanup."""
        if self.output_writer:
            self.output_writer.close()
        # self.invalid_file.close()
        if self.dbconn is not None:
            self.close_db_connection()
        self.cleanup()

    # Placeholder, intended to be overridden in derived class
    def cleanup(self):
        """cleanup."""
        pass

    def _setup_logger(self):
        """_setup_logger."""
        from logging import getLogger

        self.logger = getLogger("oakvar." + self.module_name)
        self.error_logger = getLogger("err." + self.module_name)

    def annotate(
        self, input_data, secondary_data: Dict[str, pl.DataFrame] = {}
    ) -> Dict[str, Any]:
        """annotate.

        Args:
            input_data:
            secondary_data:
        """
        return {
            "default__annotation": "no annotate has been defined",
            "input_data": input_data,
            "secondary_data": secondary_data,
        }

    def live_report_substitute(self, d):
        """live_report_substitute.

        Args:
            d:
        """
        import re
        from ..exceptions import SetupError

        if self.conf is None:
            raise SetupError(self.module_name)
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

    def add_method(self, fn):
        """add_method.

        Args:
            fn:
        """
        setattr(self.__class__, fn.__name__, fn)

    def save(self, overwrite: bool = False, interactive: bool = False):
        """save.

        Args:
            overwrite (bool): overwrite
            interactive (bool): interactive
        """
        from ..module.local import create_module_files

        create_module_files(self, overwrite=overwrite, interactive=interactive)
