# AI, ML and OakVar

**This page will be updated with more content in the future.**

One of OakVar's main aims is easy integration of genomic variant analysis results with AI/ML frameworks.

The first step toward that goal is the conversion of analysis results into DataFrames.

OakVar provides the following method to convert the analysis results in SQLite tables into [Polars](https://docs.pola.rs/py-polars/html/reference/) DataFrame.

    import oakvar as ov
    df = ov.get_df_from_db("oakvar_example.vcf.sqlite")

This will load the content of `variant` table into `df` as a Polars DataFrame.

If you want to use Pandas DataFrame instead, 

    df.to_pandas(use_pyarrow_extension_array = True)

will produce a Pandas version of the same DataFrame.

Back to `get_df_from_db` method, you can specify which table to load and a SQL expression for filtering the content.

    df = ov.get_df_from_db(
        "oakvar_example.vcf.sqlite", table_name="sample"
    )

will load the `sample` table into `df` as a DataFrame.

    df = ov.get_df_from_db(
        "oakvar_example.vcf.sqlite", 
        table_name="variant", 
        sql="base__so='MIS' and clinvar__sig like '%Pathogenic%'"
    )

will load the `variant` table, but with the filter for the variants whose consequence is missense and whose ClinVar clinical significance include `Pathogenic`.


# Apache Spark and OakVar

OakVar is natively integrated with Apache Spark, allowing annotation on the big genome project scale.

Since OakVar's annotation capability is unlimited through Python, including AI/ML-based annotation, this means that your Apache Spark pipeline can annotate variants in unlimited ways.

Let's see how it is done.

First, create a Spark session.

```python
import pyspark
from pyspark.sql import SparkSession

conf = pyspark.SparkConf().setAppName("ov")
sc = pyspark.SparkContext(conf=conf)
spark = SparkSession(sc)
```

Then, let's make a test set of variants as a Spark DataFrame.

```python
data = [
        {"chrom": "chr7", "pos":140734758, "ref_base": "T", "alt_base": "C"},
        {"chrom": "chr7", "pos":140734780, "ref_base": "-", "alt_base": "G"},
        {"chrom": "chr7", "pos":140736487, "ref_base": "GTGCGA", "alt_base": "-"},
        {"chrom": "chr7", "pos":140736487, "ref_base": "GTGCGAT", "alt_base": "-"},
        {"chrom": "chr7", "pos":140742186, "ref_base": "-", "alt_base": "T"},
        {"chrom": "chr7", "pos":140753351, "ref_base": "A", "alt_base": "G"},
        {"chrom": "chr7", "pos":140800417, "ref_base": "CT", "alt_base": "-"},
        {"chrom": "chr7", "pos":140800417, "ref_base": "CTG", "alt_base": "-"},
        {"chrom": "chr7", "pos":140807936, "ref_base": "A", "alt_base": "-"},
        {"chrom": "chr7", "pos":140924703, "ref_base": "A", "alt_base": "T"},
        {"chrom": "chr7", "pos":148847298, "ref_base": "A", "alt_base": "T"},
        {"chrom": "chr7", "pos":27199497, "ref_base": "C", "alt_base": "G"},
        {"chrom": "chr7", "pos":2958506, "ref_base": "A", "alt_base": "T"},
        {"chrom": "chr7", "pos":50319062, "ref_base": "A", "alt_base": "T"},
        {"chrom": "chr7", "pos":55019278, "ref_base": "A", "alt_base": "T"},
        {"chrom": "chr7", "pos":55019338, "ref_base": "G", "alt_base": "A"},
        {"chrom": "chr7", "pos":55181319, "ref_base": "-", "alt_base": "GGGTTG"},
        {"chrom": "chr8", "pos":127738263, "ref_base": "A", "alt_base": "T"},
        {"chrom": "chr8", "pos":43018497, "ref_base": "A", "alt_base": "G"},
        {"chrom": "chr9", "pos":107489172, "ref_base": "A", "alt_base": "T"},
        {"chrom": "chr9", "pos":130714320, "ref_base": "A", "alt_base": "T"},
        {"chrom": "chr9", "pos":132928872, "ref_base": "A", "alt_base": "T"},
        {"chrom": "chr9", "pos":136545786, "ref_base": "A", "alt_base": "T"},
        {"chrom": "chr9", "pos":21968622, "ref_base": "C", "alt_base": "-"},
        {"chrom": "chr9", "pos":21974827, "ref_base": "A", "alt_base": "T"},
        {"chrom": "chr9", "pos":37034031, "ref_base": "A", "alt_base": "T"},
        {"chrom": "chr9", "pos":5021988, "ref_base": "A", "alt_base": "T"},
]
for uid in range(len(data)):
    data[uid]["uid"] = uid
df = spark.createDataFrame(data)
print("Original DataFrame")
df.show()
```
Output:
```
Original DataFrame
+--------+-----+---------+--------+---+
|alt_base|chrom|      pos|ref_base|uid|
+--------+-----+---------+--------+---+
|       C| chr7|140734758|       T|  0|
|       G| chr7|140734780|       -|  1|
|       -| chr7|140736487|  GTGCGA|  2|
|       -| chr7|140736487| GTGCGAT|  3|
|       T| chr7|140742186|       -|  4|
|       G| chr7|140753351|       A|  5|
|       -| chr7|140800417|      CT|  6|
|       -| chr7|140800417|     CTG|  7|
|       -| chr7|140807936|       A|  8|
|       T| chr7|140924703|       A|  9|
|       T| chr7|148847298|       A| 10|
|       G| chr7| 27199497|       C| 11|
|       T| chr7|  2958506|       A| 12|
|       T| chr7| 50319062|       A| 13|
|       T| chr7| 55019278|       A| 14|
|       A| chr7| 55019338|       G| 15|
|  GGGTTG| chr7| 55181319|       -| 16|
|       T| chr8|127738263|       A| 17|
|       G| chr8| 43018497|       A| 18|
|       T| chr9|107489172|       A| 19|
+--------+-----+---------+--------+---+
only showing top 20 rows
```

Then, we create a Spark Resilient Distributed Dataset (RDD).

```python
rdd = sc.parallelize(data, 4)
```

Then, let's define a custom function which will be run in each worker node and for a partition of the RDD.

```python
import oakvar as ov

def get_ov_annotation(iterator):
    mapper = ov.get_mapper("gencode")
    clinvar = ov.get_annotator("clinvar")
    for row in iterator:
        ret = mapper.map(row)
        ret = clinvar.append_annotation(ret)
        yield ret
```

This function will be run as a standalone function in worker nodes, so the worker nodes should already have OakVar installed and their Python should have access to the installed OakVar package.

This function loads a `gencode` mapper and a `clinvar` annotation module, and for variant, runs the mapper and the annotator.

Let's apply this custom function to the variant RDD.

```python
ret = rdd.mapPartitions(get_ov_annotation).collect()
```

`ret` will be a `list` of `dict`, each `dict` corresponding to one annotated variant.

Let's create a new RDD with annotated variants. We'll use GENCODE mapper (`gencode`) and ClinVar annotator (`clinvar`). They should be already installed in the worker nodes.

```python
schema = ov.lib.util.run.get_spark_schema(["gencode", "clinvar"])
rdd = spark.createDataFrame(ret, schema)
rdd.show()
```
Output:
```bash
+---+-----+---------+--------+--------+----+------+------+-----------------+---+--------------------+--------------------+------+--------------------+------------+--------------------+---------------------+----------------------+--------------------+-----------+-----------------+
|uid|chrom|      pos|ref_base|alt_base|note|coding|  hugo|       transcript| so|             cchange|             achange|exonno|        all_mappings|clinvar__uid|        clinvar__sig|clinvar__disease_refs|clinvar__disease_names|   clinvar__rev_stat|clinvar__id|clinvar__sig_conf|
+---+-----+---------+--------+--------+----+------+------+-----------------+---+--------------------+--------------------+------+--------------------+------------+--------------------+---------------------+----------------------+--------------------+-----------+-----------------+
|  0| chr7|140734758|       T|       C|NULL|     Y|  BRAF|ENST00000646891.2|MIS|           c.2140A>G|         p.Ile714Val|    18|{"BRAF": [["A0A2U...|        NULL|Uncertain signifi...| MONDO:MONDO:00055...|  Colorectal cancer...|criteria provided...|    1410272|             NULL|
|  1| chr7|140734780|       -|       G|NULL|      |  BRAF|ENST00000646891.2|INT|c.2128-10_2128-9insC|
|  2| chr7|140736487|  GTGCGA|       -|NULL|      |  BRAF|ENST00000646891.2|INT|c.2128-1722_2128-...|
|  3| chr7|140736487| GTGCGAT|       -|NULL|      |  BRAF|ENST00000646891.2|INT|c.2128-1723_2128-...|
|  4| chr7|140742186|       -|       T|NULL|      |  BRAF|ENST00000646891.2|INT|      c.1993-2240dup|
|  5| chr7|140753351|       A|       G|NULL|     Y|  BRAF|ENST00000646891.2|MIS|           c.1784T>C|         p.Phe595Se
|  6| chr7|140800417|      CT|       -|NULL|     Y|  BRAF|ENST00000646891.2|FSD|        c.927_928del|  p.Glu309AspfsTer4
|  7| chr7|140800417|     CTG|       -|NULL|     Y|  BRAF|ENST00000646891.2|IND|        c.923_925del|         p.Ala308de
|  8| chr7|140807936|       A|       -|NULL|      |  BRAF|ENST00000646891.2|INT|         c.711+24del|
|  9| chr7|140924703|       A|       T|NULL|     Y|  BRAF|ENST00000646891.2|SYN|              c.1T>A|             p.Met1
| 10| chr7|148847298|       A|       T|NULL|     Y|  EZH2|ENST00000320356.7|SYN|              c.1T>A|             p.Met1
| 11| chr7| 27199497|       C|       G|NULL|     Y|HOXA13|ENST00000649031.1|MIS|            c.581G>C|         p.Cys194Se
| 12| chr7|  2958506|       A|       T|NULL|     Y|CARD11|ENST00000396946.9|SYN|              c.1T>A|             p.Met1
| 13| chr7| 50319062|       A|       T|NULL|     Y| IKZF1|ENST00000331340.8|MLO|              c.1A>T|             p.Met1
| 14| chr7| 55019278|       A|       T|NULL|     Y|  EGFR|ENST00000275493.7|MLO|              c.1A>T|             p.Met1?|     1|{"EGFR": [["P0053...|        NULL|                NULL|                 NULL|                  NULL|                NULL|       NULL|             NULL|
| 15| chr7| 55019338|       G|       A|NULL|     Y|  EGFR|ENST00000275493.7|MIS|             c.61G>A|          p.Ala21Thr|     1|{"EGFR": [["P0053...|        NULL|Uncertain signifi...|      MedGen:CN130014|  EGFR-related lung...|criteria provided...|     848579|             NULL|
| 16| chr7| 55181319|       -|  GGGTTG|NULL|     Y|  EGFR|ENST00000275493.7|INI|c.2309_2310insGGGTTG|p.Asp770delinsGlu...|    20|{"EGFR": [["P0053...|        NULL|                NULL|                 NULL|                  NULL|                NULL|       NULL|             NULL|
| 17| chr8|127738263|       A|       T|NULL|     Y|   MYC|ENST00000377970.6|MLO|              c.1A>T|             p.Met1?|     2|{"CASC11": [["", ...|        NULL|                NULL|                 NULL|                  NULL|                NULL|       NULL|             NULL|
| 18| chr8| 43018497|       A|       G|NULL|     Y| HOOK3|ENST00000307602.9|STL|           c.2156A>G| p.Ter719TrpextTer84|    22|{"HOOK3": [["Q86V...|        NULL|                NULL|                 NULL|                  NULL|                NULL|       NULL|             NULL|
| 19| chr9|107489172|       A|       T|NULL|     Y|  KLF4|ENST00000374672.5|SYN|              c.1T>A|             p.Met1=|     1|{"ENSG00000289987...|        NULL|                NULL|                 NULL|                  NULL|                NULL|       NULL|             NULL|
+---+-----+---------+--------+--------+----+------+------+-----------------+---+--------------------+--------------------+------+--------------------+------------+--------------------+---------------------+----------------------+--------------------+-----------+-----------------+
only showing top 20 rows
```

The annotated variants can be saved as Parquet files.

```python
df.write.parquet("annotated_variants.parquet")
```

We are considering adding more helper methods to OakVar to make this process more ergonomic. Please let us know what you think at our Discord server at [https://discord.gg/wZfkTMKTjG](https://discord.gg/wZfkTMKTjG).
::: oakvar.api.config
::: oakvar.lib.util.util
    options:
      members:
        - get_df_from_db

# API Main

OakVar functionality is available through Python API. For example, OakVar's annotation pipeline can be started with the following:

    >>> import oakvar as ov
    >>> ov.api.run(inputs=["input.vcf"], annotators=["clinvar"], report_types=["vcf"])

There is 1 to 1 correspondence between command-line interface commands and Python API functions. The table below shows such correspondence.

CLI | Python API | Functionality
----|------------|--------------
ov config system | [oakvar.api.config.system](/api/config/#oakvar.api.config.system) | Gets or sets system configuration.
ov config user | [oakvar.api.config.user](/api/config/#oakvar.api.config.user) | Gets user configuration.
ov issue | [oakvar.api.report_issues](/api/oakvar_api/#oakvar.api.report_issue) | Opens a webpage to report OakVar issues.
ov license | [oakvar.api.license](/api/oakvar_api/#oakvar.api.license) | Gets the OakVar license information.
ov module info | [oakvar.api.module.info](/api/module/#oakvar.api.module.info) | Gets information on a module.
ov module install | [oakvar.api.module.install](/api/module/#oakvar.api.module.install) | Installs modules.
ov module installbase | [oakvar.api.module.installbase](/api/module/#oakvar.api.module.installbase) | Installs system modules.
ov module ls | [oakvar.api.module.ls](/api/module/#oakvar.api.module.ls) | Lists modules.
ov module pack | [oakvar.api.module.pack](/api/module/#oakvar.api.module.pack) | Packs a module for registration at OakVar store.
ov module uninstall | [oakvar.api.module.uninstall](/api/module/#oakvar.api.module.uninstall) | Uninstalls modules.
ov module update | [oakvar.api.module.update](/api/module/#oakvar.api.module.update) | Updates modules.
ov new exampleinput | [oakvar.api.new.exampleinput](/api/new/#oakvar.api.new.exampleinput) | Creates an example input file.
ov new module | [oakvar.api.new.module](/api/new/#oakvar.api.new.module) | Creates a template for a new module.
ov report | [oakvar.api.report](/api/oakvar_api/#oakvar.api.report) | Generates report files from OakVar result databases.
ov run | [oakvar.api.run](/api/oakvar_api#oakvar.api.run) | Runs the OakVar annotation pipeline.
ov store delete | [oakvar.api.store.delete](/api/store/#oakvar.api.store.delete) | Deletes a module from the OakVar store.
ov store fetch | [oakvar.api.store.fetch](/api/store/#oakvar.api.store.fetch) | Fetches the OakVar store cache.
ov store login | [oakvar.api.store.login](/api/store/#oakvar.api.store.login) | Logs in to the OakVar store.
ov store logout | [oakvar.api.store.logout](/api/store/#oakvar.api.store.logout) | Logs out from the OakVar store.
ov store register | [oakvar.api.store.register](/api/store/#oakvar.api.store.register) | Register a module at the OakVar store.
ov store url | [oakvar.api.store.url](/api/store/#oakvar.api.store.url) | Gets the URL of the OakVar store.
ov store account change | [oakvar.api.store.account.change](/api/store_account/#oakvar.api.store.account.change) | Changes the password of an OakVar store account.
ov store account check | [oakvar.api.store.account.check](/api/store_account/#oakvar.api.store.account.check) | Checks if logged in at the OakVar store.
ov store account create | [oakvar.api.store.account.create](/api/store_account/#oakvar.api.store.account.create) | Creats an OakVar store account.
ov store account delete | [oakvar.api.store.account.delete](/api/store_account/#oakvar.api.store.account.delete) | Deletes an OakVar store account.
ov store account reset | [oakvar.api.store.account.reset](/api/store_account/#oakvar.api.store.account.reset) | Invokes a password change email for an OakVar store account.
ov system account check | [oakvar.api.system.check](/api/system/#oakvar.api.system.check) | Checks OakVar installation on the system.
ov system md | [oakvar.api.system.md](/api/system/#oakvar.api.system.md) | Gets or sets the OakVar modules directory.
ov system setup | [oakvar.api.system.setup](/api/system/#oakvar.api.system.setup) | Sets up OakVar in the system.
ov update | [oakvar.api.update](/api/oakvar_api/#oakvar.api.update) | Gets OakVar version.
ov version | [oakvar.api.version](/api/oakvar_api/#oakvar.api.version) | Gets OakVar version.

OakVar Python API has a utility function to help data science with genomic data. If an OakVar analysis produced `ov_result.sqlite` result database file, the following will produce a Polars DataFrame from `variant` level data of the result database.

    >>> import oakvar as ov
    >>> df = ov.get_df_from_db("ov_result.sqlite", table="variant")

::: oakvar.api.module
::: oakvar.api.new
::: oakvar.api
    options:
      members:
        - license
        - run
        - report
        - report_issue
        - update
        - version
::: oakvar.api.store.account
::: oakvar.api.store
::: oakvar.api.system
# CLI Commands

Please add `-h` to each command to see help for options. For example, `ov run -h`, `ov report -h`, and `ov gui -h`.

## Setup

    ov system setup [-f setup_file --email EMAIL --pw PASSWORD --clean]

`setup_file` is a YAML format file with setup options, such as email, password, and installation directory. For example, if `oakvar_setup.yml` has the following,

    email: person@company.com
    pw: password
    modules\_dir: /path/to/directory/for/oakvar/modules

`ov system setup -f oakvar_setup.yml` will use the email and password in the file and install OakVar modules in the `modules_dir`.

## Run an analysis job

    ov run input_path [option ...]

## Create annotation reports

    ov report sqlite_file_path [option ...]

`sqlite_file_path` is the path to a .sqlite file produced by `ov run`.

## Launch a GUI server

    ov gui sqlite_file_path [option ...]

`sqlite_file_path` is the path to a .sqlite file produced by `ov run`.

## Manage modules

### List modules

	ov module ls [option ...] [module_names ...]

`module_names` is a regular expression. For example, `ov module ls -a ".*cancer.*"` will list all available modules which has "cancer" in their name.
  
### Install modules

	ov module install module_names [module_name] ... [option ...]

### Uninstall modules

	ov module uninstall module_name [module_name] ... [option ...]

### Update modules

	ov module update [module_name_patterns ...] [option ...]

`module_name_patterns` is a regular expression.

### Get information on modules

	ov module info module_name [option ...]

## Manage store accounts

### Create a store account

    ov store account create

### Log in on the OakVar store

    ov store login [--email EMAIL --pw PASSWORD]

### Log out from the OakVar store

    ov store logout

### Check if logged in on the OakVar store

    ov store account check

### Change a store account password

    ov store account change

### Reset the password of a store account

    ov store account reset

### Delete a store account

    ov store account delete

## Publish modules

### Pack a module for registering at the OakVar store

    ov module pack module_name [-d OUTDIR --code-only --split]

    -d: output directory
    --code-only: only code files will be packed into a .zip file.
    --split: packed files will be split into 100MB-size files.

About packing and publishing your modules, see [here](/register).

### Register a module at the OakVar store

    ov store register module_name [--code-url URL --data-url URL --overwrite]

Details on this command, see [here](/register).

## Manage configuration

### Manage modules directory

	ov system md [NEW_DIRECTORY]

If NEW\_DIRECTORY is not given, show the current location of OakVar modules. If given, changes the location of OakVar modules to NEW\_DIRECTORY.

### Show system configuration

	ov config system [key value type]

If key, value, and type are not given, shows the current system configuration. If given, updates the system configuration for the key with the value of the type. For example,

    ov config system modules_dir /Volumes/ExtSSD/ov_modules str

will update the `modules_dir` value of the system configuration. `type` is a Python data type, such as `int`, `float`, and `str`.

## Utilities

### Create an example input file

	ov new exampleinput

`oakvar_example.vcf` file will be created with example variants.

### Create an annotation module template

	ov new module -n NAME -t TYPE

    NAME: module name
    TYPE: module type such as converter, mapper, annotator, 
          postaggregator, and reporter

A template for an OakVar module will be created at `modules_dir`/`TYPE`s/`NAME`. New module development can start with this template.

### Merge analysis result database files

	ov util mergesqlite

### Filter analysis result database files

	ov util filtersqlite

### Show analysis result database file information

	ov util sqliteinfo --fmt [json(default)|yaml|text]

# OakVar Configuration file

#### Annotate with an OakVar configuration file

For repeated jobs, using a .yml file with job definition is handy.

For example, consider the following `ov run` job:

    ov run input.vcf -a clinvar dbsnp -t csv

The configuration of this job can be written in `conf.yml` file as follows:

    run:
        annotators: 
        - clinvar
        - dbsnp
        report_types: csv

Then, this file can be used as follows.

    ov run input.vcf -c conf.yml

which will work in the same way as the first `ov run` command.

Below are the correspondence between `ov run` options and the fields in package .yml files.

| ov run option | type | package file (.yml) option |
|---------------|------|----------------------------|
| -a | list | annotators |
| -p | list | postaggregators |
| -t | list | report\_types |
| -n | string | run\_name |
| -d | string | output\_dir |
| --clean | bool | clean |
| --genome | string | genome |
| -i | string | input\_format |
| --startat | string | startat |
| --endat | string | endat |
| --skip | list | skip |
| --keep-temp | bool | keep\_temp |
| --mp | integer | mp |
| --primary-transcript | string | primary\_transcript |
| --module-options | dict | module\_options |
| --vcf2vcf | bool | vcf2vcf |
| --logtofile | bool | logtofile |
| --ignore-sample | bool | ignore\_sample |

# Developer Guide on Debugging

### Entrypoints

| Command | Entrypoint |
|----------|-----------------|
| ov      | oakvar/\_\_main\_\_.py |
| ov run | oakvar/cli/run.py|
| ov report | oakvar/cli/report.py |
| ov gui | oakvar/cli/gui.py|

oakvar/\_\_main\_\_.py is intentional, to make `python -m oakvar` style of use possible.

### Base classes

OakVar modules inherit one of OakVar base module classes. Converters, mappers, annotators, postaggregators, and reporters have different base module classes.

| Type | Module | Class |
|----------|-----------------|-----------|
| converter | oakvar/base/converter.py | BaseConverter |
| mapper | oakvar/base/mapper.py | BaseMapper |
| annotator | oakvar/base/annotator.py | BaseAnnotator |
| postaggregator | oakvar/base/postaggregator.py | BasePostAggregator |
| reporter | oakvar/cli/report.py | BaseReporter |
| common | oakvar/base/commonmodule.py | BaseCommonModule |

To develop a new OakVar module, it should inherit one of these base classes. For example, an annotator module's class definition should be:

```
from oakvar import BaseAnnotator

class Annotator(BaseAnnotator):
```

# Developer Guide on OakVar Modules

OakVar's functionalities are mostly performed by Python modules. OakVar orchestrates their execution as well as their management.

To understand OakVar's modules, let's first see which modules are already installed in the system.

    ov module ls

This will show a list of modules installed in the system. These modules are stored under OakVar *modules directory*, which can be found with 

    ov system md

Inside the *modules directory*, there are subdirectories such as the following.

    annotators
    commons
    converters
    mappers
    postaggregators
    reporters
    webapps
    webviewerwidgets

Each subdirectory represents a *type* of OakVar module. Inside each type subdirectory, another level of subdirectories exist for the modules of the type directory. For example, in `reporter` module type directory, the following subdirectories may exist, which correspond to the reporter modules in the system.

    csvreporter
    excelreporter
    stdoutreporter
    textreporter
    tsvreporter
    vcfreporter

### Anatomy of a module

Details of a specific module can be shown with `ov module info`. Let's take a look at the information of `stdoutreporter` module.

    ov module info stdoutreporter

In the output, the directory where the module is installed can be found in `location` field. In the directory of `stdoutreporter`, the following three files will exist.

    stdoutreporter.md
    stdoutreporter.py
    stdoutreporter.yml

Among these files, `.py` and `.yml` files are the two essential files of any OakVar module. `.py` file is a Python module file which handles the operation of the module. `.yml` file is a YAML format file which has the information and the configuration of the module. `.md` file is a markdown format file which will be displayed on the OakVar web store.

#### Reporter

Let's take a look at each of these files. Below is the essential parts of `stdoutreporter.yml`.

    title: Standard Output Reporter
    version: 1.2.0
    type: reporter

OakVar uses this information to manage modules. 

Below is `stdoutreporter.py`.

    from oakvar import BaseReport

    class Reporter(BaseReport):

        def setup (self):
            if self.args:
                self.levels_to_write = self.args.get("level")
            if not self.levels_to_write:
                self.levels_to_write = ['variant']

        def write_preface (self, level):
            self.level = level

        def write_header (self, level):
            line = '#'+'\t'.join([col['col_name'] for \
                col in self.extracted_cols[level]])
            print(line)

        def write_table_row (self, row):
            print('\t'.join([str(v) if v != None else '' \
                for v in list(row)]))

`stdoutreporter.py` does not have all the codes to filter and fetch annotated variants from an OakVar annotation database file. OakVar connects to `stdoutreporter.py` and calls functions `setup`, `write_preface`, `write_header`, and `write_table_row`. By defining these functions, different reporter modules can be made. More on these functions are explained in *Workflow* section.

#### Annotator

Check out a guide on interactive annotation module development [here](https://medium.com/@ryanggukkim/interactively-make-variant-annotation-modules-with-oakvar-7719e2c8bf49).

Watch a webinar on making OakVar annotation modules [here](https://www.youtube.com/watch?v=9fIxez6s7Ag).

The essential function for *annotator* modules is `annotator`. Below is `target.py` of `target` annotation module.

    from oakvar import BaseAnnotator
    import sqlite3

    class Annotator(BaseAnnotator):

        def annotate(self, input_data):
            self.cursor.execute('select rationale, agents_therapy ' +
                'from target where gene="%s";'%input_data['hugo'])
            row = self.cursor.fetchone()
            if row:
                out = {'rationale': row[0], 'therapy': row[1]}
            else:
                out = None
            return out

`annotate` function receives `input_data` which is a `dict` of a variant, such as

    {"uid": 1834, 
     "chrom": "chr1", 
     "pos": 19834895, 
     "ref_base": "A", 
     "alt_base": "G"}

If you add `input_format: crx` to your module's yml file, `input_data` will have additional information pulled from .crx file, such as

    {"uid": 1834, 
     "chrom": "chr1", 
     "pos": 19834895, 
     "ref_base": "A", 
     "alt_base": "G",
     "hugo": "GeneA",
     "transcript": "ENST0000038472",
     "so": "missense_variant",
     ...}

OakVar will feed into `annotate` of an annotator module with variants of the input file, one by one, and excepts a `dict` of the module's output for each given variant. In the above example, the output is a `dict` with two keys, `rationale` and `therapy`. OakVar will collect the `dict`s of input variants and feed them to the downstream steps. 

The two keys `rationale` and `therapy` in the above example are the output columns of the module. The output columns of a module should be defined in the module's config (`.yml`) file. `target` module's config file, `target.yml`, has the following output columns definition.

    output_columns:
    - name: therapy
      title: Recommended Therapy
      type: string
    - name: rationale
      title: Rationale
      type: string

`name`, `title`, and `type` are essential components of an output column, with `name` being the same as a key in the output `dict` by `annotate` function. OakVar will expect the keys defined as `name` in `output_columns` in a module's config file in the return value of `annotate` function of the module.

Once a module's output columns are defined in its config file and the module's `annotate` function returns a `dict` with those output columns' `name` as its keys, OakVar will do the rest to include the module's output in the annotation database and reports.

OakVar provides convenience variables to eahc module's `annotate` function. If a module has `data` subdirectory and if the subdirectory has an SQLite database file whose name is `<module name>.sqlite` (thus, in the above example, `target/data/target.sqlite`), `self.conn` and `self.cursor` are provided as an SQLite database connection and cursor objects.

#### Mapper

The essential function for *mapper* modules is `map`. A typical mapper modules will be structured as follows.

    ...
    class Mapper(BaseMapper):
        ...
        def map(self, input_data):
            ...

A mapper module's `map` function is similar to an annotator module's `annotate` function, in that it receives a `dict` of an input variant, which has keys such as `uid`, `chrom`, `pos`, `ref_base`, and `alt_base) and is expected to return an `dict` of its output. One difference is that its output `dict` is supposed to have a pre-defined set of keys. First of all, the output `dict` of `map` function should have the keys in `input_data`. Then, the following keys should be defined as well.

    coding
    hugo
    transcript
    so
    cchange
    achange
    all_mappings

More details will be explained here. Until then, you can take a look at `gencode` module's `gencode.py` to know more.

#### Converter

The essential function for *converter* modules is `convert_line`. A typical converter module will be structured as follows.

    ...
    class Converter(BaseConverter):
        ...
        def convert_line(self, l):
            ...

More will be explained later.

#### Postaggregator

The essential function for *postaggregator* modules is `annotate`. A typical postaggregator module will be structured as follows.

    ...
    class Postaggregator(BasePostaggregator):
        ...
        def annotate(self, input_data):
            ...

More will be explained later.

### Dependency control

#### Module dependency

An OakVar module can depend on other OakVar modules for it to properly function. Let's say module `annotator1` uses the output of `annotator2` and `annotator3` as its input. For `annotator1` to properly function, `annotator2` and `annotator3` should be already installed. This installation requirement is specified in the config file of `annotator1` (`annotator1.yml`) as the following:

    requires:
    - annotator2
    - annotator3

With this in place, when `annotator1` is installed with `ov module install annotator1`, the two dependency modules also will be installed automatically, if not already present in the system.

As mentioned, `annotator1` uses the output of `annotator2` and `annotator3` as its input. This dependency should be defined in `annotator1.yml` as the following.

    secondary_inputs:
      annotator2: {}
      annotator3: {}

With this simple definition, the output of `annotate2` and `annotate3` will be available as `secondary_data` variable to the `annotate` function of `annotate1` module. For example, 

    def annotate(self, input_data, secondary_data=None):
    ...

of `annotate1.py` will have `secondary_data["annotate2"]` and `secondary_data["annotate3"]` available. If `annotate2.yml` has the following output column definition,

    output_columns:
    - name: value1
      title: Value 1
      type: string
    - name: value2
      title: Value 2
      type: string

`annotate1`'s `annotate` function will be able to access those with `secondary_data["annotator2"]["value1"]` and `secondary_data["annotator2"]["value2"]"`.

Finer control of secondary input is possible as follows. For example, the following in `annotate1.yml`

    secondary_inputs:
      annotator2:
        match_columns:
          primary: uid
          secondary: uid
        use_columns:
          - value1

will mean that `annotator2` output will be available as `secondary_data["annotator2"]` to the `annotate` function of `annotator1`, that for each variant, the `uid` field in the output by `annotator2` and the `uid` field in `input_data` to the `annotate` function of `annotator1` will be match to find the correct secondary_data for the variant to the function, and that only `value1` field will be available to the function.

#### PyPI dependency

If an OakVar module needs packages from PyPI, such requirement can be specified in the module's yml file. For example, if `annotator1`'s `annotator1.yml` has the following,

    pypi_dependencies:
    - numpy

`ov module install annotator1` will automatically perform `pip install numpy` while installing `annotate1` module.


### Template generation

`ov new module` command will generate a module template folder, with template .py, .yml. and .md files for the module. The template will be in the correct folder for the module and recognized by OakVar automatically. Its usage is

    ov new module -n MODULE_NAME -t MODULE_TYPE

where MODULE_NAME is the name of the new module (numbers and small letters and up to one underscore between two letters) and MODULE_TYPE is the type of the new module (converter, mapper, annotator, postaggregator, and reporter).

Below are examples.

    ov new module -n annotator_1 -t annotator

will generate the template for the annotator module `annotator_1` in the folder `<MODULES_DIR>/annotators/annotator_1`.

    ov new module -n converter_1 -t converter

will generate the template for the converter module `converter_1` in the folder `<MODULES_DIR>/converters/converter_1`.

    ov new module -n postaggregator_1 -t postaggregator

will generate the template for the postaggregator module `postaggregator_1` in the folder `<MODULES_DIR>/postaggregators/postaggregator_1`.

### Module options

Modules can receive custom options through CLI or GUI. In `ov run`, such options to modules can be given with `--module-options` option. For example,

    ov run input.vcf --module-options annotator_1.option_1=value_1

will send the following Python `dict` to the `annotator_1` module as `self.module_options`.

    { "option_1": "value_1" }

In `annotator_1.py`, `self.module_options` will have the above `dict`.

Module options should be defined in the module's yml file. Thus, `annotator_1.yml` should have the following.

    module_options:
        annotator_1:
            option_1:
                title: Option 1
                type: string
                help: Option 1 help

Under the `module_options` key, the name of the annotator module should come. Then, the name of the option key. Then, `title`, `type`, and `help` are mandatory keys. `type` can be `string`, `int`, or `float`. With these defined, when `annotator_1` is selected on the OakVar GUI (launched by `ov gui`), an input box for `option_1` will appear under the title and will have a tooltip with the text of `help`.

# Developer Guide on Testng OakVar

OakVar has a command for testing the modules you are developing. 

```
ov test -m MODULE_NAME [MODULE_NAME]...
```

For example,

```
ov test -m clinvar
```

will test `clinvar` module, if it is in your annotators directory.

For this test to work, your module's Python script (`clinvar.py` in `clinvar` module) should have `test` method.

For example, let's say you want to test if your annotator module's `annotate` method works well for some test input. `clinvar.py` can have something like the following.

```
def test(*args, **kwargs):
    m = Annotator()
    m.base_setup()
    out = m.annotate({
        "chrom": "chr1", 
        "pos": 925952, 
        "ref_base": "G", 
        "alt_base": "A"
    })
    expected = {
        'sig': 'Uncertain significance', 
        'disease_refs': 'MedGen:CN517202', 
        'disease_names': 'not provided', 
        'rev_stat': 'criteria provided, single submitter', 
        'id': 1019397, 
        'sig_conf': None
    }
    if out == expected:
        return True, ""
    else:
        return False, \
            f"annotated output does not match expected: {out} != {expected}"
```

`Annotator()` to create an instance of your annotator and call `base_setup()` to set up the annotator instance. In the code above, expected and actual output are compared. The return value of `test` is always `Tuple[bool, str]`. `bool` shows whether the test was successful or not. `str` can have an arbitrary message.

With the `test` code above in `clinvar.py`, `ov test -m clinvar` will produce the following.

```
>ov test -m clinvar
[2024/11/10 09:08:06] clinvar: testing...
[2024/11/10 09:08:06] clinvar: ok
[2024/11/10 09:08:06] passed 1 failed 0
```

`ov test` will create `oakvar_module_test` folder under the current directory. To wipe out the test folder and perform a clean test, give `--clean` option.

`test` method can have any test logic. Below is a test example for `csvreporter`.

```
def test(*args, **kwagrs):
    from pathlib import Path
    import subprocess
    from oakvar import get_module_test_dir
    import csv

    test_dir = get_module_test_dir("csvreporter", module_type="reporter")
    if not test_dir:
        return False, "could not find csvreporter test dir."
    input_path = (test_dir / "oakvar_example.vcf").resolve()
    subprocess.run(["ov", "run", str(input_path), 
        "-t", "csvreporter", "-d", "."])
    output_path = Path(".") / (input_path.name + ".variant.csv")
    if not output_path.exists():
        return False, f"ov run did not produce {output_path}."
    reference_path = test_dir / "oakvar_example.vcf.variant.csv"
    with open(output_path, mode="r") as f:
        reader = csv.reader(f, )
        out = [row for row in reader if not row[0].startswith("#")]
    with open(reference_path, mode="r") as f:
        reader = csv.reader(f)
        ref = [row for row in reader if not row[0].startswith("#")]
    if out == ref:
        return True, ""
    else:
        return False, "output does not match reference."
```

The method invokes OakVar to do a complete run to produce the output file of the reporter module. Then, it compares the output with the reference data. 

For convenience, OakVar provides `get_module_test_dir` method, which will give the path to the `test` folder under the tested module's directory. This way, you can add input files and reference output files in the `test` folder and conveniently access them from within the `test` method.

Since `test` method is a regular Python method and the only requirement for the method is the `Tuple[bool, str]` return value, `test` can even connect to internet sources and do comparison as well.

`*args` and `**kwargs` arguments are not currently used, but reserved for future expansion of the method.

If tested modules do not have `test` method, then the test will pass.

```
ov test -m biogrid go
[2024/11/10 09:27:14] biogrid: testing...
[2024/11/10 09:27:14] biogrid: no test function. Skipping.
[2024/11/10 09:27:14] go: testing...
[2024/11/10 09:27:14] go: no test function. Skipping.
[2024/11/10 09:27:14] passed 2 failed 0
```

Testing can be done with Python API as well.

```
➜ python
Python 3.12.3
Type "help", "copyright", "credits" or "license" for more information.
>>> import oakvar as ov
>>> ov.api.test.test(["clinvar", "go"])
[2024/11/10 09:28:55] clinvar: testing...
[2024/11/10 09:28:56] clinvar: ok
[2024/11/10 09:28:56] go: testing...
[2024/11/10 09:28:56] go: no test function. Skipping.
[2024/11/10 09:28:56] passed 2 failed 0
{
    'passed': True, 
    'details': {
        'clinvar': {
            'passed': True, 
            'msg': ''
        }, 
        'go': {
            'passed': True, 
            'msg': 'no test function'
        }
    }, 
    'num_passed': 2, 
    'num_failed': 0
}
```

The return value of `oakvar.api.test.test` is a `dict`:

```
passed: bool. True if all modules passed or False
details: a dict. Keys are module names. Values are:
    passed: bool. True if the module passed or False
    msg: str. Any return message from the module's test method.
num_passed: int. Number of modules which passed
num_failed: int. Number of modules which did not pass
```

# Developer Guide on OakVar Workflow

There are a few workflows of using OakVar modules.

    ov run
    ov report
    ov gui

As mentioned, there are three workflows of using modules in OakVar.

    ov run
    ov report
    ov gui

#### ov run

When `ov run` is called, OakVar imports and executes modules in the following manner.

    input
    | recognizes input files' format with
    | converter modules' check_format function
    v
    converter module's convert_line function
    v
    mapper module's map function
    | imports annotator modules according to
    | -a option
    v
    annotator modules' annotate function
    | import postaggregator modules according to
    | -p option as well as default postaggregator
    | modules
    v
    postaggregator modules' annotate function
    | import reporter modules according to
    | -t option
    v
    reporter modules' write_preface, write_header, write_table_row functions
    |
    v
    report files

#### ov report

When `ov report` is called, OakVar imports and executes modules in the following manner.

    annotation database file
    | import reporter modules accorging to
    | -t option
    v
    reporter modules' write_preface, write_header, write_table_row functions
    |
    v
    report files

#### ov gui

Will be discussed later.

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
# GUI

OakVar's graphical user interface (GUI) is launched by

    ov gui

A web server will be started on the terminal and your default 
web browser will open a new tab, which will show the graphical 
user interface of OakVar.

The log output of the web server will be at `wcravat.log` file
under `conf_dir` shown by `ov system config`. Also,

    ov gui --debug

will display any error the server encounters on the terminal as well.

OakVar GUI has two tabs, `Jobs` and `Store`.

## Jobs

In `Jobs` tab of OakVar GUI, you can submit jobs and launch 
interactive result viewer for individual jobs.

## Store

In `Store` tab of OakVar GUI, you can install and uninstall OakVar
modules as well as explore the details of each module. OakVar's
web store brings OakVar's own modules as well as OpenCRAVAT's modules.

## Result Viewer

`ov gui` with a path to an OakVar result SQLite database file will launch
the OakVar result viewer. For example,

    ov gui sample_1.vcf.sqlite

will launch the OakVar result viewer on the analysis data in 
`sample_1.vcf.sqlite`.

Just-DNA-Seq group wrote a very nice tutorial on using OakVar GUI. Please refer to [their doc](https://just-dna-seq.readthedocs.io/en/oakvar/getting_started.html) for more details of using OakVar GUI.

# OakVar: Genomic Variant Analysis Platform

<!-- ![Logo](https://github.com/rkimoakbioinformatics/oakvar/raw/master/oakvar/gui/websubmit/images/logo.png){: style="height:240px;"} -->
<a href="https://www.youtube.com/watch?v=MNvDdL_p5s8" target="_blank"><img src="https://storage.oakvar.com/oakvar-public/website_resources%2Fscreenshot_deep_dive_into_oakvar.png" width=400 /></a>

* Annotate genomic variants with diverse annotation sources.
* Make databases of annotated variants.
* Query annotated variants with filter sets.
* Make reports in diverse formats.
* Visualize annotated variants with graphical user interface.
* Works via CLI and GUI.
* Easily develop, run, and distribute CLI and GUI genomics apps. OakVar acts as an operating system for genomics apps.
* Connect genomic data to AI/ML models.

OakVar is a genomic variant interpretation platform. Genomic variants can be annotated with diverse annotation sources, stored in databases, queried with filter sets, written to reports in diverse formats, and visualized with graphical user interfaces. Furthermore, OakVar supports command-line and graphical user interface apps which use the annotated variant data generated by OakVar, just like an operating system supports applications on it.

## Installing OakVar Modules through OakVar Store

The OakVar Store is where OakVar's modules are registered, found, and distributed. If you used OpenCRAVAT, OpenCRAVAT's modules are also available through OakVar Store if there is no updated OakVar version of the same module exists. To know which modules are available through the OakVar Store, do

```
ov module ls -a
```

This will list the OakVar modules available through the OakVar Store. To know more details of a specific module, do

```
ov module info module_name # module_name such as clinvar
```

To install modules, do

```
ov module install module_name [module_name] ...
```

A regular expression can be given as *module_name*. Thus, 

```
ov module install clin.*
```

will install all modules the name of which starts with `clin`.

## Installing through GitHub

OakVar can install custom modules directly from GitHub. It is as easy as simply giving the module's name and the URL of the folder of the module on GitHub to `ov module install`. Let's say you have a custom module hosted on the `dev` branch of your GitHub repo `yourorganization/yourrepo` in the following folder:

```
https://github.com/yourorganization/yourrepo/
    oakvar_modules/
        annotators/
            awesomeannotator/
                awssomeannotator.py
                awssomeannotator.yml
                awssomeannotator.md
                data/
                    awesomeannotator.sqlite
```

Your colleagues can install `awesomeannotator` module with the following command.

```
ov module install awesomeannotator \
 https://github.com/yourorganization/yourrepo/\
 tree/dev/oakvar_modules/annotators/awssomeannotator
```

will download the content of only the `awesomeannotator` folder in the `dev` branch of the repository, figure out that the module is an `annotator`, and put the `awesomeannotator` module under the appropriate `annotators` category folder inside your system's OakVar modules root directory.

This way, your custom module under development can be easily shared with your colleagues.

It is important to give the module's name as a separate argument and also to use a full GitHub tree URL, which has `/tree/<branch name>`, to the module's folder. If the module files are hosted at the root folder of a repository, the tree URL should end with `/tree/<branch name>`.

## Installing OakVar

Install OakVar.

    pip install oakvar

> #### Note for open-cravat users
>
> OakVar supports backward compatibility with open-cravat and thus open-cravat should be first removed before installing OakVar by `pip uninstall open-cravat`. open-cravat can simply be restored by removing OakVar by `pip uninstall oakvar` and installing open-cravat by `pip install open-cravat`. There is no side-effect of doing this switch unless you share open-cravat modules with OakVar as described below.
>
> OakVar does not share system files with nor transfer system configuration from open-cravat. OakVar's default modules directory is different.
>
> OakVar is backward-compatible with open-cravat modules. If you have been using open-cravat and want to continue to use open-cravat modules with OakVar, you can do so by setting OakVar modules directory to point to that of open-cravat with `ov system md` command. Please keep in mind that OakVar has its own updated versions for some of open-cravat modules, so if you are sharing the same modules directory between OakVar and open-cravat, `ov module update` may break oc-compatibility of some of the updated modules.

## Setup

`ov system setup` will set up OakVar with sane defaults.

Setup process can be customized with a setup file or environment variables, which can be useful in automated deployment.

System modules are automatically installed with `ov system setup`. If you want to install additional modules as a part of `ov system setup` process, you can use `--modules` option as follows.

    ov system setup --modules clinvar biogrid

### Setup with a file

A setup file in yaml format can be used. System configuration fields which are missing in the setup file will be filled with sane defaults. Setup with a file with custom locations for modules and logs can be done as

    ov system setup -f setup.yaml

where `setup.yaml` is

    modules_dir: ~/oakvar_modules
    logs_dir: ~/oakvar_logs

The filename of the setup file does not have to be `setup.yaml`. 

You can specify your OakVar store account email and password in setup.yaml as follows:

    ov_store_email: YOUR_EMAIL
    ov_store_pw: YOUR_PASSWORD

Additional modules can be specified as well in the setup file as follows.

    modules:
    - clinvar
    - biogrid

### Setup with environment variables

All system configuration fields can be overridden with environment variables. To override a system config field, set the environment variable `OV_` + upper-cased field name to a desired value. For example, 

System configuration field | Environmental variable |
---------------------------|--------------|
sys_conf_path | OV_SYS_CONF_PATH |
root_dir | OV_ROOT_DIR |
modules_dir | OV_MODULES_DIR |
log_dir | OV_LOG_DIR |
jobs_dir | OV_JOBS_DIR |
conf_dir | OV_CONF_DIR |
gui_port | OV_GUI_PORT |

The custom setup in the previous section can be done using environmental variables as

    export OV_MODULES_DIR=~/oakvar_modules
    export OV_LOGS_DIR=~/oakvar_logs
    ov system setup

Another example is installing system files in a custom directory.

    export OV_ROOT_DIR=/data/oakvar
    ov system setup

This will install OakVar system files at `/data/oakvar`.

Using environmental variablse for setup can be useful in deploying OakVar with Docker containers.

### Clean setup

If you experience any problem and want to do clean installation of OakVar, `ov system setup --clean` provides such clean installation. It will reset the system and user configuration files. `--clean` still will not delete `modules`, `jobs`, `logs`, and `conf` folders. `modules` have downloaded modules and users should manually delete this folder if they really want, because this folder can take a lot of time to recreate. `jobs`, `logs`, and `conf` folders have just contents.

# Overview of OakVar

## Modular

OakVar is a **platform** for genomic variant analyses. By platform, we mean that OakVar is modular. *Modules* written in Python are the building blocks of OakVar. OakVar achieves its functions by orchestrating such modules.

OakVar has the following core functionality:

* Annotation
* Query
* Serve applications
* Visualize

## Annotation

Annotation is adding additional information to a variant. A certain variant may have a clinical consequence such as a genetic disease or a meaning such as being rarely observed in a population. There are many sources of such annotation, and manually finding the annotation from these many sources for many variants can be laborious and daunting.

OakVar automates this annotation work by:

* Loop over variants
* Standardize annotation sources
* Manage installation of annotation sources
* Organize the annotation from different sources by variant

The main OakVar command for annotation is `ov run`. For example, the following command will annotate the variants in a VCF file, `input.vcf`, with annotation sources ClinVar and generate an annotated VCF file, `annotated.vcf` as well as a database file, `annotated.sqlite`.

    ov module install clinvar # if clinvar module is not already installed.
    ov run input.vcf -a clinvar -t vcf -n annotated

## Query

Once variants are annotated, they can be filtered by their annotation, for example to know if a sample has clinically relevant variants or not. OakVar stores annotated variants as a database, and thus variants annotated with OakVar can be filtered with SQL queries. OakVar provides a standard mechanism to query variants regardless of their annotation sources.

The main OakVar command for querying variants is `ov report`. For example, the following command will filter the variants in `annotated.sqlite` with the filter set defined in `filter.json` and produce a VCF file of filtered variants, `filtered.vcf`.

    ov report annotated.sqlite -f filter.json -s filtered -t vcf

Query options can be given to `ov run` as well. The following command will generate the same `annotated.sqlite` with annotated variants, but `annotated.vcf` will already have annotated and filtered variants.

    ov run input.vcf -a clinvar -t vcf -n annotated -f filter.json

## Visualize

OakVar comes with a graphical user interface. `ov gui` launches a job and store management web app by default, and also works as the entry point for OakVar's web apps. 

## Applications

Most common way of using OakVar is the input-to-output workflow using `ov run` and `ov report`. However, any Python-based program can access the variants annotated with OakVar since OakVar is a Python library as well. This aspect of OakVar is being actively developed and streamlined. OakVar comes with two built-in web applications - one for job submission and module management and the other for exploring annotation result, as well as one installable web application for exploring the details of a single variant.

Check back this page later for exciting future development in this area.

# Registering OakVar Modules on OakVar Store

You can publish your OakVar modules to the OakVar store with OakVar command-line interface. For example, let's say you made an awesome OakVar annotation module named `awesome` and wants to share it with the world. You can do this in three steps. 

    ov module pack awesome

This will create one or two files, depending whether your module has data folder in it or not. Your module's code will be packed into `awesome__<version>__code.zip` where `version` is the version number defined in `awesome.yml` file in your module's directory, and if your module has `data` subdirectory, `awesome__<version>__data.zip` also will be created.

If your module is bigger than 1GB, `--split` option can be given. This will split the code and the data of your module into zip part files of 1GB each. For example, if `awesome` module is 2.5GB big and most of the size is from its data, 

    ov module pack awesome --split

will produce the following files.

    awesome__1.0.0__code.zip000
    awesome__1.0.0__data.zip000
    awesome__1.0.0__data.zip001
    awesome__1.0.0__data.zip002

Then, upload these zip files to somewhere people can download. Using their URLs,

    ov store register awesome --code-url ... --data-url ...

will register your module in the OakVar store. `--data-url` is needed only if your module produced a data zip file. If you have many split zip files, `-f` option can be given with a YAML format file with code and data URLs. For example, 

    ov store register awesome -f urls.txt

with `urls.txt` of the following content

    code_url:
    - https://dropbox.com/xxxxxxxx/awesome__1.0.0__code.zip000
    data_url:
    - https://dropbox.com/xxxxxxxx/awesome__1.0.0__data.zip000
    - https://dropbox.com/xxxxxxxx/awesome__1.0.0__data.zip001
    - https://dropbox.com/xxxxxxxx/awesome__1.0.0__data.zip002

will register the module.

This way, you have total control of your module's publication. You can just delete the module zip files from where you stored them and OakVar store will automatically deregister those deleted versions. If you move the module zip files to new locations you can just register them again with new URLs.
# Scikit-Learn and OakVar Example

OakVar is a Python-based platform for analyzing genomic variants. One main aim of OakVar is easy integration of genomic data with AI/ML frameworks. In this tutorial, I’d like to show how easily such integration can be done.

## Overview
We will train classifiers which will predict the ancestry of a person using the person’s genotype data.

Let’s say we are considering only 5 variants, sampled from 5 people, each of whom belongs to one of two populations, African and European. These 5 people’s ancestry and variant presence are below.


                        Variants
    Name    Ancestry  A  B  C  D  E
    Jack    African   o  o  x  x  x
    Paul    European  x  x  o  o  o
    James   European  x  x  x  o  o
    John    African   o  o  o  x  x
    Brian   African   o  o  x  x  x

We can consider the above as the following.

        y           X
    African   1  1  0  0  0
    European  0  0  1  1  1
    European  0  0  0  1  1
    African   1  1  1  0  0
    African   1  1  0  0  0

Using [scikit-learn](https://scikit-learn.org/stable/index.html) library of Python and the above data, a classifier to predict ancestry based on these five variants can be trained as follows.

    import numpy as np
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.model_selection import train_test_split

    X = np.array([
        [1,1,0,0,0],
        [0,0,1,1,1],
        [0,0,0,1,1],
        [1,1,1,0,0],
        [1,1,0,0,0]
    ])
    y = np.array([
        "African",
        "European",
        "European",
        "African",
        "African"
    ])
    clf = MultinomialNB()
    X_train, X_test, y_train, y_test = train_test_split(X, y)
    y_pred = clf.fit(X_train, y_train).predict(X_test)
    print("y_test:", y_test)
    print("y_pred:", y_pred)
    y_test: ['African' 'European']
    y_pred: ['African' 'European']

This was a toy example. The real data we will use is [The 1000 Genomes Project](https://www.internationalgenome.org/), which has the same kind of ancestry and genotyping data of more than 2,000 people from around the world.

## Dataset
As a quick test, we will use the chromosome Y dataset of the 1000 Genomes Project, one of its smallest datasets. This dataset has the genotype and phenotype data of 1,233 people.

There are three files to download. Please download them [here](https://drive.google.com/file/d/1UA_TAMB8xBOszrRTorvX2-rH_iQy6b8Y/view?usp=sharing), [here](https://drive.google.com/file/d/1fgJRkI-NGBmhSExfW364yL7ab-1XKhDy/view?usp=sharing), and [here](https://drive.google.com/file/d/1QpcqGTZVpw5LoSsoSFkQUPHvKO9RU6HP/view?usp=sharing).

Afterwards, the following three files should be present in your working directory.

    ALL.chrY.phase3_integrated_v1b.20130502.genotypes.vcf.gz
    20130606_g1k.ped
    20131219.populations.tsv

The `.vcf.gz` file is genotyping data. The `.ped` and `.tsv` files are ancestry data.

## OakVar
If you are new to OakVar, please install it as explained in [the instruction](https://rkimoakbioinformatics.github.io/oakvar/install_system/). In brief, open a command-line interface with a Python environment and run

    pip install oakvar

to install OakVar and

    ov system setup

to set up OakVar in your system.

## Python libraries
Please install the following Python libraries.

    pip install scikit-learn
    pip install numpy
    pip install matplotlib
    pip install polars

## JupyterLab
I’ll use [JupyterLab](https://jupyter.org/) for interactive analysis and visualization. If you don’t have it yet, please install it according to [their instruction](https://jupyter.org/install). Then, launch it with

    jupyter-lab

On the JupyterLab, choose a Python 3 notebook. The codes from here are supposed to be entered on a JupyterLab notebook.

## OakVar annotation
Let’s load the chromosome Y data into an OakVar result database.

    !ov run ALL.chrY.phase3_integrated_v1b.20130502.genotypes.vcf.gz

This will perform basic annotation of the genotype data and write the result to `ALL.chrY.phase3_integrated_v1b.20130502.genotypes.vcf.gz.sqlite`.

If you are interested, the analysis result can be explored in a GUI with

    !ov gui ALL.chrY.phase3_integrated_v2b.20130502.genotypes.vcf.gz.sqlite

See [here](https://rkimoakbioinformatics.github.io/oakvar/tutorial/#visualize-annotated-variants) for how to use the GUI result viewer. Interrupt the kernel of JupyterLab to finish the viewer.

## Annotation database to arrays
As shown in the beginning of this post, we need `X` and `y` arrays to train and test classifiers with scikit-learn. `X` will be a 2D array of variants. `y` will be a 1D array of ancestry.

OakVar provides a method with which we can construct such `X` and `y` from genotyping data. Using the annotation result in the previous section,

    import oakvar as ov

    samples, uids, variants = ov.get_sample_uid_variant_arrays(
      "ALL.chrY.phase3_integrated_v2b.20130502.genotypes.vcf.sqlite"
    )

`ov.get_sample_uid_variant_arrays` returns three NumPy arrays. The first one (`samples`) is a 1D array of sample names.

    array(['HG00096', 'HG00101', 'HG00103', ..., 'NA21130', 'NA21133',
           'NA21135'], dtype='<U7')

The second one (`uids`) is a 1D array of the variant UIDs.

    array([    1,     2,     3, ..., 61868, 61869, 61870], dtype=uint32)

The third one (`variants`) is a 2D array of the presence of variants.

    array([[0., 0., 0., ..., 0., 0., 0.],
           [0., 0., 0., ..., 0., 0., 0.],
           [0., 0., 0., ..., 0., 0., 0.],
           ...,
           [0., 0., 0., ..., 0., 0., 0.],
           [0., 0., 0., ..., 0., 0., 0.],
           [0., 0., 0., ..., 0., 0., 0.]])

The relationship of the three arrays are: `samples` describes the rows of `variants` with the name of the sample of each row of `variants`, and `uids` describes the columns of `variants` with the variant UID of each column of `variants`.
We don’t have `X` and `y` yet. We still need some transformation to get them.

## y values
The 1000 Genomes project data is organized in several levels. The first level is `samples`, which are individual persons. Samples are grouped into populations, which are shown below.

    Japanese in Tokyo, Japan
    Punjabi in Lahore, Pakistan
    British in England and Scotland
    African Caribbean in Barbados
    ...

Populations are grouped into super populations and there are five super populations in the 1000 Genomes project data.

    AFR = African
    AMR = American
    EAS = East Asian
    EUR = European
    SAS = South Asian

The chromosome Y data is too small to predict populations. Thus, we will aim to predict super populations. The rows of `variants` array we retrieved in the previous section correspond to `samples`. We need an array of super populations which corresponds to `samples` array.

    import polars as pl

    df_p = pl.read_csv(
        "20131219.populations.tsv", 
        separator="\t"
    ).select(
        pl.col("Population Code", "Super Population")
    ).drop_nulls()
    df_s = pl.read_csv(
        "20130606_g1k.ped", 
        separator="\t", 
        infer_schema_length=1000
    ).select(
        pl.col("Individual ID", "Population")
    ).drop_nulls()
    df_s = df_s.join(
        df_p, 
        left_on="Population", 
        right_on="Population Code"
    )
    superpopulations = [
        df_s["Super Population"][np.where(df_s["Individual ID"] == v)[0]][0] 
        for v in samples
    ]

superpopulations will be a 1D array which corresponds to the rows of `variants`. This is our `y`.

For `X`, `variants` has too many columns (61,870 columns), allowing over-training. We use principal component analysis (PCA) to reduce its dimensionality to 2 columns.

    from sklearn import decomposition

    pca = decomposition.PCA(n_components=2)
    pca.fit(variants)
    X = pca.transform(variants)

We now have our `X` and `y` for training and testing ancestry classifiers.

    y                X
    EUR  -22.72643988 -22.48927295
    EUR   -8.68957706  13.9559764
    EUR  -22.78267228 -22.48553873
    ...

Let’s visualize this data.

    import matplotlib.pyplot as plt

    color_by_superpopulation = {
        "AFR": "#ff0000",
        "EAS": "#00ff00",
        "EUR": "#0000ff",
        "AMR": "#00ffff",
        "SAS": "#ff00ff",
    }
    colors = [color_by_superpopulation[v] for v in superpopulations]
    fig = plt.figure()
    ax = fig.add_subplot()
    ax.scatter(X[:, 0], X[:, 1], c=colors)
    plt.show()

![pca plot](https://miro.medium.com/v2/resize:fit:1108/format:webp/1*gYO4kq30VaqYyFVr_2X5_w.png)

Each dot is a sample, colored by the sample’s super population. Overall, Europeans (blue), East Asians (green), and Africans (red) make three extremities, and Americans (cyan) and South Asians (purple) connect these three extremities. However, European dots are not clearly separated from other super population dots. Meanwhile, East Asian and African dots are more clearly separated. This is understandable, because the European super population in the 1000 Genomes Project includes British, Spanish, Finnish, Italian, and people of Northern and Western European ancestry, so it is already quite diverse. We will see if trained classifiers will reflect this aspect.

## Training and testing classifiers
The first kind of classifiers we will test is K-nearest neighbor (k-NN) classifier.

    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.model_selection import train_test_split

    clf = KNeighborsClassifier()
    y = superpopulations
    X_train, X_test, y_train, y_test = train_test_split(X, y)
    y_pred = clf.fit(X_train, y_train).predict(X_test)

This classifier’s precision, accuracy, and F1 score are:

         Precision  F1 score
    AFR  0.924      0.912
    AMR  0.548      0.430
    EAS  0.962      0.971
    EUR  0.532      0.596
    SAS  0.838      0.844

    Accuracy: 0.773

Good performance with Africans and East Asians and lower performance with Europeans agree with what we saw in the PCA plot in the previous section.

The next is Random Forest classifier.

    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split

    clf = RandomForestClassifier(n_estimators=10)
    y = superpopulations
    X_train, X_test, y_train, y_test = train_test_split(X, y)
    y_pred = clf.fit(X_train, y_train).predict(X_test)

This classifier’s precision, accuracy, and F1 score are:

         Precision  F1 score
    AFR  0.944      0.944
    AMR  0.478      0.543
    EAS  0.981      0.981
    EUR  0.642      0.602
    SAS  0.924      0.897

    Accuracy: 0.825

This one performs slightly better than the k-NN one, but it has the same characteristic that it performs better with Africans and East Asians than with Europeans.

## Epilog
`get_sample_uid_variant_arrays` can be used to selectively retrieve `samples` and `variants`.

    samples, uids, variants = get_sample_uid_variant_arrays(
        "ALL.chrY.phase3_integrated_v2b.20130502.genotypes.vcf.sqlite",
        variant_criteria="gnomad3__af > 0.01"
    )

will return `variants` the gnomAD allele frequency of which is greater than 1%, if the input file was annotated with gnomad3 OakVar module as in

    ov run ALL.chrY.phase3_integrated_v2b.20130502.genotypes.vcf.sqlite -a gnomad3

`samples` and `uids` will be adjusted accordingly as well. Any OakVar module can be used for such filtration.

This was a quick demonstration of OakVar’s ability to interface genomic data and scikit-learn, a machine learning framework. Please stay tuned for future publications for more examples.
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
# Third-party Software in OakVar

OakVar uses third party software. Their names and license are listed below.

| Name | License | Note |
|------|---------|------|
| liftover | MIT | |
| aiosqlite | MIT | |
| oyaml | MIT | |
| gdown | MIT | |
| duckdb | MIT | |
| rich | MIT | |
| pyjwt | MIT | |
| polars | MIT | |
| connectorx | MIT | |
| aiohttp-cors | Apache 2.0 | |
| requests | Apache 2.0 | |
| requests-toolbelt | Apache 2.0 | |
| aiohttp | Apache 2.0 | |
| pyarrow | Apache 2.0 | |
| intervaltree | Apache 2.0 | |
| markdown | BSD | |
| nest-asyncio | BSD | |
| psutil | BSD | |
| python-dateutil | BSD | |
| download | BSD | |
| packaging | BSD | |
| mpmath | BSD | |
| multiprocess | BSD-3-Clause | |
| chardet | GNU Lesser General Public License | Unlike GPL, proprietry software developed with this library does not need to disclose its source code. |
| twobitreader | Artistic License 2.0 | The Artistic License 2.0 is an open-source license with no copyleft similar to the MIT license. Proprietary software developed with this library as a library does not need to disclose its source code.|
| Pillow | Historical Permission Notice and Disclaimer | This license is functionally identical to BSD and MIT except the option of promoting with the author's name. Proprietary software developed with this library does not need to disclose its source code.|
# Tips

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
# Tutorial

#### Installation and setup

Install OakVar and setup following [this instruction](install_system.md).

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

This will create an example input file, `oakvar_example.vcf`, in the current directory.

#### Run an annotation job

Now, we annotate the example input file with ClinVar and then create a result VCF file with annotated variants. `-a` option controls annotation sources and `-t` option report formats.

    ov run oakvar_example.vcf -a clinvar -t vcf

This will create `exampleinuput.vcf` which will have the input variants annotated with ClinVar. Additionally, `oakvar_example.vcf.sqlite` will be created. This file is a SQLite database file with annotated variants.

#### Examine the annotated variants

Let's examine the annotated variants in the previous step. `ov report` is used to show or generate the output of annotated variants.

    ov report oakvar_example.vcf.sqlite -t stdout

This will print out the annotated variants to the screen. `-t stdout` tells `ov report` to use `stdoutreporter` module, which is a reporter module and will receive annotated variants, variant by variant, from `ov report` and convert it to the standard output of the terminal.

#### Generate an Excel report of annotated variants

There are more reporter modules. `excelreporter`, an Excel format reporting module is included in OakVar by default. `-s` option defines the file name of the report file except the extension.

    ov report oakvar_example.vcf.sqlite -t excel -s annotated

This will generate `annotated.xlsx` file with annotated variants.

#### Visualize annotated variants

OakVar comes with a couple of embedded web applications, for graphical user interface-based operation of OakVar. Let's explore the annotated variants on a web browser.

    ov gui oakvar_example.vcf.sqlite

This will launch an interactive result viewer for the analysis job done in the previous section.

![interactive result viewer summary tab](images/ov_summary_exampleinputsqlite.png)

Click the sidebar and look around the tables with annotated variants and the widgets in each option. *Filter* option on the sidebar has a customizable filter section.

![interactive result viewer filter tab](images/ov_filter_example.png)

Click the brown `+` button at the left corner to add and set up filter criteria, and click `Apply` button to load filtered variants.

`ov gui` will launch a graphical user interface for managing analysis jobs and modules. 

![job submission page](images/ov_results.png)

Click `Manually enter variant instead` button followed by `Try an example` to use an example input and click `Annotate` button to run an annotation job. Optional reporters such as `VCF Reporter`,`Text Reporter` and `Excel Reporter` can be run by selecting the respective option on the right side. Additionally, modules can be selected below. The new job will show on the results option. 

![example analysis page](images/ov_analyze_example.png)

As seen below, `ClinVar` and `Gene Ontonogy` modules are available to run on the example job. 

![example analysis page](images/ov_analyze_module.png)


Installing and uninstalling modules can be managed on `Store` tab.

![web store](images/ov_gui_store.png)

# VCF to VCF Mode

With OakVar v2.5.0 and later, a fast-track annotation workflow, `vcf2vcf`, is available. The speed-up by this workflow can be an order of magnitude compared to previous versions, depending on the number of samples. For example, mapping the variants in the chromosome 20 of the 1000 Genomes Project data took about 10 minutes with --vcf2vcf in our test system. With ClinVar annotation added, about 15 minutes. The condition to use this workflow is:

- Input file format is Variant Call Format (VCF).
- Output file format is also VCF.
- Annotation SQLite database files are not needed.

To use `vcf2vcf`, just add `--vcf2vcf` to `ov run`. The output format will be always VCF, so `-t` option is not necessary. For example,

    ov run input.vcf --vcf2vcf -a clinvar

will read `input.vcf` and generate `input.vcf.vcf` with ClinVar annotation as well as GENCODE gene mapping.

    ov run input.vcf --vcf2vcf -a clinvar -n annotated

will generate `annotated.vcf` as output, due to `-n` option.
