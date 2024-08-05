import pickle
import sys
import threading
import time
import uuid

from tzlocal import get_localzone
from websocket import WebSocketApp

from config import config
from file import File


class Client:

    def __init__(self, client_id: int):
        self.__client_id = client_id
        self.__conn = None
        self.__run_app = None
        self.__bytes_left = -1  # number of bytes left to receive in multimedia message
        self.__multimedia_metadata = None
        self.__ready_for_new_message = True

    def init_connection(self):
        """
        Initialize connection with server. Send the client's timezone to help 
        server in handling time-related tasks.
        """

        def on_message(ws, message):
            if isinstance(message, str):
                print(message)
            elif isinstance(message, bytes):
                if self.__bytes_left == -1:  # first chunk
                    self.__multimedia_metadata = pickle.loads(message)
                    self.__bytes_left = self.__multimedia_metadata["size"]
                    print(self.__multimedia_metadata)
                else:
                    filename = "CLIENT_%d_RECEIVED_%s" % (
                        self.__client_id, self.__multimedia_metadata["name"])
                    with open(filename, "ab") as file:
                        file.write(message)
                        self.__bytes_left -= len(message)
                    if self.__bytes_left == 0:
                        print("File received")
                        self.__bytes_left = -1
            else:
                raise ValueError("Invalid message type")
            self.set_ready_for_new_message(True)

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

        self.__run_app = threading.Thread(target=self.__conn.run_forever,
                                          kwargs={
                                              "ping_interval": 10,
                                              "ping_timeout": 1
                                          })
        self.__run_app.daemon = True
        self.__run_app.start()
        # get current timezone and send it to server
        while not self.__conn.sock.connected:
            print("waiting for connection")
            time.sleep(1)
        print("connected")
        self.send_msg(str(get_localzone()))

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

    def set_ready_for_new_message(self, ready: bool):
        self.__ready_for_new_message = ready

    def is_ready_for_new_message(self): 
        return self.__ready_for_new_message

    def __send_file_stream(self, file_address: str, type: str):
        file = File(file_address)
        file_metadata = file.get_metadata()
        file_metadata["type"] = type
        file_metadata["client_id"] = self.__client_id
        self.__conn.send_bytes(pickle.dumps(file_metadata))

        for chunk in file.get_bytes_stream(256):
            self.__conn.send_bytes(chunk)


if __name__ == "__main__":
    client = Client(uuid.uuid4().int >> 120)
    client.init_connection()
    while True:
        if not client.is_ready_for_new_message():
            time.sleep(1)
            continue
        type = input("Enter message type: text, voice, video\n")
        if type == "text":
            message = input("Enter message (enter exit to quit): ")
            client.send_msg(message)
        elif type == "voice":
            message = input(
                "Enter voice file path or url (enter exit to quit): ")
            client.send_voice(message)
        elif type == "video":
            message = input(
                "Enter video file path or url (enter exit to quit): ")
            client.send_video(message)
        else:
            print("Invalid message type")
            break
        client.set_ready_for_new_message(False)
        if message == "exit":
            break
    client.close_connection()
    time.sleep(5)
    sys.exit(0)
