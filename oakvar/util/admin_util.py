class ReadyState(object):

    READY = 0
    MISSING_MD = 1
    UPDATE_NEEDED = 2
    NO_BASE_MODULES = 3

    messages = {
        0: "",
        1: "Modules directory not found",
        2: 'Update on system modules needed. Run "oc module install-base"',
        3: "Base modules do not exist.",
    }

    def __init__(self, code=READY):
        if code not in self.messages:
            raise ValueError(code)
        self.code = code

    @property
    def message(self):
        return self.messages[self.code]

    def __bool__(self):
        return self.code == self.READY

    def __iter__(self):
        yield "ready", bool(self)
        yield "code", self.code
        yield "message", self.message


def get_user_conf():
    from ..system import get_user_conf_path
    from ..util.util import load_yml_conf
    from os.path import exists

    conf_path = get_user_conf_path()
    if exists(conf_path):
        ret = load_yml_conf(conf_path)
        ret["conf_path"] = conf_path
        return ret
    else:
        return None


def get_current_package_version():
    from pkg_resources import get_distribution

    version = get_distribution("oakvar").version
    return version


def get_default_assembly():
    conf = get_user_conf()
    if conf:
        default_assembly = conf.get("default_assembly", None)
        return default_assembly


def get_last_assembly():
    conf = get_user_conf()
    if conf:
        last_assembly = conf.get("last_assembly")
        return last_assembly


def get_latest_package_version():
    """
    Return latest oakvar version on pypi
    """
    all_vers = get_package_versions()
    if all_vers:
        return all_vers[-1]
    else:
        return None


def get_package_versions():
    """
    Return available oakvar versions from pypi, sorted asc
    """
    import json
    from requests import get
    from requests.exceptions import ConnectionError
    from distutils.version import LooseVersion

    try:
        r = get("https://pypi.org/pypi/oakvar/json", timeout=(3, None))
    except ConnectionError:
        from ..exceptions import InternetConnectionError

        raise InternetConnectionError()
    if r.status_code == 200:
        d = json.loads(r.text)
        all_vers = list(d["releases"].keys())
        all_vers.sort(key=LooseVersion)
        return all_vers
    else:
        return None


async def get_updatable_async(modules=[], strategy="consensus"):
    from ..module import get_updatable

    update_vers, resolution_applied, resolution_failed = get_updatable(
        modules=modules, strategy=strategy
    )
    return [update_vers, resolution_applied, resolution_failed]


def get_widgets_for_annotator(annotator_name, skip_installed=False):
    from ..module.local import module_exists_local
    from ..module.remote import get_remote_module_info
    from ..module import list_remote
    from ..module.cache import get_module_cache

    linked_widgets = []
    l = list_remote()
    if not l:
        return None
    for widget_name in l:
        widget_info = get_remote_module_info(widget_name)
        if widget_info is not None and widget_info.type == "webviewerwidget":
            widget_config = get_module_cache().get_remote_module_piece_url(
                widget_name, "config"
            )
            if widget_config:
                linked_annotator = widget_config.get("required_annotator")
            else:
                linked_annotator = None
            if linked_annotator == annotator_name:
                if skip_installed and module_exists_local(widget_name):
                    continue
                else:
                    linked_widgets.append(widget_info)
    return linked_widgets


def input_formats():
    import os
    from ..system import get_modules_dir

    formats = set()
    d = os.path.join(get_modules_dir(), "converters")
    if os.path.exists(d):
        fns = os.listdir(d)
        for fn in fns:
            if fn.endswith("-converter"):
                formats.add(fn.split("-")[0])
    return formats


def install_widgets_for_module(module_name):
    from ..module import install_module

    widget_name = "wg" + module_name
    install_module(widget_name)


def fn_new_exampleinput(d):
    import shutil
    import os

    fn = "exampleinput"
    ifn = os.path.join(get_packagedir(), fn)
    ofn = os.path.join(d, fn)
    shutil.copyfile(ifn, ofn)
    return ofn


