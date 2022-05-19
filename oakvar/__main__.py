from .cli_module import parser_fn_module
from .cli_config import parser_fn_config
from .cli_util import parser_fn_util
from .cli_run import parser_fn_run
from .cli_gui import parser_fn_gui
from .cli_report import parser_fn_report
from .cli_new import parser_fn_new
from .cli_feedback import parser_fn_feedback
from .cli_version import parser_fn_version
from .cli_store import parser_fn_store

# subparsers
from argparse import ArgumentParser

p_entry = ArgumentParser(
    description="OakVar. Genomic variant analysis platform. https://github.com/rkimoakbioinformatics/oakvar"
)
sp_entry = p_entry.add_subparsers(title="Commands")

# run
p_run = sp_entry.add_parser(
    "run",
    parents=[parser_fn_run],
    add_help=False,
    description="Run a job",
    help="Run a job",
    epilog="inputs should be the first argument",
)

# report
p_report = sp_entry.add_parser(
    "report",
    parents=[parser_fn_report],
    add_help=False,
    help="Generate a report from a job",
    epilog="dbpath must be the first argument",
)

# gui
p_gui = sp_entry.add_parser(
    "gui", parents=[parser_fn_gui], add_help=False, help="Start the GUI"
)

# module
p_module = sp_entry.add_parser(
    "module",
    parents=[parser_fn_module],
    description="Manages OakVar modules",
    add_help=False,
    help="Manages OakVar modules",
)

# config
p_config = sp_entry.add_parser(
    "config",
    parents=[parser_fn_config],
    description="View and change configuration settings",
    add_help=False,
    help="View and change configurations",
)

# new
p_new = sp_entry.add_parser(
    "new",
    parents=[parser_fn_new],
    description="Create new modules",
    add_help=False,
    help="Create OakVar example input files and module templates",
)

# store
p_store = sp_entry.add_parser(
    "store",
    parents=[parser_fn_store],
    description="Publish modules to the store",
    add_help=False,
    help="Publish modules to the store",
)

# util
p_util = sp_entry.add_parser(
    "util",
    parents=[parser_fn_util],
    description="Utilities",
    add_help=False,
    help="OakVar utilities",
)

# version
p_version = sp_entry.add_parser(
    "version", parents=[parser_fn_version], add_help=False, help="Show version"
)

# feedback
p_feedback = sp_entry.add_parser(
    name="feedback",
    parents=[parser_fn_feedback],
    add_help=False,
    help="Send feedback to the developers",
)


def main():
    import sys

    try:
        args = p_entry.parse_args()
        if hasattr(args, "func"):
            args.func(args)
        else:
            p_entry.parse_args(sys.argv[1:] + ["--help"])
    except SystemExit as e:
        raise e


if __name__ == "__main__":
    main()
