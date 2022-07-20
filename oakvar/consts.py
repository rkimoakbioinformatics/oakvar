from os.path import join
from os.path import dirname

# built-in file column definitions
crm_def = [
    {"name": "original_line", "title": "Original Line", "type": "int", "width": 90},
    {"name": "tags", "title": "User Tags", "type": "string", "width": 90},
    {"name": "uid", "title": "UID", "type": "int", "width": 70},
    {
        "name": "fileno",
        "title": "Input File Number",
        "type": "int",
        "width": 90,
        "filterable": False,
        "hidden": True,
    },
]
crm_idx = [["uid"], ["tags"]]
crs_def = [
    {"name": "uid", "title": "UID", "type": "int", "width": 70},
    {"name": "sample_id", "title": "Sample", "type": "string", "width": 90},
]
crs_idx = [["uid"], ["sample_id"], ["sample_id", "uid"]]
crv_def = [
    {
        "name": "uid",
        "title": "UID",
        "type": "int",
        "width": 60,
        "hidden": True,
        "filterable": False,
    },
    {
        "name": "chrom",
        "title": "Chrom",
        "type": "string",
        "width": 50,
        "category": "single",
        "filterable": True,
    },
    {
        "name": "pos",
        "title": "Position",
        "type": "int",
        "width": 80,
        "filterable": True,
    },
    {
        "name": "ref_base",
        "title": "Ref Base",
        "type": "string",
        "width": 50,
        "filterable": False,
    },
    {
        "name": "alt_base",
        "title": "Alt Base",
        "type": "string",
        "width": 50,
        "filterable": False,
    },
    {"name": "note", "title": "Note", "type": "string", "width": 50},
]
crv_idx = [["uid"]]
crx_def = crv_def + [
    {
        "name": "coding",
        "title": "Coding",
        "type": "string",
        "width": 50,
        "category": "single",
        "categories": ["Y"],
    },
    {
        "name": "hugo",
        "title": "Gene",
        "type": "string",
        "width": 70,
        "filterable": True,
    },
    {
        "name": "transcript",
        "title": "Transcript",
        "type": "string",
        "width": 135,
        "hidden": False,
        "filterable": False,
    },
    {
        "name": "so",
        "title": "Sequence Ontology",
        "type": "string",
        "width": 120,
        "category": "single",
        "filterable": True,
    },
    {
        "name": "cchange",
        "title": "cDNA change",
        "type": "string",
        "width": 70,
        "filterable": False,
    },
    {
        "name": "achange",
        "title": "Protein Change",
        "type": "string",
        "width": 55,
        "filterable": False,
    },
    {
        "name": "all_mappings",
        "title": "All Mappings",
        "type": "string",
        "width": 100,
        "hidden": True,
        "filterable": False,
    },
]
crx_idx = [["uid"]]
crg_def = [
    {
        "name": "hugo",
        "title": "Gene",
        "type": "string",
        "width": 70,
        "filterable": True,
    },
    {"name": "note", "title": "Note", "type": "string", "width": 50},
]
crg_idx = [["hugo"]]
crt_def = [
    {"name": "primary_transcript", "title": "Primary transcript", "type": "string"},
    {"name": "alt_transcript", "title": "Alternate transcript", "type": "string"},
]
crt_idx = [["primary_transcript"]]
crl_def = [
    {"name": "uid", "title": "UID", "type": "int", "width": 70},
    {"name": "chrom", "title": "Chrom", "type": "string", "width": 80},
    {"name": "pos", "title": "Pos", "type": "int", "width": 80},
    {"name": "ref_base", "title": "Reference allele", "type": "string", "width": 80},
    {"name": "alt_base", "title": "Alternate allele", "type": "string", "width": 80},
]

exit_codes = {"alreadycrv": 2, 2: "alreadycrv"}

all_mappings_col_name = "all_mappings"
mapping_parser_name = "mapping_parser"

VARIANT = 0
GENE = 1
LEVELS = {"variant": VARIANT, "gene": GENE}

gene_level_so_exclude = ["2KU", "2KD"]

base_smartfilters = [
    {
        "name": "popstats",
        "title": "Population AF <=",
        "description": "Set a maximum allele frequency.",
        "allowPartial": True,
        "selector": {
            "type": "inputFloat",
            "defaultValue": "0.1",
        },
        "filter": {
            "operator": "and",
            "rules": [
                {
                    "operator": "or",
                    "rules": [
                        {
                            "column": "gnomad3__af",
                            "test": "lessThanEq",
                            "value": "${value}",
                        },
                        {"column": "gnomad3__af", "test": "noData"},
                    ],
                },
                {
                    "operator": "or",
                    "rules": [
                        {
                            "column": "gnomad__af",
                            "test": "lessThanEq",
                            "value": "${value}",
                        },
                        {"column": "gnomad__af", "test": "noData"},
                    ],
                },
                {
                    "operator": "or",
                    "rules": [
                        {
                            "column": "thousandgenomes__af",
                            "test": "lessThanEq",
                            "value": "${value}",
                        },
                        {
                            "column": "thousandgenomes__af",
                            "test": "noData",
                        },
                    ],
                },
            ],
        },
    },
    {
        "name": "so",
        "title": "Sequence Ontology",
        "description": "Select sequence ontologies.",
        "selector": {
            "type": "select",
            "optionsColumn": "base__so",
            "multiple": True,
            "defaultValue": ["MIS"],
        },
        "filter": {"column": "base__so", "test": "select", "value": "${value}"},
    },
    {
        "name": "chrom",
        "title": "Chromosome",
        "description": "Select chromosome(s).",
        "selector": {
            "type": "select",
            "multiple": True,
            "optionsColumn": "base__chrom",
        },
        "filter": {"column": "base__chrom", "test": "select", "value": "${value}"},
    },
    {
        "name": "coding",
        "title": "Coding",
        "description": "Include only coding/noncoding variants",
        "selector": {
            "type": "select",
            "options": {"No": True, "Yes": False},
            "defaultValue": False,
        },
        "filter": {"column": "base__coding", "test": "hasData", "negate": "${value}"},
    },
]

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

legacy_gene_level_cols_to_skip = ["base__num_variants", "base__so", "base__all_so"]
assembly_choices = ["hg38", "hg19", "hg18"]
publish_time_fmt = "%Y-%m-%dT%H:%M:%S"
install_tempdir_name = "temp"
cannonical_chroms = ["chr" + str(n) for n in range(1, 23)] + ["chrX", "chrY"]
liftover_chain_paths = {}
for g in ["hg18", "hg19"]:
    liftover_chain_paths[g] = join(dirname(__file__), "liftover", g + "ToHg38.over.chain")