def new_annotator(annot_name):
    import shutil
    import os
    from ..system import get_modules_dir
    from ..module.cache import get_module_cache

    annot_root = os.path.join(get_modules_dir(), "annotators", annot_name)
    template_root = os.path.join(get_packagedir(), "annotator_template")
    shutil.copytree(template_root, annot_root)
    for dir_path, _, fnames in os.walk(annot_root):
        for old_fname in fnames:
            old_fpath = os.path.join(dir_path, old_fname)
            new_fname = old_fname.replace("annotator_template", annot_name, 1)
            new_fpath = os.path.join(dir_path, new_fname)
            os.rename(old_fpath, new_fpath)
    get_module_cache().update_local()


def ready_resolution_console():
    return system_ready()


def recursive_update(d1, d2):
    """
    Recursively merge two dictionaries and return a copy.
    d1 is merged into d2. Keys in d1 that are not present in d2 are preserved
    at all levels. The default Dict.update() only preserved keys at the top
    level.
    """
    import copy

    d3 = copy.deepcopy(d1)  # Copy perhaps not needed. Test.
    for k, v in d2.items():
        if k in d3:
            orig_v = d3[k]
            if isinstance(v, dict):
                if isinstance(orig_v, dict) == False:
                    d3[k] = v
                else:
                    t = recursive_update(d3.get(k, {}), v)
                    d3[k] = t
            else:
                d3[k] = d2[k]
        else:
            d3[k] = v
    return d3


def report_issue():
    import webbrowser

    webbrowser.open("http://github.com/rkimoakbioinformatics/oakvar/issues")


def set_user_conf_prop(key, val):
    import oyaml as yaml
    from ..system import get_user_conf_path

    conf = get_user_conf()
    if conf:
        conf[key] = val
        wf = open(get_user_conf_path(), "w")
        yaml.dump(conf, wf, default_flow_style=False)
        wf.close()


def set_jobs_dir(d):
    from ..system import update_system_conf_file

    update_system_conf_file({"jobs_dir": d})


# return a list of module types (e.g. annotators) in the local install
def show_main_conf(args):
    import oyaml as yaml
    from ..util.util import quiet_print

    conf = get_user_conf()
    if args["fmt"] == "yaml":
        conf = yaml.dump(conf, default_flow_style=False)
    if args["to"] == "stdout":
        quiet_print(conf, args=args)
    else:
        return conf


def oakvar_version():
    version = get_current_package_version()
    return version


def system_ready():
    import os
    from ..system import get_modules_dir
    from ..exceptions import NoModulesDir
    from ..exceptions import NoSystemModule

    modules_dir = get_modules_dir()
    if not (os.path.exists(modules_dir)):
        raise NoModulesDir()
    elif not (os.path.exists(os.path.join(modules_dir, "converters", "vcf-converter"))):
        raise NoSystemModule()
    else:
        return ReadyState()


def write_user_conf(user_conf):
    import oyaml as yaml
    from ..system import get_user_conf_path

    confpath = get_user_conf_path()
    wf = open(confpath, "w")
    yaml.dump(user_conf, wf, default_flow_style=False)
    wf.close()


def get_liftover_chain_paths():
    from os.path import join

    liftover_chains_dir = get_liftover_chains_dir()
    liftover_chain_paths = {
        "hg19": join(liftover_chains_dir, "hg19ToHg38.over.chain"),
        "hg18": join(liftover_chains_dir, "hg18ToHg38.over.chain"),
    }
    return liftover_chain_paths


def get_packagedir():
    import os.path

    return os.path.abspath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    )


def get_platform():
    from platform import platform

    pl = platform()
    if pl.startswith("Windows"):
        pl = "windows"
    elif pl.startswith("Darwin") or pl.startswith("macOS"):
        pl = "macos"
    elif pl.startswith("Linux"):
        pl = "linux"
    else:
        pl = "linux"
    return pl


def get_admindb_path():
    from os.path import join as pathjoin
    from ..system import get_conf_dir

    return pathjoin(get_conf_dir(), "admin.sqlite")


def get_liftover_chains_dir():
    from os.path import join as pathjoin

    return pathjoin(get_packagedir(), "liftover")


def get_max_version_supported_for_migration():
    from distutils.version import LooseVersion

    return LooseVersion("1.7.0")
