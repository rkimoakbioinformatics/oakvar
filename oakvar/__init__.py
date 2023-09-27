from . import lib
from . import api
from . import cli
from .lib import consts
from .lib.base.runner import Runner
from .lib.base.converter import BaseConverter
from .lib.base.preparer import BasePreparer
from .lib.base.mapper import BaseMapper
from .lib.base.annotator import BaseAnnotator
from .lib.base.postaggregator import BasePostAggregator
from .lib.base.db_filter import DbFilter
from .lib.base.reporter import BaseReporter
from .lib.base.commonmodule import BaseCommonModule
from .lib.base.vcf2vcf import VCF2VCF
from .lib.base.worker import Worker
from .lib.base.worker import ParallelWorker
from .lib.base.variant import Variant
from .lib.base.app import BaseApp
from .lib.util.inout import FileReader
from .lib.util.inout import FileWriter
from .lib.util import inout
from .lib.util import admin_util
from .lib.util.util import get_df_from_db
from .lib.util.inout import read_crv
from .lib.util.seq import get_lifter
from .lib.util.seq import liftover
from .lib.util.seq import get_wgs_reader
from .lib.util.module import get_converter
from .lib.util.module import get_mapper
from .lib.util.module import get_annotator
from .lib.util.module import get_postaggregator
from .lib.util.module import get_reporter
from .cli import CliOuter
import signal

# for compatibility with oc
from .lib.exceptions import BadFormatError
from .lib.exceptions import InvalidData

Cravat = Runner
CravatReport = BaseReporter
BaseReport = BaseReporter
CravatFilter = DbFilter
constants = consts

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


wgs = None
_ = api or lib
_ = BadFormatError or InvalidData
_ = admin_util or inout
_ = (
    BaseConverter
    or BasePreparer
    or BaseAnnotator
    or BaseMapper
    or BasePostAggregator
    or BaseCommonModule
    or VCF2VCF
    or CravatReport
    or DbFilter
    or Runner
    or FileReader
    or FileWriter
    or Worker
    or ParallelWorker
    or Variant
    or BaseApp
)
_ = CravatFilter or Cravat
_ = cli or wgs
_ = stdouter
_ = get_lifter or liftover or get_wgs_reader
_ = get_df_from_db or read_crv
_ = get_converter or get_mapper or get_annotator or get_postaggregator or get_reporter
