from typing import Any
from typing import Union
from typing import List
from typing import Dict
from typing import Optional
from typing import Type
from pathlib import Path
import polars as pl
from ..base.converter import BaseConverter
from ..base.preparer import BasePreparer
from ..base.mapper import BaseMapper
from ..base.annotator import BaseAnnotator
from ..base.postaggregator import BasePostAggregator
from ..base.reporter import BaseReporter
from ..base.vcf2vcf import VCF2VCF
from ..base.commonmodule import BaseCommonModule

ov_system_output_columns: Optional[Dict[str, Dict[str, Any]]] = None


def get_ucsc_bins(start, stop=None):
    """get_ucsc_bins.

    Args:
        start:
        stop:
    """
    if stop is None:
        stop = start + 1

    def range_per_level(start, stop):
        """range_per_level.

        Args:
            start:
            stop:
        """
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


def load_class(
    path: Optional[Path], class_name=None
) -> Union[
    Type[BaseConverter],
    Type[BasePreparer],
    Type[BaseMapper],
    Type[BaseAnnotator],
    Type[BasePostAggregator],
    Type[BaseReporter],
    Type[VCF2VCF],
    Type[BaseCommonModule],
]:
    """load_class.

    Args:
        path:
        class_name:
    """
    from importlib.util import spec_from_file_location, module_from_spec
    from importlib import import_module
    from importlib import reload
    import sys
    import inspect
    import traceback
    from ..exceptions import ModuleLoadingError

    if not path:
        raise ValueError(f"{path} does not exist.")
    sys.path = [str(path.parent)] + sys.path
    module = None
    module_name = path.stem
    module_class: Optional[
        Union[
            Type[BaseConverter],
            Type[BasePreparer],
            Type[BaseMapper],
            Type[BaseAnnotator],
            Type[BasePostAggregator],
            Type[BaseReporter],
            Type[VCF2VCF],
            Type[BaseCommonModule],
        ]
    ] = None
    try:
        module = import_module(module_name)
        module = reload(module)
    except Exception:
        traceback.print_exc()
        try:
            if class_name:
                spec = spec_from_file_location(class_name, path)
                if spec is not None:
                    module = module_from_spec(spec)
                    loader = spec.loader
                    if loader is not None:
                        loader.exec_module(module)
        except Exception:
            traceback.print_exc()
            raise ModuleLoadingError(module_name=module_name)
    if module:
        if class_name:
            if hasattr(module, class_name):
                module_class = getattr(module, class_name)
                if not inspect.isclass(module_class):
                    raise ValueError(
                        f"{class_name} not found in {module.name} does not exist."
                    )
        else:
            for n in dir(module):
                if n in [
                    "Converter",
                    "MasterConverter",
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
                    "VCF2VCF",
                ]:
                    if hasattr(module, n):
                        module_class = getattr(module, n)
                        if not inspect.isclass(module_class):
                            raise ValueError(f"{module_class} is not a class.")
    if not module_class:
        raise ValueError(f"No OakVar class was found at {path}.")
    if (
        not issubclass(module_class, BaseConverter)
        and not issubclass(module_class, BasePreparer)
        and not issubclass(module_class, BaseMapper)
        and not issubclass(module_class, BaseAnnotator)
        and not issubclass(module_class, BasePostAggregator)
        and not issubclass(module_class, BaseReporter)
        and not issubclass(module_class, BaseReporter)
        and not issubclass(module_class, VCF2VCF)
        and not issubclass(module_class, BaseCommonModule)
    ):
        raise ValueError(f"{module_class} is not a proper OakVar class.")
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
    """get_argument_parser_defaults.

    Args:
        parser:
    """
    defaults = {
        action.dest: action.default
        for action in parser._actions
        if action.dest != "help"
    }
    return defaults


def detect_encoding(path):
    """detect_encoding.

    Args:
        path:
    """
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
        if detector.done or count == 10000:
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
    """get_job_version.

    Args:
        dbpath:
        platform_name:
    """
    from packaging.version import Version
    from .run import get_db_conn

    conn = get_db_conn(dbpath)
    cursor = conn.cursor()
    q = f"select colval from info where colkey='{platform_name}'"
    cursor.execute(q)
    r = cursor.fetchone()
    db_version = None
    if r is not None:
        db_version = Version(r[0])
    cursor.close()
    conn.close()
    return db_version


