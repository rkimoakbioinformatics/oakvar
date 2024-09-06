# OakVar
#
# Copyright (c) 2024 Oak Bioinformatics, LLC
#
# All rights reserved.
#
# Do not distribute or use this software without obtaining
# a license from Oak Bioinformatics, LLC.
#
# Do not use this software to develop another software
# which competes with the products by Oak Bioinformatics, LLC,
# without obtaining a license for such use from Oak Bioinformatics, LLC.
#
# For personal use of non-commercial nature, you may use this software
# after registering with `ov store account create`.
#
# For research use of non-commercial nature, you may use this software
# after registering with `ov store account create`.
#
# For use by commercial entities, you must obtain a commercial license
# from Oak Bioinformatics, LLC. Please write to info@oakbioinformatics.com
# to obtain the commercial license.
# ================
# OpenCRAVAT
#
# MIT License
#
# Copyright (c) 2021 KarchinLab
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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


class IgnoredInput(ExpectedException):
    traceback = False

    def __init__(self):
        super().__init__(msg="Ignored input line")


class NoAlternateAllele(ExpectedException):
    traceback = False

    def __init__(self):
        super().__init__(msg="No alternate allele")


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

    def __init__(self, module_name: str, msg=""):
        if msg:
            super().__init__(msg)
        else:
            super().__init__(
                f"{module_name} was not properly installed. Consider 'ov module install {module_name}'."
            )


class ModuleNotExist(ExpectedException):
    traceback = False
    halt = True
    returncode = 3

    def __init__(self, module_name, msg=None):
        if msg:
            super().__init__(msg)
        else:
            super().__init__(
                f"module [{module_name}] does not exist. Possible solutions: 'ov system setup' and/or 'ov module install {module_name}'"
            )


class NoConverterFound(ExpectedException):
    traceback = False
    halt = True

    def __init__(self, input_file):
        super().__init__(msg=f"No converter was found for {input_file}.")


class NoVariantError(ExpectedException):
    traceback = False

    def __init__(self):
        super().__init__("Reference and alternate alleles are the same.")


class NoInput(ExpectedException):
    traceback = False
    halt = True

    def __init__(self, msg=None):
        if msg:
            super().__init__(msg)
        else:
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
            msg = (
                f"OakVar system component is missing ({msg}).\n"
                + "Please run 'ov system setup' to set up OakVar."
            )
        else:
            msg = (
                "OakVar system component is missing.\nPlease run "
                + "'ov system setup' to set up OakVar."
            )
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
        super().__init__("internet connection is unavailable.")


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
                super().__init__(msg="setup error")


class LoggerError(ExpectedException):
    traceback = True
    halt = True

    def __init__(self, module_name=None):
        if module_name is not None:
            super().__init__(f"logger is None for {module_name}")
        else:
            super().__init__("logger is None")


class IncompleteModuleError(ExpectedException):
    def __init__(self, module_name: Optional[str] = None, msg: Optional[str] = None):
        if msg:
            super().__init__(msg)
        elif module_name:
            super().__init__(f"Incomplete module {module_name}")


class FilterLoadingError(ExpectedException):
    def __init__(self):
        super().__init__("filter loading error")


class DatabaseConnectionError(ExpectedException):
    traceback = True
    halt = True

    def __init__(self, module_name=None):
        if module_name is not None:
            super().__init__(f"database connection error for {module_name}")
        else:
            super().__init__("database connection error")


class DatabaseError(ExpectedException):
    traceback = True
    halt = True

    def __init__(self, msg=None):
        if msg is not None:
            super().__init__(f"database error. {msg}")
        else:
            super().__init__("database error")


class ArgumentError(ExpectedException):
    halt = False
    traceback = True

    def __init__(self, msg=None):
        if msg is not None:
            super().__init__(f"{msg}")
        else:
            super().__init__("argument")


class WrongInput(ExpectedException):
    halt = False
    traceback = False

    def __init__(self, msg=None):
        if msg is not None:
            super().__init__(f"wrong input. {msg}")
        else:
            super().__init__("wrong input")


class ServerError(Exception):
    def __init__(self, msg: str = ""):
        import traceback

        super().__init__(traceback.format_exc() + msg)


# store-related exceptions
class AuthorizationError(ExpectedException):
    traceback = False
    halt = True

    def __init__(self):
        super().__init__("authorization failed")


# end of store-related exceptions
