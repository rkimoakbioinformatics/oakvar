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


complementary_base = {
    "A": "T",
    "T": "A",
    "C": "G",
    "G": "C",
    "-": "-",
    "": "",
    "N": "N",
}


def reverse_complement(bases):
    return "".join([complementary_base[base] for base in bases[::-1]])


def switch_strand(bases, start_strand=None, dest_strand=None, pos=0):
    rev_comp = reverse_complement(bases)
    if start_strand == "-" or dest_strand == "+":
        new_pos = pos + len(bases.replace("-", "")) - 1
    elif start_strand == "+" or dest_strand == "-":
        new_pos = pos - len(bases.replace("-", "")) + 1
    else:
        err_msg = "start_strand or dest_strand must be specified as + or -"
        raise ValueError(err_msg)
    return rev_comp, new_pos


aa_123 = {
    "A": "Ala",
    "C": "Cys",
    "E": "Glu",
    "D": "Asp",
    "G": "Gly",
    "F": "Phe",
    "I": "Ile",
    "H": "His",
    "K": "Lys",
    "M": "Met",
    "L": "Leu",
    "N": "Asn",
    "Q": "Gln",
    "P": "Pro",
    "S": "Ser",
    "R": "Arg",
    "T": "Thr",
    "W": "Trp",
    "V": "Val",
    "Y": "Tyr",
    "*": "Ter",
    "": "",
}


def aa_let_to_abbv(lets):
    return "".join([aa_123[x] for x in lets])


aa_321 = {
    "Asp": "D",
    "Ser": "S",
    "Gln": "Q",
    "Lys": "K",
    "Trp": "W",
    "Asn": "N",
    "Pro": "P",
    "Thr": "T",
    "Phe": "F",
    "Ala": "A",
    "Gly": "G",
    "Cys": "C",
    "Ile": "I",
    "Leu": "L",
    "His": "H",
    "Arg": "R",
    "Met": "M",
    "Val": "V",
    "Glu": "E",
    "Tyr": "Y",
    "Ter": "*",
    "": "",
}


def aa_abbv_to_let(abbvs):
    if type(abbvs) != str:
        raise TypeError("Expected str not %s" % type(abbvs).__name__)
    if len(abbvs) % 3 != 0:
        raise ValueError("Must be evenly divisible by 3")
    out = ""
    for i in range(0, len(abbvs), 3):
        abbv = abbvs[i].upper() + abbvs[i + 1 : i + 3].lower()
        out += aa_321[abbv]
    return out


