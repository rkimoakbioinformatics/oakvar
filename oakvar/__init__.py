from typing import Union
from typing import Type
from . import api
from .cli import __main__ as cli
from . import lib
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
from .lib.util.inout import FileReader
from .lib.util.inout import FileWriter
from .lib.util import inout
from .lib.util import admin_util
from .lib.util.util import get_df_from_db
from .lib.util.inout import read_crv
from .lib.util.seq import get_lifter
from .lib.util.seq import liftover
from .lib.util.seq import get_wgs_reader
from .cli import CliOuter
import signal

# for compatibility with oc
from .lib.exceptions import BadFormatError
from .lib.exceptions import InvalidData

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


def get_converter_class(module_name: str) -> Type[BaseConverter]:
    cls = get_module_class(module_name, module_type="converter")
    if not issubclass(cls, BaseConverter):
        raise ValueError(f"{module_name} is not a converter class.")
    return cls


def get_preparer_class(module_name: str) -> Type[BasePreparer]:
    cls = get_module_class(module_name, module_type="converter")
    if not issubclass(cls, BasePreparer):
        raise ValueError(f"{module_name} is not a converter class.")
    return cls


def get_mapper_class(module_name: str) -> Type[BaseMapper]:
    cls = get_module_class(module_name, module_type="mapper")
    if not issubclass(cls, BaseMapper):
        raise ValueError(f"{module_name} is not a mapper class.")
    return cls


def get_annotator_class(module_name: str) -> Type[BaseAnnotator]:
    cls = get_module_class(module_name, module_type="mapper")
    if not issubclass(cls, BaseAnnotator):
        raise ValueError(f"{module_name} is not a mapper class.")
    return cls


def get_reporter_class(module_name: str) -> Type[BaseReporter]:
    cls = get_module_class(module_name, module_type="mapper")
    if not issubclass(cls, BaseReporter):
        raise ValueError(f"{module_name} is not a mapper class.")
    return cls


def get_annotator(module_name, input_file=None) -> BaseAnnotator:

    input_file = input_file or "__dummy__"
    ModuleClass = get_module_class(module_name)
    if not ModuleClass:
        raise ValueError(f"{module_name} was not found.")
    if not issubclass(ModuleClass, BaseAnnotator):
        raise ValueError(f"{ModuleClass} is not an annotator class.")
    module = ModuleClass(input_file=input_file)
    module.connect_db()
    module.setup()
    return module


def get_mapper(module_name, input_file=None) -> BaseMapper:
    ModuleClass = get_module_class(module_name)
    if not ModuleClass:
        raise ValueError(f"{module_name} was not found.")
    if not issubclass(ModuleClass, BaseMapper):
        raise ValueError(f"{ModuleClass} is not a mapper class.")
    module = ModuleClass(input_file=input_file)
    module.setup()
    return module


def get_module_class(
    module_name, module_type: str = ""
) -> Union[
    Type[BaseConverter],
    Type[MasterConverter],
    Type[BasePreparer],
    Type[BaseMapper],
    Type[BaseAnnotator],
    Type[BasePostAggregator],
    Type[BaseReporter],
    Type[BaseCommonModule],
]:
    from .lib.module.local import get_local_module_info
    from .lib.util.util import load_class

    module_info = get_local_module_info(module_name, module_type=module_type)
    if module_info is None:
        raise ValueError(f"{module_name} does not exist.")
    script_path = module_info.script_path
    ModuleClass = load_class(script_path)
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
)
_ = CravatFilter or Cravat
_ = cli or wgs
_ = stdouter
_ = get_lifter or liftover or get_wgs_reader
_ = get_df_from_db or read_crv
