import sys
import os
import fcntl

import gevent
from gevent.socket import wait_read

from ws4py.websocket import WebSocket

# Common stdio piping behaviour for the WebSocket handler.  Unfortunately due
# to ws4py OO failures, it's not possible to just share a common WebSocket
# class for this (WebSocketClient extends WebSocket, rather than simply
# delegating to one as WebSocketServer can).

def received_message(websocket, m):
    sys.stdout.write(m.data)
    sys.stdout.flush()

def opened(websocket):
    def connect_stdin():
        fcntl.fcntl(sys.stdin, fcntl.F_SETFL, os.O_NONBLOCK)
        while True:
            wait_read(sys.stdin.fileno())
            buf = sys.stdin.read(4096)
            if len(buf) == 0:
                break
            # XXX: Always send the data as binary, regardless of what it really is.
            websocket.send(buf, True)
        # stdin has been closed, but we'll keep the websocket open regardless
        # per netcat's behaviour.  This makes it much easier to use standard
        # shell script piping along with this tool.

    # XXX: We wait for the socket to open before reading stdin so that we
    # support behaviour like: echo foo | wssh -l ...
    gevent.spawn(connect_stdin)
