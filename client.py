import sys
from socket import AF_INET, SOCK_STREAM, socket

from app.config import DEFAULT_PORT
from app.utils import Chat
from log.settings.client_log_config import logger
from log.settings.decor_log_config import Log


class Client(Chat):
    @staticmethod
    @Log()
    def parse_message(message):
        logger.info(f"Parsing messagefrom server: {message}")
        if "response" in message and message["response"] < 300:
            return f'{message["response"]}: {message["alert"]}'
        return f'{message["response"]}: {message["error"]}'

    @classmethod
    @Log()
    def presence(cls):
        logger.info(f"Creating precense message")
        user = {"account_name": "anonymous", "status": "online"}
        return cls.template_message(action="presence", type="status", user=user)

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

        message = self.presence()
        logger.info(f"Created precense message: {message}")
        self.send_message(self.sock, message)
        logger.info(f"Sent message: {message} to server: {self.sock}")
        response = self.parse_message(self.get_message(self.sock))
        logger.info(f"Recieved response from server: {response}")


if __name__ == "__main__":
    client = Client()
    client.run()
    if "sent" in sys.argv:
        while message := input("Enter your message or Enter for exit: "):
            client.send_message(client.sock, message)
    else:
        while message := client.get_message(client.sock):
            if message != "empty":
                print(client.parse_message(message))
