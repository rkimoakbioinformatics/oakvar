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

from oakvar import BasePostAggregator


class PostAggregator(BasePostAggregator):
    def annotate(self, input_data: dict) -> dict:
        """
        Returns a dict of the annotation result for an input variant.

        Parameters:
            input_data: a dict of the result by the annotation modules
                        run for the input variant. Depending on what
                        annotation modules were run, the fields of
                        this dict vary. For example,
                        base__uid, base__chrom, base__pos, ...

        Returns:
            dict: a dict of variant annotation.
        """
        assert input_data is not None
        out = {}
        return out


_ = PostAggregator
