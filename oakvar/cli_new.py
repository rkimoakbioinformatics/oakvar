def fn_new_exampleinput(args):
    from .admin_util import fn_new_exampleinput
    from .util import get_dict_from_namespace

    args = get_dict_from_namespace(args)
    fn_new_exampleinput(args["directory"])


def fn_new_annotator(args):
    from .admin_util import new_annotator, get_local_module_info
    from .util import get_dict_from_namespace
    from .constants import custom_modules_dir

    args = get_dict_from_namespace(args)
    if args["md"] is not None:
        custom_modules_dir = args["md"]
    new_annotator(args["annotator_name"])
    module_info = get_local_module_info(args["annotator_name"])
    print(f"created {module_info.directory}")
    return module_info.directory


from argparse import ArgumentParser, RawDescriptionHelpFormatter

parser_fn_new = ArgumentParser(formatter_class=RawDescriptionHelpFormatter)
_subparsers = parser_fn_new.add_subparsers(title="Commands")

# test input file
parser_fn_new_exampleinput = _subparsers.add_parser(
    "exampleinput", help="makes a file with example input variants."
)
parser_fn_new_exampleinput.add_argument(
    "-d",
    dest="directory",
    default=".",
    help="Directory to make the example input file in",
)
parser_fn_new_exampleinput.set_defaults(func=fn_new_exampleinput)

# new-annotator
parser_fn_new_annotator = _subparsers.add_parser(
    "annotator", help="creates a new annotator"
)
parser_fn_new_annotator.add_argument(
    "-n", dest="annotator_name", default="annotator", help="Annotator name"
)
parser_fn_new_annotator.add_argument(
    "--md", default=None, help="Specify the root directory of OakVar modules"
)
parser_fn_new_annotator.set_defaults(func=fn_new_annotator)
