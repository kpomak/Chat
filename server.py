import sys
from http import HTTPStatus
from socket import AF_INET, SOCK_STREAM, socket

from app.config import DEFAULT_PORT, MAX_CONNECTIONS
from app.utils import Chat


class Server(Chat):
    @classmethod
    def reply(cls, message):
        if "action" in message and "time" in message:
            return cls.template_message(response=HTTPStatus.OK, alert="OK")
        return cls.template_message(
            response=HTTPStatus.BAD_REQUEST, error=cls.get_error()
        )

    @property
    def parse_params(self):
        params = sys.argv
        port = int(params[params.index("-p") + 1]) if "-p" in params else DEFAULT_PORT
        address = params[params.index("-a") + 1] if "-a" in params else ""
        return address, port

    def init_socket(self):
        sock = socket(AF_INET, SOCK_STREAM)
        qwe = self.parse_params
        sock.bind(self.parse_params)
        sock.listen(MAX_CONNECTIONS)
        return sock

    def run(self):
        try:
            sock = self.init_socket()
        except Exception:
            print(self.get_error())
            sys.exit(1)

        while True:
            client, _ = sock.accept()
            message = self.get_message(client)
            print(message)

            response = self.reply(message)
            self.send_message(client, response)
            client.close()


if __name__ == "__main__":
    server = Server()
    server.run()
