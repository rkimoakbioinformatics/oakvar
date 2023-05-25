from .cli.module import add_parser_ov_module
from .cli.util import get_parser_fn_util
from .cli.run import add_parser_ov_run
from .cli.gui import get_parser_fn_gui
from .cli.report import get_parser_fn_report
from .cli.new import get_parser_fn_new
from .cli.issue import get_parser_fn_issue
from .cli.version import get_parser_fn_version
from .cli.store import get_parser_fn_store
from .cli.system import add_parser_ov_system
from .cli.config import get_parser_fn_config
from .cli.license import get_parser_ov_license
from .cli.update import get_parser_ov_update
from . import CliOuter

_ = CliOuter


def get_entry_parser():
    # subparsers
    from argparse import ArgumentParser

    p_entry = ArgumentParser(
        description="OakVar. Genomic variant analysis platform. https://github.com/rkimoakbioinformatics/oakvar"
    )
    subparsers = p_entry.add_subparsers(title="Commands")
    # run
    add_parser_ov_run(subparsers)
    # report
    p_report = subparsers.add_parser(
        "report",
        parents=[get_parser_fn_report()],
        description="Generate reports from a job",
        add_help=False,
        help="Generate a report from a job",
        epilog="dbpath must be the first argument",
    )
    p_report.r_return = "A string, a named list, or a dataframe. Output of reporters"  # type: ignore
    p_report.r_examples = [  # type: ignore
        "# Generate a CSV-format report file from the job result file example.sqlite",
        '#roakvar::report(dbpath="example.sqlite", report_types="csv")',
    ]

    # module
    add_parser_ov_module(subparsers)
    # gui
    p_gui = subparsers.add_parser(
        "gui", parents=[get_parser_fn_gui()], add_help=False, help="Start the GUI"
    )
    p_gui.r_return = "`NULL`"  # type: ignore
    p_gui.r_examples = [  # type: ignore
        "# Launch OakVar GUI",
        "#roakvar::gui()",
        "# Launch OakVar Interactive Result Viewer for the OakVar analysis file example.sqlite",
        '#roakvar::gui(result="example.sqlite")',
    ]

    # config
    _ = subparsers.add_parser(
        "config",
        parents=[get_parser_fn_config()],
        description="Manages OakVar configurations",
        add_help=False,
        help="Manages OakVar configurations",
    )
    # new
    _ = subparsers.add_parser(
        "new",
        parents=[get_parser_fn_new()],
        description="Create new modules",
        add_help=False,
        help="Create OakVar example input files and module templates",
    )
    # store
    _ = subparsers.add_parser(
        "store",
        parents=[get_parser_fn_store()],
        description="Publish modules to the store",
        add_help=False,
        help="Publish modules to the store",
    )
    # util
    _ = subparsers.add_parser(
        "util",
        parents=[get_parser_fn_util()],
        description="Utilities",
        add_help=False,
        help="OakVar utilities",
    )
    # version
    p_version = subparsers.add_parser(
        "version",
        parents=[get_parser_fn_version()],
        add_help=False,
        help="Show version",
    )
    p_version.r_return = "A string. OakVar version"  # type: ignore
    p_version.r_examples = [  # type: ignore
        "# Get the version of the installed OakVar",
        "#roakvar::version()",
    ]

    # issue
    p_issue = subparsers.add_parser(
        name="issue",
        parents=[get_parser_fn_issue()],
        add_help=False,
        help="Send an issue report",
    )
    p_issue.r_return = "`NULL`"  # type: ignore
    p_issue.r_examples = [  # type: ignore
        "# Open the Issues page of the OakVar GitHub website",
        "#roakvar::issue()",
    ]

    # system
    add_parser_ov_system(subparsers)
    """_ = subparsers.add_parser(
    )"""

    # license
    _ = subparsers.add_parser(
        "license",
        parents=[get_parser_ov_license()],
        description="Shows license information.",
        add_help=False,
        help="Shows license information.",
    )

    # update
    _ = subparsers.add_parser(
        "update",
        parents=[get_parser_ov_update()],
        description="Updates OakVar to the latest version.",
        add_help=False,
        help="Updates OakVar to the latest version.",
    )
    return p_entry


def handle_exception(e: Exception):
    import sys
    from sys import stderr
    from traceback import print_exc
    from requests.exceptions import ConnectionError
    from .lib.exceptions import ExpectedException

    msg = getattr(e, "msg", None)
    if msg:
        stderr.write(msg)
        stderr.write("\n")
        stderr.flush()
    trc = getattr(e, "traceback", None)
    if trc:
        print_exc()
    isatty = hasattr(sys, "ps1")  # interactive shell?
    halt = getattr(e, "halt", False)
    returncode = getattr(e, "returncode", 1)
    if hasattr(e, "traceback") and getattr(e, "traceback"):
        import traceback

        traceback.print_exc()
    if isinstance(e, ExpectedException):
        if halt:
            if isatty:
                return False
            else:
                exit(returncode)
        else:
            if isatty:
                return False
            else:
                return False
    elif isinstance(e, KeyboardInterrupt):
        pass
    elif isinstance(e, ConnectionError):
        stderr.write(
            "Connection could not be established. Please check if the system or the server is online.\n"
        )
    else:
        raise e


def main():
    import signal
    from . import raise_break

    signal.signal(signal.SIGINT, raise_break)
    global get_entry_parser
    try:
        p_entry = get_entry_parser()
        args = p_entry.parse_args()
        if hasattr(args, "func"):
            func = args.func
            delattr(args, "func")
            ret = func(args)
            if getattr(args, "to", "return") != "stdout":
                return ret
            return True
        else:
            p_entry.print_help()
            exit(1)
    except Exception as e:
        handle_exception(e)


if __name__ == "__main__":
    main()
