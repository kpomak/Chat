import select
from http import HTTPStatus

from .exceptions import PortError


class NamedPort:
    def __init__(self, name, default):
        self.name = f"_{name}"
        self.default = default

    def __get__(self, instance, cls):
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        if not value and value != 0:
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
        if message["action"] == "message" and "user_id" in message:
            for client, event in events:
                if (
                    message["user_id"] == self.users.get_username(client)
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
            username = message["user_login"]
            if username not in self.users.usernames:
                result = "accepted"
                self.users.usernames[username] = message["client"]
                self.db.activate_client(message["user_login"])
            else:
                result = "rejected"
            response = self.template_message(action="login", username=result)

        # get_contacts
        elif message["action"] == "get_contacts":
            response = self.template_message(
                action="status code",
                response="250",
                alert=self.db.get_contacts(message["user_login"]),
            )

        # get_users
        elif message["action"] == "get_users":
            response = self.template_message(
                action="status code", response="251", alert=list(self.users.usernames)
            )

        # del_contact
        elif message["action"] == "del_contact":
            self.db.del_contact(message["user_login"], message["user_id"])
            response = self.template_message(
                action="status code",
                response="252",
                alert=f'Contact {message["user_id"]} deleted',
            )

        # add_contact
        elif message["action"] == "add_contact":
            self.db.add_contact(message["user_login"], message["user_id"])
            response = self.template_message(
                action="status code",
                response="253",
                alert=f"Contact {message['user_id']} added to contact list",
            )

        # bad request
        else:
            response = self.template_message(
                action="status code",
                response=HTTPStatus.BAD_REQUEST,
                error=self.get_error,
            )
        return message["client"], response
