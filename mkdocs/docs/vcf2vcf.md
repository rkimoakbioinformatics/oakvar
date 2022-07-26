With OakVar v2.5.0 and later, a fast-track annotation workflow, `vcf2vcf`, is available. The speed-up by this workflow can be an order of magnitude compared to previous versions, depending on the number of samples. For example, mapping the variants in the chromosome 20 of the 1000 Genomes Project data took about 10 minutes with --vcf2vcf in our test system. With ClinVar annotation added, about 15 minutes. The condition to use this workflow is:

- Input file format is Variant Call Format (VCF).
- Output file format is also VCF.
- Annotation SQLite database files are not needed.

To use `vcf2vcf`, just add `--vcf2vcf` to `ov run`. The output format will be always VCF, so `-t` option is not necessary. For example,

    ov run input.vcf --vcf2vcf -a clinvar

will read `input.vcf` and generate `input.vcf.vcf` with ClinVar annotation as well as GENCODE gene mapping.

    ov run input.vcf --vcf2vcf -a clinvar -n annotated

will generate `annotated.vcf` as output, due to `-n` option.
