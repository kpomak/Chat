import os
import sys
import time
import unittest
from http import HTTPStatus
from unittest.mock import patch
from socket import socket

sys.path.append(os.getcwd())

from app.config import DEFAULT_PORT
from server import Server


TEST_PORT = 5000
TEST_IP = "127.0.0.1"


class ServerTestCase(unittest.TestCase):
    def setUp(self):
        self.server = Server()
        self.sock = self.server.init_socket()

    def tearDown(self):
        self.sock.close()

    def test_reply(self):
        self.assertEqual(
            self.server.reply(self.server.template_message())["response"], HTTPStatus.OK
        )

    def test_reply_no_action(self):
        self.assertEqual(
            self.server.reply({"time": time.time()})["response"], HTTPStatus.BAD_REQUEST
        )

    def test_reply_no_time(self):
        self.assertEqual(
            self.server.reply({"action": "test"})["response"], HTTPStatus.BAD_REQUEST
        )

    @patch("sys.argv", ["", "-p", str(TEST_PORT), "-a", TEST_IP])
    def test_parse_params(self):
        self.assertEqual(self.server.parse_params, (TEST_IP, TEST_PORT))

    def test_parse_params_no_params(self):
        self.assertEqual(self.server.parse_params, ("", DEFAULT_PORT))

    @patch("sys.argv", ["", "-p", str(TEST_PORT)])
    def test_parse_params_no_address(self):
        self.assertEqual(self.server.parse_params, ("", TEST_PORT))

    @patch("sys.argv", ["", "-a", TEST_IP])
    def test_parse_params_no_port(self):
        self.assertEqual(self.server.parse_params, (TEST_IP, DEFAULT_PORT))

    def test_socket(self):
        self.assertIsInstance(self.sock, socket)


if __name__ == "__main__":
    unittest.main()
