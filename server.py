import random
from time import sleep

import pytz
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from db import DB, Chat
from utils import is_now_between_range_in_timezone


class ConnectionManager:

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_text(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def send_json(self, data: dict, websocket: WebSocket):
        await websocket.send_json(data)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


class Server:

    def __init__(self):
        self.__app = FastAPI()
        self.__manager = ConnectionManager()
        self.__db = DB()
        self.__init_app()

    def __init_app(self):
        app: FastAPI = self.__app

        @app.websocket("/ws/{client_id}")
        async def websocket_endpoint(websocket: WebSocket, client_id: int):
            await self.__manager.connect(websocket)
            chat = self.__db.get_chat(client_id)

            # if chat is not in db, create a new chat
            if not chat:
                timezone = None
                data = await websocket.receive()
                if data["type"] == 'websocket.receive':
                    timezone = data["text"]

                # check if timezone is valid
                try:
                    pytz.timezone(timezone)
                except pytz.exceptions.UnknownTimeZoneError:
                    await self.__manager.send_text("Invalid timezone",
                                                   websocket)
                    await websocket.close()
                    return

                chat = self.__db.create_chat(client_id, timezone)

            # handle messages
            try:
                while True:
                    data = await websocket.receive()
                    if data["type"] == 'websocket.receive':
                        if data["text"]:
                            await self.__handle_text_message(
                                websocket, data["text"], chat)
                        elif data["bytes"]:
                            await self.__handle_multimedia_message(data["bytes"]
                                                                   )

                    elif data["type"] == 'websocket.disconnect':
                        break
            except WebSocketDisconnect:
                self.__manager.disconnect(websocket)

    async def __handle_text_message(self, ws: WebSocket, message: str,
                                    chat: Chat):
        sleep(random.uniform(0, 1))
        if not is_now_between_range_in_timezone("08:00", "23:59",
                                                chat.timezone):
            return
        await self.__manager.send_text("Saved: %s" % message, ws)
        self.__db.create_message(chat.id, message)

    async def __handle_multimedia_message(self, ws: WebSocket, message: bytes):
        # _todo: handle multimedia message
        pass

    def start(self):
        uvicorn.run(self.__app,
                    host="0.0.0.0",
                    port=8000,
                    ws_ping_interval=10,
                    ws_ping_timeout=2)


if __name__ == "__main__":
    server = Server()
    server.start()
