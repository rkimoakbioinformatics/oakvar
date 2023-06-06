from typing import Optional
from typing import Any
from typing import List
from typing import Dict
import polars as pl
from .commonmodule import BaseCommonModule


class BaseMapper(object):
    def __init__(
        self,
        name: str = "",
        primary_transcript: List[str] = ["mane"],
        serveradmindb=None,
        module_options: Dict = {},
        output_columns: List[Dict[str, Any]] = [],
        wgs_reader: Optional[BaseCommonModule] = None,
    ):
        from time import time
        from pathlib import Path
        import sys
        from ..module.local import get_module_conf

        self.wgs_reader = wgs_reader
        self.module_options: Dict = module_options
        self.primary_transcript_paths: List[str] = [v for v in primary_transcript if v]
        self.primary_transcript = primary_transcript
        self.serveradmindb = serveradmindb
        self.logger = None
        self.error_logger = None
        self.col_names: List[str] = []
        self.full_col_names: Dict[str, str] = {}
        self.unique_excs = []
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
        self.set_output_columns(output_columns)
        self.var_ld: Dict[str, List[Any]] = {}
        self.df_dtypes: Dict[str, Any] = {}
        self.setup()
        self.extra_setup()
        self.setup_df()

    def set_output_columns(self, output_columns: List[Dict[str, Any]] = []):
        from ..util.util import get_crv_def
        from ..util.util import get_crx_def

        if output_columns:
            self.output_columns = output_columns.copy()
            self.conf["output_columns"] = self.output_columns.copy()
        elif "output_columns" in self.conf:
            self.output_columns = self.conf["output_columns"].copy()
        else:
            self.output_columns = get_crx_def().copy()
            self.conf["output_columns"] = self.output_columns.copy()
        crv_col_names = [col_def.get("name") for col_def in get_crv_def()]
        self.col_names = [
            v.get("name", "")
            for v in self.output_columns
            if v.get("name") not in crv_col_names
        ]

    def setup(self):
        raise NotImplementedError("Mapper must have a setup() method.")

    def extra_setup(self):
        pass

    def end(self):
        pass

    def setup_logger(self):
        from logging import getLogger

        self.logger = getLogger("oakvar.mapper")
        self.error_logger = getLogger("err." + self.module_name)

    def map(self, crv_data: dict):
        _ = crv_data

    def add_crx_to_gene_info(self, crx_data):
        from ..util.inout import AllMappingsParser

        tmap_json = crx_data["all_mappings"]
        # Return if no tmap
        if tmap_json == "":
            return
        tmap_parser = AllMappingsParser(tmap_json)
        for hugo in tmap_parser.get_genes():
            self.gene_info[hugo] = True

    def log_runtime_error(self, ln, line, e, fn=None):
        import traceback

        _ = line
        err_str = traceback.format_exc().rstrip()
        if (
            self.logger is not None
            and self.unique_excs is not None
            and err_str not in self.unique_excs
        ):
            self.unique_excs.append(err_str)
            self.logger.error(err_str)
        if self.error_logger is not None:
            self.error_logger.error(f"{fn}:{ln}\t{str(e)}")

    async def get_gene_summary_data(self, cf):
        from ..util.util import get_crx_def
        from json import loads
        from ...gui.consts import result_viewer_num_var_limit_for_gene_summary_key
        from ...gui.consts import DEFAULT_RESULT_VIEWER_NUM_VAR_LIMIT_FOR_GENE_SUMMARY
        from ..system import get_system_conf

        cols = [
            "base__" + coldef["name"]
            for coldef in get_crx_def()
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
        self.full_col_names = {
            col_name: f"{col_name}" for col_name in self.col_names if col_name != "uid"
        }
        self.df_dtypes = {}
        for col_def in self.output_columns:
            col_name = col_def.get("name")
            if not col_name or col_name not in self.col_names:
                continue
            if col_name == "uid":
                continue
            ty = col_def.get("type")
            if ty == "string":
                dtype = pl.Utf8
            elif ty == "int":
                dtype = pl.Int64
            elif ty == "float":
                dtype = pl.Float64
            else:
                dtype = pl.Utf8
            self.df_dtypes[self.full_col_names[col_name]] = dtype

    def get_series(self, df: pl.DataFrame) -> List[pl.Series]:
        for full_col_name in self.full_col_names:
            self.var_ld[full_col_name] = []
        for input_data in df.iter_rows(named=True):
            if input_data["alt_base"] in ["*", ".", ""]:
                output_dict = {}
            else:
                output_dict = self.map(input_data)
            for col_name in self.col_names:
                if not output_dict:
                    self.var_ld[self.full_col_names[col_name]].append(None)
                else:
                    if col_name in self.var_ld:
                        self.var_ld[self.full_col_names[col_name]].append(
                            output_dict.get(col_name)
                        )
                    else:
                        self.var_ld[self.full_col_names[col_name]].append(None)
        seriess = []
        for full_col_name in self.full_col_names:
            seriess.append(
                pl.Series(
                    full_col_name,
                    self.var_ld[full_col_name],
                    dtype=self.df_dtypes[full_col_name],
                ),
            )
        return seriess

    def run_df(self, df: pl.DataFrame) -> pl.DataFrame:
        seriess = self.get_series(df)
        df = df.with_columns(seriess) # type: ignore
        return df