def is_compatible_version(dbpath):
    """is_compatible_version.

    Args:
        dbpath:
    """
    from .admin_util import get_max_version_supported_for_migration
    from packaging.version import Version
    from pkg_resources import get_distribution

    max_version_supported_for_migration = get_max_version_supported_for_migration()
    try:
        ov_version = Version(get_distribution("oakvar").version)
    except Exception:
        ov_version = None
    try:
        oc_version = Version(get_distribution("open-cravat").version)
    except Exception:
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


def is_url(s: Union[str, Path]) -> bool:
    """is_url.

    Args:
        s (str): s

    Returns:
        bool:
    """
    ss = str(s)
    if ss.startswith("http://") or ss.startswith("https://"):
        return True
    else:
        return False


def get_current_time_str():
    """get_current_time_str."""
    from datetime import datetime

    t = datetime.now()
    return t.strftime("%Y:%m:%d %H:%M:%S")


def get_args_conf(args: dict) -> Dict:
    """get_args_conf.

    Args:
        args (dict): args

    Returns:
        Dict:
    """
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
    """get_args_package.

    Args:
        args (dict): args

    Returns:
        Dict:
    """
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


def get_args(parser, inargs, inkwargs) -> dict:
    """get_args.

    Args:
        parser:
        inargs:
        inkwargs:

    Returns:
        dict:
    """
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
            if value and not isinstance(value, list) and not isinstance(value, dict):
                inarg_dict[key] = [value]
    return inarg_dict


def filter_affected_cols(filter):
    """filter_affected_cols.

    Args:
        filter:
    """
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


def email_is_valid(email: Optional[str]) -> bool:
    """email_is_valid.

    Args:
        email (Optional[str]): email

    Returns:
        bool:
    """
    from re import fullmatch

    if not email:
        return False
    if fullmatch(
        r"([A-Za-z0-9]+[.\-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+", email
    ):
        return True
    else:
        return False


def pw_is_valid(pw: Optional[str]) -> bool:
    """pw_is_valid.

    Args:
        pw (Optional[str]): pw

    Returns:
        bool:
    """
    from re import fullmatch

    if not pw:
        return False
    if fullmatch(r"[a-zA-Z0-9!?$@*&\-\+]+", pw):
        return True
    else:
        return False


def load_yml_conf(yml_conf_path: Path) -> Dict[str, Any]:
    """load_yml_conf.

    Args:
        yml_conf_path (Path): yml_conf_path
    """
    from oyaml import safe_load

    with open(yml_conf_path, encoding="utf-8") as f:
        conf: dict = safe_load(f)
    if conf is None:
        conf = {}
    return conf


def compare_version(v1: str, v2: str) -> int:
    """compare_version.

    Args:
        v1:
        v2:
    """
    from packaging.version import Version

    sv1 = Version(v1)
    sv2 = Version(v2)
    if sv1 == sv2:
        return 0
    elif sv1 > sv2:
        return 1
    else:
        return -1


def version_requirement_met(version, target_version) -> bool:
    """version_requirement_met.

    Args:
        version:
        target_version:

    Returns:
        bool:
    """
    from packaging.version import Version

    if not target_version:
        return True
    return Version(version) >= Version(target_version)


def get_latest_version(versions, target_version=None):
    """get_latest_version.

    Args:
        versions:
        target_version:
    """
    from packaging.version import Version

    latest_version = ""
    for version in versions:
        if not version_requirement_met(version, target_version):
            continue
        if not latest_version or Version(version) > Version(latest_version):
            latest_version = version
    return latest_version


def escape_glob_pattern(pattern):
    """escape_glob_pattern.

    Args:
        pattern:
    """
    new_pattern = "[[]".join(["[]]".join(v.split("]")) for v in pattern.split("[")])
    return new_pattern.replace("*", "[*]").replace("?", "[?]")


def get_random_string(k=16):
    """get_random_string.

    Args:
        k:
    """
    from random import choices
    from string import ascii_lowercase

    return "".join(choices(ascii_lowercase, k=k))


def get_result_dbpath(output_dir: str, run_name: str):
    """get_result_dbpath.

    Args:
        output_dir (str): output_dir
        run_name (str): run_name
    """
    from pathlib import Path
    from ..consts import RESULT_DB_SUFFIX_DUCKDB
    from ..consts import RESULT_DB_SUFFIX_SQLITE

    dbpath: Path = Path(output_dir) / (run_name + RESULT_DB_SUFFIX_DUCKDB)
    if dbpath.exists():
        return str(dbpath)
    dbpath: Path = Path(output_dir) / (run_name + RESULT_DB_SUFFIX_SQLITE)
    return str(dbpath)


