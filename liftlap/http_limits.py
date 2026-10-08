"""Local-demo admission limits; not provider cancellation or production capacity."""
from dataclasses import dataclass
from http.server import ThreadingHTTPServer
import math
import threading


@dataclass(frozen=True)
class HTTPLimits:
    max_connections: int = 8
    backlog: int = 8
    max_body_bytes: int = 16384
    read_timeout_seconds: float = 5.0

    def __post_init__(self):
        for value in (self.max_connections, self.backlog, self.max_body_bytes):
            if type(value) is not int or value <= 0:
                raise ValueError('HTTP capacities must be positive integers')
        if (isinstance(self.read_timeout_seconds, bool)
                or not math.isfinite(self.read_timeout_seconds)
                or self.read_timeout_seconds <= 0):
            raise ValueError('HTTP read timeout must be positive and finite')


class BoundedHTTPServer(ThreadingHTTPServer):
    """No application queue: excess connections get 503 before parsing or dispatch."""
    def __init__(self, address, handler, *, limits=None):
        self.limits = limits or HTTPLimits()
        self.request_queue_size = self.limits.backlog
        self._slots = threading.BoundedSemaphore(self.limits.max_connections)
        super().__init__(address, handler)

    def process_request(self, request, client_address):
        request.settimeout(self.limits.read_timeout_seconds)
        if not self._slots.acquire(blocking=False):
            try:
                request.sendall(b'HTTP/1.0 503 Service Unavailable\r\n'
                                b'Connection: close\r\nRetry-After: 1\r\n'
                                b'Content-Length: 0\r\n\r\n')
            except OSError:
                pass
            finally:
                self.shutdown_request(request)
            return
        try:
            super().process_request(request, client_address)
        except Exception:
            self._slots.release()
            raise

    def process_request_thread(self, request, client_address):
        try:
            super().process_request_thread(request, client_address)
        finally:
            self._slots.release()
