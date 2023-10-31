# OakVar Dual License
# 
# Copyright (c) 2023 Oak Bioinformatics, LLC
# 
# This program is dual licensed under the Affero GPL-3.0 or later for non-commercial, 
# open source use, and a commercial license, which is available for purchase, 
# for commercial use.
# 
# For commercial use, please contact Oak Bioinformatics, LLC for obtaining a
# commercial license. OakVar commercial license does not impose the Affero GPL
# open-source licensing terms, conditions, and limitations. To obtain a
# commercial-use license of OakVar, please visit our website at
# https://oakbioinformatics.com or contact us at info@oakbioinformatics.com for
# more information.
# 
# ================
# OpenCRAVAT
# 
# MIT License
# 
# Copyright (c) 2021 KarchinLab
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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
