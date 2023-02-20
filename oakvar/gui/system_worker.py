from typing import Optional
from multiprocessing.managers import ListProxy
from multiprocessing.managers import DictProxy
from ..lib.module import InstallProgressHandler


def system_queue_worker(
    system_queue: ListProxy,
    system_worker_state: Optional[DictProxy],
    local_modules_changed,
    manager,
):
    from time import sleep
    import traceback
    from ..lib.module import install_module
    from ..lib.system import setup_system
    from ..lib.exceptions import ModuleToSkipInstallation

    # from .consts import SYSTEM_STATE_SETUP_KEY
    # from .consts import SYSTEM_MSG_KEY
    from .util import GuiOuter

    setup_outer = GuiOuter(kind="setup")
    install_outer = GuiOuter(kind="install")
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
                # args[SYSTEM_MSG_KEY] = SYSTEM_STATE_SETUP_KEY
                try:
                    setup_system(outer=setup_outer, **args)
                except Exception as e:
                    setup_outer.error(e)
            elif work_type == "install_module":
                module_name = data["module"]
                module_version = data["version"]
                stage_handler = InstallProgressMpDict(
                    manager,
                    module_name=module_name,
                    module_version=module_version,
                    system_worker_state=system_worker_state,
                    outer=install_outer,
                )
                try:
                    install_module(
                        module_name,
                        version=module_version,
                        stage_handler=stage_handler,
                        overwrite=True,
                        fresh=True,
                        outer=install_outer,
                    )
                    if system_worker_state:
                        remove_module_from_system_worker(
                            system_worker_state, module_name
                        )
                    # unqueue(module_name, system_queue)
                    local_modules_changed.set()
                    install_outer.write(f"finished:{module_name}::")
                except ModuleToSkipInstallation:
                    # unqueue(module_name, system_queue)
                    stage_handler.stage_start("skip")
                except Exception as e:
                    # unqueue(module_name, system_queue)
                    local_modules_changed.set()
                    stage_handler.stage_start("error")
                    exc_str = traceback.format_exc()
                    install_outer.error(exc_str)
        except KeyboardInterrupt:
            break


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
    def __init__(
        self,
        manager,
        module_name=None,
        module_version=None,
        system_worker_state=None,
        outer=None,
    ):
        super().__init__(module_name, module_version, outer)
        self.module_name = module_name
        self.module_version = module_version
        self.system_worker_state = system_worker_state
        self.manager = manager

    def _reset_progress(self, update_time=False):
        from time import time
        from .consts import SYSTEM_STATE_INSTALL_KEY

        module_data = self.system_worker_state[SYSTEM_STATE_INSTALL_KEY][
            self.module_name
        ]
        module_data["cur_size"] = 0
        module_data["total_size"] = 0
        if update_time:
            module_data["update_time"] = time()
        self.system_worker_state[SYSTEM_STATE_INSTALL_KEY][
            self.module_name
        ] = module_data

    def _stage_msg(self, stage):
        if stage is None or stage == "":
            return ""
        elif stage == "start":
            return f"start:{self.module_name}::"
        elif stage == "download_code":
            return f"download_code:{self.module_name}::"
        elif stage == "extract_code":
            return f"extract_code:{self.module_name}::"
        elif stage == "verify_code":
            return f"verify_code:{self.module_name}::"
        elif stage == "download_data":
            return f"download_data:{self.module_name}::"
        elif stage == "extract_data":
            return f"extract_data:{self.module_name}::"
        elif stage == "verify_data":
            return f"verify_data:{self.module_name}::"
        elif stage == "finish":
            return f"finish:{self.module_name}::"
        elif stage == "killed":
            return f"killed:{self.module_name}::"
        elif stage == "Unqueued":
            return f"unqueued:{self.module_name}::"
        else:
            return f"{stage}:{self.module_name}::"

    def stage_start(self, stage):
        from .consts import SYSTEM_STATE_INSTALL_KEY

        self.cur_stage = stage
        msg = self._stage_msg(self.cur_stage)
        if self.module_name not in self.system_worker_state[SYSTEM_STATE_INSTALL_KEY]:
            return
        module_data = self.system_worker_state[SYSTEM_STATE_INSTALL_KEY][
            self.module_name
        ]
        module_data["stage"] = [self.cur_stage]
        module_data["kill_signal"] = False
        self.system_worker_state[SYSTEM_STATE_INSTALL_KEY][
            self.module_name
        ] = module_data
        self._reset_progress(update_time=True)
        if self.outer:
            self.outer.write(msg)


def remove_module_from_system_worker(system_worker_state: DictProxy, module_name: str):
    from .consts import SYSTEM_STATE_INSTALL_KEY
    from .consts import SYSTEM_STATE_INSTALL_QUEUE_KEY

    if module_name in system_worker_state[SYSTEM_STATE_INSTALL_KEY]:
        del system_worker_state[SYSTEM_STATE_INSTALL_KEY][module_name]
    if module_name in system_worker_state[SYSTEM_STATE_INSTALL_QUEUE_KEY]:
        system_worker_state[SYSTEM_STATE_INSTALL_QUEUE_KEY].remove(module_name)
