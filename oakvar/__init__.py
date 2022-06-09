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


import signal

signal.signal(signal.SIGINT, raise_break)
from . import admin_util
from . import inout
from .base_converter import BaseConverter
from .base_annotator import BaseAnnotator
from .base_mapper import BaseMapper
from .base_postaggregator import BasePostAggregator
from .base_commonmodule import BaseCommonModule
from .cli_report import CravatReport
from .cravat_filter import CravatFilter
from .cli_run import Cravat
from .constants import crx_def
from .exceptions import *
from . import constants
from . import __main__ as cli
from .cli_module import ov_module_info
from .cli_module import ov_module_install
from .cli_module import ov_module_installbase
from .cli_module import ov_module_ls
from .cli_module import ov_module_uninstall
from .cli_module import ov_module_update
from .cli_run import ov_run
from .cli_report import ov_report
from .cli_gui import ov_gui
from .cli_issue import ov_issue
from .cli_new import ov_new_exampleinput
from .cli_new import ov_new_annotator
from .cli_store import ov_store_changepassword
from .cli_store import ov_store_checklogin
from .cli_store import ov_store_createaccount
from .cli_store import ov_store_publish
from .cli_store import ov_store_resetpassword
from .cli_store import ov_store_verifyemail
from .cli_system import ov_system_config
from .cli_system import ov_system_md
from .cli_system import ov_system_setup
from .cli_test import ov_util_test
from .cli_util import ov_util_addjob
from .cli_util import ov_util_filtersqlite
from .cli_util import ov_util_mergesqlite
from .cli_util import ov_util_sqliteinfo
#from .cli_util import ov_util_updateresult
from .cli_version import ov_version


wgs = None
if admin_util or inout: pass
if BaseConverter or BaseAnnotator or BaseMapper or BasePostAggregator or BaseCommonModule: pass
if CravatReport or CravatFilter or Cravat: pass
if crx_def or constants: pass
if cli or wgs: pass
if ov_module_info or ov_module_install or ov_module_installbase or ov_module_ls or ov_module_uninstall or ov_module_update: pass
if ov_report: pass
if ov_run: pass
if ov_gui: pass
if ov_issue: pass
if ov_new_exampleinput or ov_new_annotator: pass
if ov_store_verifyemail or ov_store_resetpassword or ov_store_publish or ov_store_createaccount or ov_store_checklogin or ov_store_changepassword: pass
if ov_system_setup or ov_system_md or ov_system_config: pass
if ov_util_test: pass
if ov_util_addjob or ov_util_filtersqlite or ov_util_mergesqlite or ov_util_sqliteinfo: pass
if ov_version: pass


def get_live_annotator(module_name):
    import os
    module = None
    ModuleClass = get_module(module_name)
    if ModuleClass:
        module = ModuleClass(input_file="__dummy__", live=True)
        module.annotator_name = module_name
        module.annotator_dir = os.path.dirname(module.script_path)
        module.data_dir = os.path.join(module.module_dir, "data")
        module._open_db_connection()
        module.setup()
    return module


def get_live_mapper(module_name):
    import os
    module = None
    ModuleClass = get_module(module_name)
    if ModuleClass:
        module = ModuleClass({
            "script_path":
            os.path.abspath(ModuleClass.script_path),
            "input_file":
            "__dummy__",
            "live":
            True,
        })
        module.base_setup()
    return module


def get_module(module_name, module_type=None):
    from os.path import dirname
    from .admin_util import get_local_module_info
    from .admin_util import get_module_conf
    from .util import load_class
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
        from .admin_util import get_mic
        self.live_mapper = get_live_mapper(mapper)
        for module_name in get_mic().local.keys():
            if module_name in annotator_names:
                module = get_mic().local[module_name]
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
        from .inout import AllMappingsParser
        from oakvar.constants import all_mappings_col_name
        if "uid" not in crv:
            crv["uid"] = self.variant_uid
            self.variant_uid += 1
        response = {}
        crx_data = None
        if self.live_mapper is not None:
            crx_data = self.live_mapper.map(crv)
            crx_data = self.live_mapper.live_report_substitute(crx_data)
            crx_data["tmp_mapper"] = AllMappingsParser(
                crx_data[all_mappings_col_name])
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
