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
from pathlib import Path


def exampleinput(directory: Optional[str] = ".", outer=None) -> Optional[Path]:
    """exampleinput.

    Args:
        directory (Optional[str]): Directory to create the example input file in
        outer:

    Returns:
        `None` if the given directory does not exist. Path to the created example input file if successful.
    """
    from ..lib.util.admin_util import fn_new_exampleinput

    if not directory:
        return None
    ret = fn_new_exampleinput(directory)
    if outer:
        outer.write(ret)
    return ret


def module(module_name: str, module_type: str, outer=None) -> Optional[Path]:
    """module.

    Args:
        module_name (str): Module name
        module_type (str): Module type

    Returns:
        `None` if not successful. Directory of the created module if successful.
    """
    from ..lib.util.admin_util import create_new_module
    from ..lib.module.local import get_local_module_info
    from ..lib.exceptions import ArgumentError

    if not module_name:
        e = ArgumentError("module_name should not be empty.")
        e.traceback = False
        raise e
    if not module_type:
        e = ArgumentError("module_type should not be empty.")
        e.traceback = False
        raise e
    ret = create_new_module(module_name, module_type, outer=outer)
    if not ret:
        return
    module_info = get_local_module_info(module_name)
    if module_info is not None:
        return module_info.directory
    else:
        return None
