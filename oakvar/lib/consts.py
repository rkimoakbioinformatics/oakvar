from os.path import join
from os.path import dirname
from typing import Dict

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
SAMPLE_LEVEL = "sample"
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

VARIANT_LEVEL_PRIMARY_KEY = "uid"
GENE_LEVEL_PRIMARY_KEY = "hugo"
DEFAULT_DF_SIZE = 1_000_000
DEFAULT_CONVERTER_READ_SIZE = 10_000
OAKVAR_VERSION_KEY = "oakvar"
VARIANT_LEVEL_PRIMARY_KEY_COLDEF: Dict[str, str] = {"name": "uid", "type": "int", "level": VARIANT_LEVEL, "title": "Variant ID", "desc": "Variant ID"}
GENE_LEVEL_PRIMARY_KEY_COLDEF: Dict[str, str] = {"name": "hugo", "type": "string", "level": GENE_LEVEL, "title": "HUGO Symbol", "desc": "HUGO Symbol of gene"}
LINE_NO_KEY = "lineno"
OUTPUT_COLS_KEY = "output_columns"
OUTPUT_KEY = "output"
