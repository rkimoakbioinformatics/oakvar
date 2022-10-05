from typing import Dict
from typing import Tuple
from typing import Optional


def get_ucsc_bins(start, stop=None):
    if stop is None:
        stop = start + 1

    def range_per_level(start, stop):
        BIN_OFFSETS = [512 + 64 + 8 + 1, 64 + 8 + 1, 8 + 1, 1, 0]
        SHIFT_FIRST = 17
        SHIFT_NEXT = 3

        start_bin = start
        stop_bin = max(start, stop - 1)

        start_bin >>= SHIFT_FIRST
        stop_bin >>= SHIFT_FIRST

        for offset in BIN_OFFSETS:
            yield offset + start_bin, offset + stop_bin
            start_bin >>= SHIFT_NEXT
            stop_bin >>= SHIFT_NEXT

    return [
        x
        for first, last in range_per_level(start, stop)
        for x in range(first, last + 1)
    ]



def get_caller_name(path):
    from os.path import abspath, basename

    path = abspath(path)
    basename = basename(path)
    if "." in basename:
        module_name = ".".join(basename.split(".")[:-1])
    else:
        module_name = basename
    return module_name


def load_class(path, class_name=None):
    """Load a class from the class's name and path. (dynamic importing)"""
    from os.path import dirname, basename
    from importlib.util import spec_from_file_location, module_from_spec
    from importlib import import_module
    import sys
    import inspect
    from ..exceptions import ModuleLoadingError

    path_dir = dirname(path)
    sys.path = [path_dir] + sys.path
    module = None
    module_class = None
    module_name = basename(path).split(".")[0]
    try:
        module = import_module(module_name)
    except Exception as _:
        try:
            if class_name:
                spec = spec_from_file_location(class_name, path)
                if spec is not None:
                    module = module_from_spec(spec)
                    loader = spec.loader
                    if loader is not None:
                        loader.exec_module(module)
        except Exception as _:
            raise ModuleLoadingError(module_name)
    if module:
        if class_name:
            if hasattr(module, class_name):
                module_class = getattr(module, class_name)
                if not inspect.isclass(module_class):
                    module_class = None
        else:
            for n in dir(module):
                if n in [
                    "Converter",
                    "Mapper",
                    "Annotator",
                    "PostAggregator",
                    "Reporter",
                    "CommonModule",
                    "CravatConverter",
                    "CravatMapper",
                    "CravatAnnotator",
                    "CravatPostAggregator",
                    "CravatReporter",
                    "CravatCommonModule",
                    ]:
                    if hasattr(module, n):
                        module_class = getattr(module, n)
                        if not inspect.isclass(module_class):
                            module_class = None
    del sys.path[0]
    return module_class


def get_directory_size(start_path):
    """
    Recursively get directory filesize.
    """
    from os import walk
    from os.path import join, getsize
    from ..store.consts import pack_ignore_fnames

    total_size = 0
    for dirpath, _, filenames in walk(start_path):
        for fname in filenames:
            if fname in pack_ignore_fnames:
                continue
            fp = join(dirpath, fname)
            total_size += getsize(fp)
    return total_size


def get_argument_parser_defaults(parser):
    defaults = {
        action.dest: action.default
        for action in parser._actions
        if action.dest != "help"
    }
    return defaults


def detect_encoding(path):
    from chardet.universaldetector import UniversalDetector
    from gzip import open as gzipopen

    if " " not in path:
        path = path.strip('"')
    if path.endswith(".gz"):
        f = gzipopen(path)
    else:
        f = open(path, "rb")
    detector = UniversalDetector()
    for _, line in enumerate(f):
        detector.feed(line)
        if detector.done:
            break
    detector.close()
    f.close()
    encoding = detector.result["encoding"]
    # utf-8 is superset of ascii that may include chars
    # not in the first 100 lines
    if encoding == "ascii":
        return "utf-8"
    else:
        return encoding


def get_job_version(dbpath, platform_name):
    from packaging.version import Version
    import sqlite3

    db = sqlite3.connect(dbpath)
    c = db.cursor()
    sql = f'select colval from info where colkey="{platform_name}"'
    c.execute(sql)
    r = c.fetchone()
    db_version = None
    if r is not None:
        db_version = Version(r[0])
    return db_version


def is_compatible_version(dbpath):
    from .admin_util import get_max_version_supported_for_migration
    from packaging.version import Version
    from pkg_resources import get_distribution

    max_version_supported_for_migration = get_max_version_supported_for_migration()
    try:
        ov_version = Version(get_distribution("oakvar").version)
    except:
        ov_version = None
    try:
        oc_version = Version(get_distribution("open-cravat").version)
    except:
        oc_version = None
    job_version_ov = get_job_version(dbpath, "oakvar")
    job_version_oc = get_job_version(dbpath, "open-cravat")
    if job_version_ov is None:
        if job_version_oc is None:
            compatible = False
        else:
            if job_version_oc < max_version_supported_for_migration:
                compatible = False
            else:
                compatible = True
        return compatible, job_version_oc, oc_version
    else:
        if job_version_ov < max_version_supported_for_migration:
            compatible = False
        else:
            compatible = True
        return compatible, job_version_ov, ov_version


