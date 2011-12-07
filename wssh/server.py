import sys
import os
import fcntl
import gevent
from gevent.socket import wait_read
from urlparse import urlparse

import gevent

from ws4py.exc import HandshakeError
from ws4py.server.geventserver import WebSocketServer

def handler(path):
    def handle(websocket, environ):
        if path and environ.get('PATH_INFO', '') != path:
            websocket.close()
            return
        def incoming():
            while True:
                msg = websocket.receive()
                if msg is not None:
                    print msg
                else:
                    websocket.close()
        def outgoing():
            fcntl.fcntl(sys.stdin, fcntl.F_SETFL, os.O_NONBLOCK)
            while True:
                wait_read(sys.stdin.fileno())
                line = sys.stdin.readline()
                websocket.send(line.strip())
        gevent.joinall([
            gevent.spawn(incoming),
            gevent.spawn(outgoing),
        ])
    return handle

def listen(port, path=None):
    server = WebSocketServer(('', port), handler(path))
    server.serve_forever()
