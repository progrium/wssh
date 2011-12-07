import sys

from ws4py.exc import HandshakeError
from ws4py.client.geventclient import WebSocketClient

import os
import fcntl
import gevent
from gevent.socket import wait_read

def connect(host, port, path='/'):
    try:
        try:
            ws = WebSocketClient("ws://{}:{}{}".format(
                    host, port, path))
            ws.connect()
            def outgoing():
                fcntl.fcntl(sys.stdin, fcntl.F_SETFL, os.O_NONBLOCK)
                while True:
                    wait_read(sys.stdin.fileno())
                    line = sys.stdin.readline()
                    ws.send(line.strip())
            def incoming():
                while True:
                    print ws.receive()
            gevent.joinall([
                gevent.spawn(outgoing),
                gevent.spawn(incoming),
            ])
        except (IOError, HandshakeError), e:
            print e
            sys.exit(1)
    except KeyboardInterrupt:
        ws.close()