def is_url(s) -> bool:
    if s.startswith("http://") or s.startswith("https://"):
        return True
    else:
        return False


def get_current_time_str():
    from datetime import datetime

    t = datetime.now()
    return t.strftime("%Y:%m:%d %H:%M:%S")


def get_args_conf(args: dict) -> Dict:
    from ..exceptions import ConfigurationError
    import json

    if args is None:
        return {}
    # fill with conf string
    confs = args.get("confs")
    if confs:
        try:
            confs_json = json.loads(confs.replace("'", '"'))
        except Exception:
            raise ConfigurationError()
        for k, v in confs_json.items():
            if k not in args or not args[k]:
                args[k] = v
    # fill with run_conf dict
    run_conf = args.get("run_conf")
    if run_conf and type(run_conf) is dict:
        for k, v in run_conf.items():
            if k not in args or not args[k]:
                args[k] = v
    # fill with conf
    conf_path = args.get("confpath")
    if conf_path:
        conf = load_yml_conf(conf_path).get("run", {})
        args["conf"] = conf
        if conf:
            for k, v in conf.items():
                if k not in args or not args[k]:
                    args[k] = v
    return args


def get_args_package(args: dict) -> Dict:
    if args is None:
        return {}
    package = args.get("package")
    if package:
        from ..module.local import get_local_module_info

        m_info = get_local_module_info(package)
        if m_info:
            package_conf = m_info.conf
            package_conf_run = package_conf.get("run")
            if package_conf_run:
                for k, v in package_conf_run.items():
                    if k not in args or not args[k]:
                        args[k] = v
    return args


def get_args(parser, inargs, inkwargs):
    from types import SimpleNamespace
    from argparse import Namespace

    # given args. Combines arguments in various formats.
    inarg_dict = {}
    if inargs is not None:
        for inarg in inargs:
            t = type(inarg)
            if t == list:  # ['-t', 'text']
                inarg_dict.update(**vars(parser.parse_args(inarg)))
            elif t == Namespace:  # already parsed by a parser.
                inarg_dict.update(**vars(inarg))
            elif t == SimpleNamespace:
                inarg_dict.update(**vars(inarg))
            elif t == dict:  # {'output_dir': '/rt'}
                inarg_dict.update(inarg)
    if inkwargs is not None:
        inarg_dict.update(inkwargs)
    # conf
    inarg_dict = get_args_conf(inarg_dict)
    # package
    inarg_dict = get_args_package(inarg_dict)
    # defaults
    default_args = get_argument_parser_defaults(parser)
    for k, v in default_args.items():
        if k not in inarg_dict or inarg_dict[k] is None:
            inarg_dict[k] = v
    # convert value to list if needed.
    for action in parser._actions:
        if action.dest == "help":
            continue
        if action.nargs in ["+", "*"]:
            key = action.dest
            value = inarg_dict[key]
            if value and type(value) is not list:
                inarg_dict[key] = [value]
    return inarg_dict


def filter_affected_cols(filter):
    cols = set()
    if "column" in filter:
        cols.add(filter["column"])
    else:
        for rule in filter["rules"]:
            cols.update(filter_affected_cols(rule))
    return cols


def humanize_bytes(num, binary=False):
    """Human friendly file size"""
    from math import floor, log

    exp2unit_dec = {0: "B", 1: "kB", 2: "MB", 3: "GB"}
    exp2unit_bin = {0: "B", 1: "KiB", 2: "MiB", 3: "GiB"}
    max_exponent = 3
    if binary:
        base = 1024
    else:
        base = 1000
    if num > 0:
        exponent = floor(log(num, base))
        if exponent > max_exponent:
            exponent = max_exponent
    else:
        exponent = 0
    quotient = float(num) / base**exponent
    if binary:
        unit = exp2unit_bin[exponent]
    else:
        unit = exp2unit_dec[exponent]
    quot_str = "{:.1f}".format(quotient)
    # No decimal for byte level sizes
    if exponent == 0:
        quot_str = quot_str.rstrip("0").rstrip(".")
    return "{quotient} {unit}".format(quotient=quot_str, unit=unit)


def write_log_msg(logger, e, quiet=True):
    if hasattr(e, "msg"):
        if type(e.msg) == list:
            for l in e.msg:
                logger.info(l)
                if not quiet:
                    print(l)
        else:
            logger.info(e)
            if not quiet:
                print(e)
    else:
        logger.info(e)
        if not quiet:
            print(e)


def get_simplenamespace(d):
    from types import SimpleNamespace

    if type(d) == dict:
        d = SimpleNamespace(**d)
    return d


def get_dict_from_namespace(n):
    from types import SimpleNamespace
    from argparse import Namespace

    if type(n) == SimpleNamespace or type(n) == Namespace:
        n = vars(n)
    return n


