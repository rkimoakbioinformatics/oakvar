# OakVar Dual License
# 
# Copyright (c) 2023 Oak Bioinformatics, LLC
# 
# This program is dual licensed under the Affero GPL-3.0 or later for 
# non-commercial and open source use, and under a commercial license, 
# which is available for purchase, for closed-source or commercial use.
# 
# For the commercial use, please contact Oak Bioinformatics, LLC 
# for obtaining such a license. OakVar commercial license does not impose 
# the Affero GPL open-source licensing terms, conditions, and limitations. 
# To obtain a commercial-use license of OakVar, please visit our website at
# https://oakbioinformatics.com or contact us at info@oakbioinformatics.com 
# for more information.
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
        self.module_name: str = ""
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

    def check_format(self, f, *args, **kwargs) -> bool:
        _ = f
        _ = args
        _ = kwargs
        return False

    def setup(self, *args, **kwargs):
        _ = args
        _ = kwargs

    def convert_line(self, *__args__, **__kwargs__) -> List[Dict[str, Any]]:
        return []

    def get_variant_lines(
        self, input_path: str, num_pool: int, start_line_no: int, batch_size: int
    ) -> Tuple[Dict[int, List[Tuple[int, Any]]], bool]:
        import linecache

        immature_exit: bool = False
        line_no: int = start_line_no
        end_line_no = line_no + num_pool * batch_size - 1
        lines: Dict[int, List[Tuple[int, Any]]] = {i: [] for i in range(num_pool)}
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

    def addl_operation_for_unique_variant(self, *args, **kwargs):
        _ = args
        _ = kwargs

    def get_extra_output_columns(self) -> List[Dict[str, Any]]:
        from ..module.local import get_module_conf

        conf = get_module_conf(self.module_name, module_type="converter")
        output_columns: List[Dict[str, Any]] = conf.get("extra_output_columns", [])
        return output_columns

