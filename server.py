import sys
from http import HTTPStatus
from socket import AF_INET, SOCK_STREAM, socket

from config import DEFAULT_PORT, MAX_CONNECTIONS
from utils import get_message, send_message, template_message, get_error


def reply(message):
    if "action" in message and "time" in message:
        return template_message(response=HTTPStatus.OK, alert="OK")
    return template_message(response=HTTPStatus.BAD_REQUEST, error=get_error())


def parse_params():
    params = sys.argv
    port = int(params[params.index("-p") + 1]) if "-p" in params else DEFAULT_PORT
    address = params[params.index("-a") + 1] if "-a" in params else ""
    return address, port


def init_socket():
    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind(parse_params())
    sock.listen(MAX_CONNECTIONS)
    return sock


def run_server():
    try:
        sock = init_socket()
    except Exception:
        print(get_error())
        sys.exit(1)

    while True:
        client, _ = sock.accept()
        message = get_message(client)
        print(message)

        response = reply(message)
        send_message(client, response)
        client.close()


if __name__ == "__main__":
    run_server()
