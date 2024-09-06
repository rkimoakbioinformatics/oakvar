# OakVar
#
# Copyright (c) 2024 Oak Bioinformatics, LLC
#
# All rights reserved.
#
# Do not distribute or use this software without obtaining
# a license from Oak Bioinformatics, LLC.
#
# Do not use this software to develop another software
# which competes with the products by Oak Bioinformatics, LLC,
# without obtaining a license for such use from Oak Bioinformatics, LLC.
#
# For personal use of non-commercial nature, you may use this software
# after registering with `ov store account create`.
#
# For research use of non-commercial nature, you may use this software
# after registering with `ov store account create`.
#
# For use by commercial entities, you must obtain a commercial license
# from Oak Bioinformatics, LLC. Please write to info@oakbioinformatics.com
# to obtain the commercial license.
# ================
# OpenCRAVAT
#
# MIT License
#
# Copyright (c) 2021 KarchinLab
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from typing import Optional
from typing import Tuple
from typing import Dict
from liftover.chain_file import ChainFile
from liftover.download_file import download_file

complementary_base = {
    "A": "T",
    "T": "A",
    "C": "G",
    "G": "C",
    "-": "-",
    "": "",
    "N": "N",
}

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
    "UGU": "C",
    "UGC": "C",
    "GAU": "D",
    "UUU": "F",
    "UUC": "F",
    "GGU": "G",
    "CAU": "H",
    "AUU": "I",
    "AUC": "I",
    "AUA": "I",
    "UUA": "L",
    "UUG": "L",
    "CUU": "L",
    "CUC": "L",
    "CUA": "L",
    "CUG": "L",
    "AAU": "N",
    "CCU": "P",
    "UCU": "S",
    "UCC": "S",
    "UCA": "S",
    "UCG": "S",
    "AGU": "S",
    "ACU": "T",
    "CGU": "R",
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

hg19_chrom_aliases: Dict[str, str] = {}
hg38_chrom_aliases: Dict[str, str] = {}


def load_chrom_aliases(genome: str):
    from pathlib import Path

    global hg19_chrom_aliases
    global hg38_chrom_aliases
    if genome == "hg38":
        fpath = Path(__file__).parent.parent / "assets" / "hg38.chromAlias.txt"
        d = hg38_chrom_aliases
    elif genome == "hg19":
        fpath = Path(__file__).parent.parent / "assets" / "hg19.chromAlias.txt"
        d = hg19_chrom_aliases
    else:
        return
    with open(fpath) as f:
        for line in f:
            if line[0] == "#":
                continue
            words = line.split("\t")
            for alias in words[1:]:
                d[alias] = words[0]


def get_grch37_to_hg19(chrom: str) -> str:
    global hg19_chrom_aliases
    if not hg19_chrom_aliases:
        load_chrom_aliases("hg19")
    return hg19_chrom_aliases[chrom] or ""


def get_grch38_to_hg38(chrom: str) -> str:
    global hg38_chrom_aliases
    if not hg38_chrom_aliases:
        load_chrom_aliases("hg38")
    return hg38_chrom_aliases.get(chrom, "")


def trim_input_left_adjust(ref, alt, pos, strand):
    """trim_input_left_adjust.

    Args:
        ref:
        alt:
        pos:
        strand:
    """
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


def normalize_variant_left(strand, pos, ref, alt):
    """normalize_variant_left.

    Args:
        strand:
        pos:
        ref:
        alt:
    """
    reflen = len(ref)
    altlen = len(alt)
    # Returns without change if same single nucleotide for ref and alt.
    if reflen == 1 and altlen == 1 and ref == alt:
        return pos, ref, alt
    # Trimming from the start and then the end of the sequence
    # where the sequences overlap with the same nucleotides
    new_ref2, new_alt2, new_pos = trim_input_left_adjust(ref, alt, pos, strand)
    if new_ref2 == "" or new_ref2 == ".":
        new_ref2 = "-"
    if new_alt2 == "" or new_alt2 == ".":
        new_alt2 = "-"
    return new_pos, new_ref2, new_alt2


