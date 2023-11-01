# OakVar Dual License
# 
# Copyright (c) 2023 Oak Bioinformatics, LLC
# 
# This program is dual licensed under the Affero GPL-3.0 or later for 
# non-commercial and open source use, and under a commercial license, 
# which is available for purchase, for closed-source or commercial use.
# 
# For the commercial use, please contact Oak Bioinformatics, LLC 
# for obtaining such a license. OakVar commercial license does not impose 
# the Affero GPL open-source licensing terms, conditions, and limitations. 
# To obtain a commercial-use license of OakVar, please visit our website at
# https://oakbioinformatics.com or contact us at info@oakbioinformatics.com 
# for more information.
# 
# ================
# OpenCRAVAT
# 
# MIT License
# 
# Copyright (c) 2021 KarchinLab
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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
