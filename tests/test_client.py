import os
import sys
import time
import unittest
from http import HTTPStatus
from unittest.mock import patch
from socket import socket

sys.path.append(os.getcwd())

from config import DEFAULT_PORT
from client import parse_message, parse_params, presence, connect_socket
from server import init_socket

TEST_PORT = 5000
TEST_IP = "127.0.0.1"


class ClientTestCase(unittest.TestCase):
    def setUp(self):
        @patch("sys.argv", ["", TEST_IP])
        def _connect_socket():
            return connect_socket()

        self.server_sock = init_socket()
        self.client_sock = _connect_socket()

    def tearDown(self):
        self.client_sock.close()
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
        self.assertEqual(parse_params(), (TEST_IP, TEST_PORT))

    @patch("sys.argv", ["", TEST_IP])
    def test_parse_params_no_port(self):
        self.assertEqual(parse_params(), (TEST_IP, DEFAULT_PORT))

    @patch("sys.argv", ["", TEST_IP])
    def test_connect_socket(self):
        self.assertIsInstance(self.client_sock, socket)


if __name__ == "__main__":
    unittest.main()
