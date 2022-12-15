def run(args, __name__="run"):
    from ..lib.system import custom_system_conf
    from ..lib.base.runner import Runner
    from ..lib.util.asyn import get_event_loop

    # nested asyncio
    #nest_asyncio.apply()
    # Custom system conf
    custom_system_conf = {}
    system_option = args.get("system_option")
    if system_option:
        for kv in system_option:
            if "=" not in kv:
                continue
            toks = kv.split("=")
            if len(toks) != 2:
                continue
            [k, v] = toks
            try:
                v = int(v)
            except ValueError:
                pass
            custom_system_conf[k] = v
    module = Runner(**args)
    loop = get_event_loop()
    return loop.run_until_complete(module.main())

