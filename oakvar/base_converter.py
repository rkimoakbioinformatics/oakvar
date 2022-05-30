class BaseConverter(object):
    IGNORE = "converter_ignore"

    def __init__(self):
        self.format_name = None
        self.output_dir = None
        self.run_name = None
        self.input_assembly = None
        self.format_name = None
        self.module_name = None

    def check_format(self, *__args__, **__kwargs__):
        raise NotImplemented

    def setup(self, *__args__, **__kwargs__):
        raise NotImplemented

    def convert_line(self, *__args__, **__kwargs__):
        raise NotImplemented

    def convert_file(self, file, *__args__, exc_handler=None, **__kwargs__):
        ln = 0
        for line in file:
            ln += 1
            try:
                yield ln, line, self.convert_line(line)
            except Exception as e:
                if exc_handler:
                    exc_handler(ln, line, e)
                    continue
                else:
                    raise e

    def addl_operation_for_unique_variant(self, __wdict__, __wdict_no__):
        pass
