OakVar is a **platform** for genomic variant analyses. It has the following core functionality:

* Annotation
* Query
* Serve applications

## Annotation

Annotation is adding additional information to a variant. A certain variant may have a clinical consequence such as a genetic disease or a meaning such as being rarely observed in a population. There are many sources of such annotation, and manually finding the annotation from these many sources for many variants can be laborious and daunting.

OakVar automates this annotation work by:

* Loop over variants
* Standardize annotation sources
* Manage installation of annotation sources
* Organize the annotation from different sources by variant

The main OakVar command for annotation is `ov run`. For example, the following command will annotate the variants in a VCF file, `input.vcf`, with annotation sources ClinVar and COSMIC and generate an annotated VCF file, `annotated.vcf` as well as a database file, `annotated.sqlite`.

    ov run input.vcf -a clinvar cosmic -t vcf -n annotated

## Query

Once variants are annotated, they can be filtered by their annotation, for example to know if a sample has clinically relevant variants or not. OakVar stores annotated variants as a database, and thus variants annotated with OakVar can be filtered with SQL queries. OakVar provides a standard mechanism to query variants regardless of their annotation sources.

The main OakVar command for querying variants is `ov report`. For example, the following command will filter the variants in `annotated.sqlite` with the filter set defined in `filter.json` and produce a VCF file of filtered variants, `filtered.vcf`.

    ov report annotated.sqlite -f filter.json -s filtered -t vcf

Query options can be given to `ov run` as well. The following command will generate the same `annotated.sqlite` with annotated variants, but `annotated.vcf` will already have annotated and filtered variants.

    ov run input.vcf -a clinvar cosmic -t vcf -n annotated -f filter.json

## Applications

Most common way of using OakVar is the input-to-output workflow using `ov run` and `ov report`. However, any Python-based program can access the variants annotated with OakVar since OakVar is a Python library as well. This aspect of OakVar is being actively developed and streamlined. OakVar comes with two built-in web applications - one for job submission and module management and the other for exploring annotation result, as well as one installable web application for exploring the details of a single variant.

Check back this page later for exciting future development in this area.