codon_table = {
    "ATG": "M",
    "GCT": "A",
    "GCC": "A",
    "GCA": "A",
    "GCG": "A",
    "TGT": "C",
    "TGC": "C",
    "GAT": "D",
    "GAC": "D",
    "GAA": "E",
    "GAG": "E",
    "TTT": "F",
    "TTC": "F",
    "GGT": "G",
    "GGC": "G",
    "GGA": "G",
    "GGG": "G",
    "CAT": "H",
    "CAC": "H",
    "ATT": "I",
    "ATC": "I",
    "ATA": "I",
    "AAA": "K",
    "AAG": "K",
    "TTA": "L",
    "TTG": "L",
    "CTT": "L",
    "CTC": "L",
    "CTA": "L",
    "CTG": "L",
    "AAT": "N",
    "AAC": "N",
    "CCT": "P",
    "CCC": "P",
    "CCA": "P",
    "CCG": "P",
    "CAA": "Q",
    "CAG": "Q",
    "TCT": "S",
    "TCC": "S",
    "TCA": "S",
    "TCG": "S",
    "AGT": "S",
    "AGC": "S",
    "ACT": "T",
    "ACC": "T",
    "ACA": "T",
    "ACG": "T",
    "CGT": "R",
    "CGC": "R",
    "CGA": "R",
    "CGG": "R",
    "AGA": "R",
    "AGG": "R",
    "GTT": "V",
    "GTC": "V",
    "GTA": "V",
    "GTG": "V",
    "TGG": "W",
    "TAT": "Y",
    "TAC": "Y",
    "TGA": "*",
    "TAA": "*",
    "TAG": "*",
    "AUG": "M",
    "GCU": "A",
    "GCC": "A",
    "GCA": "A",
    "GCG": "A",
    "UGU": "C",
    "UGC": "C",
    "GAU": "D",
    "GAC": "D",
    "GAA": "E",
    "GAG": "E",
    "UUU": "F",
    "UUC": "F",
    "GGU": "G",
    "GGC": "G",
    "GGA": "G",
    "GGG": "G",
    "CAU": "H",
    "CAC": "H",
    "AUU": "I",
    "AUC": "I",
    "AUA": "I",
    "AAA": "K",
    "AAG": "K",
    "UUA": "L",
    "UUG": "L",
    "CUU": "L",
    "CUC": "L",
    "CUA": "L",
    "CUG": "L",
    "AAU": "N",
    "AAC": "N",
    "CCU": "P",
    "CCC": "P",
    "CCA": "P",
    "CCG": "P",
    "CAA": "Q",
    "CAG": "Q",
    "UCU": "S",
    "UCC": "S",
    "UCA": "S",
    "UCG": "S",
    "AGU": "S",
    "AGC": "S",
    "ACU": "T",
    "ACC": "T",
    "ACA": "T",
    "ACG": "T",
    "CGU": "R",
    "CGC": "R",
    "CGA": "R",
    "CGG": "R",
    "AGA": "R",
    "AGG": "R",
    "GUU": "V",
    "GUC": "V",
    "GUA": "V",
    "GUG": "V",
    "UGG": "W",
    "UAU": "Y",
    "UAC": "Y",
    "UGA": "*",
    "UAA": "*",
    "UAG": "*",
}


def translate_codon(bases, fallback=None):
    if len(bases) != 3:
        if fallback is None:
            return KeyError(bases)
        else:
            return fallback
    else:
        return codon_table[bases]


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

    path_dir = dirname(path)
    sys.path = [path_dir] + sys.path
    module = None
    module_class = None
    module_name = basename(path).split(".")[0]
    try:
        module = import_module(module_name)
    except Exception as _:
        from traceback import print_exc

        print_exc()
        try:
            if class_name:
                spec = spec_from_file_location(class_name, path)
                if spec is not None:
                    module = module_from_spec(spec)
                    loader = spec.loader
                    if loader is not None:
                        loader.exec_module(module)
        except Exception as _:
            print_exc()
            raise
    if module:
        if class_name:
            module_class = getattr(module, class_name)
        else:
            for n in dir(module):
                if n.startswith("Cravat") or n == "Mapper" or n == "Reporter":
                    c = getattr(module, n)
                    if inspect.isclass(c):
                        module_class = c
                        break
    del sys.path[0]
    return module_class


def get_directory_size(start_path):
    """
    Recursively get directory filesize.
    """
    from os import walk
    from os.path import join, getsize

    total_size = 0
    for dirpath, _, filenames in walk(start_path):
        for fname in filenames:
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
    for n, line in enumerate(f):
        if n > 100:
            break
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
    from distutils.version import LooseVersion
    import sqlite3

    db = sqlite3.connect(dbpath)
    c = db.cursor()
    sql = f'select colval from info where colkey="{platform_name}"'
    c.execute(sql)
    r = c.fetchone()
    db_version = None
    if r is not None:
        db_version = LooseVersion(r[0])
    return db_version


def is_compatible_version(dbpath):
    from .admin_util import get_max_version_supported_for_migration
    from distutils.version import LooseVersion
    from pkg_resources import get_distribution

    max_version_supported_for_migration = get_max_version_supported_for_migration()
    try:
        ov_version = LooseVersion(get_distribution("oakvar").version)
    except:
        ov_version = None
    try:
        oc_version = LooseVersion(get_distribution("open-cravat").version)
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


def is_url(s):
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
    import json

    # fill with conf string
    confs = args.get("confs")
    if confs:
        try:
            confs_json = json.loads(confs.replace("'", '"'))
        except Exception:
            from ..exceptions import ConfigurationError

            raise ConfigurationError()
        for k, v in confs_json.items():
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
        print(msg, flush=True)


