# Technical Details

## How a representative transcript is chosen.

A genomic location can be shared by multiple isoforms of a gene, therefore one variant can result in different consequences in different isoforms of a gene. For simplicity and convenience, it is customary to pick a "representative transcript (isoform)" of a gene and use it to denote the molecular consequence of a variant.

However, sometimes different researchers picked different isoforms as the representative one for a gene, which made communication and collaboration difficult.

In this context, [MANE Transcripts](https://useast.ensembl.org/info/genome/genebuild/mane.html) were born. As a collaboration project between NCBI and EMBL-EBI, MANE transcripts aim to be a useful set of one representative isoform for one gene.

OakVar picks MANE Select isoforms as representative isoforms by default. Howver, with `--primary-transcript` option to `ov run`, you can pick a different isoform as a representative isoform of a gene as well. 

    --primary-transcript mane-clinical

will pick MANE Clinical Plus set transcripts as representative ones.

    --primary-transcript file.txt

where `file.txt` is in the space-delimited format

    GENE TRANSCRIPT

will pick the TRANSCRIPT as the representative one for the GENE. For the genes which are not defined in `file.txt`, MANE Select will be used if no other option is given to `--primary-transcript`, or MANE Clinical Plus will be used if `mane-clinical` is additionally given.

OakVar collects molecular consequence results for all the isoforms where a given variant maps in `base__all_mappings` column in the `variant` table in the result SQLite database.
