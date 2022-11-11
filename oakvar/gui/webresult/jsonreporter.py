from oakvar import BaseReporter
import sys


class Reporter(BaseReporter):
    def __init__(self, args):
        self.no_log = True
        self.no_status_update = True
        self.levels_to_write = None
        self.data = {}
        self.keep_json_all_mapping = True
        self.data = {}
        super().__init__(args)

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


def main():
    reporter = Reporter(sys.argv)
    reporter.run()