def quiet_print(msg, args=None, quiet=None):
    from .util import get_dict_from_namespace

    args = get_dict_from_namespace(args)
    if quiet is None:
        if args and args.get("quiet") is not None:
            quiet = args.get("quiet")
        else:
            quiet = True
    if quiet == False:
        if args:
            outfn = args.get("outfn", print)
        else:
            outfn = print
        outfn(msg, flush=True)


def email_is_valid(email: str) -> bool:
    from re import fullmatch

    if fullmatch(
        r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+", email
    ):
        return True
    else:
        return False


def pw_is_valid(pw: str) -> bool:
    from re import fullmatch

    if fullmatch(r"[a-zA-Z0-9!?@*&\-\+]+", pw):
        return True
    else:
        return False


def load_yml_conf(yml_conf_path):
    from oyaml import safe_load

    with open(yml_conf_path, encoding="utf-8") as f:
        conf = safe_load(f)
    if conf == None:
        conf = {}
    return conf


def compare_version(v1, v2):
    from packaging.version import Version
    sv1 = Version(v1)
    sv2 = Version(v2)
    if sv1 == sv2:
        return 0
    elif sv1 > sv2:
        return 1
    else:
        return -1


def show_logo():
    print(
        r"""
  ______             __        __     __                    
 /      \           /  |      /  |   /  |                   
/$$$$$$  |  ______  $$ |   __ $$ |   $$ | ______    ______  
$$ |  $$ | /      \ $$ |  /  |$$ |   $$ |/      \  /      \ 
$$ |  $$ | $$$$$$  |$$ |_/$$/ $$  \ /$$/ $$$$$$  |/$$$$$$  |
$$ |  $$ | /    $$ |$$   $$<   $$  /$$/  /    $$ |$$ |  $$/ 
$$ \__$$ |/$$$$$$$ |$$$$$$  \   $$ $$/  /$$$$$$$ |$$ |      
$$    $$/ $$    $$ |$$ | $$  |   $$$/   $$    $$ |$$ |      
 $$$$$$/   $$$$$$$/ $$/   $$/     $/     $$$$$$$/ $$/       
""",
        flush=True,
    )


def get_email_pw_from_input(email=None, pw=None, pwconfirm=False) -> Tuple[str, str]:
    from getpass import getpass

    email = email or ""
    pw = pw or ""
    done = False
    startover = False
    while not done:
        while not email or startover:
            startover = False
            if email:
                email = input(f"e-mail [{email}]: ") or email
            else:
                email = input(f"e-mail: ")
            if not email_is_valid(email):
                print(f"invalid e-mail")
                email = None
        while not pw and not startover:
            pw = getpass("Password (or just enter to start over): ")
            if pw == "":
                startover = True
                break
            if not pw_is_valid(pw):
                print(f"invalid password")
                pw = None
        if pwconfirm:
            pwagain = None
            while not pwagain and not startover:
                pwagain = getpass("Password again (or just enter to start over): ")
                if pwagain == "":
                    pw = ""
                    startover = True
                    break
                if not pw_is_valid(pwagain):
                    print(f"invalid password")
                    pwagain = None
                elif pw != pwagain:
                    print(f"password mismatch")
                    pwagain = None
                elif pw == pwagain:
                    done = True
                    break
        else:
            done = True
    return email, pw


def get_email_from_args(args={}) -> Optional[str]:
    return args.get("email")


def version_requirement_met(version, target_version) -> bool:
    from packaging.version import Version
    if not target_version:
        return True
    return Version(version) >= Version(target_version)

def get_latest_version(versions, target_version=None):
    from packaging.version import Version

    latest_version = ""
    for version in versions:
        if not version_requirement_met(version, target_version):
            continue
        if not latest_version or Version(version) > Version(latest_version):
            latest_version = version
    return latest_version


def update_status(status: str, status_writer=None, args=None, force=False):
    if args and not args.do_not_change_status and status_writer:
        status_writer.queue_status_update("status", status, force=force)


def announce_module(module, status_writer=None, args=None):
    if args and not args.quiet:
        quiet_print("\t{0:30s}\t".format(module.name), args=args)
    update_status(
        "Running {name}".format(name=module.name),
        status_writer=status_writer,
        args=args,
        force=True,
    )


def log_variant_exception(
    lnum=0,
    line="",
    __input_data__=None,
    unique_excs=[],
    logger=None,
    error_logger=None,
    e=None,
):
    import traceback

    if logger:
        err_str = traceback.format_exc().rstrip()
        if err_str.endswith("None"):
            err_str_log = str(e)
        else:
            err_str_log = err_str
        if not err_str_log in unique_excs:
            unique_excs.append(err_str_log)
            logger.error(err_str_log)
    if error_logger:
        error_logger.error("\n[{:d}]{}\n({})\n#".format(lnum, line.rstrip(), str(e)))

def wait_for_y():
    while True:
        resp = input("Proceed? ([y]/n) > ")
        if resp == "y" or resp == "":
            break
        if resp == "n":
            return True
        else:
            continue

def get_random_string(k=16):
    from random import choices
    from string import ascii_lowercase
    return "".join(choices(ascii_lowercase, k=k))

