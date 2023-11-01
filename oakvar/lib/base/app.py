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

from typing import Dict
from typing import Any

class BaseApp:
    def __init__(self, *args, module_name: str="", **kwargs):
        import sys
        from pathlib import Path
        from ..exceptions import ModuleLoadingError
        from ..module.local import get_module_conf

        _ = args
        _ = kwargs
        if module_name:
            self.module_name = module_name
        else:
            main_fpath = Path(sys.modules[self.__class__.__module__].__file__ or "")
            self.module_name = main_fpath.stem
        if not self.module_name:
            raise ModuleLoadingError(msg=f"App ({self.__class__.__name__}) could not be loaded.")
        self.conf: Dict[str, Any] = get_module_conf(self.module_name, module_type="app") or {}
