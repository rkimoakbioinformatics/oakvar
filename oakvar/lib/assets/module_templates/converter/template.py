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
