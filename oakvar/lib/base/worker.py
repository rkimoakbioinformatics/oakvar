from typing import Optional
from typing import Any
from typing import List
from typing import Dict
from typing import Tuple
from typing import Union
import polars as pl
import ray
import numpy as np
import numpy.typing
from pathlib import Path
from .converter import BaseConverter
from ..consts import DEFAULT_CONVERTER_READ_SIZE
from .mapper import BaseMapper
from .annotator import BaseAnnotator


class Worker:
    def __init__(
        self,
        input_paths: Optional[List[str]] = None,
        converter: Optional[BaseConverter] = None,
        mapper: Optional[BaseMapper] = None,
        annotators: Optional[List[BaseAnnotator]] = None,
        converter_name: Optional[str] = None,
        mapper_name: Optional[str] = None,
        annotator_names: Optional[str] = None,
        ignore_sample: bool = False,
        run_conf: Dict[str, Dict[str, Any]] = {},
        genome: Optional[str] = None,
        dbpath: str = "",
        samples: Optional[List[str]] = None,
        batch_size: int = DEFAULT_CONVERTER_READ_SIZE,
        output: Optional[Dict[str, Dict[str, Any]]] = None,
        df_headers: Optional[Dict[str, Dict[str, pl.PolarsDataType]]] = None,
        offset_levels: List[str] = [],
        use_duckdb: bool = False,
    ):
        import duckdb
        import sqlite3
        from oakvar.lib.base.converter import BaseConverter
        from oakvar.lib.base.mapper import BaseMapper
        from oakvar.lib.base.annotator import BaseAnnotator
        from oakvar.lib.util.module import get_converter
        from oakvar.lib.util.module import get_mapper
        from oakvar.lib.util.module import get_annotator

        self.dfs: Dict[str, pl.DataFrame] = {}
        self.use_duckdb = use_duckdb
        self.batch_size: int = batch_size
        self.converter: BaseConverter
        self.annotators: List[BaseAnnotator]
        self.mapper: BaseMapper
        self.input_paths: Optional[List[str]] = input_paths
        self.fileno: int = 0
        self.dbpath = Path(dbpath)
        self.start_line_no: int = 1
        self.offset: int = 0
        self.offset_levels: List[str] = offset_levels
        if converter:
            self.converter = converter
        elif converter_name:
            self.converter = get_converter(
                converter_name,
                ignore_sample=ignore_sample,
                module_options=run_conf.get(converter_name, {}),
                genome=genome,
                output=output,
                df_headers=df_headers,
            )
            self.converter.setup_df(
                input_paths=input_paths,
                samples=samples,
                batch_size=batch_size,
                override=False,
            )
        else:
            raise Exception("converter instance or converter_name should be given.")
        if mapper:
            self.mapper = mapper
        elif mapper_name:
            self.mapper = get_mapper(mapper_name, use_duckdb=use_duckdb)
        else:
            raise Exception("mapper instance or mapper_name should be given.")
        if annotators:
            self.annotators = annotators
        elif annotator_names is not None:
            self.annotators = []
            for annotator_name in annotator_names:
                self.annotators.append(get_annotator(annotator_name))
        else:
            self.annotators = []
        self.uid_offset = 1
        self.conn: Optional[Union[duckdb.DuckDBPyConnection, sqlite3.Connection]] = None

    def setup_file(self, input_path: str, fileno: int = 0):
        self.fileno = fileno
        self.converter.setup_file(input_path, fileno=fileno)

    def run_df(self) -> bool:
        if not self.input_paths:
            return False
        if not self.converter.input_path:
            self.setup_file(self.input_paths[0], fileno=0)
        (
            lines,
            line_nos,
            num_lines,
            num_lines_by_batch,
            num_alts_by_batch,
            has_more_data,
        ) = self.converter.get_variant_lines(
            self.converter.input_path, num_core=1, batch_size=self.batch_size
        )
        if len(lines) == 0:
            return has_more_data
        if not num_alts_by_batch:
            num_alts_by_batch = [num_lines]
        self._run_df(lines, line_nos, num_lines, num_alts_by_batch[0])
        last_val: int = self.renumber_uid(self.offset)
        self.offset = last_val + 1
        if not has_more_data:
            if self.fileno < len(self.input_paths) - 1:
                self.fileno += 1
                self.setup_file(self.input_paths[self.fileno])
        return has_more_data

    def log_error(self, e: Exception, input_data: Dict[str, Any]) -> Tuple[Optional[str], int]:
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

    def _run_df(
        self,
        lines: numpy.typing.NDArray[Any],
        line_nos: numpy.typing.NDArray[np.int32],
        num_lines: int,
        total_num_alts: int,
    ):
        from ..consts import VARIANT_LEVEL
        from ..consts import VARIANT_LEVEL_PRIMARY_KEY
        from ..consts import GENE_LEVEL
        from ..consts import GENE_LEVEL_PRIMARY_KEY
        from ..consts import ERR_LEVEL
        from ..consts import FILENO_KEY
        from ..consts import LINENO_KEY
        from ..consts import ERRNO_KEY
        from ..consts import ERR_KEY
        from ..consts import LEVEL
        from ..util.run import initialize_err_series_data

        dfs = self.converter.get_dfs(lines, line_nos, num_lines, total_num_alts)
        if not dfs:
            return
        var_ld: Dict[str, Dict[str, List[Any]]] = {}
        var_ld[ERR_LEVEL] = initialize_err_series_data()
        counts: Dict[str, int] = {}
        max_counts: Dict[str, int] = {}
        module_sets = [[self.mapper], self.annotators]
        for module_set in module_sets:
            for module in module_set:
                output = module.output
                for table_name, col_names in module.col_names.items():
                    table_level = output.get(table_name, {}).get(LEVEL, module.conf.get(LEVEL, ""))
                    counts[table_name] = 0
                    df = dfs.get(table_level)
                    if df is not None:
                        max_counts[table_name] = df.height
                        var_ld[table_name] = {}
                        for col_name in col_names:
                            var_ld[table_name][col_name] = [None] * max_counts[table_name]
        df = dfs.get(VARIANT_LEVEL)
        if df is None:
            return
        mapper = self.mapper
        for input_data in df.iter_rows(named=True):
            input_level: str = VARIANT_LEVEL
            df = dfs.get(input_level)
            if df is None:
                continue
            try:
                output_dict = mapper.map(input_data)
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
            keycol: str
            if module.input_level == GENE_LEVEL:
                df = dfs.get(GENE_LEVEL)
                keycol = GENE_LEVEL_PRIMARY_KEY
            else:
                df = dfs.get(VARIANT_LEVEL)
            for module_set in module_sets:
                for module in module_set:
                    input_level: str = module.input_level
                    df = dfs.get(input_level)
                    if hasattr(module, "map"):
                        func = module.map
                    else:
                        func = module.annotate
                    if df is None:
                        continue
                    keycol: str
                    if module.input_level == GENE_LEVEL:
                        df = dfs.get(GENE_LEVEL)
                        keycol = GENE_LEVEL_PRIMARY_KEY
                    else:
                        df = dfs.get(VARIANT_LEVEL)
                    output_dict: Dict[str, List[Dict[str, Any]]] = {}
                    if input_data["alt_base"] in ["*", ".", ""]:
                        counts[VARIANT_LEVEL] += 1
                    else:
                        try:
                            output_dict = func(input_data)
                        except Exception as e:
                            err, errno = module.log_error(e, input_data)
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
                for row in df.iter_rows(named=True):
                    keyval: Any = row[keycol]
                    if self.secondary_data_required:
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
                                    if keycol not in table_row:
                                        table_ld[keycol] = keyval
                                if table_name == self.level:
                                    counts[table_name] += 1
                                elif table_data:
                                    counts[table_name] += 1
                                if counts[table_name] == table_max_count:
                                    for col_name, table_col_ld in table_ld.items():
                                        table_col_ld.extend([None] * df.height)
                                    max_counts[table_name] += df.height
                        else:
                            table_name = self.module_name
                            if self.module_name == "biogrid":
                                import pdb; pdb.set_trace()
                            table_ld = var_ld[table_name]
                            table_count = counts[table_name]
                            table_max_count = max_counts[table_name]
                            for col_name, value in output_dict.items():
                                table_ld[col_name][table_count] = value
                            if keycol not in output_dict:
                                table_ld[keycol][table_count] = keyval
                            counts[table_name] += 1
                            if counts[table_name] == table_max_count:
                                for col_name, table_col_ld in table_ld.items():
                                    table_col_ld.extend([None] * df.height)
                                max_counts[table_name] += df.height
        try:
            dfs = self.mapper.run_df(dfs, var_ld)
        except Exception:
            import traceback

            traceback.print_exc()
            return
        for m in self.annotators:
            dfs = m.run_df(dfs)
        self.dfs = dfs

    def renumber_uid(self, offset: int) -> int:
        from ..consts import VARIANT_LEVEL
        from ..consts import VARIANT_LEVEL_PRIMARY_KEY
        from ..consts import SAMPLE_LEVEL_KEY

        last_val: int = 0
        for table_name, df in self.dfs.items():
            if table_name in self.offset_levels or table_name.startswith(
                SAMPLE_LEVEL_KEY
            ):
                if df.height == 0:
                    if table_name == VARIANT_LEVEL:
                        last_val = 0
                else:
                    df.replace(
                        VARIANT_LEVEL_PRIMARY_KEY,
                        df[VARIANT_LEVEL_PRIMARY_KEY] + offset,
                    )
                    if table_name == VARIANT_LEVEL:
                        last_val = df[VARIANT_LEVEL_PRIMARY_KEY][-1]
        return last_val

    def save_df(self, dbpath: Path):
        import sqlite3
        from ..util.run import open_result_database
        from ..consts import GENE_LEVEL

        if not self.conn:
            self.conn = open_result_database(dbpath, self.use_duckdb)
        for table_name, df in self.dfs.items():
            table_col_names_str = ", ".join([f'"{v}"' for v in df.columns])
            values_str = ", ".join(["?"] * len(df.columns))
            if isinstance(self.conn, sqlite3.Connection):
                if table_name == GENE_LEVEL:
                    q = f"insert or ignore into {table_name} ({table_col_names_str}) values ({values_str})"
                else:
                    q = f"insert into {table_name} ({table_col_names_str}) values ({values_str})"
                for row in df.iter_rows():
                    self.conn.execute(q, row)
            else:
                if table_name == GENE_LEVEL:
                    self.conn.sql(
                        f"insert into {table_name} select * from df on conflict do nothing"
                    )
                else:
                    self.conn.sql(f"insert into {table_name} select * from df")
            self.conn.commit()
        if not isinstance(self.conn, sqlite3.Connection):
            self.conn.close()
        self.dfs = {}

    def close_db(self):
        if self.conn:
            self.conn.close()

    def get_conversion_stats(self):
        return self.converter.get_conversion_stats()


