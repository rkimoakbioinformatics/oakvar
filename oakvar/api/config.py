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

from typing import Optional
from typing import Union


def user() -> Optional[dict]:
    """Gets user configuration.

    Returns:
        OakVar user configuration
    """
    from ..lib.util.admin_util import get_user_conf

    conf = get_user_conf()
    return conf


def system(
    key: Optional[str] = None, value: Optional[str] = None, type: str = "str"
) -> Optional[Union[str, int, float, dict]]:
    """Gets or sets system configuration.

    Args:
        key (Optional[str]): key
        value (Optional[str]): value
        type (Optional[str]): type

    Returns:
        With no argument, system configuration is returned as a dict. With only key given, the system configuration value for the key is returned. With key, value, and type given, system configuration is updated with the value of the type for the key. If type is omitted, str is assumed.
    """
    from ..lib.system import get_sys_conf_value
    from ..lib.system import set_sys_conf_value
    from ..lib.system import get_system_conf

    if key:
        if value:
            if not type:
                type = "str"
            set_sys_conf_value(key, value, type)
            return value
        else:
            v = get_sys_conf_value(key)
            return v
    else:
        conf = get_system_conf()
        return conf
