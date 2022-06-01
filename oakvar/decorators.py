def cli_func(func):

    def run_cli_func(*args, **kwargs):
        args = get_args(*args, **kwargs)
        try:
            return func(args)
        except Exception as e:
            from .__main__ import handle_exception
            handle_exception(e)

    def get_args(*args, **kwargs):
        from .util import get_args
        parser = get_parser(func.__name__)
        final_args = get_args(parser, args, kwargs)
        return final_args

    return run_cli_func

def get_parser(parser_name):
    from .__main__ import get_entry_parser
    from typing import Any
    p_entry = get_entry_parser()
    pp_dict: dict[str, Any] = get_commands(p_entry)
    for pp_cmd, pp_parser in pp_dict.items():
        ppp_dict = get_commands(pp_parser)
        if ppp_dict:
            for ppp_cmd, ppp_parser in ppp_dict.items():
                cmd = f"ov_{pp_cmd}_{ppp_cmd}"
                if cmd == parser_name:
                    return ppp_parser
        else:
            cmd = f"ov_{pp_cmd}"
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