@ray.remote
class ParallelWorker(Worker):
    def run_df(
        self,
        actor_num: int,
        num_actors: int,
        num_lines: int,
        num_lines_by_batch: Optional[List[int]],
        num_alts_by_batch: Optional[List[int]],
        lines: numpy.typing.NDArray[Any],
        line_nos: numpy.typing.NDArray[np.int32],
    ):
        import math

        batch_size: int = math.ceil(num_lines / num_actors)
        start_line_no: int
        end_line_no: int
        if num_lines_by_batch is not None:
            if actor_num == 0:
                start_line_no = 0
            else:
                start_line_no: int = sum(num_lines_by_batch[:actor_num - 1])
            if num_actors > 1:
                end_line_no: int = sum(num_lines_by_batch[:actor_num])
            else:
                end_line_no = num_lines
        else:
            start_line_no: int = actor_num * batch_size
            end_line_no: int = min((actor_num + 1) * batch_size, num_lines)
        num_lines_batch: int = end_line_no - start_line_no
        if num_alts_by_batch:
            num_alts = num_alts_by_batch[actor_num]
        else:
            num_alts = num_lines
        return self._run_df(
            lines[start_line_no:end_line_no],
            line_nos[start_line_no:end_line_no],
            num_lines_batch,
            num_alts,
        )
