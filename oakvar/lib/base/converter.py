from typing import Optional
from typing import Tuple
from typing import List
from typing import Iterator


class BaseConverter(object):
    IGNORE = "converter_ignore"

    def __init__(self):
        self.format_name = None
        self.output_dir = None
        self.run_name = None
        self.module_name: Optional[str] = None
        self.version = None
        self.conf: dict = {}
        self.input_path = ""
        self.input_paths: Optional[List[str]] = None

    def check_format(self, *__args__, **__kwargs__):
        pass

    def setup(self, *__args__, **__kwargs__):
        pass

    def convert_line(self, *__args__, **__kwargs__) -> List[dict]:
        return []

    def convert_file(
        self, file, *__args__, exc_handler=None, **__kwargs__
    ) -> Iterator[Tuple[int, List[dict]]]:
        line_no = 0
        for line in file:
            line_no += 1
            try:
                yield line_no, self.convert_line(line)
            except Exception as e:
                if exc_handler:
                    exc_handler(line_no, e)
                else:
                    raise e
        return None

    def addl_operation_for_unique_variant(self, __wdict__, __wdict_no__):
        pass
