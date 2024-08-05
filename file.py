import os
import re
from enum import Enum

import requests
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
        """
        Get metadata of the file.
        """
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
                while True:
                    data = file.read(size)
                    if not data:
                        break
                    yield data
        elif self.__type == File.Type.REMOTE:
            response = requests.get(self.__address, stream=True)
            for chunk in response.iter_content(size):
                yield chunk
