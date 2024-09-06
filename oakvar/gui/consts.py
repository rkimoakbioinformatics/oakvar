# OakVar
#
# Copyright (c) 2024 Oak Bioinformatics, LLC
#
# All rights reserved.
#
# Do not distribute or use this software without obtaining
# a license from Oak Bioinformatics, LLC.
#
# Do not use this software to develop another software
# which competes with the products by Oak Bioinformatics, LLC,
# without obtaining a license for such use from Oak Bioinformatics, LLC.
#
# For personal use of non-commercial nature, you may use this software
# after registering with `ov store account create`.
#
# For research use of non-commercial nature, you may use this software
# after registering with `ov store account create`.
#
# For use by commercial entities, you must obtain a commercial license
# from Oak Bioinformatics, LLC. Please write to info@oakbioinformatics.com
# to obtain the commercial license.
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

DEFAULT_GUI_PORT = 8080
default_gui_port_ssl = 8443
DEFAULT_JOB_TABLE_PAGESIZE = 10
job_table_pagesize_key = "job_table_pagesize"
DEFAULT_RESULT_VIEWER_NUM_VAR_LIMIT_FOR_GENE_SUMMARY = 100000
result_viewer_num_var_limit_for_gene_summary_key = (
    "result_viewer_num_var_limit_for_gene_summary"
)
DEFAULT_RESULT_VIEWER_NUM_VAR_LIMIT_FOR_SUMMARY_WIDGET = 1000
result_viewer_num_var_limit_for_summary_widget_key = (
    "result_viewer_num_var_limit_for_summary_widget"
)
LOG_FN = "gui.log"
DEFAULT_PRIVATE_KEY = "default_private_key"
COOKIE_KEY = "oakvar_token"
WS_COOKIE_KEY = "ws_id"
SYSTEM_STATE_CONNECTION_KEY = "connection"
SYSTEM_STATE_SETUP_KEY = "setup"
SYSTEM_STATE_INSTALL_KEY = "install"
SYSTEM_STATE_INSTALL_QUEUE_KEY = "install_queue"
SYSTEM_MSG_KEY = "msg_kind"
SYSTEM_MESSAGE_DB_FNAME = "system_messages.sqlite"
SYSTEM_MESSAGE_TABLE = "system_messages"
SYSTEM_ERROR_TABLE = "system_errors"
INSTALL_KILL_SIGNAL = "kill_signal"
PORT_KEY = "port"
SYSCONF_PORT_KEY = "gui_port"
SYSCONF_SSL_PORT_KEY = "gui_port_ssl"
SYSCONF_HOST_KEY = "gui_host"
SYSCONF_SSL_HOST_KEY = "gui_host_ssl"
SSL_ENABELD_KEY = "ssl_enabled"
