from oakvar import BasePreparer


class Preparer(BasePreparer):
    def prepare(self, input_data: dict):
        self.writer.write_data(input_data)

    def postloop(self):
        pass


_ = Preparer
