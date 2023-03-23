import select
import sys
from collections import deque
from http import HTTPStatus
from socket import AF_INET, SOCK_STREAM, socket

from app.config import DEFAULT_PORT, MAX_CONNECTIONS, TIMEOUT
from app.utils import Chat, Users
from log.settings.decor_log_config import Log
from log.settings.server_log_config import logger


class Server(Chat):
    def __init__(self):
        self.users = Users()
        self.messages = deque()
        self.dispatcher = select.poll()

    @Log()
    def reply(self, message):
        logger.info(f"Replying on message: {message}")

        if "body" in message:
            return self.template_message(body=message["body"])
        if "action" in message and "time" in message:
            return self.template_message(response=HTTPStatus.OK, alert="OK")
        return self.template_message(
            response=HTTPStatus.BAD_REQUEST, error=self.get_error
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

    def check_messages(self, events):
        for client, event in events:
            if event & select.POLLIN:
                try:
                    message = self.get_message(self.users.sockets[client])
                except Exception:
                    logger.info(f"Client {client} disconnected")
                    self.dispatcher.unregister(self.users.sockets[client])
                    self.users.sockets[client].close()
                    del self.users.sockets[client]
                else:
                    message["client"] = client
                    logger.info(f"message {message} recieved from client {client}")
                    self.messages.append(message)

    def answer_on_messages(self, events):
        while self.messages:
            message = self.messages.popleft()
            if "action" in message and message["action"] == "username":
                username = message["user"].get("username")
                response = self.template_message(
                    username="accepted"
                    if username not in self.users.usernames
                    else "rejected"
                )
                self.users.usernames[username] = message["client"]
            self.send_message(self.users.sockets[message["client"]], response)

            # response = self.reply(message)

            # for client, event in events:
            #     if event & select.POLLOUT:
            #         logger.info(f"Sending message {message} to client {client}")
            #         response = self.reply(message)
            #         self.send_message(self.clients[client], response)

    @Log()
    def run(self):
        try:
            sock = self.init_socket()
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
            finally:
                for client in self.users.sockets.values():
                    self.dispatcher.register(client, select.POLLIN | select.POLLOUT)
            events = self.dispatcher.poll(TIMEOUT)
            if events:
                self.answer_on_messages(events)
                self.check_messages(events)


if __name__ == "__main__":
    server = Server()
    server.run()
