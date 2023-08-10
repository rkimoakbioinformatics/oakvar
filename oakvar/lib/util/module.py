from typing import Optional
from typing import Union
from typing import Type
from pathlib import Path
from ..base.converter import BaseConverter
from ..base.preparer import BasePreparer
from ..base.mapper import BaseMapper
from ..base.annotator import BaseAnnotator
from ..base.postaggregator import BasePostAggregator
from ..base.reporter import BaseReporter
from ..base.commonmodule import BaseCommonModule
from ..base.vcf2vcf import VCF2VCF


def get_converter(module_name, *args, **kwargs) -> BaseConverter:
    ModuleClass = get_module_class(module_name, module_type="converter")
    if not ModuleClass:
        raise ValueError(f"{module_name} was not found.")
    if not issubclass(ModuleClass, BaseConverter):
        raise ValueError(f"{ModuleClass} is not a converter class.")
    module = ModuleClass(*args, **kwargs)
    return module


def get_mapper(module_name, *args, **kwargs) -> BaseMapper:
    ModuleClass = get_module_class(module_name)
    if not ModuleClass:
        raise ValueError(f"{module_name} was not found.")
    if not issubclass(ModuleClass, BaseMapper):
        raise ValueError(f"{ModuleClass} is not a mapper class.")
    module = ModuleClass(*args, **kwargs)
    return module


def get_annotator(module_name, *args, **kwargs) -> BaseAnnotator:
    ModuleClass = get_module_class(module_name)
    if not ModuleClass:
        raise ValueError(f"{module_name} was not found.")
    if not issubclass(ModuleClass, BaseAnnotator):
        raise ValueError(f"{ModuleClass} is not an annotator class.")
    module = ModuleClass(*args, **kwargs)
    module.connect_db()
    module.setup()
    return module


def get_postaggregator(module_name, *args, **kwargs) -> BasePostAggregator:
    ModuleClass = get_module_class(module_name)
    if not ModuleClass:
        raise ValueError(f"{module_name} was not found.")
    if not issubclass(ModuleClass, BasePostAggregator):
        raise ValueError(f"{ModuleClass} is not an annotator class.")
    module = ModuleClass(*args, **kwargs)
    module.setup()
    return module


def get_reporter(module_name, *args, **kwargs) -> BaseReporter:
    ModuleClass = get_module_class(module_name)
    if not ModuleClass:
        raise ValueError(f"{module_name} was not found.")
    if not issubclass(ModuleClass, BaseReporter):
        raise ValueError(f"{ModuleClass} is not an annotator class.")
    print(f"@ args={args}, kwargs={kwargs}")
    module = ModuleClass(*args, **kwargs)
    module.setup()
    return module


def get_module_class(
    module_name, module_type: str = ""
) -> Union[
    Type[BaseConverter],
    Type[BasePreparer],
    Type[BaseMapper],
    Type[BaseAnnotator],
    Type[BasePostAggregator],
    Type[BaseReporter],
    Type[BaseCommonModule],
    Type[VCF2VCF],
]:
    from ..module.local import get_local_module_info
    from .util import load_class

    module_info = get_local_module_info(module_name, module_type=module_type)
    if module_info is None:
        raise ValueError(f"{module_name} does not exist.")
    ModuleClass = load_class(module_info.script_path)
    return ModuleClass


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
