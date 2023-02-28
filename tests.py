import time
import unittest
from http import HTTPStatus
from socket import socket
from unittest.mock import patch

from config import DEFAULT_PORT
from server import init_socket, reply, parse_params as server_params
from client import (
    parse_message,
    presence,
    connect_socket,
    parse_params as client_params,
)
from utils import template_message

TEST_PORT = 5000
TEST_IP = "127.0.0.1"


class ServerTestCase(unittest.TestCase):
    def setUp(self):
        self.sock = init_socket()

    def tearDown(self):
        self.sock.close()

    def test_reply(self):
        self.assertEqual(reply(template_message())["response"], HTTPStatus.OK)

    def test_reply_no_action(self):
        self.assertEqual(
            reply({"time": time.time()})["response"], HTTPStatus.BAD_REQUEST
        )

    def test_reply_no_time(self):
        self.assertEqual(reply({"action": "test"})["response"], HTTPStatus.BAD_REQUEST)

    @patch("sys.argv", ["", "-p", str(TEST_PORT), "-a", TEST_IP])
    def test_parse_params(self):
        self.assertEqual(server_params(), (TEST_IP, TEST_PORT))

    def test_parse_params_no_params(self):
        self.assertEqual(server_params(), ("", DEFAULT_PORT))

    @patch("sys.argv", ["", "-p", str(TEST_PORT)])
    def test_parse_params_no_address(self):
        self.assertEqual(server_params(), ("", TEST_PORT))

    @patch("sys.argv", ["", "-a", TEST_IP])
    def test_parse_params_no_port(self):
        self.assertEqual(server_params(), (TEST_IP, DEFAULT_PORT))

    def test_socket(self):
        self.assertIsInstance(self.sock, socket)


class ClientTestCase(unittest.TestCase):
    def setUp(self):
        self.server_sock = init_socket()

    def tearDown(self):
        self.server_sock.close()

    def test_parse_message_ok(self):
        message_ok = {
            "response": HTTPStatus.OK,
            "alert": "OK",
        }
        self.assertEqual(
            parse_message(message_ok),
            "200: OK",
        )

    def test_parse_message_bad(self):
        message_bad = {
            "response": HTTPStatus.BAD_REQUEST,
            "error": "BAD_REQUEST",
        }
        self.assertEqual(
            parse_message(message_bad),
            "400: BAD_REQUEST",
        )

    def test_presence(self):
        message_presence = {
            "action": "presence",
            "type": "status",
            "time": time.time(),
            "user": {
                "account_name": "anonymous",
                "status": "online",
            },
        }
        self.assertEqual(presence(), message_presence)

    @patch("sys.argv", ["", TEST_IP, str(TEST_PORT)])
    def test_parse_params(self):
        self.assertEqual(client_params(), (TEST_IP, TEST_PORT))

    @patch("sys.argv", ["", TEST_IP])
    def test_parse_params_no_port(self):
        self.assertEqual(client_params(), (TEST_IP, DEFAULT_PORT))

    @patch("sys.argv", ["", TEST_IP])
    def test_connect_socket(self):
        sock = connect_socket()
        self.assertIsInstance(sock, socket)
        sock.close()


if __name__ == "__main__":
    unittest.main()
