from typing import Optional
from typing import Any
from typing import List
from typing import Dict
from typing import Tuple
import polars as pl
import ray
from pathlib import Path
from .converter import BaseConverter
from .mapper import BaseMapper
from .annotator import BaseAnnotator


class OakVarRunner:
    def __init__(self, converter: BaseConverter, mapper: BaseMapper, annotators: List[BaseAnnotator]):
        from oakvar.lib.base.converter import BaseConverter
        from oakvar.lib.base.mapper import BaseMapper
        from oakvar.lib.base.annotator import BaseAnnotator

        self.dfs: Dict[str, pl.DataFrame] = {}
        self.converter: BaseConverter = converter
        self.mapper: BaseMapper = mapper
        self.annotators: List[BaseAnnotator] = annotators

    def setup_df(self, input_paths: List[str], samples: Optional[List[str]] = None):
        self.converter.setup_df(input_paths=input_paths, samples=samples)

    def setup_df_file(self, input_path: str, fileno: int):
        self.converter.setup_df_file(input_path, fileno)

    def run_df(self, lines_data: List[Tuple[str, int]], uid_start: int, fileno: int) -> int:
        return self.run_df_single(lines_data, uid_start, fileno)

    def run_df_single(self, lines_data: List[Tuple[str, int]], uid_start: int, fileno: int) -> int:
        from ..consts import VARIANT_LEVEL

        dfs = self.converter.get_dfs(fileno, lines_data, uid_start)
        dfs = self.mapper.run_df(dfs)
        for m in self.annotators:
            dfs = m.run_df(dfs)
        self.dfs = dfs
        return self.dfs[VARIANT_LEVEL].height

    def renumber_uid(self, uid_offset: int):
        from ..consts import VARIANT_LEVEL
        from ..consts import VARIANT_LEVEL_PRIMARY_KEY

        self.dfs[VARIANT_LEVEL].replace(VARIANT_LEVEL_PRIMARY_KEY, self.dfs[VARIANT_LEVEL][VARIANT_LEVEL_PRIMARY_KEY] + uid_offset)
        return self.dfs[VARIANT_LEVEL][VARIANT_LEVEL_PRIMARY_KEY][-1]

    def save_df(self, dbpath: Path, use_duckdb: bool=False):
        from ..util.run import open_result_database
        from ..consts import GENE_LEVEL

        conn = open_result_database(dbpath, use_duckdb)
        for table_name, df in self.dfs.items():
            table_col_names_str = ", ".join(df.columns)
            values_str = ", ".join(["?"] * len(df.columns))
            if table_name == GENE_LEVEL:
                q = f"insert or ignore into {table_name} ({table_col_names_str}) values ({values_str})"
            else:
                q = f"insert into {table_name} ({table_col_names_str}) values ({values_str})"
            for row in df.iter_rows():
                conn.execute(q, row)
        conn.commit()
        conn.close()

    def get_conversion_stats(self):
        return self.converter.get_conversion_stats()

@ray.remote
class MultiRunner(OakVarRunner):
    def __init__(self, converter_name: str, mapper_name: str, annotator_names: List[str], ignore_sample: bool, run_conf: Dict[str, Any]):
        from oakvar.lib.util.module import get_converter
        from oakvar.lib.util.module import get_mapper
        from oakvar.lib.util.module import get_annotator
        from oakvar.lib.base.converter import BaseConverter
        from oakvar.lib.base.mapper import BaseMapper
        from oakvar.lib.base.annotator import BaseAnnotator

        self.dfs: Dict[str, pl.DataFrame] = {}
        self.converter: BaseConverter = get_converter(converter_name, ignore_sample=ignore_sample, module_options=run_conf.get(converter_name, {}))
        self.mapper: BaseMapper = get_mapper(mapper_name)
        self.annotators: List[BaseAnnotator] = []
        for module_name in annotator_names:
            self.annotators.append(get_annotator(module_name))

    def run_df(self, actor_num: int, lines_datas: Dict[int, List[Tuple[str, int]]], uid_start: int, fileno: int) -> int:
        lines_data: List[Tuple[str, int]] = lines_datas[actor_num]
        return self.run_df_single(lines_data, uid_start, fileno)

