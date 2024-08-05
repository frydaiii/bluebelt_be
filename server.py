import pickle
from time import sleep

import pytz
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from db import DB, Chat, Message
from utils import is_now_between_range_in_timezone
from typing import List
from fastapi import Query


class ConnectionManager:

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> bool:
        if len(self.active_connections) >= 50:
            await websocket.close()
            return False
        await websocket.accept()
        self.active_connections.append(websocket)
        return True

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
        """
        Initialize the FastAPI app with routes and websocket endpoint.
        """
        app: FastAPI = self.__app

        @app.websocket("/ws/{client_id}")
        async def websocket_endpoint(websocket: WebSocket, client_id: int):
            """
            Handle websocket connections from clients. Each client is identified
            by a unique client_id. Please note that the client must send its timezone
            as the first message after connecting.
            """
            ok = await self.__manager.connect(websocket)
            if not ok:
                return
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
            bytes_left = -1  # number of bytes left to receive in multimedia message
            filename = None  # filename of multimedia message
            try:
                while True:
                    data = await websocket.receive()
                    if data["type"] == 'websocket.receive':
                        if "text" in data:
                            await self.__handle_text_message(
                                websocket, data["text"], chat)
                        elif "bytes" in data:
                            if bytes_left == -1:  # new multimedia message
                                bytes_left, filename = self.__parse_metadata(
                                    data["bytes"], chat.timezone)
                            elif bytes_left > 0:
                                bytes_left = await self.__handle_multimedia_message(
                                    websocket, data["bytes"], filename,
                                    bytes_left, chat)
                                if bytes_left == 0:
                                    bytes_left = -1  # reset

                    elif data["type"] == 'websocket.disconnect':
                        break
            except WebSocketDisconnect:
                self.__manager.disconnect(websocket)

        @app.get("/messages")
        async def get_messages(chat_id: int,
                               limit: int = Query(10, ge=1, le=100),
                               offset: int = Query(0, ge=0)):
            """
            Retrieve messages for a specific chat with pagination using limit and offset.
            """
            messages = self.__db.get_messages(chat_id,
                                              limit=limit,
                                              offset=offset)
            return messages

    async def __handle_text_message(self, ws: WebSocket, message: str,
                                    chat: Chat):
        """
        Handle text message from client if it is in the valid time range.
        """
        if not is_now_between_range_in_timezone("05:00", "23:59",
                                                chat.timezone):
            self.__db.create_message(chat.id, message, Message.Status.UNSUCCESS)
            return
        self.__db.create_message(chat.id, message, Message.Status.SUCCESS)
        await self.__manager.send_text("Saved: %s" % message, ws)

    def __parse_metadata(self, message: bytes,
                         timezone: str) -> tuple[str, str | None]:
        """
        Parse metadata of multimedia message and attach filename to save 
        if it is in the valid time range. Return number of bytes left and filename.
        """
        metadata = pickle.loads(message)
        bytes_left = metadata["size"]
        filename = None
        if metadata["type"] == "voice" and is_now_between_range_in_timezone(
                "08:00", "12:00", timezone):
            filename = metadata["name"]
            sleep(1)
        elif metadata["type"] == "video" and is_now_between_range_in_timezone(
                "08:00", "23:59", timezone):
            filename = metadata["name"]
            sleep(2)
        return bytes_left, filename

    async def __handle_multimedia_message(self, ws: WebSocket, message: bytes,
                                          file_to_save: str | None, bytes_left,
                                          chat: Chat) -> int:
        """
        Handle multimedia message from client and return number of bytes left.
        """
        if file_to_save:
            with open(file_to_save, "ab") as f:
                f.write(message)
        bytes_left -= len(message)
        if bytes_left == 0 and file_to_save:
            self.__db.create_message(chat.id, file_to_save,
                                     Message.Status.SUCCESS)
            await self.__manager.send_text("Saved multimedia message", ws)
        if bytes_left == 0 and not file_to_save:
            self.__db.create_message(chat.id, "", Message.Status.UNSUCCESS)
            await self.__manager.send_text("Discarded multimedia message", ws)
        return bytes_left

    def start(self):
        """
        Start the server.
        """
        uvicorn.run(self.__app,
                    host="0.0.0.0",
                    port=8000,
                    ws_max_queue=500,
                    ws_ping_interval=10,
                    ws_ping_timeout=2)


if __name__ == "__main__":
    server = Server()
    server.start()
