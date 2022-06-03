from .decorators import cli_func
from .decorators import cli_entry


@cli_entry
def cli_ov_new_exampleinput(args):
    ov_new_exampleinput(args)


@cli_func
def ov_new_exampleinput(args):
    from .admin_util import fn_new_exampleinput
    return fn_new_exampleinput(args.get("directory"))


@cli_entry
def cli_ov_new_annotator(args):
    args.quiet = False
    return ov_new_annotator(args)


@cli_func
def ov_new_annotator(args):
    from .admin_util import new_annotator, get_local_module_info
    from .util import quiet_print
    new_annotator(args.get("annotator_name"))
    module_info = get_local_module_info(args.get("annotator_name"))
    if module_info is not None:
        quiet_print(f"created {module_info.directory}", args)
        return module_info.directory
    else:
        return None


def get_parser_fn_new():
    from argparse import ArgumentParser, RawDescriptionHelpFormatter
    parser_fn_new = ArgumentParser(formatter_class=RawDescriptionHelpFormatter)
    _subparsers = parser_fn_new.add_subparsers(title="Commands")

    # test input file
    parser_cli_new_exampleinput = _subparsers.add_parser(
        "exampleinput", help="makes a file with example input variants.")
    parser_cli_new_exampleinput.add_argument(
        "-d",
        dest="directory",
        default=".",
        help="Directory to make the example input file in",
    )
    parser_cli_new_exampleinput.add_argument("--quiet",
                                             default=True,
                                             help="Run quietly")
    parser_cli_new_exampleinput.set_defaults(func=cli_ov_new_exampleinput)
    parser_cli_new_exampleinput.r_return = "A string. Location of the example input file"  # type: ignore
    parser_cli_new_exampleinput.r_examples = [  # type: ignore
        "# Create an example input file in the current working directory",
        "ov.new.exampleinput()",
        "# Create an example input file at /home/user1/",
        "ov.new.exampleinput(directory=\"/home/user1\")"
    ]

    # new-annotator
    parser_cli_new_annotator = _subparsers.add_parser(
        "annotator", help="creates a new annotator")
    parser_cli_new_annotator.add_argument("-n",
                                          dest="annotator_name",
                                          default="exampleannotator",
                                          help="Annotator name")
    parser_cli_new_annotator.add_argument(
        "--md",
        default=None,
        help="Specify the root directory of OakVar modules")
    parser_cli_new_annotator.add_argument("--quiet",
                                          default=True,
                                          help="No print to stdout")
    parser_cli_new_annotator.set_defaults(func=cli_ov_new_annotator)
    parser_cli_new_annotator.r_return = "A string. Location of the new annotator module"  # type: ignore
    parser_cli_new_annotator.r_examples = [  # type: ignore
        "# Create an annotator template at the OakVar modules directory/annotators/annotatortest",
        "ov.new.annotator(annotator_name=\"annotatortest\")"
    ]
    return parser_fn_new
