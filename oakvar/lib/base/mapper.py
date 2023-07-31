from typing import Optional
from typing import Any
from typing import List
from typing import Dict
from typing import Union
from typing import Tuple
import polars as pl
from .commonmodule import BaseCommonModule


class BaseMapper(object):
    def __init__(
        self,
        name: str = "",
        primary_transcript: List[str] = ["mane"],
        serveradmindb=None,
        module_options: Dict = {},
        output: Union[List[Dict[str, Any]], Dict[str, Dict[str, Any]]] = [],
        wgs_reader: Optional[BaseCommonModule] = None,
        use_duckdb: bool = False,
    ):
        from time import time
        from pathlib import Path
        import sys
        from ..module.local import get_module_conf
        from ..consts import VARIANT_LEVEL

        self.use_duckdb = use_duckdb
        self.wgs_reader = wgs_reader
        self.module_options: Dict = module_options
        self.primary_transcript_paths: List[str] = [v for v in primary_transcript if v]
        self.primary_transcript = primary_transcript
        self.serveradmindb = serveradmindb
        self.logger = None
        self.error_logger = None
        self.col_names: Dict[str, List[str]] = {}
        self.unique_excs: Dict[str, int] = {}
        self.output: Dict[str, Dict[str, Any]] = {}
        self.level = VARIANT_LEVEL
        self.t = time()
        self.script_path = Path(sys.modules[self.__class__.__module__].__file__ or "")
        if name:
            self.module_name = name
        else:
            self.module_name = self.script_path.stem
        self.name = self.module_name
        self.module_dir = self.script_path.parent
        self.gene_info = {}
        self.setup_logger()
        self.conf: Dict[str, Any] = (
            get_module_conf(self.module_name, module_type="mapper") or {}
        )
        self.set_output(output)
        self.df_headers: Dict[str, Dict[str, pl.PolarsDataType]] = {}
        self.setup()
        self.setup_df()

    def set_output(
        self, output: Union[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]
    ):
        from ..consts import VARIANT_LEVEL
        from ..consts import OUTPUT_KEY
        from ..consts import OUTPUT_COLS_KEY
        from ..consts import ERR_LEVEL
        from ..util.util import get_ov_system_output_columns

        if not output:
            output = self.conf.get(
                OUTPUT_KEY, self.conf.get(OUTPUT_COLS_KEY, [])
            ).copy()
        if isinstance(output, dict):
            self.output = output.copy()
        else:
            self.output[VARIANT_LEVEL] = {"level": VARIANT_LEVEL, OUTPUT_COLS_KEY: []}
            for coldef in output:
                if coldef.get("table") is True:
                    table_name = f"{self.module_name}__{coldef['name']}"
                    self.output[table_name] = {"level": self.level, OUTPUT_COLS_KEY: []}
                    for table_coldef in coldef.get("table_headers", []):
                        if not self.use_duckdb:
                            if "[]" in table_coldef["type"]:
                                table_coldef["type"] = "string"
                        self.output[table_name][OUTPUT_COLS_KEY].append(
                            table_coldef.copy()
                        )
                else:
                    self.output[VARIANT_LEVEL][OUTPUT_COLS_KEY].append(coldef.copy())
        if ERR_LEVEL not in self.output:
            self.output[ERR_LEVEL] = get_ov_system_output_columns()[ERR_LEVEL]
        self.conf[OUTPUT_KEY] = self.output.copy()
        self.col_names = {
            table_name: [
                coldef["name"]
                for coldef in self.output[table_name].get(OUTPUT_COLS_KEY, [])
            ]
            for table_name in self.output.keys()
        }

    def setup(self):
        raise NotImplementedError("Mapper must have a setup() method.")

    def end(self):
        pass

    def setup_logger(self):
        from logging import getLogger

        self.logger = getLogger("oakvar.mapper")
        self.error_logger = getLogger("err." + self.module_name)

    def map(self, crv_data: dict) -> Dict[str, List[Dict[str, Any]]]:
        _ = crv_data
        return {}

    def add_crx_to_gene_info(self, crx_data):
        from ..util.inout import AllMappingsParser

        tmap_json = crx_data["all_mappings"]
        # Return if no tmap
        if tmap_json == "":
            return
        tmap_parser = AllMappingsParser(tmap_json)
        for hugo in tmap_parser.get_genes():
            self.gene_info[hugo] = True

    def log_error(self, e, input_data: Dict[str, Any]) -> Tuple[Optional[str], int]:
        from traceback import format_exc
        from zlib import crc32
        from oakvar.lib.exceptions import ExpectedException
        from ..consts import FILENO_KEY
        from ..consts import LINENO_KEY

        if isinstance(e, ExpectedException):
            err_str = str(e)
        else:
            err_str = format_exc().rstrip()
        fileno: int = input_data[FILENO_KEY]
        lineno: int = input_data[LINENO_KEY]
        if err_str not in self.unique_excs:
            err_no = crc32(bytes(err_str, "utf-8"))
            self.unique_excs[err_str] = err_no
            if self.logger:
                self.logger.error(f"Error [{err_no}]: {fileno}:{lineno} {err_str}")
            return err_str, err_no
        else:
            err_no = self.unique_excs[err_str]
            return None, err_no

    async def get_gene_summary_data(self, cf):
        from json import loads
        from ...gui.consts import result_viewer_num_var_limit_for_gene_summary_key
        from ...gui.consts import DEFAULT_RESULT_VIEWER_NUM_VAR_LIMIT_FOR_GENE_SUMMARY
        from ..system import get_system_conf
        from ..util.util import get_ov_system_output_columns
        from ..consts import VARIANT_LEVEL
        from ..consts import OUTPUT_COLS_KEY

        cols = [
            "base__" + coldef["name"]
            for coldef in get_ov_system_output_columns()
            .get(VARIANT_LEVEL, {})
            .get(OUTPUT_COLS_KEY, [])
            if coldef["name"] not in ["cchange", "exonno"]
        ]
        cols.extend(["tagsampler__numsample"])
        data = {}
        rows = await cf.exec_db(cf.get_variant_data_for_cols, cols)
        sys_conf = get_system_conf()
        result_viewer_num_var_limit_for_gene_summary = sys_conf.get(
            result_viewer_num_var_limit_for_gene_summary_key,
            DEFAULT_RESULT_VIEWER_NUM_VAR_LIMIT_FOR_GENE_SUMMARY,
        )
        if len(rows) > result_viewer_num_var_limit_for_gene_summary:
            return {}
        rows_by_hugo = {}
        for row in rows:
            all_mappings = loads(row["base__all_mappings"])
            for hugo in all_mappings.keys():
                if hugo not in rows_by_hugo:
                    rows_by_hugo[hugo] = []
                rows_by_hugo[hugo].append(row)
        hugos = await cf.exec_db(cf.get_filtered_hugo_list)
        for hugo in hugos:
            rows = rows_by_hugo[hugo]
            input_data = {}
            for i in range(len(cols)):
                input_data[cols[i]] = [row[i] for row in rows]
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

    def setup_df(self):
        from ..util.run import get_df_headers

        self.df_headers = get_df_headers(self.output)

    def get_series(self, df: pl.DataFrame) -> Dict[str, List[pl.Series]]:
        from ..consts import VARIANT_LEVEL
        from ..consts import VARIANT_LEVEL_PRIMARY_KEY
        from ..consts import GENE_LEVEL
        from ..consts import GENE_LEVEL_PRIMARY_KEY
        from ..consts import ERR_LEVEL
        from ..consts import FILENO_KEY
        from ..consts import LINENO_KEY
        from ..consts import ERRNO_KEY
        from ..consts import ERR_KEY
        from ..util.run import initialize_err_series_data

        var_ld = {}
        var_ld[ERR_LEVEL] = initialize_err_series_data()
        counts: Dict[str, int] = {}
        max_counts: Dict[str, int] = {}
        for table_name, col_names in self.col_names.items():
            counts[table_name] = 0
            max_counts[table_name] = df.height
            var_ld[table_name] = {}
            for col_name in col_names:
                var_ld[table_name][col_name] = [None] * max_counts[table_name]
        for input_data in df.iter_rows(named=True):
            output_dict: Dict[str, List[Dict[str, Any]]]
            if input_data["alt_base"] in ["*", ".", ""]:
                output_dict = {}
                counts[VARIANT_LEVEL] += 1
            else:
                try:
                    output_dict = self.map(input_data)
                except Exception as e:
                    err, errno = self.log_error(e, input_data)
                    output_dict = {
                        VARIANT_LEVEL: [],
                        ERR_LEVEL: [
                            {
                                FILENO_KEY: input_data[FILENO_KEY],
                                LINENO_KEY: input_data[LINENO_KEY],
                                VARIANT_LEVEL_PRIMARY_KEY: input_data[
                                    VARIANT_LEVEL_PRIMARY_KEY
                                ],
                                ERRNO_KEY: errno,
                                ERR_KEY: err,
                            }
                        ],
                    }
            for table_name, table_data in output_dict.items():
                table_ld = var_ld[table_name]
                table_max_count: int = max_counts[table_name]
                if table_name == GENE_LEVEL:
                    for table_row in table_data:
                        key_val = table_row.get(GENE_LEVEL_PRIMARY_KEY)
                        if key_val is None:
                            continue
                        if (
                            counts[table_name] == 0
                            or key_val not in table_ld[GENE_LEVEL_PRIMARY_KEY]
                        ):
                            for col_name, value in table_row.items():
                                table_ld[col_name][counts[table_name]] = value
                            counts[table_name] += 1
                        if counts[table_name] == table_max_count:
                            for col_name, table_col_ld in table_ld.items():
                                table_col_ld.extend([None] * df.height)
                            max_counts[table_name] += df.height
                            table_max_count = max_counts[table_name]
                else:
                    for table_row in table_data:
                        for col_name, value in table_row.items():
                            if not self.use_duckdb and isinstance(value, list):
                                value = str(value)
                            table_ld[col_name][counts[table_name]] = value
                        if table_name == VARIANT_LEVEL:
                            counts[table_name] += 1
                        elif table_row:
                            counts[table_name] += 1
                        if counts[table_name] == table_max_count:
                            for col_name, table_col_ld in table_ld.items():
                                table_col_ld.extend([None] * df.height)
                            max_counts[table_name] += df.height
                            table_max_count = max_counts[table_name]
        for table_name, table_ld in var_ld.items():
            for col_name in table_ld.keys():
                var_ld[table_name][col_name] = var_ld[table_name][col_name][
                    : counts[table_name]
                ]
        seriess: Dict[str, List[pl.Series]] = {}
        for table_name, table_ld in var_ld.items():
            seriess[table_name] = []
            for col_name in self.col_names[table_name]:
                dtype = self.df_headers[table_name][col_name]
                if not self.use_duckdb:
                    if isinstance(dtype, pl.List):
                        dtype = pl.Utf8
                series = pl.Series(col_name, var_ld[table_name][col_name], dtype=dtype)
                seriess[table_name].append(series)
        return seriess

    def run_df(self, dfs: Dict[str, pl.DataFrame]) -> Dict[str, pl.DataFrame]:
        from ..consts import VARIANT_LEVEL
        from ..consts import ERR_LEVEL

        seriess = self.get_series(dfs[VARIANT_LEVEL])
        for table_name, table_seriess in seriess.items():
            if table_name in dfs:
                if table_name == ERR_LEVEL:
                    dfs[table_name].vstack(pl.DataFrame(table_seriess), in_place=True)
                else:
                    dfs[table_name] = dfs[table_name].with_columns(table_seriess)
            else:
                dfs[table_name] = pl.DataFrame(table_seriess)
        return dfs
