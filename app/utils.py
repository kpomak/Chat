import json
import random
import time

from app.config import ENCODING, ERRORS, MAX_PACKAGE_LENGTH


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
        return self.sockets_list[self.usernames_list[username]]


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
    def template_message(action="msg", **kwargs):
        message = {"action": action, "time": time.time()}
        for key, value in kwargs.items():
            message[key] = value
        return message

    @property
    def get_error(self):
        return random.choice(ERRORS)
