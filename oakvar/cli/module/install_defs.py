from typing import Optional
from ...lib.module import InstallProgressHandler


class InstallProgressStdout(InstallProgressHandler):
    def __init__(
        self,
        module_name: Optional[str] = None,
        module_version: Optional[str] = None,
        outer=None,
    ):
        super().__init__(
            module_name=module_name, module_version=module_version, outer=outer
        )
        self.system_worker_state = None

    def stage_start(self, stage):
        self.cur_stage = stage
        if self.outer:
            self.outer.write(self._stage_msg(stage))
