loop = None

def get_event_loop():
    from sys import platform as sysplatform
    from asyncio import get_event_loop

    global loop
    if not loop:
        if sysplatform == "win32":  # Required to use asyncio subprocesses
            #from asyncio import ProactorEventLoop  # type: ignore
            import asyncio
            #loop = ProactorEventLoop()
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            loop = get_event_loop()
        else:
            loop = get_event_loop()
    return loop