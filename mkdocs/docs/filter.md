# Filters

Your initial `ov run` may produce a result database with unnecessary variants. Reports generated with this database can be too big as well. You can generate a trimmed down version of the result database and corresponding reports using filters.

A filter is a JSON object specifying the conditions used to filter variants. An example filter JSON object is below.

```
{
    "sample": {
        "require": [
            "sample1",
            "sample2",
        ],
        "reject": [
            "sample3",
            "sample4",
        ]
    },
    "genes": [
        "KRAS",
        "BRAF"
    ],
    "variant": {
        "operator": "and",
        "rules": [
            {
                "column": "gnomad3__af",
                "test": "lessThan",
                "value": 0.01,
                "negate": false
            },
            {
                "operator": "or",
                "rules": [
                    {
                        "column": "clinvar__sig",
                        "test": "stringContains",
                        "value": "Pathogenic",
                        "negate": false
                    },
                    {
                        "column: "cadd__phred",
                        "test": "greaterThan",
                        "value": 20,
                        "negate": false
                    }
                ],
                "negate": NEGATE
            }
        ],
        "negate": NEGATE
    }
}
```
This filter means variants that meet the following conditions.

```
(they appear in sample1 or sample2, but not in sample3 nor sample4) AND
(they are from the gene KRAS or BRAF) AND
(their gnomAD3 allele frequency is less than 0.01) AND
(their ClinVar significance has Pathogenic OR their CADD Phred is greater than 20)
```

`sample` and `genes` can be omitted, which would mean not filtering by samples and genes.

The complete specification of the filter JSON object is below:

```
{
    "sample": {
        "require": [
            "Sample to include",
            "Sample to include",
            ...
        ],
        "reject": [
            "Sample name to exclude",
            "Sample to exclude",
            ...
        ]
    },
    "genes": [
        "Gene to include",
        "Gene to include",
        ...
    ],
    "variant": {
        "operator": OPERATOR ("and" or "or"),
        "rules": [
            // One filter object can define the filter on one database column.
            {
                "column": "Column name in the result database" (such as "gnomad3__af"),
                "test": TEST_TYPE
                "value": VALUE
                "negate": NEGATE (true or false)
            },
            // Filter objects can be grouped and nested in another filter object.
            {
                "operator": OPERATOR,
                "rules": [
                    // Filter objects for columns, separated by a comma
                ],
                "negate": NEGATE
            }
        ],
        "negate": NEGATE
    }
}

```

`TEST_TYPE` is one of "equals", "lessThanEq", "lessThan", "greatherThanEq", "greaterThan", "hasData", "stringContains", "stringStarts", "stringEnds", "between", "in", "select", and "inList".

`VALUE` is string, integer, float, or in the case of TEST\_TYPE `select`, a list of string, integer, or float.

Filter JSON objects can be downloaded as JSON files from the GUI result viewer, using the export button in the Filter tab.

## Generating reports with filtered variants

Filters can be used directly with `ov run`. In this way, an input file is processed to produce a result database of all the variants in the input file, and reports are generated with filtered variants only. For example,

```
ov run input.vcf -f filter.json -t vcf
```

will process and generate `input.vcf.sqlite` that has all the variants in `input.vcf`, and then generate `input.vcf.vcf` with only the variants that met the filtering conditions defined in `filter.json`.

`ov report` also can be used to do the same:

```
ov report input.vcf.sqlite -f filter.json -t vcf
```

## Generating a filtered version of a result database

A trimmed version of a result database with filtered variants can be generated as well. This way, repeated report generation will not repeat the filtration. The trimmed database can be used for the GUI result viewer as well. To make such a trimmed version, use `ov util filtersqlite` command. For example,

```
ov util filtersqlite input.vcf.sqlite -f filter.json
```

will generate `input.vcf.filtered.sqlite` with the variants in `input.vcf.sqlite` that met the conditions defined in `filter.json`.

The suffix `filtered` in `input.vcf.filtered.sqlite` can be changed with `--suffix` option:

```
ov util filtersqlite input.vcf.sqlite -f filter.json --suffix trimmed
```

will produce `input.vcf.trimmed.sqlite`.

The output directory to store the filtered databases can be specified with `-o` option. 

Multiple result databases can be processed at once:

```
ov util filtersqlite input_1.vcf.sqlite input_2.vcf.sqlite -f filter.json
```
will process `input_1.vcf.sqlite` and `input_2.vcf.sqlite` one by one.

## Filtering with SQL

Instead of a filter JSON object, SQL conditions can be directly used to filter variants as well. To do so, use `--filtersql` option. This option can be used in `ov run` and `ov report`. For example,

```
ov run input.vcf --filtersql "v.base__chrom='chr1'" -t csv
```

will generate a CSV format output file of the variants that are filtered by the criterion that the chromosome of the variant is chr1.

The `v.` in front of `base__chrom` means the `variant` table in the result database. `g.` will mean the `gene` table, and `s` the sample table.

`base__chrom` means `base` module's `chrom` column. `base` module is an abstract column which includes the basic variant information as well as the mapper module. Other column names are used as they are. After a module name and "`__`" (double underline), a column name follows. Thus, `clinvar__sig` means `cliuvar` module's `sig` column. Thus, generating a VCF format output of the variants filtered with the criterion that the variants are `Pathogenic` in ClinVar would be

```
ov report input.vcf --filtersql "clinvar__sig='Pathogenic'" -t vcf
```

SQL's `where` command syntax is used. Thus, `and` and `or` can be used as well. For example,

```
ov report input.vcf -a clinvar --filtersql "base__hugo='BRCA1' and clinvar__sig like '%Pathogenic%' -t vcf"
```

will annotate the input file with the ClinVar module and generate a VCF format output of the variants filtered by two criteria, the gene being BRCA1 and the ClinVar significance has `Pathogenic`.
