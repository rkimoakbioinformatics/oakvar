from typing import Optional


class ExpectedException(Exception):
    halt = False
    traceback = True
    msg = ""
    returncode = 1

    def __init__(self, msg=""):
        self.msg = msg
        super().__init__(f"{msg}")


class NoGenomeException(ExpectedException):
    traceback = False
    halt = True

    def __init__(self):
        super().__init__("genome assembly should be selected.")


class InvalidGenomeAssembly(ExpectedException):
    traceback = False
    halt = True

    def __init__(self, genome_assembly):
        super().__init__(f"{genome_assembly} is an invalid genome assembly.")


class InvalidData(ExpectedException):
    pass


class ConfigurationError(ExpectedException):
    traceback = True


class BadFormatError(InvalidData):
    pass


class IgnoredVariant(InvalidData):
    traceback = False


class NoAlternateAllele(ExpectedException):
    traceback = False


class LiftoverFailure(InvalidData):
    traceback = False
    pass


class FileIntegrityError(Exception):
    traceback = False

    def __init__(self, path):
        super().__init__(path)


class KillInstallException(ExpectedException):
    traceback = False

    pass


class InvalidFilter(ExpectedException):
    traceback = False

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
        self.msg = "\n".join(self.msg)

    def __str__(self):
        return str(self.msg)


class ModuleInstallationError(ExpectedException):
    traceback = False
    halt = False

    def __init__(self, msg):
        super().__init__(msg)


class ModuleNotExist(ExpectedException):
    traceback = False
    halt = True
    returncode = 3

    def __init__(self, module_name, msg=None):
        if msg:
            super().__init__(msg)
        else:
            super().__init__(f"module [{module_name}] does not exist.")


class NoConverterFound(ExpectedException):
    traceback = False
    halt = True

    def __init__(self, input_file):
        super().__init__(f"No converter was found for {input_file}.")


class NoVariantError(ExpectedException):
    traceback = False

    def __init__(self):
        super().__init__("Reference and alternate alleles are the same.")


class NoInput(ExpectedException):
    traceback = False
    halt = True

    def __init__(self):
        super().__init__("No valid input was given.")


class InvalidInputFormat(ExpectedException):
    traceback = False
    halt = True

    def __init__(self, fmt=""):
        super().__init__(f"invalid input format: {fmt}")


class SystemMissingException(ExpectedException):
    traceback = False

    def __init__(self, msg=""):
        if msg is not None and msg != "":
            msg = f"OakVar system component is missing ({msg}).\nPlease run 'ov system setup' to set up OakVar."
        else:
            msg = f"OakVar system component is missing.\nPlease run 'ov system setup' to set up OakVar."
        super().__init__(msg)


class IncompatibleResult(ExpectedException):
    traceback = False

    def __init__(self):
        super().__init__(
            "incompatible result file version. Please report with `ov issue`."
        )


class ModuleLoadingError(ExpectedException):
    traceback = True
    halt = True

    def __init__(self, module_name: Optional[str] = None, msg: Optional[str] = None):
        if msg:
            super().__init__(msg=msg)
        else:
            super().__init__(msg=f"module loading error for {module_name}")


class StoreServerError(ExpectedException):
    traceback = False
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
    def __init__(self, module_name, version, msg=None):
        if msg:
            super().__init__(msg)
        else:
            super().__init__(f"{module_name}=={version} does not exist.")


class ModuleToSkipInstallation(ExpectedException):
    traceback = False

    def __init__(self, module_name, msg=None):
        if msg:
            super().__init__(f"{msg}")
        else:
            super().__init__(f"Skipping installation of {module_name}")


class SetupError(ExpectedException):
    traceback = True
    halt = True

    def __init__(self, module_name=None, msg=None):
        if msg:
            super().__init__(msg=msg)
        else:
            if module_name:
                super().__init__(msg=f"setup for {module_name}")
            else:
                super().__init__(msg=f"setup error")


class LoggerError(ExpectedException):
    traceback = True
    halt = True

    def __init__(self, module_name=None):
        if module_name is not None:
            super().__init__(f"logger is None for {module_name}")
        else:
            super().__init__(f"logger is None")


class IncompleteModuleError(ExpectedException):
    def __init__(self, module_name: Optional[str] = None, msg: Optional[str] = None):
        if msg:
            super().__init__(msg)
        elif module_name:
            super().__init__(f"Incomplete module {module_name}")


class FilterLoadingError(ExpectedException):
    def __init__(self):
        super().__init__(f"filter loading error")


class DatabaseConnectionError(ExpectedException):
    traceback = True
    halt = True

    def __init__(self, module_name=None):
        if module_name is not None:
            super().__init__(f"database connection error for {module_name}")
        else:
            super().__init__(f"database connection error")


class DatabaseError(ExpectedException):
    traceback = True
    halt = True

    def __init__(self, msg=None):
        if msg is not None:
            super().__init__(f"database error. {msg}")
        else:
            super().__init__(f"database error")


class ArgumentError(ExpectedException):
    halt = False
    traceback = True

    def __init__(self, msg=None):
        if msg is not None:
            super().__init__(f"{msg}")
        else:
            super().__init__(f"argument")


class WrongInput(ExpectedException):
    halt = False
    traceback = False

    def __init__(self, msg=None):
        if msg is not None:
            super().__init__(f"wrong input. {msg}")
        else:
            super().__init__(f"wrong input")


class ServerError(Exception):
    def __init__(self, msg: str = ""):
        import traceback

        super().__init__(traceback.format_exc() + msg)


# store-related exceptions
class AuthorizationError(ExpectedException):
    traceback = False
    halt = True

    def __init__(self):
        super().__init__(f"authorization failed")


# end of store-related exceptions
