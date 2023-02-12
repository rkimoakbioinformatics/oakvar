from typing import Optional
from oakvar import BaseAnnotator


class Annotator(BaseAnnotator):
    def annotate(self, input_data: dict, secondary_data: Optional[dict] = None):
        assert input_data is not None
        _ = secondary_data
        out = {}
        return out
