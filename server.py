import sys
from http import HTTPStatus
from socket import AF_INET, SOCK_STREAM, socket
import select

from app.config import TIMEOUT, DEFAULT_PORT, MAX_CONNECTIONS
from app.utils import Chat
from log.settings.server_log_config import logger
from log.settings.decor_log_config import Log


class Server(Chat):
    @classmethod
    @Log()
    def reply(cls, message):
        logger.info(f"Replying on message: {message}")
        if "action" in message and "time" in message:
            return cls.template_message(response=HTTPStatus.OK, alert="OK")
        return cls.template_message(
            response=HTTPStatus.BAD_REQUEST, error=cls.get_error
        )

    @property
    @Log()
    def parse_params(self):
        params = sys.argv
        port = int(params[params.index("-p") + 1]) if "-p" in params else DEFAULT_PORT
        address = params[params.index("-a") + 1] if "-a" in params else ""
        logger.info(
            f"Address: {address if address else '0.0.0.0'} and port: {port} from CLI"
        )
        return address, port

    @Log()
    def init_socket(self):
        sock = socket(AF_INET, SOCK_STREAM)
        sock.bind(self.parse_params)
        sock.settimeout(TIMEOUT)
        sock.listen(MAX_CONNECTIONS)
        logger.info(
            f"Socket was succefully created with max average of connections: {MAX_CONNECTIONS}"
        )
        return sock

    @Log()
    def run(self):
        try:
            sock = self.init_socket()
        except Exception:
            logger.critical(
                f"Achtung!!! Ein kritischer Fehler wurde bemerkt! Was ist los? {self.get_error}"
            )
            sys.exit(1)

        clients = {}
        while True:
            dispatcher = select.poll()
            try:
                client, addr = sock.accept()
            except OSError:
                pass
            else:
                logger.info(f"Connected client: {client} from address: {addr}")
                clients[client.fileno()] = client
            finally:
                for fileno, client in clients.items():
                    dispatcher.register(client, select.POLLIN)
            events = dispatcher.poll(TIMEOUT)

            for client, event in events:
                if event & select.POLLIN:
                    print(client, event)

            # client, addr = sock.accept()
            # logger.info(f"Connected client: {client} from address: {addr}")
            # message = self.get_message(client)
            # logger.info(f"Recieved message from client: {message}")

            # response = self.reply(message)
            # logger.info(f"Created response on clients message: {response}")
            # self.send_message(client, response)
            # logger.info(f"Sent response: {response} to client: {client}")
            # client.close()
            # logger.info(
            #     f"Connecttion with client: {client} by address: {addr} was closed"
            # )


if __name__ == "__main__":
    server = Server()
    server.run()
