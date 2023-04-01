from typing import Optional
from typing import Tuple
from typing import List
from typing import Iterator


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
        self.input_path = ""
        self.input_paths: Optional[List[str]] = None
        self.ignore_sample: bool = ignore_sample
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

    def convert_line(self, *__args__, **__kwargs__) -> List[dict]:
        return []

    def convert_file(
        self,
        f,
        logger,
        error_logger,
        serveradmindb,
        input_path,
        input_fname,
        unique_excs,
        err_holder,
        *__args__,
        exc_handler=None,
        batch_size: int = 0,
        core_num: int = 0,
        start_line: int = 0,
        **__kwargs__,
    ) -> Iterator[Tuple[int, List[dict]]]:
        import linecache

        line_no = start_line + batch_size * core_num + 1
        end_line_no = line_no + batch_size - 1 if batch_size else 0
        if not input_path:
            input_path = f.name
        while True:
            line = linecache.getline(input_path, line_no)
            # print(f"@ core_num={core_num}. line_no={line_no}. line={line[:-1]}")
            if not line:
                break
            line = line[:-1]
            try:
                yield line_no, self.convert_line(line)
            except Exception as e:
                if exc_handler:
                    exc_handler(
                        logger,
                        error_logger,
                        serveradmindb,
                        input_path,
                        input_fname,
                        line_no,
                        e,
                        unique_excs,
                        err_holder,
                    )
                else:
                    raise e
            if line_no >= end_line_no:
                break
            line_no += 1
        return None

    def addl_operation_for_unique_variant(self, __wdict__, __wdict_no__):
        pass

    def save(self, overwrite: bool = False, interactive: bool = False):
        from ..module.local import create_module_files

        create_module_files(self, overwrite=overwrite, interactive=interactive)
