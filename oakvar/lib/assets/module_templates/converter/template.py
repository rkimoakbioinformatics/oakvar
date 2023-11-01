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

from typing import List
from typing import Dict
from oakvar import BaseConverter


class Converter(BaseConverter):
    def check_format(self, f) -> bool:
        """
        Detect the format of an input file.

        Arguments:
            f: a file handle to an input file
        Returns:
            bool: True if the input file is for this converter,
                  False if not.

        The example below checks if the input file's first line indicates
        VCF file format.
        """
        line = f.readline()
        return line.startswith("##fileformat=VCF")

    # If your converter module needs something else than
    # the standard way of opening a text input file,
    # read line by line, and coverting each line into
    # a list of dictionaries of variants,
    # you may want to start with modifying
    # convert_file method. In that case, uncomment
    # the below convert_file method and add your implementation.
    #
    # def convert_file(
    #     self, file, *__args__, exc_handler=None, **__kwargs__
    # ) -> Iterator[Tuple[int, List[dict]]]:
    #     line_no = 0
    #     for line in file:
    #         line_no += 1
    #         try:
    #             yield line_no, self.convert_line(line)
    #         except Exception as e:
    #             if exc_handler:
    #                 exc_handler(line_no, e)
    #             else:
    #                 raise e
    #     return None

    def convert_line(self, line) -> List[Dict]:
        """
        Converts a line from an input file to OakVar's variant dict.

        Arguments:
            l: a string of a line from an input file
        Returns:
            dict: a list of dicts, each dict for a variant collected
                  from the input line. Each dict should have
                  the following required fields:

                  chrom: chromosome name [str]
                  pos: chromosomal position [int]
                  ref_base: reference bases [str]
                  alt_base: altername bases [str]

                  Optional fields for each dict are:

                  sample_id: the ID or name of a sample having the variant [list[str]]
                  tags: a custom tag given to the variant [list[str]]
        """
        _ = line
        var_dicts = []
        var_dict = {
            "chrom": "chr1",
            "pos": 2878349,
            "ref_base": "A",
            "alt_base": "T",
            "sample_id": "sample1",
        }
        var_dicts.append(var_dict)
        return var_dicts
