import gevent
from gevent.event import Event

from ws4py.server.geventserver import UpgradableWSGIHandler
from ws4py.server.wsgi.middleware import WebSocketUpgradeMiddleware
from ws4py.websocket import WebSocket

from . import common

# Handles the WebSocket once it has been upgraded by the HTTP layer.
class StdioPipedWebSocket(WebSocket):
    def received_message(self, m):
        common.received_message(self, m)

    def opened(self):
        common.opened(self)

    def closed(self, code, reason):
        pass

# Simple HTTP server implementing only one endpoint which upgrades to the
# stdin/stdout connected WebSocket.
class SimpleWebSocketServer(gevent.pywsgi.WSGIServer):
    handler_class = UpgradableWSGIHandler

    def __init__(self, host, port, path):
        gevent.pywsgi.WSGIServer.__init__(self, (host, port), log=None)

        self.path = path
        self.application = self
        self.shutdown_cond = Event()

        self.ws_upgrade = WebSocketUpgradeMiddleware(app=self.ws_handler,
                websocket_class=StdioPipedWebSocket)

    def __call__(self, environ, start_response):
        if self.path and environ['PATH_INFO'] != self.path:
            start_response('400 Not Found', [])
        else:
            # Hand-off the WebSocket upgrade negotiation to ws4py...
            return self.ws_upgrade(environ, start_response)

    def ws_handler(self, websocket):
        # Stop accepting new connections after we receive our first one (a la
        # netcat).
        self.stop_accepting()

        # Transfer control to the websocket_class.
        g = gevent.spawn(websocket.run)
        g.join()

        # WebSocket connection terminated, exit program.
        self.shutdown_cond.set()

    def handle_one_websocket(self):
        self.start()
        self.shutdown_cond.wait()

def listen(port, path=None):
    # XXX: Should add support to limit the listening interface.
    server = SimpleWebSocketServer('', port, path)
    server.handle_one_websocket()