def normalize_variant_dict_left(wdict):
    """normalize_variant_dict_left.

    Args:
        wdict:
    """
    from ..exceptions import NoVariantError

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
    ) = normalize_variant_left("+", p, r, a)
    wdict["pos"] = new_pos
    wdict["ref_base"] = new_ref
    wdict["alt_base"] = new_alt
    if wdict["ref_base"] == wdict["alt_base"]:
        raise NoVariantError()
    return wdict


def reverse_complement(bases):
    """reverse_complement.

    Args:
        bases:
    """
    return "".join([complementary_base[base] for base in bases[::-1]])


def get_lifter(source_assembly: str, to_assembly: str = "") -> Optional[ChainFile]:
    """get_lifter.

    Args:
        source_assembly (str): source_assembly

    Returns:
        Optional[liftover.ChainFile]:
    """
    from os import makedirs
    from pathlib import Path
    from ..system import get_liftover_dir
    from ..consts import SYSTEM_GENOME_ASSEMBLY

    liftover_dir = get_liftover_dir()
    if not liftover_dir:
        return None
    if not liftover_dir.exists():
        makedirs(liftover_dir, exist_ok=True)
    if not to_assembly:
        to_assembly = SYSTEM_GENOME_ASSEMBLY
    chain_file_basename = (
        f"{source_assembly.lower()}To{to_assembly.capitalize()}.over.chain.gz"
    )
    chain_file_path: Path = liftover_dir / chain_file_basename
    if not chain_file_path.exists():
        url = f"https://hgdownload.cse.ucsc.edu/goldenPath/{source_assembly.lower()}/liftOver/{chain_file_basename}"
        download_file(url, chain_file_path)
    lifter = ChainFile(str(chain_file_path), source_assembly, to_assembly)
    return lifter


def liftover_one_pos(
    chrom: str,
    pos: int,
    lifter=None,
    source_assembly: Optional[str] = None,
) -> Optional[Tuple[str, int]]:
    """liftover_one_pos.

    Args:
        chrom (str): Chromosome
        pos (int): Position
        lifter: liftover.ChainFile instance. Use `oakvar.get_lifter` to get one.
        source_assembly (Optional[str]): Genome assembly of input.
            If `lifter` is given, this parameter will be ignored.

    Returns:
        (chromosome, position) if liftover was successful. `None` if not.
    """
    from ..exceptions import LiftoverFailure

    if not lifter:
        if not source_assembly:
            raise ValueError("Either lifter or source_assembly should be given")
        lifter = get_lifter(source_assembly)
    if not lifter:
        raise ValueError(f"LiftOver not found for {source_assembly}")
    hits = None
    try:
        hits = lifter.convert_coordinate(chrom, pos - 1)
    except KeyError:
        raise LiftoverFailure(msg=f"{chrom} not found in {source_assembly}")
    except Exception:
        raise
    converted = None
    if hits:
        converted = (hits[0][0], hits[0][1] + 1)
    else:
        hits_prev = lifter.convert_coordinate(chrom, pos - 2)
        hits_next = lifter.convert_coordinate(chrom, pos)
        if hits_prev and hits_next:
            hit_prev_1 = hits_prev[0]
            hit_next_1 = hits_next[0]
            pos_prev = hit_prev_1[1]
            pos_next = hit_next_1[1]
            if pos_prev == pos_next - 2:
                converted = (hit_prev_1[0], pos_prev + 1 + 1)
            elif pos_prev == pos_next + 2:
                converted = (hit_prev_1[0], pos_prev - 1 + 1)
    return converted


