import sys
import threading
import time
from socket import AF_INET, SOCK_STREAM, socket
from PyQt6 import QtCore, QtWidgets
from client.gui import welcome

from config.settigs import DEFAULT_PORT, TIMEOUT
from config.utils import Chat, BaseVerifier
from client.client_utils import MessageHandlerMixin
from client.models import ClientDBase
from log.settings.client_log_config import logger
from log.settings.decor_log_config import Log


class ClientVerifier(BaseVerifier):
    def __init__(cls, name, bases, namespaces):
        super().__init__(name, bases, namespaces)

        for attr in namespaces.values():
            if isinstance(attr, socket):
                raise TypeError("Socket shouldn't be created at class level")

        params = cls.attrs[f"_{name}_attrs"]
        if "accept" in params or "listen" in params:
            raise TypeError("Accept or listen methods are not allowed")


class Client(Chat, MessageHandlerMixin, metaclass=ClientVerifier):
    def __init__(self):
        self.lock = threading.Lock()
        self.username = None

    @Log()
    def create_message(self, **kwargs):
        logger.info(f"Creating message from user {self.username}")
        return self.template_message(user_login=self.username, **kwargs)

    @Log()
    def presence(self):
        logger.info(f"Creating precense message")
        return self.create_message(action="presence")

    @property
    @Log()
    def parse_params(self):
        params = sys.argv
        port = int(params[2]) if len(params) > 2 else DEFAULT_PORT
        address = params[1]
        logger.info(f"Address: {address} and port: {port} from CLI")
        return address, port

    @Log()
    def connect_socket(self):
        sock = socket(AF_INET, SOCK_STREAM)
        address, port = self.parse_params
        sock.connect((address, port))
        logger.info(f"Connection to server {address}:{port} was succefully created")
        return sock

    @Log()
    def run(self):
        try:
            self.sock = self.connect_socket()
        except Exception:
            logger.critical(
                f"Achtung!!! Ein kritischer Fehler wurde bemerkt! Was ist los? {self.get_error}"
            )
            sys.exit(1)

    @Log()
    def recieve_message(self):
        try:
            message = self.get_message(self.sock)
        except Exception:
            logger.critical("Fatal error by recieving message")
            sys.exit(1)
        else:
            logger.info(f"Recieved message {message}")
            return self.parse_message(message)

    @Log()
    def set_username(self, app):
        while not self.username:
            Dialog = QtWidgets.QDialog()
            dialog = welcome.UiDialog()
            dialog.setupUi(Dialog)
            Dialog.show()
            app.exec()
            self.username = input("Enter your username: ")
            message = self.create_message(action="login")
            self.send_message(self.sock, message)
            if self.recieve_message() == "rejected":
                print(f"Sorry, username {self.username} is busy :(")
                self.username = None

    def connect_db(self, db):
        self.db = db
        self.send_message(self.sock, self.create_message(action="get_users"))

    @Log()
    def outgoing(self):
        while message := input(
            "\nEnter message or command from list below:"
            "\n(/get_contacts, /get_users, /add_contact, /del_contact)"
            "\nFor exit leave empty and press Enter\n"
        ):
            if message.startswith("/"):
                context = {}
                message = message[1:]
                if message in ("get_contacts", "get_users"):
                    context["action"] = message
                elif message in ("add_contact", "del_contact"):
                    context["action"] = message
                    context["user_id"] = input("Enter username of target: ")
                if context:
                    self.send_message(self.sock, self.create_message(**context))
            else:
                message = self.create_message(
                    action="message",
                    body=message,
                    user_id=input("Enter username of target: "),
                )
                with self.lock:
                    self.db.add_message(
                        message["user_id"],
                        message["body"],
                        message["time"],
                        recieved=False,
                    )
                self.send_message(self.sock, message)

    @Log()
    def incomming(self):
        while message := self.recieve_message():
            print(message)

    @Log()
    def main_loop(self):
        transmitter = threading.Thread(target=self.outgoing)
        transmitter.daemon = True
        transmitter.start()

        reciever = threading.Thread(target=self.incomming)
        reciever.daemon = True
        reciever.start()

        while True:
            time.sleep(TIMEOUT)
            if transmitter.is_alive() and reciever.is_alive():
                continue
            break


def main():
    app = QtWidgets.QApplication(sys.argv)

    client = Client()
    client.run()
    client.set_username(app)
    db = ClientDBase(client.username)
    client.connect_db(db)
    client.main_loop()


if __name__ == "__main__":
    main()
