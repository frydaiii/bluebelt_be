import os
import pickle
import struct
import uuid
from enum import Enum
import re

import requests
from websocket import create_connection

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
        self.__conn = create_connection(
            "%s/%d" % (config["ws_endpoint"], self.__client_id))

    def get_id(self):
        return self.__client_id

    def send_msg(self, text: str):
        ret = self.__conn.send_text(text)
        while ret < len(text):
            ret += self.__conn.send_text(text[ret:])

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
    client = Client(uuid.uuid4().int)
    client.init_connection()
    client.send_msg("Hello")
    client.close_connection()
    # with closing(create_connection("%s/%d"%(config["ws_endpoint"], client.get_id()))) as conn:
    #     while True:
    #         print(1)
    #         message = input("Enter message: ")
    #         conn.send(message)
    #         result = conn.recv()
    #         print(f"Received: {result}")
    #         if message == "exit":
    #             break
