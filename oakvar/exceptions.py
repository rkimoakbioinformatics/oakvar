class ExpectedException(Exception):
    halt = False
    traceback = False
    handled = False
    msg = ""
    returncode = 1

    def __init__(self, msg=""):
        self.msg = msg
        super().__init__(f"error: {msg}")


class NormalExit(ExpectedException):
    returncode = 0


class NoGenomeException(ExpectedException):

    def __init__(self):
        super().__init__("genome assembly should be selected.")
        self.halt = True


class InvalidGenomeAssembly(ExpectedException):

    def __init__(self, genome_assembly):
        super().__init__(f"{genome_assembly} is an invalid genome assembly.")
        self.halt = True


class InvalidData(ExpectedException):
    nolog = True


class ConfigurationError(ExpectedException):
    traceback = True


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
    traceback = False

    def __init__(self, wrong_samples, wrong_colnames):
        self.msg = []
        if len(wrong_samples) > 0:
            self.msg.append("Filter sample names do not exist: " +
                            " ".join(wrong_samples))
        if len(wrong_colnames) > 0:
            self.msg.append("Filter column names do not exist: " +
                            " ".join(wrong_colnames))

    def __str__(self):
        return str(self.msg)


class ModuleNotExist(ExpectedException):
    traceback = False
    halt = True
    returncode = 3

    def __init__(self, module_name):
        super().__init__("module [{}] does not exist.".format(module_name))


class InvalidModule(ExpectedException):

    def __init__(self, module_name):
        super().__init__(f"module {module_name} is invalid.")


class NoVariantError(ExpectedException):

    def __init__(self):
        super().__init__("Reference and alternate alleles are the same.")


class NoInputException(ExpectedException):
    halt = True

    def __init__(self):
        super().__init__("no input was given.")


class InvalidInputFormat(ExpectedException):
    halt = True

    def __init__(self, fmt=""):
        super().__init__(f"invalid input format {fmt}")


class SystemMissingException(ExpectedException):

    def __init__(self, msg=""):
        if msg is not None and msg != "":
            msg = f"OakVar is not ready ({msg}). 'ov system setup' to set up OakVar."
        else:
            msg = f"OakVar is not ready. 'ov system setup' to set up OakVar."
        super().__init__(msg)


class NoModulesDir(ExpectedException):

    def __init__(self):
        super().__init__(
            "no modules directory. Run `ov system setup` to setup.")


class NoSystemModule(ExpectedException):

    def __init__(self):
        super().__init__("no system module. Run `ov system setup` to setup.")


class IncompatibleResult(ExpectedException):

    def __init__(self):
        super().__init__(
            "incompatible result file version. Please report with `ov issue`.")


class ModuleLoadingError(ExpectedException):
    halt = True

    def __init__(self, module_name):
        super().__init__(msg=f"module loading error for {module_name}")


class UnknownInputFormat(ExpectedException):
    halt = True

    def __init__(self, input_format):
        super().__init__(
            f"converter for {input_format} is not found. Please check if a converter is available for the format with `ov module ls -a -t converter`."
        )


class AbsentJobConf(ExpectedException):
    halt = True

    def __init__(self, job_conf_path):
        super().__init__(f"{job_conf_path} does not exist.")


class StoreIncorrectLogin(ExpectedException):
    halt = True

    def __init__(self):
        super().__init__(f"store login is incorrect.")


class StoreServerError(ExpectedException):
    halt = True

    def __init__(self, status_code=500, text=None):
        if text is None:
            super().__init__(f"store server error [{status_code}].")
        else:
            super().__init__(f"store server error [{status_code}]: {text}.")


class InternetConnectionError(ExpectedException):

    def __init__(self):
        super().__init__(f"internet connection is unavailable.")


class ModuleVersionError(ExpectedException):

    def __init__(self, module_name, version):
        super().__init__(f"{module_name}=={version} does not exist.")


class SetupError(ExpectedException):
    halt = True
    traceback = True

    def __init__(self, module_name=None):
        if module_name is None:
            super().__init__(msg=f"setup error")
        else:
            super().__init__(msg=f"setup for {module_name}")


class LoggerError(ExpectedException):
    halt = True

    def __init__(self, module_name=None):
        if module_name is not None:
            super().__init__(f"logger is None for {module_name}")
        else:
            super().__init__(f"logger is None")


class IncompleteModuleError(ExpectedException):

    def __init__(self, module_name):
        super().__init__(f"incomplete module {module_name}")


class FilterLoadingError(ExpectedException):

    def __init__(self):
        super().__init__(f"filter loading error")


class ParserError(ExpectedException):
    halt = True

    def __init__(self, module_name=None):
        if module_name is not None:
            super().__init__(f"parser loading error for {module_name}")
        else:
            super().__init__(f"parser loading error")


class DatabaseConnectionError(ExpectedException):
    halt = True

    def __init__(self, module_name=None):
        if module_name is not None:
            super().__init__(f"database connection error for {module_name}")
        else:
            super().__init__(f"database connection error")


class DatabaseError(ExpectedException):
    halt = True

    def __init__(self, msg=None):
        if msg is not None:
            super().__init__(f"database error. {msg}")
        else:
            super().__init__(f"database error")

class ArgumentError(ExpectedException):
    halt=False
    traceback=True
    def __init__(self, msg=None):
        if msg is not None:
            super().__init__(f"error: argument. {msg}")
        else:
            super().__init__(f"error: argument")

class WrongInput(ExpectedException):
    halt=False
    traceback=False
    def __init__(self, msg=None):
        if msg is not None:
            super().__init__(f"error: input does not exist. {msg}")
        else:
            super().__init__(f"error: input does not exist.")
