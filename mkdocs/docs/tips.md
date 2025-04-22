## Genome assembly

The latest T2T genome can be used as input. Add `--genome hs1` to `ov run`. For example,

    ov run oakvar_example.vcf --genome hs1

## Batch processing

We recommend using a [job configuration file](conf.md) for batch processing. Let's say you want to process 100 VCF files with multiple annotator modules, filter the result with complex filter conditions, and generate VCF output files of the filtered variants. This process can be defined in a job configuration file as shown below, for example:

```
run:
  annotators:
    - cgl
    - cgc
    - cancer_genome_interpreter
    - gnomad3
    - dbsnp
  filterpath: ./filter.json
  report_types:
    - vcf
```

Make sure that you have installed the necessary annotation modules.

Let's say the above configuration is saved as `ov.yml`. See [Filtering](filter.md) for how to make `filter.json`. Then, you can run

```
ov run input1.vcf input2.vcf ... input100.vcf -c ov.yml
```
which will process each of the 100 input files one by one, filter them, and generate 100 report files (input1.vcf.vcf, input2.vcf.vcf, etc) with the variants filtered by the conditions defined in `filter.json`.
