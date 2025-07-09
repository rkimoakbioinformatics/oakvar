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

