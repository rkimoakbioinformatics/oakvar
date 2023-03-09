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
        except Exception:
            raise
        to_dels = []
        for ws_id in self.wss:
            ws_t = self.wss[ws_id]
            if ws_t.closed:
                to_dels.append(ws_id)
        for ws_id in to_dels:
            del self.wss[ws_id]
        last_msg_id = get_last_msg_id(self.conn)
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
        from .consts import SYSTEM_STATE_INSTALL_KEY
        from .consts import SYSTEM_MSG_KEY
        from .consts import SYSTEM_MESSAGE_TABLE

        if ws is None or not self.system_worker_state:
            return last_msg_id
        self.cursor.execute(
            f"select uid, kind, msg, dt from {SYSTEM_MESSAGE_TABLE} where uid > ?",
            (last_msg_id,),
        )
        ret = self.cursor.fetchall()
        if ret:
            last_msg_id = max([v[0] for v in ret])
            setup_items = []
            install_items = []
            for row in ret:
                kind = row[1]
                if kind == "setup":
                    setup_items.append({"kind": kind, "msg": row[2], "dt": row[3]})
                elif kind == "install":
                    install_items.append({"kind": kind, "msg": row[2], "dt": row[3]})
                else:
                    setup_items.append({"kind": kind, "msg": row[2], "dt": row[3]})
            if setup_items:
                await ws.send_json(
                    {SYSTEM_MSG_KEY: SYSTEM_STATE_SETUP_KEY, "items": setup_items}
                )
            if install_items:
                await ws.send_json(
                    {SYSTEM_MSG_KEY: SYSTEM_STATE_INSTALL_KEY, "items": install_items}
                )
        return last_msg_id

    async def process_system_worker_state(self, ws=None, last_msg_id=0):
        if ws is None:
            return last_msg_id
        last_msg_id = await self.process_setup_state(ws=ws, last_msg_id=last_msg_id)
        return last_msg_id
