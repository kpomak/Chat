import select
import sys
import argparse
from collections import deque
from socket import AF_INET, SOCK_STREAM, socket

from app.config import DEFAULT_PORT, MAX_CONNECTIONS, TIMEOUT
from app.utils import Chat, Users, ExchangeMessageMixin, NamedPort
from app.exceptions import PortError
from log.settings.decor_log_config import Log
from log.settings.server_log_config import logger


class Server(Chat, ExchangeMessageMixin):
    port = NamedPort("server_port", DEFAULT_PORT)

    def __init__(self):
        self.users = Users()
        self.messages = deque()
        self.dispatcher = select.poll()

    @property
    @Log()
    def parse_params(self):
        params = sys.argv
        port = int(params[params.index("-p") + 1]) if "-p" in params else ""
        address = params[params.index("-a") + 1] if "-a" in params else ""
        logger.info(
            f"Address: {address if address else '0.0.0.0'} "
            f"and port: {port if port else 'by default'} from CLI"
        )
        return address, port

    @Log()
    def init_socket(self):
        sock = socket(AF_INET, SOCK_STREAM)
        address, self.port = self.arg_parser()
        sock.bind((address, self.port))
        sock.settimeout(TIMEOUT)
        sock.listen(MAX_CONNECTIONS)
        logger.info(
            f"Socket was succefully created with max average of connections: {MAX_CONNECTIONS}"
        )
        return sock

    @Log()
    def disconnect_client(self, client):
        logger.info(f"Client {client} disconnected")
        self.dispatcher.unregister(self.users.sockets[client])
        self.users.sockets[client].close()
        self.users.delete_user(client)

    @Log()
    def check_messages(self, events):
        for client, event in events:
            if event & select.POLLIN:
                try:
                    message = self.get_message(self.users.sockets[client])
                except Exception:
                    self.disconnect_client(client)
                else:
                    message["client"] = client
                    logger.info(f"message {message} recieved from client {client}")
                    self.messages.append(message)

    @Log()
    def answer_on_messages(self, events):
        while self.messages:
            message = self.messages.popleft()
            if "action" in message:
                client, response = self.exchange_service(message, events)
                self.send_message(self.users.sockets[client], response)

    @Log()
    def run(self):
        try:
            sock = self.init_socket()
        except PortError as p:
            logger.critical(f"Advertencia! Error detectado ;) {p}")
            sys.exit(1)
        except Exception:
            logger.critical(
                f"Achtung!!! Ein kritischer Fehler wurde bemerkt! Was ist los? {self.get_error}"
            )
            sys.exit(1)

        while True:
            try:
                client, addr = sock.accept()
            except OSError:
                pass
            else:
                logger.info(f"Connected client: {client} from address: {addr}")
                self.users.sockets[client.fileno()] = client
                self.dispatcher.register(client, select.POLLIN | select.POLLOUT)

            events = self.dispatcher.poll(TIMEOUT)
            if events:
                self.answer_on_messages(events)
                self.check_messages(events)


if __name__ == "__main__":
    server = Server()
    server.run()
