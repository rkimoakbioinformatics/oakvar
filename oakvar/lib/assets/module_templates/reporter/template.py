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

from oakvar import BaseReporter
from typing import Union
from typing import Any
from typing import Dict
from typing import List


class Reporter(BaseReporter):
    """Reporter module template."""

    def write_preface(self, level: str):
        """Method to set up output files and write "preface".
        Preface means content before the headers for output columns.
        Opening an output file and saving the file handler should be done
        in this method.

        Args:
            level (str): Level of reporting. For example, "variant" or "gene".
        """
        _ = level
        pass

    def write_header(self, level: str):
        """Method to write column headers.
        This method is supposed to write column headers.
        The file handler saved in write_preface method is supposed to be
        used here to write column headers.

        Args:
            level (str): Level of reporting. For example, "variant" or "gene".
        """
        _ = level
        pass

    def write_table_row(self, row: Union[Dict[str, Any], List[Any]]):
        """Method to write annotation results.

        The file handler saved in write_preface method is supposed to be
        used here to write column headers.

        Variants are sent to this method one by one as `row`. It is either
        a dictionary or a list. If `self.dictrow` is `True`, a dict will be
        passed to this method. If not, a list will. The dict's keys will be
        output column names. If a list is passed, `self.columns` will have
        the column information in the same order as in the list.

        Args:
            row (Union[Dict[str, Any], List[Any]]): annotation result for a variant.
        """
        _ = row
        pass
