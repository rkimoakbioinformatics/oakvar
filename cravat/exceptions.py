class ExpectedException(Exception):
    halt = None

class NormalExit(ExpectedException):
    pass

class NoGenomeException(ExpectedException):
    def __init__(self):
        super().__init__("error: genome assembly should be selected.")
        self.halt = True

class InvalidGenomeAssembly(ExpectedException):
    def __init__(self, genome_assembly):
        super().__init__(f"error: {genome_assembly} is an invalid genome assembly.")
        self.halt = True

class InvalidData(ExpectedException):
    nolog = True

class ConfigurationError(ExpectedException):
    pass


class BadFormatError(InvalidData):
    pass


class LiftoverFailure(InvalidData):
    pass


class FileIntegrityError(Exception):
    def __init__(self, path):
        super().__init__(path)


class KillInstallException(ExpectedException):
    pass


class InvalidFilter(ExpectedException):
    notraceback = True

    def __init__(self, wrong_samples, wrong_colnames):
        self.msg = []
        if len(wrong_samples) > 0:
            self.msg.append(
                "Filter sample names do not exist: " + " ".join(wrong_samples)
            )
        if len(wrong_colnames) > 0:
            self.msg.append(
                "Filter column names do not exist: " + " ".join(wrong_colnames)
            )

    def __str__(self):
        return str(self.msg)


class InvalidModule(ExpectedException):
    def __init__(self, module_name):
        super().__init__("error: module [{}] does not exist.".format(module_name))


class NoVariantError(ExpectedException):
    def __init__(self):
        super().__init__("Reference and alternate alleles are the same.")

class NoInputException(ExpectedException):
    def __init__(self):
        super().__init__("error: no input was given.")

class SystemMissingException(ExpectedException):
    def __init__(self, msg=""):
        if msg is not None and msg != "":
            msg = f"OakVar is not ready ({msg}). 'ov system setup' to set up OakVar."
        else:
            msg = f"OakVar is not ready. 'ov system setup' to set up OakVar."
        super().__init__(msg)