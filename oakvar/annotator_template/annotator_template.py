import sys
from oakvar import BaseAnnotator


class Annotator(BaseAnnotator):
    def setup(self):
        pass

    def annotate(self, input_data, secondary_data=None):
        out = {}
        out["uid"] = input_data.get("uid")
        if secondary_data:
            out["secondary_uid"] = secondary_data.get("uid")
        return out

    def cleanup(self):
        pass


if __name__ == "__main__":
    annotator = Annotator(sys.argv)
    annotator.run()
