import sys

import gevent
from gevent.event import Event

from ws4py.exc import HandshakeError
from ws4py.client.geventclient import WebSocketClient

from . import common

# Handles the WebSocket once it has been upgraded by the HTTP layer.
class StdioPipedWebSocketClient(WebSocketClient):
    shutdown_cond = Event()

    def received_message(self, m):
        common.received_message(self, m)

    def opened(self):
        common.opened(self)

    def closed(self, code, reason):
        self.shutdown_cond.set()

    def connect_and_wait(self):
        self.connect()
        self.shutdown_cond.wait()

def connect(host, port, path='/'):
    client = StdioPipedWebSocketClient("ws://{}:{}{}".format(host, port, path))
    try:
        client.connect_and_wait()
    except (IOError, HandshakeError), e:
        print >> sys.stderr, e
