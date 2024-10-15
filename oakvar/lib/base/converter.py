# OakVar
#
# Copyright (c) 2024 Oak Bioinformatics, LLC
#
# All rights reserved.
#
# Do not distribute or use this software without obtaining
# a license from Oak Bioinformatics, LLC.
#
# Do not use this software to develop another software
# which competes with the products by Oak Bioinformatics, LLC,
# without obtaining a license for such use from Oak Bioinformatics, LLC.
#
# For personal use of non-commercial nature, you may use this software
# after registering with `ov store account create`.
#
# For research use of non-commercial nature, you may use this software
# after registering with `ov store account create`.
#
# For use by commercial entities, you must obtain a commercial license
# from Oak Bioinformatics, LLC. Please write to info@oakbioinformatics.com
# to obtain the commercial license.
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
from typing import Union


class BaseConverter(object):
    IGNORE = "converter_ignore"

    def __init__(
        self,
        name: Optional[str] = None,
        title: Optional[str] = None,
        module_conf: dict = {},
        module_options: dict = {},
        ignore_sample: bool = False,
        code_version: Optional[str] = None,
    ):
        self.module_type = "converter"
        self.format_name = None
        self.output_dir = None
        self.run_name = None
        self.module_name: str = ""
        self.version = None
        self.conf: dict = module_conf
        self.input_path: str = ""
        self.input_paths: Optional[List[str]] = None
        self.ignore_sample: bool = ignore_sample
        self.header_num_line: int = 0
        self.line_no: int = 0
        if name:
            self.module_name = name
        self.title = title
        if not self.conf and self.title:
            self.conf["title"] = self.title
        elif self.conf and "title" in self.conf:
            self.title = self.conf["title"]
        if module_conf:
            self.conf.update(module_conf)
        self.module_options = module_options
        if code_version:
            self.code_version: str = code_version
        else:
            if "code_version" in self.conf:
                self.code_version: str = self.conf["version"]
            elif "version" in self.conf:
                self.code_version: str = self.conf["version"]
            else:
                self.code_version: str = ""

    def check_format(self, input_path, *args, **kwargs) -> bool:
        _ = input_path
        _ = args
        _ = kwargs
        ret = False
        return ret

    def setup(self, *args, **kwargs):
        _ = args
        _ = kwargs

    def convert_line(self, line, *args, **kwargs) -> Union[str, List[Dict[str, Any]]]:
        _ = line
        _ = args
        _ = kwargs
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
