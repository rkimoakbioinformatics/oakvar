from typing import Optional
from typing import Type
from pathlib import Path


def get_converter(name: str, *args, **kwargs) -> Optional[Type]:
    from .util import load_class
    from ..module.local import get_module_py

    cls = load_class(get_module_py(name, module_type="converter"))
    if not cls:
        return None
    converter = cls(*args, name=name, **kwargs)
    if not hasattr(converter, "format_name"):
        converter.format_name = name.split("-")[0]
    return converter


def get_converter_for_input_file(input_file: Optional[Path]) -> Optional[Type]:
    from ..base.converter import BaseConverter
    from ..module.local import get_module_names_for_module_type

    module_names = get_module_names_for_module_type("converter")
    for module_name in module_names:
        module: Optional[BaseConverter] = get_converter(module_name)
        if not module:
            continue
        if module.check_format(input_file):
            return module
    return None
