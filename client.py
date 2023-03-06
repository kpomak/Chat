import sys
from socket import AF_INET, SOCK_STREAM, socket

from app.config import DEFAULT_PORT
from app.utils import Chat


class Client(Chat):
    @staticmethod
    def parse_message(message):
        if "response" in message and message["response"] < 300:
            return f'{message["response"]}: {message["alert"]}'
        return f'{message["response"]}: {message["error"]}'

    @classmethod
    def presence(cls):
        user = {"account_name": "anonymous", "status": "online"}
        return cls.template_message(action="presence", type="status", user=user)

    @property
    def parse_params(self):
        params = sys.argv
        port = int(params[2]) if len(params) > 2 else DEFAULT_PORT
        address = params[1]
        return address, port

    def connect_socket(self):
        sock = socket(AF_INET, SOCK_STREAM)
        address, port = self.parse_params
        print()
        sock.connect((address, port))
        return sock

    def run(self):
        try:
            sock = self.connect_socket()
        except Exception:
            print(self.get_error)
            sys.exit(1)

        message = self.presence()
        self.send_message(sock, message)
        response = self.parse_message(self.get_message(sock))
        print(response)


if __name__ == "__main__":
    client = Client()
    client.run()
