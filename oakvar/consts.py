from os.path import join
from os.path import dirname

STDIN = "stdin"
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
LIFTOVER_FILE_SUFFIX = "." + LIFTOVER_LEVEL_KEY
VARIANT_LEVEL_OUTPUT_SUFFIX = ".var"
GENE_LEVEL_OUTPUT_SUFFIX = ".gen"
crm_idx = [["uid"], ["tags"]]
crs_idx = [["uid"], ["sample_id"], ["sample_id", "uid"]]
crv_idx = [["uid"]]
crx_idx = [["uid"]]
crg_idx = [["hugo"]]

exit_codes = {"alreadycrv": 2, 2: "alreadycrv"}

all_mappings_col_name = "all_mappings"
mapping_parser_name = "mapping_parser"

VARIANT = 0
GENE = 1
LEVELS = {"variant": VARIANT, "gene": GENE}

gene_level_so_exclude = ["2KU", "2KD"]

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

assembly_choices = ["hg38", "hg19", "hg18"]
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
JOB_STATUS_ABORTED = "Abort"
JOB_STATUS_ERROR = "Error"

MODULE_OPTIONS_KEY = "module_options"

