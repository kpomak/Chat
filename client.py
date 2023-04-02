import sys
import threading
import time
from socket import AF_INET, SOCK_STREAM, socket

from app.config import DEFAULT_PORT, TIMEOUT
from app.utils import Chat, BaseVerifier
from log.settings.client_log_config import logger
from log.settings.decor_log_config import Log


class ServerVerifier(BaseVerifier):
    pass


class Client(Chat, metaclass=ServerVerifier):
    def __init__(self):
        self.username = None

    @Log()
    def parse_message(self, message):
        logger.info(f"Parsing messagefrom server: {message}")

        if message["action"] == "login":
            return message["username"]

        if message["action"] == "notification":
            return f'{message["response"]}'

        if message["action"] == "msg" and message["to_user"] == self.username:
            return f"{message['body']}"

        if message["action"] == "status code":
            if message["response"] < 400:
                return f'{message["response"]}: {message["alert"]}'
            return f'{message["response"]}: {message["error"]}'

    @Log()
    def create_message(self, **kwargs):
        user = {"username": self.username, "status": "online"}
        logger.info(f"Creating message from user {user['username']}")
        return self.template_message(type="status", user=user, **kwargs)

    @Log()
    def presence(self):
        logger.info(f"Creating precense message")
        return self.create_message(action="presence")

    @property
    @Log()
    def parse_params(self):
        params = sys.argv
        port = int(params[2]) if len(params) > 2 else DEFAULT_PORT
        address = params[1]
        logger.info(f"Address: {address} and port: {port} from CLI")
        return address, port

    @Log()
    def connect_socket(self):
        sock = socket(AF_INET, SOCK_STREAM)
        address, port = self.parse_params
        sock.connect((address, port))
        logger.info(f"Connection to server {address}:{port} was succefully created")
        return sock

    @Log()
    def run(self):
        try:
            self.sock = self.connect_socket()
        except Exception:
            logger.critical(
                f"Achtung!!! Ein kritischer Fehler wurde bemerkt! Was ist los? {self.get_error}"
            )
            sys.exit(1)

    @Log()
    def recieve_message(self):
        try:
            message = self.get_message(self.sock)
        except Exception:
            logger.critical("Fatal error by recieving message")
            sys.exit(1)
        else:
            logger.info(f"Recieved message {message}")
            return self.parse_message(message)

    @Log()
    def set_username(self):
        while not self.username:
            self.username = input("Enter your username ")
            message = self.create_message(action="login")
            self.send_message(self.sock, message)
            if self.recieve_message() == "rejected":
                print(f"Sorry, username {self.username} is busy :(")
                self.username = None

    @Log()
    def outgoing(self):
        while message := input(
            'Enter message or command "/users_list"\nLeave empty and press Enter for exit'
        ):
            if not message:
                break
            elif message == "/users_list":
                self.send_message(
                    self.sock, self.create_message(action="commands", body=message)
                )
            else:
                self.send_message(
                    self.sock,
                    self.create_message(
                        action="msg",
                        body=message,
                        to_user=input("Enter username of target "),
                    ),
                )

    @Log()
    def incomming(self):
        while message := self.recieve_message():
            print(message)


if __name__ == "__main__":
    client = Client()
    client.run()
    client.set_username()

    transmitter = threading.Thread(target=client.outgoing)
    transmitter.daemon = True
    transmitter.start()

    reciever = threading.Thread(target=client.incomming)
    reciever.daemon = True
    reciever.start()

    while True:
        time.sleep(TIMEOUT)
        if transmitter.is_alive() and reciever.is_alive():
            continue
        break
