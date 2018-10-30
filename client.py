#!/usr/bin/env python
import sys
import ssl
import socket
from socketserver import StreamRequestHandler
from utils import UDPStreamSocket


class SSLTCPClient(object):
    def __init__(self, hostname, port, handler):
        self.hostname = hostname
        self.port = port
        self.handler = handler

        # FIXME: SSL should be a subclass
        self.context = ssl.create_default_context(
            purpose=ssl.Purpose.SERVER_AUTH)
        self.context.load_verify_locations('private/cert.pem')

    def startup(self):
        with socket.create_connection((self.hostname, self.port)) as sock:
            with self.context.wrap_socket(
                sock, server_hostname=self.hostname
            ) as ssock:
                self.handler(ssock, (self.hostname, self.port), self)


class UDPClient(object):
    def __init__(self, hostname, port, handler):
        self.hostname = hostname
        self.port = port
        self.handler = handler

    def startup(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0) as ssock:
            usock = UDPStreamSocket(ssock, (self.hostname, self.port))
            self.handler(usock, (self.hostname, self.port), self)


class HelloHandler(StreamRequestHandler):
    def handle(self):
        print('Connected to {}:{}'.format(*self.client_address))
        self.wfile.write(b'Hello!\n')
        data = self.rfile.readline().strip()
        print(data)


def main(argv):
    PORT = 7777
    ADDR = 'localhost'

    client = UDPClient(ADDR, PORT, HelloHandler)
    client.startup()

    print('Done')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
