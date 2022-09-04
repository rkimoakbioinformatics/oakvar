## Installation

OakVar and open-cravat share the same package name, thus if your system already have open-cravat, then for oakvar to properly function, open-cravat should be uninstalled first.

    pip uninstall open-cravat

Then, install OakVar.

    pip install oakvar

Then, set up OakVar.

    ov system setup

## Setup

`ov system setup` will set up OakVar with sane defaults.

Setup process can be customized with a setup file or environment variables, which can be useful in automated deployment.

### Clean setup

`ov system setup --clean` provides clean installation. It will reset the system and user configuration files. --clean still do not delete `modules`, `jobs`, `logs`, and `conf` folders. The system conf file is already reset with `--clean` and the other files in `conf` are just content. What are in `jobs` and `logs` are also just content. `modules` have downloaded modules and users should manually delete this folder if they really want, because this folder can take a lot of time to recreate and also, there are users who keep this folder in a USB drive or something and move it around, while installing and deleting oakvar.

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

