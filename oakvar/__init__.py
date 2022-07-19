from .cli.version import version
from .cli.util import sqliteinfo
from .cli.util import mergesqlite
from .cli.util import filtersqlite
from .cli.util import addjob
from .cli.test import test
from .cli.system import setup
from .cli.system import md
from .cli.system import config
from .cli.store import register
from .cli.store.account import reset
from .cli.store.account import create
from .cli.store.account import check
from .cli.store.account import change
from .cli.store import fetch
from .cli.module import pack
from .cli.store.oc import oc_publish
from .cli.store.oc import oc_newaccount
from .cli.store.oc import oc_changepw
from .cli.store.oc import oc_resetpw
from .cli.store.oc import oc_verifyemail
from .cli.store.oc import oc_checklogin
from .cli.new import annotator
from .cli.new import exampleinput
from .cli.issue import issue
from .cli.gui import gui
from .cli.report import report
from .cli.run import run
from .cli.module import update
from .cli.module import uninstall
from .cli.module import ls
from .cli.module import installbase
from .cli.module import install
from .cli.module import info
from .cli.config import user
from . import __main__ as cli
from . import consts
from .exceptions import *
from .consts import crx_def
from .cli.run import Cravat
from .base.cravat_filter import CravatFilter
from .cli.report import CravatReport
from .base.commonmodule import BaseCommonModule
from .base.postaggregator import BasePostAggregator
from .base.mapper import BaseMapper
from .base.annotator import BaseAnnotator
from .base.converter import BaseConverter
from .base.vcf2vcf import VCF2VCF
from .util import inout
from .util import admin_util
import signal

BaseReport = CravatReport
# for compatibility with oc
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


signal.signal(signal.SIGINT, raise_break)
# from .cli.util import ov_util_updateresult


wgs = None
_ = admin_util or inout
_ = (
    BaseConverter
    or BaseAnnotator
    or BaseMapper
    or BasePostAggregator
    or BaseCommonModule
    or VCF2VCF
)
_ = CravatReport or CravatFilter or Cravat
_ = crx_def or consts
_ = cli or wgs
_ = info or install or installbase or ls or uninstall or update
_ = report or run or gui or issue or version or user
_ = exampleinput or annotator
_ = reset or register or create or check or change or fetch or pack
_ = setup or md or config
_ = test
_ = addjob or filtersqlite or mergesqlite or sqliteinfo
_ = (
    oc_publish
    or oc_newaccount
    or oc_changepw
    or oc_resetpw
    or oc_verifyemail
    or oc_checklogin
)


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
        module._open_db_connection()
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
    from .module.local import get_local_module_info
    from .module.local import get_module_conf
    from .util.util import load_class

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
        from .module.cache import get_module_cache

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
        from .util.inout import AllMappingsParser
        from .consts import all_mappings_col_name

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
