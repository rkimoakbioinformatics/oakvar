def cli_entry(func):
    def change_args_for_cli(args):
        args.quiet = False
        args.to = "stdout"
        ret = func(args)
        exit(ret)

    return change_args_for_cli


def cli_func(func):
    def run_cli_func(*args, **kwargs):
        from argparse import Namespace
        from ..__main__ import handle_exception

        if len(args) > 0:
            if isinstance(args[0], Namespace):
                if getattr(args[0], "quiet", None) == None:
                    setattr(args[0], "quiet", True)
        elif kwargs.get("quiet") == None:
            kwargs["quiet"] = True
        args = get_args(*args, **kwargs)
        try:
            ret = func(args, **kwargs)
            if args.get("to") == "stdout":
                if ret == False:
                    ret = 1
                else:
                    ret = None
            return ret
        except Exception as e:
            handle_exception(e)

    def get_args(*args, **kwargs):
        from ..util.util import get_args
        from inspect import signature

        s = signature(func)
        name = s.parameters["__name__"].default
        parser = get_parser(name)
        args = get_args(parser, args, kwargs)
        return args

    return run_cli_func


def get_parser(parser_name):
    from ..__main__ import get_entry_parser
    from typing import Any

    p_entry = get_entry_parser()
    pp_dict: dict[str, Any] = get_commands(p_entry)
    for pp_cmd, pp_parser in pp_dict.items():
        ppp_dict = get_commands(pp_parser)
        if ppp_dict:
            for ppp_cmd, ppp_parser in ppp_dict.items():
                pppp_dict = get_commands(ppp_parser)
                if pppp_dict:
                    for pppp_cmd, pppp_parser in pppp_dict.items():
                        cmd = f"{pp_cmd} {ppp_cmd} {pppp_cmd}"
                        if cmd == parser_name:
                            return pppp_parser
                else:
                    cmd = f"{pp_cmd} {ppp_cmd}"
                    if cmd == parser_name:
                        return ppp_parser
        else:
            cmd = f"{pp_cmd}"
            if cmd == parser_name:
                return pp_parser
    return None


def get_commands(p):
    from argparse import _SubParsersAction
    from typing import Any

    cmds: dict[str, Any] = {}
    for a in p._actions:
        if type(a) == _SubParsersAction:
            cmds = a.choices
            break
    return cmds
