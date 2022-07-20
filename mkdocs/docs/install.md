## Installation

    pip uninstall open-cravat # (if open-cravat is already installed)
    pip install oakvar
    ov system setup

## Setup

`ov system setup` will set up OakVar with sane defaults.

Setup process can be customized with a setup file or environment variables, which can be useful in automated deployment.

### Setup with a file

A setup file in yaml format can be used. System configuration fields which are missing in the setup file will be filled with sane defaults. Setup with a file with custom locations for modules and logs can be done as

    ov system setup -f setup.yaml

where setup.yaml is

    modules_dir: ~/oakvar_modules
    logs_dir: ~/oakvar_logs

### Setup with environment variables

All system configuration fields can be overridden with environment variables. To override a system config field, set the environment variable `OV_` + upper-cased field name to a desired value. For example, 

System configuration field | Environmental variable |
---------------------------|--------------|
sys_conf_path | OV_SYS_CONF_PATH |
modules_dir | OV_MODULES_DIR |
log_dir | OV_LOG_DIR |
jobs_dir | OV_JOBS_DIR |
conf_dir | OV_CONF_DIR |
gui_port | OV_GUI_PORT |

The custom setup in the previous section can be done using environmental variables as

    export OV_MODULES_DIR=~/oakvar_modules
    export OV_LOGS_DIR=~/oakvar_logs
    ov system setup

