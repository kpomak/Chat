import json
import random
import time
from config import MAX_PACKAGE_LENGTH, ENCODING, ERRORS


def get_message(sock):
    response = sock.recv(MAX_PACKAGE_LENGTH).decode(ENCODING)
    return json.loads(response)


def send_message(sock, message):
    message = json.dumps(message).encode(ENCODING)
    sock.send(message)


def template_message(action="msg", **kwargs):
    message = {"action": action, "time": time.time()}
    for key, value in kwargs.items():
        message[key] = value
    return message


def get_error():
    return random.choice(ERRORS)
