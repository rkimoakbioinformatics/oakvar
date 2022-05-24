def args_func(func):
    def get_dict_from_namespace(n):
        from types import SimpleNamespace
        from argparse import Namespace
        if type(n) == SimpleNamespace or type(n) == Namespace:
            n = vars(n)
        return func(n)
    return get_dict_from_namespace
