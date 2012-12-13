import sys
import os
import fcntl

import string

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
        if self.opts.text_mode == 'auto':
            # This represents all printable, ASCII characters.  Only these
            # characters can pass through as a WebSocket text frame.
            self.textset = set(c for c in string.printable if ord(c) < 128)

    def received_message(self, websocket, m):
        if self.opts.verbosity >= 3:
            mode_msg = 'binary' if m.is_binary else 'text'
            print >> sys.stderr, "[received payload of length %d as %s]" % (len(m.data), mode_msg)
        sys.stdout.write(m.data)
        if self.opts.new_lines:
          sys.stdout.write("\n")
        sys.stdout.flush()

    def should_send_binary_frame(self, buf):
        if self.opts.text_mode == 'auto':
            return not set(buf).issubset(self.textset)
        elif self.opts.text_mode == 'text':
            return False
        else:
            return True

    def opened(self, websocket):
        def connect_stdin():
            fcntl.fcntl(sys.stdin, fcntl.F_SETFL, os.O_NONBLOCK)
            while True:
                wait_read(sys.stdin.fileno())
                buf = sys.stdin.read(4096)
                if len(buf) == 0:
                    break
                binary=self.should_send_binary_frame(buf)
                if self.opts.verbosity >= 3:
                    mode_msg = 'binary' if binary else 'text'
                    print >> sys.stderr, "[sending payload of length %d as %s]" % (len(buf), mode_msg)
                websocket.send(buf, binary)

            if self.opts.verbosity >= 2:
                print >> sys.stderr, '[EOF on stdin, shutting down input]'

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
