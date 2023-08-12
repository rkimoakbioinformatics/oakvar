from typing import Optional
from typing import Any
from typing import List
from typing import Dict
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
        print(f"@ getting lines")
        (
            lines,
            line_nos,
            num_lines,
            total_num_alts,
            has_more_data,
        ) = self.converter.get_variant_lines(
            self.converter.input_path, num_core=1, batch_size=self.batch_size
        )
        if not lines:
            return has_more_data
        print(f"@ num_lines={num_lines}, total_num_alts={total_num_alts}, len lines={len(lines)}")
        if not total_num_alts:
            total_num_alts = [num_lines]
        print(f"@ running _run_df")
        self._run_df(lines, line_nos, num_lines, total_num_alts[0])
        print(f"@ renumbering")
        last_val: int = self.renumber_uid(self.offset)
        print(f"@ setup_file...")
        self.offset = last_val + 1
        if not has_more_data:
            if self.fileno < len(self.input_paths) - 1:
                self.fileno += 1
                self.setup_file(self.input_paths[self.fileno])
        print(f"@ done")
        return has_more_data

    def _run_df(
        self,
        lines: numpy.typing.NDArray[Any],
        line_nos: numpy.typing.NDArray[np.int32],
        num_lines: int,
        total_num_alts: int,
    ):
        print(f"@ getting converter dfs")
        dfs = self.converter.get_dfs(lines, line_nos, num_lines, total_num_alts)
        print(f"@ after converter dfs={dfs}")
        if not dfs:
            return
        try:
            print(f"@ getting mapper dfs")
            dfs = self.mapper.run_df(dfs)
        except Exception:
            import traceback

            traceback.print_exc()
            return
        for m in self.annotators:
            print(f"@ getting {m} dfs")
            dfs = m.run_df(dfs)
        self.dfs = dfs

    def renumber_uid(self, offset: int) -> int:
        from ..consts import VARIANT_LEVEL
        from ..consts import VARIANT_LEVEL_PRIMARY_KEY
        from ..consts import SAMPLE_LEVEL_KEY

        last_val: int = 0
        print(f"@ offset_levels={self.offset_levels}, dfs={self.dfs}")
        for table_name, df in self.dfs.items():
            print(f"@ table_name={table_name}")
            if table_name in self.offset_levels or table_name.startswith(
                SAMPLE_LEVEL_KEY
            ):
                print(f"@ => to renumber. df={df}")
                if df.height == 0:
                    if table_name == VARIANT_LEVEL:
                        last_val = 0
                else:
                    print(f"@ => renumbering {table_name}")
                    df.replace(
                        VARIANT_LEVEL_PRIMARY_KEY,
                        df[VARIANT_LEVEL_PRIMARY_KEY] + offset,
                    )
                    if table_name == VARIANT_LEVEL:
                        last_val = df[VARIANT_LEVEL_PRIMARY_KEY][-1]
                    print(f"@ => last_val={last_val}")
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
            print(f"@ table_name={table_name}, df={df.columns}")
            if isinstance(self.conn, sqlite3.Connection):
                if table_name == GENE_LEVEL:
                    q = f"insert or ignore into {table_name} ({table_col_names_str}) values ({values_str})"
                else:
                    q = f"insert into {table_name} ({table_col_names_str}) values ({values_str})"
                print(f"@ q={q}")
                for row in df.iter_rows():
                    print(f"@ row={row}")
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
        print(f"@ actor_num={actor_num}, batch_size={batch_size}, num_lines_batch={num_lines_batch}, total_num_alts={num_alts_by_batch}, num_alts={num_alts}, len lines={len(lines)}, start_line_no={start_line_no}, end_line_no={end_line_no}")
        return self._run_df(
            lines[start_line_no:end_line_no],
            line_nos[start_line_no:end_line_no],
            num_lines_batch,
            num_alts,
        )
