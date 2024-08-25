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

