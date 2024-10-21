`--filtersql` can be used to generated filtered output files. This option can be used in `ov run` and `ov report`. For example,

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
