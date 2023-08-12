from typing import Any
from typing import Optional
from typing import Dict


class Variant:
    def __init__(
        self,
        chrom: str,
        pos: int,
        end_pos: int,
        ref_base: Optional[str],
        alt_base: Optional[str],
        tags: str,
        fileno: int,
        lineno: int,
    ):
        self.chrom: str = chrom
        self.pos: int = pos
        self.end_pos: int = end_pos
        self.ref_base: Optional[str] = ref_base
        self.alt_base: Optional[str] = alt_base
        self.ori_pos: int = pos
        self.ori_end_pos: int = end_pos
        self.ori_ref_base: Optional[str] = ref_base
        self.ori_alt_base: Optional[str] = alt_base
        self.tags: str = tags
        self.fileno: int = fileno
        self.lineno: int = lineno
        self.sample_data: Dict[str, Dict[str, Any]] = {}
        self.other_data: Dict[str, Dict[str, Any]] = {}

    def add_sample_data(self, sample: str, d: Dict[str, Any]):
        self.sample_data[sample] = d

    def add_other_data(self, table_name: str, d: Dict[str, Any]):
        self.other_data[table_name] = d
