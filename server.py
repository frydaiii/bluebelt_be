from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn


class ConnectionManager:

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


class Server:

    def __init__(self):
        self.__app = FastAPI()
        self.__manager = ConnectionManager()

    def init(self):
        app: FastAPI = self.__app

        @app.websocket("/ws/{client_id}")
        async def websocket_endpoint(websocket: WebSocket, client_id: int):
            await self.__manager.connect(websocket)
            try:
                while True:
                    data = await websocket.receive()
                    if data["text"]:
                        self.__handle_text_message(data["text"])
                        length = len(data["text"])
                    elif data["bytes"]:
                        self.__handle_multimedia_message(data["bytes"])
                        length = len(data["bytes"])
                    await self.__manager.send_personal_message(
                        f"You data size: {length}", websocket)
                    # await self.__manager.broadcast(f"Client #{client_id} says: {data}")
            except WebSocketDisconnect:
                self.__manager.disconnect(websocket)
                await self.__manager.broadcast(
                    f"Client #{client_id} left the chat")

    def __handle_text_message(message: str):
        return f"<h1>{message}</h1>"

    def __handle_multimedia_message(message: bytes):
        # _todo: handle multimedia message
        pass

    def start(self):
        uvicorn.run(self.__app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    server = Server()
    server.start()
