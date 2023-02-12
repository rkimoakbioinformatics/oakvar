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

    def convert_line(self, l) -> List[Dict]:
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
        _ = l
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
