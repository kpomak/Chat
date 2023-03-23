import sys
import threading
from socket import AF_INET, SOCK_STREAM, socket

from app.config import DEFAULT_PORT
from app.utils import Chat
from log.settings.client_log_config import logger
from log.settings.decor_log_config import Log


class Client(Chat):
    def __init__(self):
        self.username = None

    @staticmethod
    @Log()
    def parse_message(message):
        logger.info(f"Parsing messagefrom server: {message}")

        if "username" in message:
            if message["username"] == "accepted":
                return True
            return False

        if "body" in message:
            return f"{message['body']}"

        if "response" in message and message["response"] < 300:
            return f'{message["response"]}: {message["alert"]}'

        return f'{message["response"]}: {message["error"]}'

    @Log()
    def presence(self):
        logger.info(f"Creating precense message")
        user = {"username": self.username, "status": "online"}
        return self.template_message(action="presence", type="status", user=user)

    @property
    @Log()
    def parse_params(self):
        params = sys.argv
        port = (
            int(params[2]) if len(params) > 2 and params[2].isdigit() else DEFAULT_PORT
        )
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

    def recieve_message(self):
        try:
            message = self.get_message(self.sock)
        except Exception:
            logger.critical("Fatal error by recieving message")
            sys.exit(1)
        else:
            logger.info(f"Recieved message {message}")
            return self.parse_message(message)

    def set_username(self):
        while not self.username:
            self.username = input("Enter your username ")
            message = self.presence()
            message["action"] = "username"
            self.send_message(self.sock, message)
            if not self.recieve_message():
                print(f"Sorry, username {self.username} is busy :(")
                self.username = None


if __name__ == "__main__":
    client = Client()
    client.run()
    client.set_username()
    print(client.username)

    # if "send" in sys.argv:
    #     while message := input("Enter your message or Enter for exit: "):
    #         _message = client.template_message(body=message)
    #         logger.info(f"Message {_message} was sent")
    #         client.send_message(client.sock, _message)
    # else:
