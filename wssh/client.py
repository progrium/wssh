import sys

import gevent
from gevent.event import Event

from ws4py.exc import HandshakeError
from ws4py.client.geventclient import WebSocketClient

from . import common

# Handles the WebSocket once it has been upgraded by the HTTP layer.
class StdioPipedWebSocketClient(WebSocketClient):

    def __init__(self, url, opts):
        WebSocketClient.__init__(self, url)

        self.shutdown_cond = Event()
        self.opts = opts
        self.iohelper = common.StdioPipedWebSocketHelper(self.shutdown_cond, opts)

    def received_message(self, m):
        self.iohelper.received_message(self, m)

    def opened(self):
        if self.opts.verbosity >= 1:
            peername, peerport = self.sock.getpeername()
            print >> sys.stderr, "[%s] %d open" % (peername, peerport)
        self.iohelper.opened(self)

    def closed(self, code, reason):
        self.shutdown_cond.set()

    def connect_and_wait(self):
        self.connect()
        self.shutdown_cond.wait()

def connect(args, host, port, path='/'):
    client = StdioPipedWebSocketClient("ws://{}:{}{}".format(host, port, path), args)
    try:
        client.connect_and_wait()
    except (IOError, HandshakeError), e:
        print >> sys.stderr, e
