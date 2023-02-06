from multiprocessing.managers import DictProxy


class WebSocketHandlers:
    def __init__(
        self, system_worker_state=None, wss={}, system_message_last_ids={}, logger=None
    ):
        from .system_message_db import get_system_message_db_conn

        self.routes = []
        self.system_worker_state = system_worker_state
        self.wss = wss
        self.system_message_last_ids = system_message_last_ids
        self.logger = logger
        self.conn = get_system_message_db_conn()
        self.cursor = self.conn.cursor()
        self.add_routes()

    def add_routes(self):
        self.routes = []
        self.routes.append(["GET", "/ws", self.connect])

    async def connect(self, request):
        import asyncio
        from aiohttp.web import WebSocketResponse
        import concurrent.futures
        from uuid import uuid4
        from .consts import WS_COOKIE_KEY
        from .consts import SYSTEM_STATE_CONNECTION_KEY
        from .consts import SYSTEM_MSG_KEY
        from .system_message_db import get_last_msg_id

        assert self.system_worker_state is not None
        ws_id = request.cookies.get(WS_COOKIE_KEY)
        if ws_id and ws_id in self.wss:
            del self.wss[ws_id]
        ws_id = str(uuid4())
        ws = WebSocketResponse(timeout=60 * 60 * 24 * 365)
        self.wss[ws_id] = ws
        await ws.prepare(request)
        try:
            await ws.send_json(
                {SYSTEM_MSG_KEY: SYSTEM_STATE_CONNECTION_KEY, WS_COOKIE_KEY: ws_id}
            )
        except ConnectionResetError:
            raise
        except Exception as e:
            raise
        to_dels = []
        for ws_id in self.wss:
            ws_t = self.wss[ws_id]
            if ws_t.closed:
                to_dels.append(ws_id)
        for ws_id in to_dels:
            del self.wss[ws_id]
        last_msg_id = get_last_msg_id(self.conn)
        print(f"@ last_msg_id={last_msg_id}")
        while True:
            try:
                await asyncio.sleep(1)
                if ws.closed:
                    break
                last_msg_id = await self.process_system_worker_state(
                    ws=ws, last_msg_id=last_msg_id
                )
            except concurrent.futures._base.CancelledError:
                pass
            except ConnectionResetError:
                break
            except Exception as e:
                if self.logger:
                    self.logger.exception(e)
                break
        return ws

    async def process_setup_state(self, ws=None, last_msg_id=0):
        from .consts import SYSTEM_STATE_SETUP_KEY
        from .consts import SYSTEM_MSG_KEY
        from .consts import SYSTEM_MESSAGE_TABLE

        if ws is None or not self.system_worker_state:
            return last_msg_id
        self.cursor.execute(
            f"select uid, msg, dt from {SYSTEM_MESSAGE_TABLE} where uid > ?",
            (last_msg_id,),
        )
        ret = self.cursor.fetchall()
        if ret:
            print(f"@ last_msg_id={last_msg_id}")
            print(f"@ => ret={ret}")
            last_msg_id = max([v[0] for v in ret])
            data = []
            for row in ret:
                data.append({"msg": row[1], "dt": row[2]})
            await ws.send_json({SYSTEM_MSG_KEY: SYSTEM_STATE_SETUP_KEY, "msg": data})
        return last_msg_id

    async def process_install_state(self, ws=None):
        from .consts import SYSTEM_STATE_INSTALL_KEY

        if ws is None or not self.system_worker_state:
            return
        if SYSTEM_STATE_INSTALL_KEY not in self.system_worker_state:
            return
        install_datas = self.system_worker_state[SYSTEM_STATE_INSTALL_KEY]
        for _, data in install_datas.items():
            await ws.send_json(data)
        await self.delete_done_install_states()

    async def delete_done_install_states(self):
        from .consts import SYSTEM_STATE_INSTALL_KEY

        if SYSTEM_STATE_INSTALL_KEY not in self.system_worker_state:
            return
        install_datas: DictProxy = self.system_worker_state[SYSTEM_STATE_INSTALL_KEY]
        to_del = []
        for module_name, data in install_datas.items():
            if data["stage"] in ["finish", "error", "skip", "killed"]:
                to_del.append(module_name)
        for module_name in to_del:
            del install_datas[module_name]

    async def process_system_worker_state(self, ws=None, last_msg_id=0):
        if ws is None:
            return last_msg_id
        last_msg_id = await self.process_setup_state(ws=ws, last_msg_id=last_msg_id)
        # await self.process_install_state(ws=ws, last_msg_id=last_msg_id)
        return last_msg_id
