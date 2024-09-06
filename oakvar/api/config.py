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
