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
