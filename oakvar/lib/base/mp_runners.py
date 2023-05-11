from typing import Type


def init_worker():
    import signal

    signal.signal(signal.SIGINT, signal.SIG_IGN)


def annot_from_queue(
    start_queue, end_queue, queue_populated, serveradmindb, logtofile, log_path
):
    from ..util.util import load_class
    from logging import getLogger, StreamHandler, FileHandler, Formatter
    from queue import Empty
    from ..exceptions import ModuleLoadingError
    from ..base.annotator import BaseAnnotator

    while True:
        try:
            task = start_queue.get(True, 1)
        except Empty:
            if queue_populated:
                break
            else:
                continue
        logger = None
        module, kwargs = task
        try:
            logger = getLogger(module.name)
            if logtofile and log_path:
                log_handler = FileHandler(log_path, "a")
            else:
                log_handler = StreamHandler()
            formatter = Formatter(
                "%(asctime)s %(name)-20s %(message)s", "%Y/%m/%d %H:%M:%S"
            )
            log_handler.setFormatter(formatter)
            logger.addHandler(log_handler)
        except Exception:
            import traceback

            traceback.print_exc()
        try:
            kwargs["serveradmindb"] = serveradmindb
            annotator_class = load_class(module.script_path)
            if not issubclass(annotator_class, BaseAnnotator):
                err = ModuleLoadingError(module_name=module.name)
                if logger:
                    logger.exception(err)
                continue
            annotator = annotator_class(**kwargs)
            annotator.run()
            end_queue.put(module.name)
        except Exception:
            err = ModuleLoadingError(module_name=module.name)
            if logger:
                logger.exception(err)

