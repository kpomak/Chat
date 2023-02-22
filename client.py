import sys
from socket import AF_INET, SOCK_STREAM, socket

from config import DEFAULT_PORT
from utils import get_error, get_message, send_message, template_message


def parse_message(message):
    if "response" in message and message["response"] < 300:
        return f'{message["response"]}: {message["alert"]}'
    return f'{message["response"]}: {message["error"]}'


def presence():
    user = {"account_name": "anonymous", "status": "online"}
    return template_message(action="presence", type="status", user=user)


def run_client():
    params = sys.argv
    try:
        port = int(params[2]) if len(params) > 2 else DEFAULT_PORT
        address = params[1]
        sock = socket(AF_INET, SOCK_STREAM)
        sock.connect((address, port))
    except Exception:
        print(get_error())
        sys.exit(1)

    message = presence()
    send_message(sock, message)
    response = parse_message(get_message(sock))
    print(response)


if __name__ == "__main__":
    run_client()
