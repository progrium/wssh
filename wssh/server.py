import sys

import gevent
from gevent.event import Event

from ws4py.server.geventserver import UpgradableWSGIHandler
from ws4py.server.wsgi.middleware import WebSocketUpgradeMiddleware
from ws4py.websocket import WebSocket

from . import common

# Handles the WebSocket once it has been upgraded by the HTTP layer.
class StdioPipedWebSocket(WebSocket):
    def my_setup(self, helper, opts):
        self.iohelper = helper
        self.opts = opts

    def received_message(self, m):
        self.iohelper.received_message(self, m)

    def opened(self):
        if self.opts.verbosity >= 1:
            peername, peerport = self.sock.getpeername()
            print >> sys.stderr, "connect from [%s] %d" % (peername, peerport)
        self.iohelper.opened(self)

    def closed(self, code, reason):
        pass

# Simple HTTP server implementing only one endpoint which upgrades to the
# stdin/stdout connected WebSocket.
class SimpleWebSocketServer(gevent.pywsgi.WSGIServer):
    handler_class = UpgradableWSGIHandler

    def __init__(self, host, port, path, opts):
        gevent.pywsgi.WSGIServer.__init__(self, (host, port), log=None)

        self.host = host
        self.port = port
        self.path = path
        self.application = self

        self.shutdown_cond = Event()
        self.opts = opts
        self.iohelper = common.StdioPipedWebSocketHelper(self.shutdown_cond, opts)

        self.ws_upgrade = WebSocketUpgradeMiddleware(app=self.ws_handler,
                websocket_class=StdioPipedWebSocket)

    def __call__(self, environ, start_response):
        request_path = environ['PATH_INFO']
        if self.path and request_path != self.path:
            if self.opts.verbosity >= 2:
                print "refusing to serve request for path '%s'" % request_path
            start_response('400 Not Found', [])
            return ['']
        else:
            # Hand-off the WebSocket upgrade negotiation to ws4py...
            return self.ws_upgrade(environ, start_response)

    def ws_handler(self, websocket):
        # Stop accepting new connections after we receive our first one (a la
        # netcat).
        self.stop_accepting()

        # Pass custom arguments over to our WebSocket instance.  The design of
        # gevent's pywsgi layer leaves a lot to be desired in terms of proper
        # dependency injection patterns...
        websocket.my_setup(self.iohelper, self.opts)

        # Transfer control to the websocket_class.
        g = gevent.spawn(websocket.run)
        g.join()

        # WebSocket connection terminated, exit program.
        self.shutdown_cond.set()

    def handle_one_websocket(self):
        self.start()
        if self.opts.verbosity >= 1:
            if self.path:
                path_stmt = "path '%s'" % (self.path)
            else:
                path_stmt = 'all paths'
            print >> sys.stderr, 'listening on [any] %d for %s...' % (self.port, path_stmt)
        self.shutdown_cond.wait()

def listen(args, port, path):
    # XXX: Should add support to limit the listening interface.
    server = SimpleWebSocketServer('', port, path, args)
    try:
        server.handle_one_websocket()
    except IOError, e:
        print >> sys.stderr, e
