from typing import Optional
from multiprocessing.managers import ListProxy
from multiprocessing.managers import DictProxy
from ..module import InstallProgressHandler

def system_queue_worker(system_queue: ListProxy, system_worker_state: Optional[DictProxy], local_modules_changed):
    from time import sleep
    from ..module import install_module
    from ..system import setup_system
    from ..exceptions import ModuleToSkipInstallation
    from .consts import SYSTEM_STATE_SETUP_KEY
    from .consts import SYSTEM_MSG_KEY

    while True:
        try:
            sleep(1)
            if not system_queue:
                continue
            data = system_queue[0]
            work_type = data.get("work_type")
            system_queue.pop(0)
            if work_type == "setup":
                args = data.get("args")
                args[SYSTEM_MSG_KEY] = SYSTEM_STATE_SETUP_KEY
                setup_system(args=args)
            elif work_type == "install_module":
                module_name = data["module"]
                module_version = data["version"]
                initialize_system_worker_state_for_install(system_worker_state, module_name=module_name, module_version=module_version)
                stage_handler = InstallProgressMpDict(
                    module_name=module_name, module_version=module_version, system_worker_state=system_worker_state, quiet=False
                )
                try:
                    install_module(
                        module_name,
                        version=module_version,
                        stage_handler=stage_handler,
                        args={"overwrite": True},
                        fresh=True,
                    )
                    #unqueue(module_name, system_queue)
                    local_modules_changed.set()
                except ModuleToSkipInstallation:
                    #unqueue(module_name, system_queue)
                    stage_handler.stage_start("skip")
                except:
                    #unqueue(module_name, system_queue)
                    stage_handler.stage_start("error")
                    raise
        except KeyboardInterrupt:
            break
        except Exception as _:
            import traceback
            traceback.print_exc()
            local_modules_changed.set()

def unqueue(module_name: Optional[str], system_queue):
    if not system_queue or not module_name:
        return
    data_to_del = None
    for data in system_queue:
        if data.get("module") == module_name:
            data_to_del = data
            break
    if data_to_del:
        system_queue.remove(data_to_del)

class InstallProgressMpDict(InstallProgressHandler):
    def __init__(self, module_name=None, module_version=None, system_worker_state=None, quiet=True):
        super().__init__(module_name, module_version)
        self.module_name = module_name
        self.module_version = module_version
        self.system_worker_state = system_worker_state
        self.quiet = quiet

    def _reset_progress(self, update_time=False):
        from time import time
        from .consts import SYSTEM_STATE_INSTALL_KEY
        module_data = self.system_worker_state[SYSTEM_STATE_INSTALL_KEY][self.module_name]
        module_data["cur_chunk"] = 0
        module_data["cur_size"] = 0
        module_data["total_size"] = 0
        if update_time:
            module_data["update_time"] = time()
        self.system_worker_state[SYSTEM_STATE_INSTALL_KEY][self.module_name] = module_data

    def stage_start(self, stage):
        from ..util.util import quiet_print
        from .consts import SYSTEM_STATE_INSTALL_KEY

        self.cur_stage = stage
        msg = self._stage_msg(self.cur_stage)
        initialize_system_worker_state_for_install(self.system_worker_state, module_name=self.module_name)
        module_data = self.system_worker_state[SYSTEM_STATE_INSTALL_KEY][self.module_name]
        module_data["stage"] = [self.cur_stage]
        module_data["message"].append(self._stage_msg(self.cur_stage))
        module_data["kill_signal"] = False
        self.system_worker_state[SYSTEM_STATE_INSTALL_KEY][self.module_name] = module_data
        self._reset_progress(update_time=True)
        quiet_print(msg, {"quiet": self.quiet})


def initialize_system_worker_state_for_install(system_worker_state: Optional[DictProxy], module_name="", module_version=""):
    from time import time
    from .consts import SYSTEM_STATE_INSTALL_KEY
    from .consts import SYSTEM_MSG_KEY
    if system_worker_state is None:
        return
    d = {}
    d[SYSTEM_MSG_KEY] = SYSTEM_STATE_INSTALL_KEY
    d["stage"] = ""
    d["message"] = []
    d["module_name"] = module_name
    d["module_version"] = module_version
    d["cur_chunk"] = 0
    d["total_chunk"] = 0
    d["cur_size"] = 0
    d["total_size"] = 0
    d["update_time"] = time()
    d["kill"] = False
    system_worker_state[SYSTEM_STATE_INSTALL_KEY][module_name] = d

