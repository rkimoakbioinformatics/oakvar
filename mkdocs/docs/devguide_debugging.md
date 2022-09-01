### Entrypoints

| Command | Entrypoint |
|----------|-----------------|
| ov      | oakvar/\_\_main\_\_.py |
| ov run | oakvar/cli/run.py|
| ov report | oakvar/cli/report.py |
| ov gui | oakvar/cli/gui.py|

oakvar/\_\_main\_\_.py is intentional, to make `python -m oakvar` style of use possible.

### Base classes

OakVar modules inherit one of OakVar base module classes. Converters, mappers, annotators, postaggregators, and reporters have different base module classes.

| Type | Module | Class |
|----------|-----------------|-----------|
| converter | oakvar/base/converter.py | BaseConverter |
| mapper | oakvar/base/mapper.py | BaseMapper |
| annotator | oakvar/base/annotator.py | BaseAnnotator |
| postaggregator | oakvar/base/postaggregator.py | BasePostAggregator |
| reporter | oakvar/cli/report.py | BaseReporter |
| common | oakvar/base/commonmodule.py | BaseCommonModule |

To develop a new OakVar module, it should inherit one of these base classes. For example, an annotator module's class definition should be:

```
from oakvar import BaseAnnotator

class Annotator(BaseAnnotator):
```

