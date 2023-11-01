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

from os.path import join
from os.path import dirname
from typing import Dict

LEVEL = "level"
VARIANT_LEVEL_PRIMARY_KEY = "uid"
GENE_LEVEL_PRIMARY_KEY = "hugo"
OLD_INPUT_LEVEL_KEY = "crv"
OLD_VARIANT_LEVEL_KEY = "crx"
OLD_GENE_LEVEL_KEY = "crg"
INPUT_LEVEL_KEY = "variant"
VARIANT_LEVEL_KEY = "variant"
GENE_LEVEL_KEY = "gene"
SAMPLE_LEVEL_KEY = "sample"
STANDARD_INPUT_FILE_SUFFIX = "." + INPUT_LEVEL_KEY
VARIANT_LEVEL_MAPPED_FILE_SUFFIX = "." + VARIANT_LEVEL_KEY
GENE_LEVEL_MAPPED_FILE_SUFFIX = "." + GENE_LEVEL_KEY
SAMPLE_FILE_SUFFIX = "." + SAMPLE_LEVEL_KEY
VARIANT_LEVEL_OUTPUT_SUFFIX = ".var"
GENE_LEVEL_OUTPUT_SUFFIX = ".gen"
crm_idx = [[VARIANT_LEVEL_PRIMARY_KEY], ["tags"]]
crs_idx = [
    [VARIANT_LEVEL_PRIMARY_KEY],
    ["sample_id"],
    ["sample_id", VARIANT_LEVEL_PRIMARY_KEY],
]
crv_idx = [[VARIANT_LEVEL_PRIMARY_KEY]]
crx_idx = [[VARIANT_LEVEL_PRIMARY_KEY]]
crg_idx = [["hugo"]]

all_mappings_col_name = "all_mappings"
mapping_parser_name = "mapping_parser"

VARIANT = 0
GENE = 1
LEVELS = {"variant": VARIANT, "gene": GENE}
VARIANT_LEVEL = "variant"
GENE_LEVEL = "gene"
ERR_LEVEL = "err"

module_tag_desc = {
    "allele frequency": "modules for studying allele frequency across populations",
    "cancer": "tools for cancer research",
    "clinical relevance": "tools for assessing clinical relevance of variants",
    "converters": "modules for using the result of other tools as oakvar input",
    "dbnsfp": "modules ported from dbNSFP",
    "denovo": "modules related to denovo variants",
    "evolution": "modules for studying variants in evolutionary context",
    "genes": "modules for studying variants at the gene level",
    "genomic features": "modules for studying genomic features",
    "interaction": "modules for studying molecular interactions",
    "literature": "modules for variant-related literature",
    "multiple assays": "modules for multiplex assays",
    "non coding": "modules for studying noncoding variants",
    "protein visualization": "modules to visualize variants on protein structures",
    "reporters": "modules for generating output formats",
    "variant effect prediction": "modules to predict variant effects",
    "variants": "modules to study variants at the variant level",
    "visualization widgets": "modules for visualizing variants",
}

publish_time_fmt = "%Y-%m-%dT%H:%M:%S"
install_tempdir_name = "temp"
cannonical_chroms = ["chr" + str(n) for n in range(1, 23)] + ["chrX", "chrY"]
liftover_chain_paths = {}
for g in ["hg18", "hg19"]:
    liftover_chain_paths[g] = join(
        dirname(__file__), "liftover", g + "ToHg38.over.chain"
    )
RESULT_DB_SUFFIX_SQLITE = ".sqlite"
RESULT_DB_SUFFIX_DUCKDB = ".duckdb"
LOG_SUFFIX = ".log"
ERROR_LOG_SUFFIX = ".err"

JOB_STATUS_UPDATE_INTERVAL = 10  # seconds
JOB_STATUS_FINISHED = "Finished"
JOB_STATUS_ERROR = "Error"

MODULE_OPTIONS_KEY = "module_options"
SYSTEM_GENOME_ASSEMBLY = "hg38"

DEFAULT_CONVERTER_READ_SIZE = 10_000
OAKVAR_VERSION_KEY = "oakvar"
VARIANT_LEVEL_PRIMARY_KEY_COLDEF: Dict[str, str] = {
    "name": VARIANT_LEVEL_PRIMARY_KEY,
    "type": "int",
    LEVEL: VARIANT_LEVEL,
    "title": "Variant ID",
    "desc": "Variant ID",
}
GENE_LEVEL_PRIMARY_KEY_COLDEF: Dict[str, str] = {
    "name": "hugo",
    "type": "string",
    LEVEL: GENE_LEVEL,
    "title": "HUGO Symbol",
    "desc": "HUGO Symbol of gene",
}
FILENO_KEY = "fileno"
LINENO_KEY = "lineno"
ERRNO_KEY = "errno"
OUTPUT_COLS_KEY = "output_columns"
OUTPUT_KEY = "output"
ERR_KEY = "err"
MAPPER_TABLE_NAME = "mapper"
SAMPLE_HAS = "has"
CHROM = "chrom"
POS = "pos"
END_POS = "end_pos"
REF_BASE = "ref_base"
ALT_BASE = "alt_base"
ORI_CHROM = "ori_chrom"
ORI_POS = "ori_pos"
ORI_END_POS = "ori_end_pos"
ORI_REF_BASE = "ori_ref_base"
ORI_ALT_BASE = "ori_alt_base"
VALID = "valid"
ERROR = "error"
NO_ALT_ALLELE = "noallele"
