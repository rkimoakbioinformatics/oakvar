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
        self.format_name = None
        self.module_name: Optional[str] = None
        self.version = None
        self.conf: dict = {}

    def check_format(self, *__args__, **__kwargs__):
        pass

    def setup(self, *__args__, **__kwargs__):
        pass

    def convert_line(self, *__args__, **__kwargs__) -> List[dict]:
        return []

    def convert_file(self, file, *__args__, exc_handler=None, **__kwargs__) -> Iterator[Tuple[int, str, List[dict]]]:
        ln = 0
        for line in file:
            ln += 1
            try:
                yield ln, line, self.convert_line(line)
            except Exception as e:
                if exc_handler:
                    exc_handler(file, ln, line, e)
                    continue
                else:
                    raise e
        return None

    def addl_operation_for_unique_variant(self, __wdict__, __wdict_no__):
        pass
