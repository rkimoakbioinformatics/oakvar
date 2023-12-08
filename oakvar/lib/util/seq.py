# OakVar Dual License
# 
# Copyright (c) 2023 Oak Bioinformatics, LLC
# 
# This program is dual licensed under the Affero GPL-3.0 or later for 
# non-commercial and open source use, and under a commercial license, 
# which is available for purchase, for closed-source or commercial use.
# 
# For the commercial use, please contact Oak Bioinformatics, LLC 
# for obtaining such a license. OakVar commercial license does not impose 
# the Affero GPL open-source licensing terms, conditions, and limitations. 
# To obtain a commercial-use license of OakVar, please visit our website at
# https://oakbioinformatics.com or contact us at info@oakbioinformatics.com 
# for more information.
# 
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

grch37_to_hg19 = {
    "GL000202.1": "chr11_gl000202_random",
    "GL000244.1": "chrUn_gl000244",
    "GL000235.1": "chrUn_gl000235",
    "GL000238.1": "chrUn_gl000238",
    "GL000226.1": "chrUn_gl000226",
    "GL000218.1": "chrUn_gl000218",
    "GL000249.1": "chrUn_gl000249",
    "GL000242.1": "chrUn_gl000242",
    "GL000221.1": "chrUn_gl000221",
    "GL000192.1": "chr1_gl000192_random",
    "GL000223.1": "chrUn_gl000223",
    "GL000232.1": "chrUn_gl000232",
    "GL000206.1": "chr17_gl000206_random",
    "GL000240.1": "chrUn_gl000240",
    "GL000214.1": "chrUn_gl000214",
    "GL000212.1": "chrUn_gl000212",
    "GL000199.1": "chr9_gl000199_random",
    "GL000248.1": "chrUn_gl000248",
    "GL000195.1": "chr7_gl000195_random",
    "GL000215.1": "chrUn_gl000215",
    "GL000225.1": "chrUn_gl000225",
    "GL000216.1": "chrUn_gl000216",
    "GL000194.1": "chr4_gl000194_random",
    "GL000217.1": "chrUn_gl000217",
    "GL000197.1": "chr8_gl000197_random",
    "GL000222.1": "chrUn_gl000222",
    "GL000200.1": "chr9_gl000200_random",
    "GL000211.1": "chrUn_gl000211",
    "GL000247.1": "chrUn_gl000247",
    "GL000233.1": "chrUn_gl000233",
    "GL000210.1": "chr21_gl000210_random",
    "GL000198.1": "chr9_gl000198_random",
    "GL000245.1": "chrUn_gl000245",
    "GL000234.1": "chrUn_gl000234",
    "GL000203.1": "chr17_gl000203_random",
    "GL000239.1": "chrUn_gl000239",
    "GL000213.1": "chrUn_gl000213",
    "GL000227.1": "chrUn_gl000227",
    "GL000208.1": "chr19_gl000208_random",
    "GL000230.1": "chrUn_gl000230",
    "GL000231.1": "chrUn_gl000231",
    "GL000228.1": "chrUn_gl000228",
    "GL000243.1": "chrUn_gl000243",
    "GL000229.1": "chrUn_gl000229",
    "GL000205.1": "chr17_gl000205_random",
    "GL000224.1": "chrUn_gl000224",
    "GL000191.1": "chr1_gl000191_random",
    "GL000196.1": "chr8_gl000196_random",
    "GL000193.1": "chr4_gl000193_random",
    "GL000201.1": "chr9_gl000201_random",
    "GL000237.1": "chrUn_gl000237",
    "GL000246.1": "chrUn_gl000246",
    "GL000241.1": "chrUn_gl000241",
    "GL000204.1": "chr17_gl000204_random",
    "GL000207.1": "chr18_gl000207_random",
    "GL000209.1": "chr19_gl000209_random",
    "GL000219.1": "chrUn_gl000219",
    "GL000220.1": "chrUn_gl000220",
    "GL000236.1": "chrUn_gl000236",
    "GL000255.1": "chr6_qbl_hap6",
    "GL000251.1": "chr6_cox_hap2",
    "GL000252.1": "chr6_dbb_hap3",
    "GL000256.1": "chr6_ssto_hap7",
    "GL000253.1": "chr6_mann_hap4",
    "GL000258.1": "chr17_ctg5_hap1",
    "GL000254.1": "chr6_mcf_hap5",
    "GL000257.1": "chr4_ctg9_hap1",
    "GL000250.1": "chr6_apd_hap1",
}

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


def get_lifter(source_assembly: str, to_assembly: str="") -> Optional[ChainFile]:
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
    chain_file_basename = f"{source_assembly.lower()}To{to_assembly.capitalize()}.over.chain.gz"
    chain_file_path: Path = liftover_dir / chain_file_basename
    if not chain_file_path.exists():
        url = f"https://hgdownload.cse.ucsc.edu/goldenPath/{source_assembly.lower()}/liftOver/{chain_file_basename}"
        download_file(url, chain_file_path)
    lifter = ChainFile(str(chain_file_path), SYSTEM_GENOME_ASSEMBLY, source_assembly)
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

    liftover_failure_msg: str = f"No positional mapping was found in {SYSTEM_GENOME_ASSEMBLY}."
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
