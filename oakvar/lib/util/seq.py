from typing import Optional
from typing import Tuple
from pyliftover import LiftOver

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


def get_lifter(source_assembly: str) -> Optional[LiftOver]:
    """get_lifter.

    Args:
        source_assembly (str): source_assembly

    Returns:
        Optional[LiftOver]:
    """
    from os import makedirs
    from ..system import get_liftover_dir
    from ..consts import SYSTEM_GENOME_ASSEMBLY

    liftover_dir = get_liftover_dir()
    if not liftover_dir:
        return None
    if not liftover_dir.exists():
        makedirs(liftover_dir, exist_ok=True)
    lifter = LiftOver(
        source_assembly, to_db=SYSTEM_GENOME_ASSEMBLY, cache_dir=liftover_dir
    )
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
        lifter: LiftOver instance. Use `oakvar.get_lifter` to get one.
        source_assembly (Optional[str]): Genome assembly of input. If `lifter` is given, this parameter will be ignored.

    Returns:
        (chromosome, position) if liftover was successful. `None` if not.
    """
    if not lifter:
        if not source_assembly:
            raise ValueError(f"Either lifter or source_assembly should be given")
        lifter = get_lifter(source_assembly)
    if not lifter:
        raise ValueError(f"LiftOver not found for {source_assembly}")
    # res = Optional[[(chrom, pos, strand, score)...]]
    hits = lifter.convert_coordinate(chrom, pos - 1)
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

    if not lifter:
        if not source_assembly:
            raise ValueError(f"Either lifter or source_assembly should be given")
        lifter = get_lifter(source_assembly)
    if not lifter:
        raise ValueError(f"LiftOver not found for {source_assembly}")
    if ref is None:
        converted = liftover_one_pos(chrom, pos, lifter=lifter)
        if converted is None:
            raise LiftoverFailure("Liftover failure")
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
            raise LiftoverFailure("Liftover failure")
        newchrom = converted[0]
        newpos = converted[1]
    elif reflen >= 1 and altlen == 0:  # del
        pos1 = pos
        pos2 = pos + reflen - 1
        converted1 = liftover_one_pos(chrom, pos1, lifter=lifter)
        converted2 = liftover_one_pos(chrom, pos2, lifter=lifter)
        if converted1 is None or converted2 is None:
            raise LiftoverFailure("Liftover failure")
        newchrom = converted1[0]
        newpos1 = converted1[1]
        newpos2 = converted2[1]
        newpos = min(newpos1, newpos2)
    elif reflen == 0 and altlen >= 1:  # ins
        converted = liftover_one_pos(chrom, pos, lifter=lifter)
        if converted is None:
            raise LiftoverFailure("Liftover failure")
        newchrom = converted[0]
        newpos = converted[1]
    else:
        pos1 = pos
        pos2 = pos + reflen - 1
        converted1 = liftover_one_pos(chrom, pos1, lifter=lifter)
        converted2 = liftover_one_pos(chrom, pos2, lifter=lifter)
        if converted1 is None or converted2 is None:
            raise LiftoverFailure("Liftover failure")
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
