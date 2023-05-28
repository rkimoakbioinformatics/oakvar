from typing import Optional
from typing import Any
from typing import List
from typing import Dict
from typing import Tuple


class BaseConverter(object):
    IGNORE = "converter_ignore"

    def __init__(
        self,
        name: Optional[str] = None,
        title: Optional[str] = None,
        module_conf: dict = {},
        ignore_sample: bool = False,
        code_version: Optional[str] = None,
    ):
        self.module_type = "converter"
        self.format_name = None
        self.output_dir = None
        self.run_name = None
        self.module_name: Optional[str] = None
        self.version = None
        self.conf: dict = {}
        self.input_path: str = ""
        self.input_paths: Optional[List[str]] = None
        self.ignore_sample: bool = ignore_sample
        self.header_num_line: int = 0
        self.line_no: int = 0
        if name:
            self.module_name = name
        self.title = title
        if self.title and self.conf is not None:
            self.conf["title"] = self.title
        elif self.conf and "title" in self.conf:
            self.title = self.conf["title"]
        if module_conf:
            self.conf = module_conf.copy()
        if code_version:
            self.code_version: str = code_version
        else:
            if "code_version" in self.conf:
                self.code_version: str = self.conf["version"]
            elif "version" in self.conf:
                self.code_version: str = self.conf["version"]
            else:
                self.code_version: str = ""

    def check_format(self, *__args__, **__kwargs__):
        pass

    def setup(self, *__args__, **__kwargs__):
        pass

    def convert_line(self, *__args__, **__kwargs__) -> List[Dict[str, Any]]:
        return []

    def get_variant_lines(
        self, input_path: str, mp: int, start_line_no: int, batch_size: int
    ) -> Tuple[Dict[int, List[Tuple[int, Any]]], bool]:
        import linecache

        immature_exit: bool = False
        line_no: int = start_line_no
        end_line_no = line_no + mp * batch_size - 1
        lines: Dict[int, List[Tuple[int, Any]]] = {i: [] for i in range(mp)}
        chunk_no: int = 0
        chunk_size: int = 0
        while True:
            line = linecache.getline(input_path, line_no)
            if not line:
                break
            line = line[:-1]
            lines[chunk_no].append((line_no, line))
            chunk_size += 1
            if line_no >= end_line_no:
                immature_exit = True
                break
            line_no += 1
            if chunk_size >= batch_size:
                chunk_no += 1
                chunk_size = 0
        return lines, immature_exit

    def prepare_for_mp(self):
        pass

    def write_extra_info(self, wdict: dict):
        _ = wdict
        pass

    def save(self, overwrite: bool = False, interactive: bool = False):
        from ..module.local import create_module_files

        create_module_files(self, overwrite=overwrite, interactive=interactive)

    def get_standardized_module_option(self, v: Any) -> Any:
        from ..util.run import get_standardized_module_option

        return get_standardized_module_option(v)
