#!/usr/bin/env python
import sys
import ssl
import socket
from socketserver import StreamRequestHandler
from threading import Thread
from utils import UDPStreamSocket


class BaseServer(object):
    def __init__(self, bind, handler):
        self.bind = bind
        self.handler = handler
        self._shutdown = False
        self.socket = None

    def startup(self):
        self.socket = self.make_socket()
        self.do_bind()
        self.do_listen()

    def do_bind(self):
        self.socket.bind(self.bind)

    def do_listen(self):
        self.socket.listen()

    def serve_one_client(self):
        (client, address) = self.do_accept()
        with client:
            self.handle_client(client, address)

    def handle_client(self, client, address):
        self.handler(client, address, self)

    def serve_forever(self):
        while not self._shutdown:
            self.serve_one_client()

    def shutdown(self):
        if self.socket is not None:
            self.socket.close()
            self.socket = None
        self._shutdown = True

    def make_socket(self):
        raise NotImplementedError

    def accept_client(self):
        raise NotImplementedError


class ThreadingMixIn(object):
    def handle_client(self, client, address):
        thread = Thread(target=super().handle_client, args=(client, address))
        thread.start()


class TLSMixIn(object):
    certificate_path = 'private/cert.pem'
    private_key_path = 'private/private.key'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.context = ssl.create_default_context(
            purpose=ssl.Purpose.CLIENT_AUTH)
        self.context.load_cert_chain(
            self.certificate_path, self.private_key_path)

    def make_socket(self):
        sock = super().make_socket()
        ssock = self.context.wrap_socket(sock, server_side=True)
        return ssock


class TCPServer(ThreadingMixIn, BaseServer):
    def make_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return sock

    def do_accept(self):
        return self.socket.accept()


class TLSServer(TLSMixIn, TCPServer):
    pass


class UDPServer(ThreadingMixIn, BaseServer):
    # The calculated max payload size is 65507
    # Let's stay under that
    max_packet_size = 32768

    def make_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return sock

    def do_listen(self):
        pass

    def do_accept(self):
        data, client_addr = self.socket.recvfrom(self.max_packet_size)
        sock = UDPStreamSocket(self.socket, client_addr, data)
        return sock, client_addr


class UpperStreamHandler(StreamRequestHandler):
    def handle(self):
        data = self.rfile.readline()
        print("{} wrote:".format(self.client_address[0]))
        print(data)
        self.wfile.write(data.upper())


def main(argv):
    PORT = 7777
    BIND = '0.0.0.0'

    server = TLSServer((BIND, PORT), UpperStreamHandler)
    server.startup()
    server.serve_one_client()
    server.shutdown()

    print('Done')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
