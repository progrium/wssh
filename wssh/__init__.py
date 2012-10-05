import sys
from urlparse import urlparse

from . import client
from . import server

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('url', metavar='URL', type=str,
            help='URL of a WebSocket endpoint with or without ws:// or wss://')
    parser.add_argument('-l', action='store_true', 
            help='start in listen mode, creating a server')
    args = parser.parse_args()

    url = args.url
    if not url.startswith("ws://") and not url.startswith("wss://"):
        url = "ws://{}".format(url)
    url = urlparse(url)

    port = url.port
    if port == None:
        if url.scheme == "wss":
            port = 443
        else:
            port = 80

    if args.l:
        server.listen(port, url.path)
    else:
        client.connect(url.hostname, port, url.path)

    
