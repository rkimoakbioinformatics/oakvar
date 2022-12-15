def setup(args, __name__="system setup"):
    from ..lib.system import setup_system

    return setup_system(args)


def md(args, __name__="system md"):
    from ..lib.system import set_modules_dir, get_modules_dir
    from ..lib.util.util import quiet_print

    d = args.get("directory")
    if d:
        set_modules_dir(d)
    d = get_modules_dir()
    if args.get("to") == "stdout":
        if d is not None:
            quiet_print(d, args=args)
    else:
        return d


def check(args, __name__="system check"):
    from ..lib.system import check

    ret = check(args)
    return ret

