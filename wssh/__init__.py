import sys

from ws4py.exc import HandshakeError
from ws4py.client.threadedclient import WebSocketClient

#WebSocketClient.upgrade_header = 'X-Upgrade'

class CommandLineClient(WebSocketClient):
    def opened(self, protocols, extensions):
        WebSocketClient.opened(self, protocols, extensions)
        print "Connected."
        
    def received_message(self, m):
        print m

def main():
    url = sys.argv[1]
    
    try:
        try:
            ws = CommandLineClient(url)
            ws.connect()
        except HandshakeError, e:
            print e
            sys.exit(1)
        while True:
            ws.send(raw_input())
    except KeyboardInterrupt:
        ws.close()
    