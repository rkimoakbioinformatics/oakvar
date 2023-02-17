## Installation

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

### Clean setup

If you experience any problem and want to do clean installation of OakVar, `ov system setup --clean` provides such clean installation. It will reset the system and user configuration files. `--clean` still will not delete `modules`, `jobs`, `logs`, and `conf` folders. `modules` have downloaded modules and users should manually delete this folder if they really want, because this folder can take a lot of time to recreate. `jobs`, `logs`, and `conf` folders have just contents.

