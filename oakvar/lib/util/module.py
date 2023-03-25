from typing import Optional
from typing import Type
from pathlib import Path
from ..base.converter import BaseConverter
from ..base.mapper import BaseMapper
from ..base.annotator import BaseAnnotator


def get_converter(name: str, *args, **kwargs) -> Optional[Type]:
    from .util import load_class
    from ..module.local import get_module_py

    cls = load_class(get_module_py(name, module_type="converter"))
    if not issubclass(cls, BaseConverter):
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


def get_annotator(name: str, *args, **kwargs) -> BaseAnnotator:
    from .util import load_class
    from ..module.local import get_module_py

    cls = load_class(get_module_py(name, module_type="annotator"))
    if not issubclass(cls, BaseAnnotator):
        raise ValueError(f"{name} is not an annotator module.")
    module = cls(*args, name=name, **kwargs)
    return module


def get_mapper(name: str, *args, **kwargs) -> BaseMapper:
    from .util import load_class
    from ..module.local import get_module_py
    from ..exceptions import ModuleNotExist

    cls = load_class(get_module_py(name, module_type="mapper"))
    if not cls:
        raise ModuleNotExist(module_name=name)
    if not issubclass(cls, BaseMapper):
        raise ValueError(f"{name} is not a mapper class.")
    module = cls(*args, name=name, **kwargs)
    return module
