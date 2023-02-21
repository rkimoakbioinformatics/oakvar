from oakvar import BaseReporter


class Reporter(BaseReporter):
    def __init__(self, *args, **kwargs):
        self.no_log = True
        self.levels_to_write = None
        self.data = {}
        self.keep_json_all_mapping = True
        self.data = {}
        if kwargs:
            super().__init__(**kwargs)
        if args and isinstance(args[0], dict):
            super().__init__(**args[0])

    def write_preface(self, level):
        self.data[level] = []
        self.level = level

    def write_table_row(self, row):
        self.data[self.level].append(
            [row[col] for col in self.colnames_to_display[self.level]]
        )

    def end(self):
        info = {}
        norows = len(self.data[self.level])
        info["norows"] = norows
        self.data["info"] = info
        self.data["colinfo"] = self.colinfo
        self.data["warning_msgs"] = self.warning_msgs
        self.data["total_norows"] = self.total_norows
        return self.data
