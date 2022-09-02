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