def liftover(
    chrom: str,
    pos: int,
    ref: Optional[str] = None,
    alt: Optional[str] = None,
    get_ref: bool = False,
    lifter=None,
    source_assembly: Optional[str] = None,
    wgs_reader=None,
):
    """liftover.

    Args:
        chrom (str): chrom
        pos (int): pos
        ref (Optional[str]): ref
        alt (Optional[str]): alt
        get_ref (bool): get_ref
        lifter:
        source_assembly (Optional[str]): source_assembly
        wgs_reader:
    """
    from oakvar.lib.exceptions import LiftoverFailure
    from oakvar.lib.util.seq import reverse_complement
    from oakvar.lib.consts import SYSTEM_GENOME_ASSEMBLY

    liftover_failure_msg: str = f"There is no conversion to {SYSTEM_GENOME_ASSEMBLY}."
    if not lifter:
        if not source_assembly:
            raise ValueError("Either lifter or source_assembly should be given")
        lifter = get_lifter(source_assembly)
    if not lifter:
        raise ValueError(f"LiftOver not found for {source_assembly}")
    if ref is None:
        converted = liftover_one_pos(chrom, pos, lifter=lifter)
        if converted is None:
            raise LiftoverFailure(liftover_failure_msg)
        newchrom = converted[0]
        newpos = converted[1]
        if get_ref:
            if not wgs_reader:
                wgs_reader = get_wgs_reader()
                if not wgs_reader:
                    raise LiftoverFailure(
                        "No wgs_reader was given. Use oakvar.get_wgs_reader to get one."
                    )
            ref = wgs_reader.get_bases(newchrom, newpos).upper()
        return [newchrom, newpos, ref, alt]
    reflen = len(ref)
    altlen = len(alt) if alt else 1
    if reflen == 1 and altlen == 1:
        converted = liftover_one_pos(chrom, pos, lifter=lifter)
        if converted is None:
            raise LiftoverFailure(liftover_failure_msg)
        newchrom = converted[0]
        newpos = converted[1]
    elif reflen >= 1 and altlen == 0:  # del
        pos1 = pos
        pos2 = pos + reflen - 1
        converted1 = liftover_one_pos(chrom, pos1, lifter=lifter)
        converted2 = liftover_one_pos(chrom, pos2, lifter=lifter)
        if converted1 is None or converted2 is None:
            raise LiftoverFailure(liftover_failure_msg)
        newchrom = converted1[0]
        newpos1 = converted1[1]
        newpos2 = converted2[1]
        newpos = min(newpos1, newpos2)
    elif reflen == 0 and altlen >= 1:  # ins
        converted = liftover_one_pos(chrom, pos, lifter=lifter)
        if converted is None:
            raise LiftoverFailure(liftover_failure_msg)
        newchrom = converted[0]
        newpos = converted[1]
    else:
        pos1 = pos
        pos2 = pos + reflen - 1
        converted1 = liftover_one_pos(chrom, pos1, lifter=lifter)
        converted2 = liftover_one_pos(chrom, pos2, lifter=lifter)
        if converted1 is None or converted2 is None:
            raise LiftoverFailure(liftover_failure_msg)
        newchrom1 = converted1[0]
        newpos1 = converted1[1]
        newpos2 = converted2[1]
        newchrom = newchrom1
        newpos = min(newpos1, newpos2)
    if not wgs_reader:
        wgs_reader = get_wgs_reader()
        if not wgs_reader:
            raise LiftoverFailure(
                "No wgs_reader was given. Use oakvar.get_wgs_reader to get one."
            )
    hg38_ref = wgs_reader.get_bases(newchrom, newpos)
    if hg38_ref == reverse_complement(ref):  # strand reversal
        newref = hg38_ref
        newalt = reverse_complement(alt)
    else:  # same strand
        newref = ref
        newalt = alt
    return [newchrom, newpos, newref, newalt]


def get_wgs_reader(assembly="hg38"):
    """get_wgs_reader.

    Args:
        assembly:
    """
    from ... import get_module

    ModuleClass = get_module(assembly + "wgs")
    if ModuleClass is None:
        wgs = None
    else:
        wgs = ModuleClass()
        wgs.setup()
    return wgs
