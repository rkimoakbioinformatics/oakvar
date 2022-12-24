from .api import version
from .api.util import sqliteinfo as util_sqliteinfo
from .api.util import mergesqlite as util_mergesqlite
from .api.util import filtersqlite as util_filtersqlite
from .api.util import addjob as util_addjob
from .api.test import test
from .api.system import setup as system_setup
from .api.system import md as system_md
from .api.store import register as store_register
from .api.store.account import reset as store_account_reset
from .api.store.account import create as store_account_create
from .api.store.account import check as store_account_check
from .api.store.account import change as store_account_change
from .api.store import fetch as store_fetch
from .api.module import pack as module_pack
from .api.new import module as new_annotator
from .api.new import exampleinput as new_exampleinput
from .api.issue import issue
from .api.report import report
from .api.run import run
from .api.module import update as module_update
from .api.module import uninstall as module_uninstall
from .api.module import ls as module_ls
from .api.module import installbase as module_installbase
from .api.module import install as module_install
from .api.module import info as module_info
from .api.config import user as config_user
from .api.config import system as config_system
from . import api as api
from .cli import __main__ as cli
from .cli.report import report
from .lib import consts
from .lib.exceptions import *
from .lib.base.runner import Runner
from .lib.base.converter import BaseConverter
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
import signal

# for compatibility with oc
Cravat = Runner
CravatReport = BaseReporter
BaseReport = BaseReporter
CravatFilter = ReportFilter
constants = consts


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


# from .api.util import ov_util_updateresult

wgs = None
_ = admin_util or inout
_ = (
    BaseConverter
    or BasePreparer
    or BaseAnnotator
    or BaseMapper
    or BasePostAggregator
    or BaseCommonModule
    or VCF2VCF
)
_ = CravatReport or ReportFilter or Runner
_ = CravatFilter or Cravat
_ = FileReader or FileWriter
_ = cli or wgs
_ = (
    module_info
    or module_install
    or module_installbase
    or module_ls
    or module_uninstall
    or module_update
)
_ = report or run or issue or version or config_user or config_system
_ = new_exampleinput or new_annotator
_ = (
    store_account_reset
    or store_register
    or store_account_create
    or store_account_check
    or store_account_change
    or store_fetch
    or module_pack
)
_ = system_setup or system_md
_ = test
_ = util_addjob or util_filtersqlite or util_mergesqlite or util_sqliteinfo


def get_live_annotator(module_name, input_file=None):
    import os

    module = None
    input_file = input_file or "__dummy__"
    ModuleClass = get_module(module_name)
    if ModuleClass:
        module = ModuleClass(input_file=input_file, live=True)
        module.annotator_name = module_name
        module.name = module_name
        module.annotator_dir = os.path.dirname(module.script_path)
        module.data_dir = os.path.join(module.module_dir, "data")
        module.connect_db()
        module.setup()
    return module


def get_live_mapper(module_name, input_file=None):
    from os.path import abspath

    module = None
    ModuleClass = get_module(module_name)
    if ModuleClass:
        module = ModuleClass(
            {
                "script_path": abspath(ModuleClass.script_path),
                "input_file": input_file or None,
                "live": True,
            }
        )
        module.name = module_name
        module.setup()
    return module


def get_module(module_name, module_type=None):
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
        ModuleClass.script_path = script_path
        ModuleClass.module_name = module_name
        ModuleClass.module_dir = dirname(script_path)
        ModuleClass.conf = module_conf
    return ModuleClass


def get_wgs_reader(assembly="hg38"):
    ModuleClass = get_module(assembly + "wgs")
    if ModuleClass is None:
        wgs = None
    else:
        wgs = ModuleClass()
        wgs.setup()
    return wgs


class LiveAnnotator:
    def __init__(self, mapper="hg38", annotators=[]):
        self.live_annotators = {}
        self.load_live_modules(mapper, annotators)
        self.variant_uid = 1
        self.live_mapper = None

    def load_live_modules(self, mapper, annotator_names):
        from .lib.module.cache import get_module_cache

        self.live_mapper = get_live_mapper(mapper)
        for module_name in get_module_cache().local.keys():
            if module_name in annotator_names:
                module = get_module_cache().local[module_name]
                if "secondary_inputs" in module.conf:
                    continue
                annotator = get_live_annotator(module.name)
                if annotator is None:
                    continue
                self.live_annotators[module.name] = annotator

    def clean_annot_dict(self, d):
        keys = d.keys()
        for key in keys:
            value = d[key]
            if value == "" or value == {}:
                d[key] = None
            elif type(value) is dict:
                d[key] = self.clean_annot_dict(value)
        if type(d) is dict:
            all_none = True
            for key in keys:
                if d[key] is not None:
                    all_none = False
                    break
            if all_none:
                d = None
        return d

    def annotate(self, crv):
        from .lib.util.inout import AllMappingsParser
        from .lib.consts import all_mappings_col_name

        if "uid" not in crv:
            crv["uid"] = self.variant_uid
            self.variant_uid += 1
        response = {}
        crx_data = None
        if self.live_mapper is not None:
            crx_data = self.live_mapper.map(crv)
            crx_data = self.live_mapper.live_report_substitute(crx_data)
            crx_data["tmp_mapper"] = AllMappingsParser(crx_data[all_mappings_col_name])
        for k, v in self.live_annotators.items():
            try:
                if crx_data is not None:
                    annot_data = v.annotate(input_data=crx_data)
                    annot_data = v.live_report_substitute(annot_data)
                    if annot_data == "" or annot_data == {}:
                        annot_data = None
                    elif type(annot_data) is dict:
                        annot_data = self.clean_annot_dict(annot_data)
                    response[k] = annot_data
            except Exception as _:
                import traceback

                traceback.print_exc()
                response[k] = None
        if crx_data is not None and "tmp_mapper" in crx_data:
            del crx_data["tmp_mapper"]
        if crx_data is not None:
            response["base"] = crx_data
        return response
