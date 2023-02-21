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
