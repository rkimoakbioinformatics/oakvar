from .cli_module import get_parser_fn_module
from .cli_config import get_parser_fn_config
from .cli_util import get_parser_fn_util
from .cli_run import get_parser_fn_run
from .cli_gui import get_parser_fn_gui
from .cli_report import get_parser_fn_report
from .cli_new import get_parser_fn_new
from .cli_issue import get_parser_fn_issue
from .cli_version import get_parser_fn_version
from .cli_store import get_parser_fn_store
from .cli_system import get_parser_fn_system


def get_entry_parser():
    # subparsers
    from argparse import ArgumentParser
    p_entry = ArgumentParser(
        description=
        "OakVar. Genomic variant analysis platform. https://github.com/rkimoakbioinformatics/oakvar"
    )
    sp_entry = p_entry.add_subparsers(title="Commands")
    # run
    p_run = sp_entry.add_parser(
        "run",
        parents=[get_parser_fn_run()],
        add_help=False,
        description="Run a job",
        help="Run a job",
        epilog="inputs should be the first argument",
    )
    p_run.r_return = "A string, a named list, or a dataframe. Output of reporters"
    p_run.r_examples = [
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
    p_report.r_return = "A string, a named list, or a dataframe. Output of reporters"
    p_report.r_examples = [
        "# Generate a CSV-format report file from the job result file example.sqlite",
        "ov.report(dbpath=\"example.sqlite\", reporttypes=\"csv\")"
    ]

    # gui
    p_gui = sp_entry.add_parser("gui",
                                parents=[get_parser_fn_gui()],
                                add_help=False,
                                help="Start the GUI")
    p_gui.r_return = "`NULL`"
    p_gui.r_examples = [
        "# Launch OakVar GUI",
        "ov.gui()",
        "# Launch OakVar Interactive Result Viewer for the OakVar analysis file example.sqlite",
        "ov.gui(result=\"example.sqlite\")"
    ]

    # module
    p_module = sp_entry.add_parser(
        "module",
        parents=[get_parser_fn_module()],
        description="Manages OakVar modules",
        add_help=False,
        help="Manages OakVar modules",
    )
    # config
    p_config = sp_entry.add_parser(
        "config",
        parents=[get_parser_fn_config()],
        description="View and change configuration settings",
        add_help=False,
        help="View and change configurations",
    )
    # new
    p_new = sp_entry.add_parser(
        "new",
        parents=[get_parser_fn_new()],
        description="Create new modules",
        add_help=False,
        help="Create OakVar example input files and module templates",
    )
    # store
    p_store = sp_entry.add_parser(
        "store",
        parents=[get_parser_fn_store()],
        description="Publish modules to the store",
        add_help=False,
        help="Publish modules to the store",
    )
    # util
    p_util = sp_entry.add_parser(
        "util",
        parents=[get_parser_fn_util()],
        description="Utilities",
        add_help=False,
        help="OakVar utilities",
    )
    # version
    p_version = sp_entry.add_parser("version",
                                    parents=[get_parser_fn_version()],
                                    add_help=False,
                                    help="Show version")
    p_version.r_return = "A string. OakVar version"
    p_version.r_examples = [
        "# Get the version of the installed OakVar",
        "ov.version()"
    ]

    # issue
    p_issue = sp_entry.add_parser(name="issue",
                                     parents=[get_parser_fn_issue()],
                                     add_help=False,
                                     help="Send an issue report")
    p_issue.r_return = "`NULL`"
    p_issue.r_examples = [
        "# Open the Issues page of the OakVar GitHub website",
        "ov.issue()"
    ]

    # system
    p_system = sp_entry.add_parser(name="system",
                                   parents=[get_parser_fn_system()],
                                   add_help=False,
                                   help="Setup OakVar")
    return p_entry


def main():
    from sys import argv
    from .exceptions import ExpectedException
    global get_entry_parser
    try:
        p_entry = get_entry_parser()
        args = p_entry.parse_args()
        if hasattr(args, "func"):
            args.func(args)
        else:
            p_entry.parse_args(argv[1:] + ["--help"])
    except ExpectedException as e:
        from sys import stderr
        stderr.write(str(e) + "\n")
        stderr.flush()
    except SystemExit as e:
        raise e
    except Exception as e:
        raise e


if __name__ == "__main__":
    main()
