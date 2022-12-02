from typing import Dict
from typing import Tuple
from typing import Optional

ov_system_output_columns: Optional[dict] = None

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
    count = 0
    encoding = None
    for line in f:
        detector.feed(line)
        count += 1
        if detector.done or count == 100000:
            encoding = detector.result["encoding"]
            break
    detector.close()
    f.close()
    if not encoding:
        encoding = "utf-8"
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
    if args is None:
        return {}
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
    print("")
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


def escape_glob_pattern(pattern):
    new_pattern = "[[]".join(["[]]".join(v.split("]")) for v in pattern.split("[")])
    return new_pattern.replace("*", "[*]").replace("?", "[?]")


def get_random_string(k=16):
    from random import choices
    from string import ascii_lowercase

    return "".join(choices(ascii_lowercase, k=k))


def get_result_dbpath(output_dir: str, run_name: str):
    from pathlib import Path
    from ..consts import result_db_suffix

    return str(Path(output_dir) / (run_name + result_db_suffix))

def get_unique_path(path: str):
    from pathlib import Path

    count = 1
    p = Path(path)
    stem = p.stem
    suffix = p.suffix
    while p.exists():
        p = Path(f"{stem}_{count}{suffix}")
    return str(p)


def yield_tabular_lines(l, col_spacing=2, indent=0):
    if not l:
        return
    sl = []
    n_toks = len(l[0])
    max_lens = [0] * n_toks
    for toks in l:
        if len(toks) != n_toks:
            raise RuntimeError("Inconsistent sub-list length")
        stoks = [str(x) for x in toks]
        sl.append(stoks)
        stoks_len = [len(x) for x in stoks]
        max_lens = [max(x) for x in zip(stoks_len, max_lens)]
    for stoks in sl:
        jline = " " * indent
        for i, stok in enumerate(stoks):
            jline += stok + " " * (max_lens[i] + col_spacing - len(stok))
        yield jline


def print_tabular_lines(l, args=None):
    for line in yield_tabular_lines(l):
        if args:
            quiet_print(line, args=args)
        else:
            print(line)

def log_module(module, logger):
    if logger:
        code_version = None
        if hasattr(module, "conf"):
            code_version = module.conf.get("code_version") or module.conf.get("version")
        if not code_version and hasattr(module, "version"):
            code_version = module.version
        if not code_version:
            code_version = "?"
        logger.info(f"module: {module.name}=={code_version} {module.script_path}")

def get_ov_system_output_columns() -> dict:
    from pathlib import Path
    from oyaml import safe_load

    global ov_system_output_columns
    if ov_system_output_columns:
        return ov_system_output_columns
    fp = Path(__file__).parent.parent / "assets" / "output_columns.yml"
    with open(fp) as f:
        ov_system_output_columns = safe_load(f)
    if not ov_system_output_columns:
        return {}
    return ov_system_output_columns

def get_crv_def() -> list:
    from ..consts import INPUT_LEVEL_KEY

    output_columns: dict = get_ov_system_output_columns()
    return output_columns[INPUT_LEVEL_KEY]

def get_crx_def() -> list:
    from ..consts import VARIANT_LEVEL_KEY

    output_columns: dict = get_ov_system_output_columns()
    return output_columns[VARIANT_LEVEL_KEY]

def get_crg_def() -> list:
    from ..consts import GENE_LEVEL_KEY

    output_columns: dict = get_ov_system_output_columns()
    return output_columns[GENE_LEVEL_KEY]

def get_crs_def() -> list:
    from ..consts import SAMPLE_LEVEL_KEY

    output_columns: dict = get_ov_system_output_columns()
    return output_columns[SAMPLE_LEVEL_KEY]

def get_crm_def() -> list:
    from ..consts import MAPPING_LEVEL_KEY

    output_columns: dict = get_ov_system_output_columns()
    return output_columns[MAPPING_LEVEL_KEY]

def get_crl_def() -> list:
    from ..consts import LIFTOVER_LEVEL_KEY

    output_columns: dict = get_ov_system_output_columns()
    return output_columns[LIFTOVER_LEVEL_KEY]

