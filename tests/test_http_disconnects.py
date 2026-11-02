import errno
from http.server import BaseHTTPRequestHandler
import unittest
from unittest.mock import Mock, patch

from zoomconnect.server import DemoHandler
from zoomconnect.positions_server import PositionHandler


class DisconnectedClientTests(unittest.TestCase):
    def handler(self, handler_type):
        handler = handler_type.__new__(handler_type)
        handler.close_connection = False
        handler.send_response = Mock()
        handler.send_header = Mock()
        handler.end_headers = Mock()
        handler.wfile = Mock()
        return handler

    def dispatch(self, handler):
        with patch.object(BaseHTTPRequestHandler, 'handle', autospec=True,
                          side_effect=lambda current: current._send(200, b'ZOOMCONNECT')):
            handler.handle()

    def test_body_disconnects_close_only_the_failed_request(self):
        for handler_type in (DemoHandler, PositionHandler):
            for error_type in (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
                with self.subTest(handler=handler_type.__name__, error=error_type.__name__):
                    handler = self.handler(handler_type)
                    handler.wfile.write.side_effect = error_type('client disconnected')
                    self.dispatch(handler)
                    self.assertTrue(handler.close_connection)
                    handler.send_response.assert_called_once_with(200)

    def test_disconnect_during_headers_is_also_contained(self):
        for handler_type in (DemoHandler, PositionHandler):
            with self.subTest(handler=handler_type.__name__):
                handler = self.handler(handler_type)
                handler.end_headers.side_effect = ConnectionResetError('client disconnected')
                self.dispatch(handler)
                self.assertTrue(handler.close_connection)
                handler.wfile.write.assert_not_called()

    def test_unrelated_io_errors_are_not_hidden(self):
        for handler_type in (DemoHandler, PositionHandler):
            with self.subTest(handler=handler_type.__name__):
                handler = self.handler(handler_type)
                handler.wfile.write.side_effect = OSError(errno.ENOSPC, 'unrelated error')
                with self.assertRaises(OSError) as caught:
                    self.dispatch(handler)
                self.assertEqual(caught.exception.errno, errno.ENOSPC)
