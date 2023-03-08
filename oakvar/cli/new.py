from . import cli_entry
from . import cli_func


@cli_entry
def cli_new_exampleinput(args):
    exampleinput(args)


@cli_func
def exampleinput(args, __name__="new exampleinput"):
    from ..api.new import exampleinput

    return exampleinput(args.get("directory"))


@cli_entry
def cli_new_module(args):
    return module(args)


@cli_func
def module(args, __name__="new module"):
    from ..api.new import module

    ret = module(args.get("name"), args.get("type"), outer=args.get("outer"))
    if ret:
        print(f"Created {ret}")


def get_parser_fn_new():
    from argparse import ArgumentParser, RawDescriptionHelpFormatter

    parser_fn_new = ArgumentParser(formatter_class=RawDescriptionHelpFormatter)
    _subparsers = parser_fn_new.add_subparsers(title="Commands")

    # test input file
    parser_cli_new_exampleinput = _subparsers.add_parser(
        "exampleinput", help="makes a file with example input variants."
    )
    parser_cli_new_exampleinput.add_argument(
        "-d",
        dest="directory",
        default=".",
        help="Directory to make the example input file in",
    )
    parser_cli_new_exampleinput.add_argument(
        "--quiet", action="store_true", default=None, help="run quietly"
    )
    parser_cli_new_exampleinput.set_defaults(func=cli_new_exampleinput)
    parser_cli_new_exampleinput.r_return = "A string. Location of the example input file"  # type: ignore
    parser_cli_new_exampleinput.r_examples = [  # type: ignore
        "# Create an example input file in the current working directory",
        "#roakvar::new.exampleinput()",
        "# Create an example input file at /home/user1/",
        '#roakvar::new.exampleinput(directory="/home/user1")',
    ]

    # new-annotator
    parser_cli_new_annotator = _subparsers.add_parser(
        "module", help="creates a new module skeleton."
    )
    parser_cli_new_annotator.add_argument("-n", dest="name", help="Module name")
    parser_cli_new_annotator.add_argument("-t", dest="type", help="Module type")
    parser_cli_new_annotator.add_argument(
        "--quiet", action="store_true", default=None, help="No print to stdout"
    )
    parser_cli_new_annotator.set_defaults(func=cli_new_module)
    parser_cli_new_annotator.r_return = "A string. Location of the new annotator module"  # type: ignore
    parser_cli_new_annotator.r_examples = [  # type: ignore
        "# Create an annotator template at the OakVar modules directory/annotators/annotatortest",
        '#roakvar::new.annotator(annotator_name="annotatortest")',
    ]
    return parser_fn_new
