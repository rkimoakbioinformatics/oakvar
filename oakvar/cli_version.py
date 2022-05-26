def fn_version(args):
    from .admin_util import oakvar_version
    from .util import get_dict_from_namespace

    args = get_dict_from_namespace(args)
    ret = oakvar_version()
    if args["to"] == "stdout":
        print(ret)
    else:
        return ret


def get_parser_fn_version():
    from argparse import ArgumentParser

    # shows version
    parser_fn_version = ArgumentParser()
    parser_fn_version.add_argument(
        "--to", default="stdout", help='"stdout" to print. "return" to return')
    parser_fn_version.set_defaults(func=fn_version)
    return parser_fn_version
