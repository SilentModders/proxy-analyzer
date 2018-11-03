#!/usr/bin/env python
import sys
from time import sleep
from threading import Thread
from examples.client import HelloClient
from examples.server import UpperServer


def main(argv):
    url = 'tls://localhost:7777'
    server = UpperServer.create_server(url)
    client = HelloClient.create_client(url)
    server.startup()
    server_thread = Thread(target=server.serve_one_client)
    server_thread.start()
    client.startup()
    server_thread.join()
    server.shutdown()
    
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
