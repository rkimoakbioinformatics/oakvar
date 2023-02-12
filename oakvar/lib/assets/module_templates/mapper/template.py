from oakvar import BaseMapper


class Mapper(BaseMapper):
    def map(self, input_data: dict) -> dict:
        """
        Returns a dict of the result of mapping an input variant
        to a gene model.

        Parameters:
            input_data: a dict of a variant. It should have the following
            fields:
                chrom: chromosome
                pos: position
                ref_base: reference bases
                alt_base: alternate bases

        Returns:
            dict: a dict of variant mapping. The following fields are
                  mandatory.
                  chrom: str
                  pos: int
                  ref_base: str
                  alt_base: str
                  transcript: primary transcript, str
                  so: sequence ontology of the input variant on
                      the primary transcript, [str]
                  cchange: cDNA change by the input variant on
                           the primary transcript, str
                  achange: amino acid change by the input variant on
                           the primary transcript, str
                  all_mappings: list, dict
        """
        assert input_data is not None
        out = {}
        return out
