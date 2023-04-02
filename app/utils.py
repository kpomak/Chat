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
            # Проверяем, является ли значение функцией
            if isinstance(value, FunctionType):
                # Если да, то проверяем наличие декоратора
                if hasattr(value, "__closure__"):
                    # Достаем аргументы декоратора
                    args = value.__closure__
                    # Записываем в метаданные метода
                    arguments.append(args)
        print(arguments)

        # try:
        #     bytecode = dis.Bytecode(value)
        # except TypeError:
        #     pass
        # else:
        #     for instance in bytecode:
        #         print(instance)

        # try:
        #     result = dis.dis(value)
        # except TypeError:
        #     print(key, "/" * 30)
        # else:
        #     if result:
        #         for item in result:
        #             try:
        #                 print(item, type(item), dir(item))
        #                 with open("dis.log", "a", "utf-8") as f:
        #                     f.write(str({item: type(item)}))
        #             except TypeError:
        #                 print("Erop")


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
