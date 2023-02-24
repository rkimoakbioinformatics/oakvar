from . import cli_entry
from . import cli_func


@cli_entry
def cli_run(args):
    ret = run(args)
    return ret


@cli_func
def run(args, __name__="run"):
    from ..api import run

    ret = run(**args)
    return ret


def add_parser_ov_run(subparsers):
    parser_ov_run = subparsers.add_parser(
        "run",
        prog="ov run input_file_path_1 input_file_path_2 ...",
        description="Run OakVar on input files.",
        help="Run a job",
        epilog="inputs should be the first argument",
    )
    parser_ov_run.r_return = "A string, a named list, or a dataframe. Output of reporters"  # type: ignore
    parser_ov_run.r_examples = [  # type: ignore
        "# Annotate the input file `input` with ClinVar and COSMIC modules ",
        "# and make a VCF-format report of annotated variants.",
        '#roakvar::run.input(inputs="input", annotators=list("clinvar", "cosmic"), report_types="vcf")',
    ]
    parser_ov_run.add_argument(
        "inputs",
        nargs="*",
        default=[],
        help="Input file(s). One or more variant files in a supported format like VCF.  "
        + "See the -i/--input-format flag for supported formats. In the special case "
        + "where you want to add annotations to an existing OakVar analysis, "
        + "provide the output sqlite database from the previous run as input instead of a variant input file.",
    )
    parser_ov_run.add_argument(
        "-a",
        nargs="+",
        dest="annotators",
        default=[],
        help="Annotator module names or directories. If --package is used also, annotator modules defined with -a will be added.",
    )
    parser_ov_run.add_argument(
        "-A",
        nargs="+",
        dest="annotators_replace",
        default=[],
        help="Annotator module names or directories. If --package option also is used, annotator modules defined with -A will replace those defined with --package. -A has priority over -a.",
    )
    parser_ov_run.add_argument(
        "-e", nargs="+", dest="excludes", default=[], help="modules to exclude"
    )
    parser_ov_run.add_argument(
        "-n", dest="run_name", nargs="+", help="name of oakvar run"
    )
    parser_ov_run.add_argument(
        "-d",
        dest="output_dir",
        nargs="+",
        default=None,
        help="directory for output files",
    )
    parser_ov_run.add_argument(
        "--startat",
        dest="startat",
        choices=[
            "converter",
            "preparer",
            "mapper",
            "annotator",
            "aggregator",
            "postaggregator",
            "reporter",
        ],
        default=None,
        help="starts at given stage",
    )
    parser_ov_run.add_argument(
        "--endat",
        dest="endat",
        choices=[
            "converter",
            "preparer",
            "mapper",
            "annotator",
            "aggregator" "postaggregator",
            "reporter",
        ],
        default=None,
        help="ends after given stage.",
    )
    parser_ov_run.add_argument(
        "--skip",
        dest="skip",
        nargs="+",
        choices=[
            "converter",
            "preparer",
            "mapper",
            "annotator",
            "aggregator",
            "postaggregator",
            "reporter",
        ],
        default=[],
        help="skips given stage(s).",
    )
    parser_ov_run.add_argument(
        "-c", "--confpath", dest="confpath", default=None, help="path to a conf file"
    )
    parser_ov_run.add_argument(
        "-t",
        nargs="+",
        dest="report_types",
        default=[],
        help="Reporter types or reporter module directories",
    )
    parser_ov_run.add_argument(
        "-l",
        "--genome",
        dest="genome",
        default=None,
        help="reference genome of input. OakVar will lift over to hg38 if needed.",
    )
    parser_ov_run.add_argument(
        "-x",
        dest="cleandb",
        action="store_true",
        help="deletes the existing result database and creates a new one.",
    )
    parser_ov_run.add_argument(
        "--newlog",
        dest="newlog",
        action="store_true",
        default=None,
        help="deletes the existing log file and creates a new one.",
    )
    parser_ov_run.add_argument(
        "--note", dest="note", default="", help="note for the job"
    )
    parser_ov_run.add_argument(
        "--mp",
        dest="mp",
        default=None,
        help="number of processes to use to run annotators",
    )
    parser_ov_run.add_argument(
        "-i",
        "--input-format",
        default=None,
        help="Force input format",
    )
    parser_ov_run.add_argument(
        "--temp-files",
        dest="keep_temp",
        action="store_true",
        default=False,
        help="Leave temporary files after run is complete.",
    )
    parser_ov_run.add_argument(
        "--keep-temp",
        dest="keep_temp",
        action="store_true",
        default=False,
        help="Leave temporary files after run is complete.",
    )
    parser_ov_run.add_argument(
        "--writeadmindb",
        dest="writeadmindb",
        action="store_true",
        default=False,
        help="Write job information to admin db after job completion",
    )
    parser_ov_run.add_argument(
        "-j",
        "--jobname",
        dest="job_name",
        type=str,
        nargs="+",
        default=None,
        help="Job ID for server version",
    )
    parser_ov_run.add_argument(
        "--separatesample",
        dest="separatesample",
        action="store_true",
        default=False,
        help="Separate variant results by sample",
    )
    parser_ov_run.add_argument(
        "--primary-transcript",
        dest="primary_transcript",
        nargs="+",
        default=["mane"],
        help='"mane" for MANE transcripts as primary transcripts, or a path to a file of primary transcripts. MANE is default.',
    )
    parser_ov_run.add_argument(
        "--cleanrun",
        dest="clean",
        action="store_true",
        default=False,
        help="Deletes all previous output files for the job and generate new ones.",
    )
    parser_ov_run.add_argument(
        "--module-options",
        dest="module_options",
        nargs="*",
        help="Module-specific option in module_name.key=value syntax. For example, --module-options vcfreporter.type=separate",
    )
    parser_ov_run.add_argument(
        "--system-option",
        dest="system_option",
        nargs="*",
        default=[],
        help="System option in key=value syntax. For example, --system-option modules_dir=/home/user/oakvar/modules",
    )
    parser_ov_run.add_argument(
        "--package", dest="package", default=None, help="Use package"
    )
    parser_ov_run.add_argument("--filtersql", default=None, help="Filter SQL")
    parser_ov_run.add_argument(
        "--includesample", nargs="+", default=None, help="Sample IDs to include"
    )
    parser_ov_run.add_argument(
        "--excludesample", nargs="+", default=None, help="Sample IDs to exclude"
    )
    parser_ov_run.add_argument("--filter", default=None)
    parser_ov_run.add_argument(
        "-f", dest="filterpath", default=None, help="Path to a filter file"
    )
    parser_ov_run.add_argument(
        "--pp",
        dest="preparers",
        nargs="+",
        default=[],
        help="Names or directories of preparer modules, which will be run in the given order.",
    )
    parser_ov_run.add_argument(
        "-m",
        dest="mapper_name",
        nargs="+",
        default=[],
        help="Mapper module name or mapper module directory",
    )
    parser_ov_run.add_argument(
        "-p",
        nargs="+",
        dest="postaggregators",
        default=[],
        help="Postaggregators to run. Additionally, tagsampler and vcfinfo will automatically run depending on conditions.",
    )
    parser_ov_run.add_argument(
        "--vcf2vcf",
        action="store_true",
        default=False,
        help="analyze with the vcf to vcf workflow. It is faster than a normal run, but only if both input and output formats are VCF.",
    )
    parser_ov_run.add_argument("--uid", default=None, help="Optional UID of the job")
    parser_ov_run.add_argument(
        "--logtofile",
        action="store_true",
        help="Path to a log file. If given without a path, the job's run_name.log will be the log path.",
    )
    parser_ov_run.add_argument(
        "--loglevel",
        default="INFO",
        help="Logging level (DEBUG, INFO, WARN, ERROR)",
    )
    parser_ov_run.add_argument(
        "--combine-input",
        action="store_true",
        help="Combine input files into one result",
    )
    parser_ov_run.add_argument(
        "--input-encoding",
        default=None,
        help="Encoding of input files",
    )
    parser_ov_run.set_defaults(func=cli_run)
