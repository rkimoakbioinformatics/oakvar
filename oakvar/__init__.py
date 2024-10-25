# OakVar
#
# Copyright (c) 2024 Oak Bioinformatics, LLC
#
# All rights reserved.
#
# Do not distribute or use this software without obtaining
# a license from Oak Bioinformatics, LLC.
#
# Do not use this software to develop another software
# which competes with the products by Oak Bioinformatics, LLC,
# without obtaining a license for such use from Oak Bioinformatics, LLC.
#
# For personal use of non-commercial nature, you may use this software
# after registering with `ov store account create`.
#
# For research use of non-commercial nature, you may use this software
# after registering with `ov store account create`.
#
# For use by commercial entities, you must obtain a commercial license
# from Oak Bioinformatics, LLC. Please write to info@oakbioinformatics.com
# to obtain the commercial license.
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

import signal
from . import lib
from . import api
from . import cli
from .lib import consts
from .lib.base.runner import Runner
from .lib.base.converter import BaseConverter
from .lib.base.master_converter import MasterConverter
from .lib.base.preparer import BasePreparer
from .lib.base.mapper import BaseMapper
from .lib.base.annotator import BaseAnnotator
from .lib.base.postaggregator import BasePostAggregator
from .lib.base.report_filter import ReportFilter
from .lib.base.reporter import BaseReporter
from .lib.base.commonmodule import BaseCommonModule
from .lib.base.vcf2vcf import VCF2VCF
from .lib.base.app import BaseApp
from .lib.util.inout import FileReader
from .lib.util.inout import FileWriter
from .lib.util import inout
from .lib.util import admin_util
from .lib.util.util import get_df_from_db
from .lib.util.util import get_sample_uid_variant_arrays
from .lib.util.inout import read_crv
from .lib.util.seq import get_lifter
from .lib.util.seq import liftover
from .lib.util.seq import get_wgs_reader
from .cli import CliOuter
# for compatibility with oc
from .lib.exceptions import BadFormatError
from .lib.exceptions import InvalidData
# for Rust spawn
import multiprocessing
multiprocessing.set_start_method("spawn", force=True)


Cravat = Runner
CravatReport = BaseReporter
BaseReport = BaseReporter
CravatFilter = ReportFilter
constants = consts

#

stdouter = CliOuter()


def raise_break(__signal_number__, __stack_frame__):
    import os
    import platform
    import psutil

    pl = platform.platform()
    if pl.startswith("Windows"):
        pid = os.getpid()
        for child in psutil.Process(pid).children(recursive=True):
            try:
                child.kill()
            except psutil.NoSuchProcess:  # keep
                pass
        os.kill(pid, signal.SIGTERM)
    elif pl.startswith("Linux"):
        pid = os.getpid()
        for child in psutil.Process(pid).children(recursive=True):
            try:
                child.kill()
            except psutil.NoSuchProcess:  # keep
                pass
        os.kill(pid, signal.SIGTERM)
    elif pl.startswith("Darwin") or pl.startswith("macOS"):
        pid = os.getpid()
        for child in psutil.Process(pid).children(recursive=True):
            try:
                child.kill()
            except psutil.NoSuchProcess:  # keep
                pass
        os.kill(pid, signal.SIGTERM)


def get_annotator(module_name, input_file=None) -> BaseAnnotator:
    from .lib.exceptions import ModuleLoadingError

    try:
        module = None
        input_file = input_file or "__dummy__"
        ModuleClass = get_module(module_name)
        if ModuleClass is None:
            raise ModuleLoadingError(module_name)
        module = ModuleClass(input_file=input_file)
        if module is None:
            raise ModuleLoadingError(module_name)
        module.connect_db()
        module.setup()
        return module
    except Exception:
        import traceback
        msg = traceback.format_exc()
        raise ModuleLoadingError(msg=msg)


def get_mapper(module_name, input_file=None) -> BaseMapper:
    from .lib.exceptions import ModuleLoadingError

    module = None
    ModuleClass = get_module(module_name, module_type="mapper")
    if ModuleClass is None:
        raise ModuleLoadingError(module_name)
    if not issubclass(ModuleClass, BaseMapper):
        raise ModuleLoadingError(msg=f"{module_name} is not a mapper module.")
    module = ModuleClass(input_file=input_file)
    if module is None:
        raise ModuleLoadingError(module_name)
    module.name = module_name
    module.setup()
    return module


def get_converter(module_name, *args, input_file=None, **kwargs):
    module = None
    ModuleClass = get_module(module_name, module_type="converter")
    if ModuleClass:
        module = ModuleClass()
        module.name = module_name
        module.setup(input_file, *args, **kwargs)
    return module


def get_module(module_name, module_type: str = ""):
    from os.path import dirname
    from .lib.module.local import get_local_module_info
    from .lib.module.local import get_module_conf
    from .lib.util.util import load_class

    ModuleClass = None
    module_conf = get_module_conf(module_name, module_type=module_type)
    module_info = get_local_module_info(module_name)
    if module_info is not None:
        script_path = module_info.script_path
        ModuleClass = load_class(script_path)
        ModuleClass.script_path = script_path  # type: ignore
        ModuleClass.module_name = module_name  # type: ignore
        ModuleClass.module_dir = dirname(script_path)  # type: ignore
        ModuleClass.conf = module_conf  # type: ignore
    return ModuleClass


wgs = None
_ = api or lib
_ = BadFormatError or InvalidData
_ = admin_util or inout
_ = (
    BaseConverter
    or MasterConverter
    or BasePreparer
    or BaseAnnotator
    or BaseMapper
    or BasePostAggregator
    or BaseCommonModule
    or VCF2VCF
    or CravatReport
    or ReportFilter
    or Runner
    or FileReader
    or FileWriter
    or BaseApp
)
_ = CravatFilter or Cravat
_ = cli or wgs
_ = stdouter
_ = get_lifter or liftover or get_wgs_reader
_ = get_df_from_db or get_sample_uid_variant_arrays or read_crv
