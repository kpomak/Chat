import json
import random
import time
import select
from http import HTTPStatus

from .config import ENCODING, ERRORS, MAX_PACKAGE_LENGTH
from .exceptions import PortError


class NamedPort:
    def __init__(self, name, default):
        self.name = f"_{name}"
        self.default = default

    def __get__(self, instance, cls):
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        if not value:
            value = self.default

        if value < 0:
            raise PortError(value)

        instance.__dict__[self.name] = value

    def __delete__(self, instance):
        raise AttributeError("Port deleting  os not implemented")


class Users:
    def __init__(self):
        self.sockets_list = {}
        self.usernames_list = {}

    @property
    def sockets(self):
        return self.sockets_list

    @property
    def usernames(self):
        return self.usernames_list

    def get_socket(self, username):
        return self.sockets_list.get(self.usernames_list.get(username))

    def get_username(self, fileno):
        for key, value in self.usernames_list.items():
            if value == fileno:
                return key

    def delete_user(self, fileno):
        username = self.get_username(fileno)
        if username:
            del self.usernames_list[username]
        del self.sockets_list[fileno]


class ExchangeMessageMixin:
    def exchange_service(self, message, events):
        # p2p delivery
        if message["action"] == "msg" and "to_user" in message:
            for client, event in events:
                if (
                    message["to_user"] == self.users.get_username(client)
                    and event & select.POLLOUT
                ):
                    return client, message

        # presence message
        if message["action"] == "presence":
            response = self.template_message(
                action="status code", response=HTTPStatus.OK, alert="OK"
            )

        # sign up message
        elif message["action"] == "login":
            username = message["user"].get("username")
            response = self.template_message(
                action="login",
                username="accepted"
                if username not in self.users.usernames
                else "rejected",
            )
            self.users.usernames[username] = message["client"]

        # commands
        elif message["action"] == "commands" and message["body"] == "/users_list":
            response = self.template_message(
                action="notification", response=list(self.users.usernames.keys())
            )

        # bad request
        else:
            response = self.template_message(
                action="status code",
                response=HTTPStatus.BAD_REQUEST,
                error=self.get_error,
            )
        return message["client"], response


class Chat:
    @staticmethod
    def get_message(sock):
        response = sock.recv(MAX_PACKAGE_LENGTH).decode(ENCODING)
        return json.loads(response)

    @staticmethod
    def send_message(sock, message):
        message = json.dumps(message).encode(ENCODING)
        sock.send(message)

    @staticmethod
    def template_message(**kwargs):
        action = kwargs["action"] if "action" in kwargs else "msg"
        message = {"action": action, "time": time.time()}
        for key, value in kwargs.items():
            message[key] = value
        return message

    @property
    def get_error(self):
        return random.choice(ERRORS)
