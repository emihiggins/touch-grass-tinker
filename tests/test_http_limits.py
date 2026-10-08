import json
import socket
import threading
import time
import unittest
from unittest.mock import patch

from liftlap.http_limits import BoundedHTTPServer, HTTPLimits
from liftlap.server import Handler


class HTTPAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.entered = threading.Event()
        entered = self.entered
        class SignaledHandler(Handler):
            def do_POST(self):
                entered.set()
                super().do_POST()
        self.server = BoundedHTTPServer(('127.0.0.1', 0), SignaledHandler,
                                      limits=HTTPLimits(max_connections=1, read_timeout_seconds=.3))
        self.thread = threading.Thread(target=self.server.serve_forever, kwargs={'poll_interval': .01}, daemon=True)
        self.thread.start()
        self.clients = []

    def tearDown(self):
        for client in self.clients:
            client.close()
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def connect(self):
        client = socket.create_connection(self.server.server_address, timeout=2)
        self.clients.append(client)
        return client

    def request(self, client, headers, body=b''):
        head = ('POST /api/interpret HTTP/1.0\r\nHost: 127.0.0.1:'
                + str(self.server.server_port) + '\r\n' + headers + '\r\n\r\n')
        client.sendall(head.encode() + body)

    def response(self, client):
        chunks = []
        while True:
            data = client.recv(65536)
            if not data: break
            chunks.append(data)
        raw = b''.join(chunks)
        header, body = raw.split(b'\r\n\r\n', 1)
        return int(header.split()[1]), json.loads(body) if body else None

    def test_timeout_and_busy_never_dispatch_and_capacity_recovers(self):
        with patch('liftlap.server.handle_api', return_value={'ok': True}) as dispatch:
            first = self.connect()
            self.request(first, 'Content-Length: 100', b'{')
            self.assertTrue(self.entered.wait(1))
            second = self.connect()
            self.assertEqual(self.response(second)[0], 503)
            status, body = self.response(first)
            self.assertEqual(status, 408)
            self.assertEqual(body['code'], 'body_timeout')
            dispatch.assert_not_called()
            self.assertTrue(self.server._slots.acquire(timeout=1))
            self.server._slots.release()
            third = self.connect()
            self.request(third, 'Content-Length: 2', b'{}')
            self.assertEqual(self.response(third), (200, {'ok': True}))
            dispatch.assert_called_once()

    def test_framing_size_and_eof_rejected_before_dispatch(self):
        cases = [('Content-Length: 2\r\nContent-Length: 2', b'{}', 400),
                 ('Transfer-Encoding: chunked', b'', 400),
                 ('Content-Length: 16385', b'', 413),
                 ('Content-Length: 20', b'{}', 400)]
        with patch('liftlap.server.handle_api') as dispatch:
            for headers, data, expected in cases:
                with self.subTest(headers=headers):
                    client = self.connect()
                    self.request(client, headers, data)
                    client.shutdown(socket.SHUT_WR)
                    self.assertEqual(self.response(client)[0], expected)
                    self.assertTrue(self.server._slots.acquire(timeout=1))
                    self.server._slots.release()
            dispatch.assert_not_called()

    def test_partial_body_progress_does_not_reset_total_deadline(self):
        with patch('liftlap.server.handle_api') as dispatch:
            client = self.connect()
            start = time.monotonic()
            self.request(client, 'Content-Length: 100', b'{')
            self.assertTrue(self.entered.wait(1))
            time.sleep(.12)
            client.sendall(b' ')
            time.sleep(.12)
            client.sendall(b' ')
            self.assertEqual(self.response(client)[0], 408)
            self.assertLess(time.monotonic() - start, .48)
            dispatch.assert_not_called()

    def test_configuration_rejects_unbounded_values(self):
        for kwargs in ({'max_connections': 0}, {'backlog': -1}, {'max_body_bytes': True},
                       {'read_timeout_seconds': float('inf')}, {'read_timeout_seconds': 0}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                HTTPLimits(**kwargs)
