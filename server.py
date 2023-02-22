import sys
from socket import AF_INET, SOCK_STREAM, socket

from config import DEFAULT_PORT, MAX_CONNECTIONS
from utils import get_message, send_message, template_message, get_error


def reply(message):
    if "action" in message and "time" in message:
        return template_message(response=200)
    return template_message(response=400, error=get_error())


def run_server():
    params = sys.argv
    try:
        port = int(params[params.index("-p") + 1]) if "-p" in params else DEFAULT_PORT
        server_address = params[params.index("-a") + 1] if "-a" in params else ""
        sock = socket(AF_INET, SOCK_STREAM)
        sock.bind((server_address, port))
    except Exception:
        print(get_error())
        sys.exit(1)

    sock.listen(MAX_CONNECTIONS)

    while True:
        client, _ = sock.accept()
        message = get_message(client)
        print(message)

        response = reply(message)
        send_message(client, response)
        client.close()


if __name__ == "__main__":
    run_server()
