#### Installation

First, let's install OakVar.

    pip install oakvar

#### Setup

Then, we set up OakVar, including configuration files, system folders, an OakVar account, and OakVar store cache files.

    ov system setup

#### Check system configuration

How OakVar has been set up can be viewed with `ov config system` command.

    ov config system

    publish_url: https://store.oakvar.com
    store_url: https://store.oakvar.com
    ...
    default_assembly: hg38
    sys_conf_path: /Users/Shared/oakvar/conf/system.yml
    root_dir: /Users/Shared/oakvar
    modules_dir: /Users/Shared/oakvar/modules
    conf_dir: /Users/Shared/oakvar/conf
    jobs_dir: /Users/Shared/oakvar/jobs
    log_dir: /Users/Shared/oakvar/logs

`modules_dir` is where OakVar modules for conversion, mapping, annotation, and reporting as well as OakVar applications are stored.

#### Install ClinVar annotation module

In this tutorial, we will annotate variants with [ClinVar](https://www.ncbi.nlm.nih.gov/clinvar). To do so, we install the ClinVar module.

    ov module install clinvar

#### Uninstall a module

Just to practice uninstalling a module, we'll install and then uninstall [BioGRID](http://thebiogrid.org).

    ov module install biogrid
    ov module uninstall biogrid

#### Create an example input

Next, we need some variants to annotate. OakVar has a built-in variant file for this purpose.

    ov new exampleinput

This will create an example input file, `exampleinput`, in the current directory.

#### Run an annotation job

Now, we annotate the example input file with ClinVar and then create a result VCF file with annotated variants. `-a` option controls annotation sources and `-t` option report formats.

    ov run exampleinput -a clinvar -t vcf

This will create `exampleinuput.vcf` which will have the input variants annotated with ClinVar.

#### Generate an Excel report of annotated variants

Excel format reporting module is included in OakVar by default. `-s` option defines the file name of the report file except the extension.

    ov report exampleinput.sqlite -t excel -s annotated

This will generate `annotated.xlsx`.

#### 
