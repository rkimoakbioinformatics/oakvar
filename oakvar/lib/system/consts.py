#
# env keys
#
env_key_prefix = "OV_"

#
# Directories
#
conf_dir_name = "conf"
modules_dir_name = "modules"
jobs_dir_name = "jobs"
log_dir_name = "logs"
cache_dirs = ["readme", "logo", "conf"]
LIFTOVER_DIR_NAME = "liftover"

#
# file names
#
sys_conf_fname = "system.yml"
user_conf_fname = "oakvar.yml"
user_dir_fname = ".oakvar"

#
# system conf keys
#
sys_conf_path_key = "sys_conf_path"
root_dir_key = "root_dir"
conf_dir_key = "conf_dir"
jobs_dir_key = "jobs_dir"
log_dir_key = "log_dir"
modules_dir_key = "modules_dir"
package_dir_key = "package_dir"
LIFTOVER_DIR_KEY = "liftover_dir"
base_modules_key = "base_modules"
max_num_concurrent_annotators_per_job_key = "max_num_concurrent_annotators_per_job"
max_num_concurrent_modules_per_job_key = "max_num_concurrent_modules_per_job"
default_assembly_key = "default_assembly"
report_filter_max_num_cache_per_user_key = "report_filter_max_num_cache_per_user"

#
# default system conf values
#
DEFAULT_MAX_NUM_CONCURRENT_JOBS = 1
default_gui_port = 8080
default_gui_port_ssl = 8443
default_assembly = "hg38"
default_postaggregator_names = ["tagsampler", "vcfinfo"]
DEFAULT_REPORT_FILTER_MAX_NUM_CACHE_PER_USER = 20

#
# Server
#
DEFAULT_SERVER_DEFAULT_USERNAME = "default"
ADMIN_ROLE = "admin"
USER_ROLE = "user"
ADMIN_DB_FN = "server.sqlite"