def get_unique_path(path: str):
    """get_unique_path.

    Args:
        path (str): path
    """
    from pathlib import Path

    count = 1
    p = Path(path)
    stem = p.stem
    suffix = p.suffix
    while p.exists():
        p = Path(f"{stem}_{count}{suffix}")
    return str(p)


def print_list_of_dict(ld: List[Dict], outer=None):
    """print_list_of_dict.

    Args:
        ld (List[Dict]):
        outer:
    """
    from rich.console import Console
    from rich.table import Table
    from rich import box

    if not ld:
        return
    table = Table(show_header=True, title_style="bold", box=box.SQUARE)
    headers = list(ld[0].keys())
    for header in headers:
        table.add_column(header)
    for d in ld:
        row = []
        for header in headers:
            v = d[header]
            if type(v) == list:
                v = ", ".join(v)
            else:
                v = str(v)
            row.append(v)
        table.add_row(*row)
    console = Console(file=outer)
    console.print(table)


def log_module(module, logger):
    """log_module.

    Args:
        module:
        logger:
    """
    if logger:
        code_version = None
        if hasattr(module, "conf"):
            code_version = module.conf.get("code_version") or module.conf.get("version")
        if not code_version and hasattr(module, "version"):
            code_version = module.version
        if not code_version:
            code_version = "?"
        logger.info(f"module: {module.name}=={code_version} {module.script_path}")


def get_ov_system_output_columns() -> Dict[str, Dict[str, Any]]:
    """get_ov_system_output_columns.

    Args:

    Returns:
        Dict[str, List[Dict[str, Any]]]:
    """
    from pathlib import Path
    from oyaml import safe_load
    from copy import deepcopy

    global ov_system_output_columns
    if ov_system_output_columns:
        return deepcopy(ov_system_output_columns)
    fp = Path(__file__).parent.parent / "assets" / "output_columns.yml"
    with open(fp) as f:
        ov_system_output_columns = safe_load(f)
    if not ov_system_output_columns:
        return {}
    return deepcopy(ov_system_output_columns)


def get_result_db_conn(db_path: str):
    """get_result_db_conn.

    Args:
        db_path (str): db_path
    """
    import sqlite3
    from pathlib import Path

    p = Path(db_path)
    if not p.exists():
        return None
    conn = sqlite3.connect(p)
    return conn


def get_df_from_db(
    db_path: str,
    table_name: str = "variant",
    sql: Optional[str] = None,
    num_cores: int = 1,
    conn=None,
) -> Optional[pl.DataFrame]:
    """Gets a Polars DataFrame of a table in an OakVar result database.

    Args:
        db_path (str): Path to the OakVar result database file
                       from which a Polars DataFrame will be extracted.
        table_name (str): Table name to dump to the DataFrame
        sql (Optional[str]): Custom SQL to apply before dumping to the DataFrame.
            For example,
            `"select base__uid, base__chrom, base__pos from variant where
            clinvar__sig='Pathogenic'"`.
        num_cores (int): Number of CPU cores to use

    Returns:
        DataFrame of the given or default table of the OakVar result database
    """
    import sys
    from pathlib import Path
    from os import environ
    from urllib.parse import quote
    import platform

    environ["RUST_LOG"] = "connectorx=warn,connectorx_python=warn"
    partition_ons = {
        "variant": "base__uid",
        "gene": "base__hugo",
        "sample": "base__uid",
        "mapping": "base__uid",
    }
    df = None
    db_path_to_use = str(Path(db_path).resolve())
    partition_on = partition_ons.get(table_name)
    if conn is not None:
        db_conn = conn
    else:
        db_conn = get_result_db_conn(db_path_to_use)
        if not db_conn:
            return None
    if partition_on and table_name:
        c = db_conn.cursor()
        c.execute(f"select {partition_on} from {table_name} limit 1")
        ret = c.fetchone()
        if not ret:
            sys.stderr.write(f"{partition_on} does not exist in {table_name}")
            c.close()
            if conn is None:
                db_conn.close()
            return None
        else:
            c.close()
            if conn is None:
                db_conn.close()
    if not sql:
        sql = f"select * from {table_name}"
    ol_pl = platform.platform()
    if ol_pl.startswith("Windows"):
        conn_url = f"sqlite://{quote(db_path_to_use)}"
    else:
        conn_url = f"sqlite://{db_path_to_use}"
    if partition_on and num_cores > 1:
        df = pl.read_database(
            sql, conn_url, partition_on=partition_on, partition_num=num_cores
        )
    else:
        df = pl.read_database(sql, conn_url)
    return df
