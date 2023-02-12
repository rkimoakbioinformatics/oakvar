from oakvar import BaseReporter


class Reporter(BaseReporter):
    def write_preface(self, level):
        _ = level
        pass

    def write_header(self, level):
        _ = level
        pass

    def write_table_row(self, row):
        _ = row
        pass
