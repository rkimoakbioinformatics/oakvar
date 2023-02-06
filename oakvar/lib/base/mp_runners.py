def init_worker():
    import signal

    signal.signal(signal.SIGINT, signal.SIG_IGN)


def annot_from_queue(start_queue, end_queue, queue_populated, serveradmindb, logtofile):
    from ..util.util import load_class
    from logging import getLogger, StreamHandler, FileHandler, Formatter
    from queue import Empty
    from ..exceptions import ModuleLoadingError

    while True:
        try:
            task = start_queue.get(True, 1)
        except Empty:
            if queue_populated:
                break
            else:
                continue
        module, kwargs = task
        logger = getLogger(module.name)
        if logtofile:
            log_handler = FileHandler(kwargs["log_path"], "a")
        else:
            log_handler = StreamHandler()
        formatter = Formatter(
            "%(asctime)s %(name)-20s %(message)s", "%Y/%m/%d %H:%M:%S"
        )
        log_handler.setFormatter(formatter)
        logger.addHandler(log_handler)
        try:
            kwargs["serveradmindb"] = serveradmindb
            annotator_class = load_class(module.script_path, "Annotator")
            if not annotator_class:
                annotator_class = load_class(module.script_path, "CravatAnnotator")
            annotator = annotator_class(**kwargs)
            annotator.run()
            end_queue.put(module.name)
        except Exception as _:
            err = ModuleLoadingError(module_name=module.name)
            logger.exception(err)


def mapper_runner(
    crv_path,
    seekpos,
    chunksize,
    run_name,
    output_dir,
    module_name,
    pos_no,
    primary_transcript,
    serveradmindb,
):
    from ..util.util import load_class
    from ..module.local import get_local_module_info

    output = None
    module = get_local_module_info(module_name)
    if module is not None:
        kwargs = {
            "input_file": crv_path,
            "run_name": run_name,
            "seekpos": seekpos,
            "chunksize": chunksize,
            "postfix": f".{pos_no:010.0f}",
            "output_dir": output_dir,
        }
        if primary_transcript is not None:
            kwargs["primary_transcript"] = primary_transcript.split(";")
        kwargs["serveradmindb"] = serveradmindb
        genemapper_class = load_class(module.script_path, "Mapper")
        genemapper = genemapper_class(**kwargs)
        output = genemapper.run(pos_no)
    return output
