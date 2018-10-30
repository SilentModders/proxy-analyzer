#!/usr/bin/env python
import sys
import ssl
import socket
from socketserver import StreamRequestHandler


class SSLTCPClient(object):
    def __init__(self, hostname, port, handler):
        self.hostname = hostname
        self.port = port
        self.handler = handler

        #FIXME: SSL should be a subclass
        self.context = ssl.create_default_context(
            purpose=ssl.Purpose.SERVER_AUTH)
        self.context.load_verify_locations('private/cert.pem')

    def startup(self):
        with socket.create_connection((self.hostname, self.port)) as sock:
            with self.context.wrap_socket(
                sock, server_hostname=self.hostname
            ) as ssock:
                self.handler(ssock, (self.hostname, self.port), self)


class HelloHandler(StreamRequestHandler):
    def handle(self):
        print('Connected to {}:{}'.format(*self.client_address))
        self.wfile.write(b'Hello!\n')
        self.data = self.rfile.readline().strip()
        print(self.data)


def main(argv):
    PORT = 7777
    ADDR = 'localhost'

    client = SSLTCPClient(ADDR, PORT, HelloHandler)
    client.startup()

    print('Done')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
