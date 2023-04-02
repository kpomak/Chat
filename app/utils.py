import json
import time
import random
import dis
from types import FunctionType

from app.config import MAX_PACKAGE_LENGTH, ENCODING, ERRORS


class BaseVerifier(type):
    def __init__(cls, name, bases, namespaces):
        super().__init__(name, bases, namespaces)

        arguments = []
        for key, value in namespaces.items():
            if isinstance(value, FunctionType) and hasattr(value, "__closure__"):
                try:
                    args = value.__closure__[0].cell_contents
                except TypeError:
                    args = value
                arguments.append(args)
        for func in arguments:
            print(func)


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
