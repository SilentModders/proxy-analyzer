#!/usr/bin/env python
import sys
import ssl
import socket
from socketserver import StreamRequestHandler
from utils import UDPStreamSocket


class BaseClient(object):
    def __init__(self, hostname, port, handler):
        self.hostname = hostname
        self.port = port
        self.handler = handler

    def make_socket(self):
        raise NotImplementedError

    def startup(self):
        with self.make_socket() as sock:
            self.handler(sock, (self.hostname, self.port), self)


class TCPClient(BaseClient):
    def make_socket(self):
        sock = socket.create_connection((self.hostname, self.port))
        return sock


class UDPClient(BaseClient):
    def make_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        server_addr = self.hostname, self.port
        usock = UDPStreamSocket(ssock, server_addr, self_close=True)
        return usock


class TLSMixIn(object):
    certifcate_path = 'private/server.pem'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.context = ssl.create_default_context(
           purpose=ssl.Purpose.SERVER_AUTH)
        self.context.load_verify_locations(self.certifcate_path)

    def make_socket(self):
        sock = super().make_socket()
        ssock = self.context.wrap_socket(sock, server_hostname=self.hostname)
        return ssock


class TLSClient(TLSMixIn, TCPClient):
    pass


class HelloHandler(StreamRequestHandler):
    def handle(self):
        print('Connected to {}:{}'.format(*self.client_address))
        self.wfile.write(b'Hello!\n')
        data = self.rfile.readline().strip()
        print(data)


def main(argv):
    PORT = 7777
    ADDR = 'localhost'

    client = TLSClient(ADDR, PORT, HelloHandler)
    client.startup()

    print('Done')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
