from typing import Optional
from typing import Any
from typing import List
from typing import Dict
from typing import Tuple
import polars as pl
import ray
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

    def setup_file(self, input_path: str, fileno: int = 0):
        self.fileno = fileno
        self.converter.setup_file(input_path, fileno=fileno)

    def run_df(self) -> bool:
        if not self.input_paths:
            return False
        if not self.converter.input_path:
            self.setup_file(self.input_paths[0], fileno=0)
        lines_data, has_more_data = self.converter.get_variant_lines(
            self.converter.input_path, num_core=1
        )
        #if self.converter.start_line_no < 3800:
        #    return True
        self._run_df(lines_data[0])
        last_val: int = self.renumber_uid(self.offset)
        self.offset = last_val + 1
        if not has_more_data:
            if self.fileno < len(self.input_paths) - 1:
                self.fileno += 1
                self.setup_file(self.input_paths[self.fileno])
        return has_more_data

    def _run_df(self, lines_data: List[Tuple[str, int]]):
        dfs = self.converter.get_dfs(lines_data)
        if not dfs:
            return
        try:
            dfs = self.mapper.run_df(dfs)
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

        last_val: int = 0
        for level in self.offset_levels:
            if level not in self.dfs:
                continue
            if self.dfs[level].height == 0:
                if level == VARIANT_LEVEL:
                    last_val = 0
            else:
                self.dfs[level].replace(
                    VARIANT_LEVEL_PRIMARY_KEY,
                    self.dfs[level][VARIANT_LEVEL_PRIMARY_KEY] + offset,
                )
                if level == VARIANT_LEVEL:
                    last_val = self.dfs[level][VARIANT_LEVEL_PRIMARY_KEY][-1]
        return last_val

    def save_df(self, dbpath: Path):
        import sqlite3
        from ..util.run import open_result_database
        from ..consts import GENE_LEVEL

        conn = open_result_database(dbpath, self.use_duckdb)
        for table_name, df in self.dfs.items():
            table_col_names_str = ", ".join(df.columns)
            values_str = ", ".join(["?"] * len(df.columns))
            if isinstance(conn, sqlite3.Connection):
                if table_name == GENE_LEVEL:
                    q = f"insert or ignore into {table_name} ({table_col_names_str}) values ({values_str})"
                else:
                    q = f"insert into {table_name} ({table_col_names_str}) values ({values_str})"
                for row in df.iter_rows():
                    conn.execute(q, row)
            else:
                if table_name == GENE_LEVEL:
                    conn.sql(
                        f"insert into {table_name} select * from df on conflict do nothing"
                    )
                else:
                    conn.sql(f"insert into {table_name} select * from df")
            conn.commit()
        conn.close()
        self.dfs = {}

    def get_conversion_stats(self):
        return self.converter.get_conversion_stats()


@ray.remote
class ParallelWorker(Worker):
    def run_df(self, actor_num: int, lines_datas: Dict[int, List[Tuple[str, int]]]):
        lines_data: List[Tuple[str, int]] = lines_datas[actor_num]
        return self._run_df(lines_data)
