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
from typing import Dict
from pathlib import Path


def setup(
    clean: bool = False,
    refresh_db: bool = False,
    clean_cache_files: bool = False,
    setup_file: Optional[Union[Path, str]] = None,
    email: str = "",
    pw: str = "",
    create_account: bool = False,
    custom_system_conf: Optional[Dict] = None,
    publish_time: str = "",
    outer=None,
    system_worker_state=None,
    sg_mode: bool = False,
):
    """setup.

    Args:
        clean (bool): Perform clean installation. Installed modules and analysis results are not erased.
        refresh_db (bool): Refreshes store server data.
        clean_cache_files (bool): Cleans store cache files.
        setup_file (Optional[Union[Path, str]]): Path to a custom system configuration file. If given, the system configuraton from this file will be used instead of default system configuratoin values.
        email (Optional[str]): OakVar store account Email
        pw (Optional[str]): OakVar store account password
        custom_system_conf (Optional[Dict]): Custom system configuration as a Dict
        publish_time (str): publish_time
        system_worker_state:
        outer:
    """
    from ..lib.system import setup_system

    if isinstance(setup_file, str):
        setup_file = Path(setup_file)
    return setup_system(
        clean=clean,
        refresh_db=refresh_db,
        clean_cache_files=clean_cache_files,
        setup_file=setup_file,
        email=email,
        pw=pw,
        create_account=create_account,
        publish_time=publish_time,
        custom_system_conf=custom_system_conf,
        outer=outer,
        system_worker_state=system_worker_state,
        sg_mode=sg_mode
    )


def md(directory: Optional[Union[Path, str]] = None) -> Optional[Path]:
    """Gets or sets OakVar modules directory.

    Args:
        directory (Optional[Union[Path, str]]): Path to a new OakVar modules directory. If given, OakVar modules directory will be set to this value.

    Returns:
        Path of the new or existing OakVar modules directory. `None` if `directory` is not given and an OakVar modules directory is not defined in the system configuration.
    """
    from ..lib.system import set_modules_dir, get_modules_dir

    if directory:
        set_modules_dir(directory)
        return Path(directory)
    else:
        d = get_modules_dir()
        return d


def check(outer=None) -> bool:
    """Performs OakVar system checkup.

    Args:
        outer:

    Returns:
        True if all tests passed. False if not.
    """
    from ..lib.system import check

    ret = check(outer=outer)
    return ret
