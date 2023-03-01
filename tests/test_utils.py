import os
import sys
import json
import time
import unittest
from unittest.mock import patch

sys.path.append(os.getcwd())

from utils import get_error, template_message, get_message, send_message
from config import ERRORS, ENCODING, MAX_PACKAGE_LENGTH
from server import init_socket
from client import connect_socket

TEST_IP = "127.0.0.1"


class TestSocket:
    def __init__(self, message):
        self.encoded_message = json.dumps(message).encode(ENCODING)

    def recv(self, package_length=MAX_PACKAGE_LENGTH):
        return self.encoded_message

    def send(self, message):
        self.sent = json.loads(message.decode(ENCODING))


class UtilsTestCase(unittest.TestCase):
    def setUp(self):
        @patch("sys.argv", ["", TEST_IP])
        def _connect_socket():
            return connect_socket()

        self.time = time.time()
        self.message = {"action": "msg", "time": self.time}
        self.server_sock = init_socket()
        self.client_sock = _connect_socket()
        self.test_sock = TestSocket(self.message)

    def tearDown(self):
        self.client_sock.close()
        self.server_sock.close()

    def test_get_errors(self):
        self.assertIsInstance(get_error(), str)
        self.assertIn(get_error(), ERRORS)

    def test_template_message(self):
        self.assertEqual(template_message(time=self.time), self.message)

    def test_template_message_kwargs(self):
        kwargs = {"test_key": "test_value"}
        self.assertEqual(template_message(**kwargs)["test_key"], "test_value")

    def test_get_message(self):
        test_sock = TestSocket(self.message)
        message = get_message(test_sock)
        self.assertEqual(message, self.message)

    def test_send_message(self):
        send_message(self.test_sock, self.message)
        self.assertEqual(self.test_sock.sent, self.message)


if __name__ == "__main__":
    unittest.main()
