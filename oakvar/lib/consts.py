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

from os.path import join
from os.path import dirname

INPUT_LEVEL_KEY = "crv"
VARIANT_LEVEL_KEY = "crx"
GENE_LEVEL_KEY = "crg"
SAMPLE_LEVEL_KEY = "crs"
MAPPING_LEVEL_KEY = "crm"
LIFTOVER_LEVEL_KEY = "crl"
STANDARD_INPUT_FILE_SUFFIX = "." + INPUT_LEVEL_KEY
VARIANT_LEVEL_MAPPED_FILE_SUFFIX = "." + VARIANT_LEVEL_KEY
GENE_LEVEL_MAPPED_FILE_SUFFIX = "." + GENE_LEVEL_KEY
SAMPLE_FILE_SUFFIX = "." + SAMPLE_LEVEL_KEY
MAPPING_FILE_SUFFIX = "." + MAPPING_LEVEL_KEY
VARIANT_LEVEL_OUTPUT_SUFFIX = ".var"
GENE_LEVEL_OUTPUT_SUFFIX = ".gen"
crm_idx = [["uid"], ["tags"]]
crs_idx = [["uid"], ["sample_id"], ["sample_id", "uid"]]
crv_idx = [["uid"]]
crx_idx = [["uid"]]
crg_idx = [["hugo"]]

all_mappings_col_name = "all_mappings"
mapping_parser_name = "mapping_parser"

VARIANT = 0
GENE = 1
LEVELS = {"variant": VARIANT, "gene": GENE}
VARIANT_LEVEL = "variant"
GENE_LEVEL = "gene"

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
result_db_suffix = ".sqlite"
LOG_SUFFIX = ".log"
ERROR_LOG_SUFFIX = ".err"

JOB_STATUS_UPDATE_INTERVAL = 10  # seconds
JOB_STATUS_FINISHED = "Finished"
JOB_STATUS_ERROR = "Error"

MODULE_OPTIONS_KEY = "module_options"
SYSTEM_GENOME_ASSEMBLY = "hg38"
