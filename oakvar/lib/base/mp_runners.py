# OakVar Dual License
# 
# Copyright (c) 2023 Oak Bioinformatics, LLC
# 
# This program is dual licensed under the Affero GPL-3.0 or later for 
# non-commercial and open source use, and under a commercial license, 
# which is available for purchase, for closed-source or commercial use.
# 
# For the commercial use, please contact Oak Bioinformatics, LLC 
# for obtaining such a license. OakVar commercial license does not impose 
# the Affero GPL open-source licensing terms, conditions, and limitations. 
# To obtain a commercial-use license of OakVar, please visit our website at
# https://oakbioinformatics.com or contact us at info@oakbioinformatics.com 
# for more information.
# 
# ================
# OpenCRAVAT
# 
# MIT License
# 
# Copyright (c) 2021 KarchinLab
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

def init_worker():
    import signal

    signal.signal(signal.SIGINT, signal.SIG_IGN)


def annot_from_queue(
    start_queue, end_queue, queue_populated, serveradmindb, logtofile, log_path
):
    import sys
    from logging import getLogger
    from logging import StreamHandler
    from logging import FileHandler
    from logging import Formatter
    from queue import Empty
    from ..util.util import load_class
    from ..exceptions import ModuleLoadingError

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
            logger.setLevel("INFO")
            if logtofile and log_path:
                log_handler = FileHandler(log_path, "a")
            else:
                log_handler = StreamHandler(stream=sys.stdout)
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
            kwargs["logger"] = logger
            annotator_class = load_class(module.script_path, "Annotator")
            if not annotator_class:
                annotator_class = load_class(module.script_path, "CravatAnnotator")
            if annotator_class:
                annotator = annotator_class(**kwargs)
                annotator.run()
                end_queue.put(module.name)
            else:
                raise ModuleLoadingError(msg=f"Annotator of {module.name} could not be loaded.")
        except Exception:
            err = ModuleLoadingError(module_name=module.name)
            if logger:
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
    from ..exceptions import ModuleLoadingError

    output = None
    module = get_local_module_info(module_name)
    if module is not None:
        if primary_transcript:
            primary_transcript = primary_transcript.split(";")
        genemapper_class = load_class(module.script_path, "Mapper")
        if genemapper_class:
            genemapper = genemapper_class(
                input_file=crv_path,
                run_name=run_name,
                seekpos=seekpos,
                chunksize=chunksize,
                postfix=f".{pos_no:010.0f}",
                primary_transcript=primary_transcript,
                serveradmindb=serveradmindb,
                output_dir=output_dir,
            )
            output = genemapper.run(pos_no)
        else:
            raise ModuleLoadingError(msg=f"Mapper of {module_name} could not be loaded.")
    return output
