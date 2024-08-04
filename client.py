import os
import pickle
import re
import threading
import time
import uuid
from enum import Enum

import requests
from tzlocal import get_localzone
from websocket import WebSocketApp

from config import config
from utils import is_downloadable, is_url


class File:

    class Type(Enum):
        LOCAL = 1
        REMOTE = 2

    def __init__(self, address: str):
        self.__address = address  # file path or url
        if os.path.exists(self.__address):
            self.__type = File.Type.LOCAL
        elif is_url(self.__address) and is_downloadable(self.__address):
            self.__type = File.Type.REMOTE
        else:
            return TypeError("Invalid file address")

    def get_metadata(self) -> dict:
        if self.__type == File.Type.LOCAL:
            return {
                "name": os.path.basename(self.__address),
                "size": os.path.getsize(self.__address)
            }
        elif self.__type == File.Type.REMOTE:
            response = requests.head(self.__address)
            content_disposition = response.headers.get('content-disposition')
            if content_disposition:
                filename = re.findall("filename=(.+)", content_disposition)[0]
                return {
                    "name": filename,
                    "size": int(response.headers.get('content-length', 0))
                }
            else:
                raise ValueError(
                    "Filename not found in content-disposition of this file")

    def get_file_name(self) -> str:
        if self.__type == File.Type.LOCAL:
            return os.path.basename(self.__address)
        elif self.__type == File.Type.REMOTE:
            response = requests.head(self.__address)
            content_disposition = response.headers.get('content-disposition')
            if content_disposition:
                filename = re.findall("filename=(.+)", content_disposition)[0]
                return filename
            else:
                raise ValueError(
                    "Filename not found in content-disposition of this file")

    def get_file_size(self) -> int:
        if self.__type == File.Type.LOCAL:
            return os.path.getsize(self.__address)
        elif self.__type == File.Type.REMOTE:
            response = requests.head(self.__address)
            return int(response.headers.get('content-length', 0))

    def get_bytes_stream(self, size: int = 1024):
        if self.__type == File.Type.LOCAL:
            with open(self.__address, 'rb') as file:
                yield file.read(size)
        elif self.__type == File.Type.REMOTE:
            response = requests.get(self.__address, stream=True)
            for chunk in response.iter_content(size):
                yield chunk


class Client:

    def __init__(self, client_id: int):
        self.__client_id = client_id
        self.__conn = None

    def init_connection(self):

        def on_message(ws, message):
            print(f"Reply from server: {message}")

        def on_ping(ws, data):
            # print("Got a ping! A pong reply has already been automatically sent.")
            pass

        def on_pong(ws, data):
            # print("Got a pong! No need to respond")
            pass

        print("init connection with client id %d" % self.__client_id)
        self.__conn = WebSocketApp("%s/%d" %
                                   (config["ws_endpoint"], self.__client_id),
                                   on_message=on_message,
                                   on_ping=on_ping,
                                   on_pong=on_pong)

        t = threading.Thread(target=self.__conn.run_forever,
                             kwargs={
                                 "ping_interval": 10,
                                 "ping_timeout": 1
                             })
        t.start()
        # get current timezone and send it to server
        while not self.__conn.sock.connected:
            print("waiting for connection")
            time.sleep(1)
        self.send_msg(str(get_localzone()))
        # t.join()

    def get_id(self):
        return self.__client_id

    def send_msg(self, text: str):
        self.__conn.send_text(text)

    def send_voice(self, file_address: str):
        self.__send_file_stream(file_address, "voice")

    def send_video(self, file_address: str):
        self.__send_file_stream(file_address, "video")

    def close_connection(self):
        self.__conn.close()

    def __send_file_stream(self, file_address: str, type: str):
        file = File(file_address)
        file_metadata = file.get_metadata()
        file_metadata["type"] = type
        self.__conn.send_bytes(pickle.dumps(file_metadata))

        for chunk in file_metadata["size"]:
            ret = self.__conn.send_bytes(chunk)
            while ret < len(chunk):
                ret += self.__conn.send_bytes(chunk[ret:])


if __name__ == "__main__":
    client = Client(uuid.uuid4().int >> 120)
    client.init_connection()
    while True:
        message = input("Enter message: ")
        client.send_msg(message)
        if message == "exit":
            break
