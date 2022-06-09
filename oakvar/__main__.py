from .cli_module import get_parser_fn_module
from .cli_util import get_parser_fn_util
from .cli_run import get_parser_ov_run
from .cli_gui import get_parser_fn_gui
from .cli_report import get_parser_fn_report
from .cli_new import get_parser_fn_new
from .cli_issue import get_parser_fn_issue
from .cli_version import get_parser_cli_version
from .cli_store import get_parser_fn_store
from .cli_system import get_parser_ov_system

def get_entry_parser():
    # subparsers
    from argparse import ArgumentParser
    p_entry = ArgumentParser(
        description=
        "OakVar. Genomic variant analysis platform. https://github.com/rkimoakbioinformatics/oakvar"
    )
    p_entry.add_argument("--to", default="stdout")
    sp_entry = p_entry.add_subparsers(title="Commands")
    # run
    p_ov_run = sp_entry.add_parser(
        "run",
        parents=[get_parser_ov_run()],
        add_help=False,
        description="Run a job",
        help="Run a job",
        epilog="inputs should be the first argument",
    )
    p_ov_run.r_return = "A string, a named list, or a dataframe. Output of reporters"  # type: ignore
    p_ov_run.r_examples = [  # type: ignore
        "# Annotate the input file `input` with ClinVar and COSMIC modules and make a VCF-format report of annotated variants.",
        "ov.run.input(inputs=\"input\", annotators=list(\"clinvar\", \"cosmic\"), reports=\"vcf\")"
    ]

    # report
    p_report = sp_entry.add_parser(
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
        "ov.report(dbpath=\"example.sqlite\", reports=\"csv\")"
    ]

    # gui
    p_gui = sp_entry.add_parser("gui",
                                parents=[get_parser_fn_gui()],
                                add_help=False,
                                help="Start the GUI")
    p_gui.r_return = "`NULL`"  # type: ignore
    p_gui.r_examples = [  # type: ignore
        "# Launch OakVar GUI", "ov.gui()",
        "# Launch OakVar Interactive Result Viewer for the OakVar analysis file example.sqlite",
        "ov.gui(result=\"example.sqlite\")"
    ]

    # module
    _ = sp_entry.add_parser(
        "module",
        parents=[get_parser_fn_module()],
        description="Manages OakVar modules",
        add_help=False,
        help="Manages OakVar modules",
    )
    # config
    # new
    _ = sp_entry.add_parser(
        "new",
        parents=[get_parser_fn_new()],
        description="Create new modules",
        add_help=False,
        help="Create OakVar example input files and module templates",
    )
    # store
    _ = sp_entry.add_parser(
        "store",
        parents=[get_parser_fn_store()],
        description="Publish modules to the store",
        add_help=False,
        help="Publish modules to the store",
    )
    # util
    _ = sp_entry.add_parser(
        "util",
        parents=[get_parser_fn_util()],
        description="Utilities",
        add_help=False,
        help="OakVar utilities",
    )
    # version
    p_version = sp_entry.add_parser("version",
                                    parents=[get_parser_cli_version()],
                                    add_help=False,
                                    help="Show version")
    p_version.r_return = "A string. OakVar version"  # type: ignore
    p_version.r_examples = [  # type: ignore
        "# Get the version of the installed OakVar", "ov.version()"
    ]

    # issue
    p_issue = sp_entry.add_parser(name="issue",
                                  parents=[get_parser_fn_issue()],
                                  add_help=False,
                                  help="Send an issue report")
    p_issue.r_return = "`NULL`"  # type: ignore
    p_issue.r_examples = [  # type: ignore
        "# Open the Issues page of the OakVar GitHub website", "ov.issue()"
    ]

    # system
    _ = sp_entry.add_parser(name="system",
                            parents=[get_parser_ov_system()],
                            add_help=False,
                            help="Setup OakVar")
    return p_entry


def handle_exception(e: Exception):
    from sys import stderr
    msg = getattr(e, "msg", None)
    if msg:
        stderr.write(msg + "\n")
        stderr.flush()
    trc = getattr(e, "traceback", None)
    if trc:
        from traceback import print_exc
        print_exc()
    from .exceptions import ExpectedException
    import sys
    isatty = hasattr(sys, 'ps1')  # interactive shell?
    halt = getattr(e, "halt", False)
    returncode = getattr(e, "returncode", 1)
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
    else:
        raise e


def main():
    from sys import argv
    global get_entry_parser
    try:
        p_entry = get_entry_parser()
        args = p_entry.parse_args()
        if hasattr(args, "func"):
            ret = args.func(args)
            if getattr(args, "to", "return") != "stdout":
                return ret
            return True
        else:
            p_entry.parse_args(argv[1:] + ["--help"])
    except Exception as e:
        handle_exception(e)


if __name__ == "__main__":
    main()
