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

from . import cli_entry
from . import cli_func


@cli_entry
def cli_system_setup(args):
    setup(args)


@cli_func
def setup(args, __name__="system setup"):
    from ..api.system import setup

    return setup(**args)


@cli_entry
def cli_system_md(args):
    return md(args)


@cli_func
def md(args, __name__="system md"):
    from ..api.system import md

    outer = args["outer"]
    del args["outer"]
    ret = md(**args)
    if ret:
        outer.write(ret)
    return ret


@cli_entry
def cli_system_check(args):
    return check(args)


@cli_func
def check(args, __name__="system check"):
    from ..api.system import check

    ret = check(**args)
    return ret


def add_parser_ov_system_setup(subparsers):
    parser_cli_ov_system_setup = subparsers.add_parser(
        "setup", help="Sets up OakVar system", description="Sets up OakVar system"
    )
    parser_cli_ov_system_setup.add_argument(
        "-f", dest="setup_file", default=None, help="setup file to use"
    )
    parser_cli_ov_system_setup.add_argument(
        "--email", help="email for an OakVar store account"
    )
    parser_cli_ov_system_setup.add_argument(
        "--pw", help="password for an OakVar store account"
    )
    parser_cli_ov_system_setup.add_argument(
        "--clean",
        action="store_true",
        default=False,
        help="Performs clean installation",
    )
    parser_cli_ov_system_setup.add_argument(
        "--quiet", action="store_true", default=None, help="run quietly"
    )
    parser_cli_ov_system_setup.add_argument(
        "--modules", default=[], help="Modules to install", nargs="*"
    )
    parser_cli_ov_system_setup.set_defaults(func=cli_system_setup)
    parser_cli_ov_system_setup.r_return = "A boolean. TRUE if successful, FALSE if not"  # type: ignore
    parser_cli_ov_system_setup.r_examples = [  # type: ignore
        "# Set up OakVar with defaults",
        "#roakvar::system.setup()",
        "# Set up OakVar with a setup file",
        '#roakvar::system.setup(setup_file="setup.yml")',
    ]


def add_parser_ov_system_md(subparsers):
    parser_cli_system_md = subparsers.add_parser(
        "md",
        help="displays or changes OakVar modules directory.",
        description="displays or changes OakVar modules directory.",
    )
    parser_cli_system_md.add_argument(
        "directory", nargs="?", help="sets modules directory."
    )
    parser_cli_system_md.set_defaults(func=cli_system_md)
    parser_cli_system_md.r_return = "A string. OakVar modules directory"  # type: ignore
    parser_cli_system_md.r_examples = [  # type: ignore
        "# Get the OakVar modules directory",
        "#roakvar::system.md()",
        "# Set the OakVar modules directory to /home/user1/.oakvar/modules",
        '#roakvar::system.md(directory="/home/user1/.oakvar/modules")',
    ]


def add_parser_ov_system_config(subparsers):
    from .config import cli_config_system

    parser_cli_system_config = subparsers.add_parser(
        "config", help="show or change system configuration."
    )
    parser_cli_system_config.add_argument("key", nargs="?", help="Configuration key")
    parser_cli_system_config.add_argument(
        "value", nargs="?", help="Configuration value"
    )
    parser_cli_system_config.add_argument(
        "--fmt", default="json", help="Format of output. json or yaml."
    )
    parser_cli_system_config.add_argument(
        "--quiet", action="store_true", default=None, help="run quietly"
    )
    parser_cli_system_config.set_defaults(func=cli_config_system)
    parser_cli_system_config.r_return = "A named list. System config information"  # type: ignore
    parser_cli_system_config.r_examples = [  # type: ignore
        "# Get named list of the OakVar system configuration",
        "#roakvar::system.config()",
        "# Get the OakVar system configuration in YAML text",
        '#roakvar::system.config(fmt="yaml")'
        "# Print to stdout the OakVar system configuration in YAML text",
        '#roakvar::system.config(fmt="yaml", to="stdout")',
    ]


def add_parser_ov_system_check(subparsers):
    parser_cli_system_check = subparsers.add_parser(
        "check", help="check if OakVar is set up correctly"
    )
    parser_cli_system_check.add_argument(
        "--quiet", action="store_true", default=None, help="run quietly"
    )
    parser_cli_system_check.set_defaults(func=cli_system_check)
    parser_cli_system_check.r_return = "A boolean. true if no problem or false if not."  # type: ignore
    parser_cli_system_check.r_examples = [  # type: ignore
        "# Check if OakVar is set up correctly.",
        "#roakvar::system.check()",
    ]


def add_parser_ov_system(subparser):
    parser_ov_system = subparser.add_parser(
        name="system",
        help="Commands on OakVar system",
    )
    subparsers = parser_ov_system.add_subparsers()
    add_parser_ov_system_setup(subparsers)
    add_parser_ov_system_md(subparsers)
    add_parser_ov_system_config(subparsers)
    add_parser_ov_system_check(subparsers)
