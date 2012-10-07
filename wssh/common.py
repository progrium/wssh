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
class StdioPipedWebSocketHelper:
    def __init__(self, shutdown_cond, opts):
        self.shutdown_cond = shutdown_cond
        self.opts = opts

    def received_message(self, websocket, m):
        sys.stdout.write(m.data)
        sys.stdout.flush()

    def opened(self, websocket):
        def connect_stdin():
            fcntl.fcntl(sys.stdin, fcntl.F_SETFL, os.O_NONBLOCK)
            while True:
                wait_read(sys.stdin.fileno())
                buf = sys.stdin.read(4096)
                if len(buf) == 0:
                    break
                # XXX: Always send the data as binary, regardless of what it really is.
                websocket.send(buf, True)
            # If -q was passed, shutdown the program after EOF and the
            # specified delay.  Otherwise, keep the socket open even with no
            # more input flowing (consistent with netcat's behaviour).
            if self.opts.quit_on_eof is not None:
                if self.opts.quit_on_eof > 0:
                    gevent.sleep(self.opts.quit_on_eof)
                self.shutdown_cond.set()

        # XXX: We wait for the socket to open before reading stdin so that we
        # support behaviour like: echo foo | wssh -l ...
        gevent.spawn(connect_stdin)
