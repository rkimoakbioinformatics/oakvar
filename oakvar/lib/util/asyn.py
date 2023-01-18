loop = None


def get_event_loop():
    # from sys import platform as sysplatform
    import asyncio
    import nest_asyncio

    # import uvloop

    # uvloop.install()
    # asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    global loop
    if not loop:
        # if sysplatform == "win32":  # Required to use asyncio subprocesses
        #    #from asyncio import ProactorEventLoop  # type: ignore
        #    import asyncio
        #    #loop = ProactorEventLoop()
        #    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        #    loop = get_event_loop()
        # else:
        #    loop = get_event_loop()
        loop = asyncio.get_event_loop()
        nest_asyncio.apply(loop)
    return loop