def trim_input(ref, alt, pos, strand):
    pos = int(pos)
    reflen = len(ref)
    altlen = len(alt)
    minlen = min(reflen, altlen)
    new_ref = ref
    new_alt = alt
    new_pos = pos
    for nt_pos in range(0, minlen):
        if ref[reflen - nt_pos - 1] == alt[altlen - nt_pos - 1]:
            new_ref = ref[: reflen - nt_pos - 1]
            new_alt = alt[: altlen - nt_pos - 1]
        else:
            break
    new_ref_len = len(new_ref)
    new_alt_len = len(new_alt)
    minlen = min(new_ref_len, new_alt_len)
    new_ref2 = new_ref
    new_alt2 = new_alt
    for nt_pos in range(0, minlen):
        if new_ref[nt_pos] == new_alt[nt_pos]:
            if strand == "+":
                new_pos += 1
            elif strand == "-":
                new_pos -= 1
            new_ref2 = new_ref[nt_pos + 1 :]
            new_alt2 = new_alt[nt_pos + 1 :]
        else:
            new_ref2 = new_ref[nt_pos:]
            new_alt2 = new_alt[nt_pos:]
            break
    return new_ref2, new_alt2, new_pos


def standardize_pos_ref_alt(strand, pos, ref, alt):
    reflen = len(ref)
    altlen = len(alt)
    # Returns without change if same single nucleotide for ref and alt.
    if reflen == 1 and altlen == 1 and ref == alt:
        return pos, ref, alt
    # Trimming from the start and then the end of the sequence
    # where the sequences overlap with the same nucleotides
    new_ref2, new_alt2, new_pos = trim_input(ref, alt, pos, strand)
    if new_ref2 == "" or new_ref2 == ".":
        new_ref2 = "-"
    if new_alt2 == "" or new_alt2 == ".":
        new_alt2 = "-"
    return new_pos, new_ref2, new_alt2


def normalize_variant(wdict):
    chrom = wdict["chrom"]
    if not chrom.startswith("chr"):
        wdict["chrom"] = "chr" + chrom
    p, r, a = (
        int(wdict["pos"]),
        wdict["ref_base"],
        wdict["alt_base"],
    )
    (
        new_pos,
        new_ref,
        new_alt,
    ) = standardize_pos_ref_alt("+", p, r, a)
    wdict["pos"] = new_pos
    wdict["ref_base"] = new_ref
    wdict["alt_base"] = new_alt
    if wdict["ref_base"] == wdict["alt_base"]:
        from ..exceptions import NoVariantError

        raise NoVariantError()
    return wdict


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
    """
    Load a .yml file into a dictionary. Return an empty dictionary if file is
    empty.
    """
    from oyaml import safe_load

    with open(yml_conf_path, encoding="utf-8") as f:
        conf = safe_load(f)
    if conf == None:
        conf = {}
    return conf


def compare_version(v1, v2):
    from distutils.version import LooseVersion

    sv1 = LooseVersion(v1)
    sv2 = LooseVersion(v2)
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


def get_email_pw_from_input(pwconfirm=False) -> Tuple[str, str]:
    from getpass import getpass

    email = ""
    pw = ""
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


def get_latest_version(versions: list):
    from distutils.version import LooseVersion

    latest_version = ""
    for version in versions:
        if not latest_version:
            latest_version = version
            continue
        if LooseVersion(version) > LooseVersion(latest_version):
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
            logger.error(err_str_log)
        else:
            lines = err_str.split("\n")
            last_line = lines[-1]
            err_str_log = (
                "\n".join(lines[:-1]) + "\n" + ":".join(last_line.split(":")[:2])
            )
            logger.error(err_str_log)
        if err_str_log not in unique_excs:
            unique_excs.append(err_str_log)
    if error_logger:
        error_logger.error("\n[{:d}]{}\n({})\n#".format(lnum, line.rstrip(), str(e)))
