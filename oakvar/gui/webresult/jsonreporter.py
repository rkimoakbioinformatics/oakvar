from oakvar import BaseReporter


class Reporter(BaseReporter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.no_log = True
        self.levels_to_write = None
        self.data = {}
        self.keep_json_all_mapping = True
        self.data = {}
        self.dictrow = True

    def write_preface(self, level):
        self.data[level] = []
        self.level = level

    def write_table_row(self, row):
        self.data[self.level].append(
            [row[col] for col in self.columns_to_report[self.level]]
        )

    def end(self):
        info = {}
        norows = len(self.data[self.level])
        info["norows"] = norows
        self.data["info"] = info
        self.data["colinfo"] = self.colinfo
        self.data["total_norows"] = self.total_norows
        return self.data
