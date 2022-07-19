# env keys
env_key_prefix = "OV_"

# Directories
custom_modules_dir = None
conf_dir_name = "conf"
modules_dir_name = "modules"
jobs_dir_name = "jobs"
log_dir_name = "logs"
cache_dirs = ["readme", "logo", "conf"]

#
# file names
#
sys_conf_fname = "system.yml"
user_conf_fname = "oakvar.yml"
user_dir_fname = ".oakvar"
live_conf_fname = "live.yml"

#
# system conf keys
#
sys_conf_path_key = "sys_conf_path"
user_conf_path_key = "user_conf_path"

root_dir_key = "root_dir"
conf_dir_key = "conf_dir"
jobs_dir_key = "jobs_dir"
log_dir_key = "log_dir"
modules_dir_key = "modules_dir"
package_dir_key = "package_dir"

base_modules_key = "base_modules"
max_num_concurrent_annotators_per_job_key = "max_num_concurrent_annotators_per_job"
default_assembly_key = "default_assembly"

#
# default system conf values
#
default_num_input_line_warning_cutoff = 25000
default_gui_input_size_limit = 500
default_max_num_concurrent_jobs = 4
default_max_num_concurrent_annotators_per_job = 1
default_multicore_mapper_mode = True
default_gui_port = 8080
default_gui_port_ssl = 8443
default_assembly = "hg38"
default_postaggregator_names = ["tagsampler", "casecontrol", "varmeta", "vcfinfo"]

#
# oc
#
oc_system_conf_fname = "cravat-system.yml"
oc_cravat_conf_fname = "cravat.yml"
