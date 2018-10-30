#!/usr/bin/env python
import sys
import ssl
import socket
from socketserver import UDPServer, StreamRequestHandler
from threading import Thread
from utils import UDPStreamSocket


class SSLTCPServer(object):
    def __init__(self, bind, handler):
        self.bind = bind
        self.handler = handler
        self._shutdown = False
        self.socket = None

        #FIXME: SSL should be a subclass
        self.context = ssl.create_default_context(
            purpose=ssl.Purpose.CLIENT_AUTH)
        self.context.load_cert_chain('private/cert.pem', 'private/private.key')

    def startup(self, backlog=5):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.bind)
        self.socket.listen(backlog)
        self.socket = self.context.wrap_socket(self.socket, server_side=True)

    def serve_one_client(self):
        (client, address) = self.socket.accept()
        with client:
            self.handle_client(client, address)

    def handle_client(self, client, address):
        thread = Thread(target=self.handler, args=(client, address, self))
        thread.start()

    def serve_forever(self):
        while not self._shutdown:
            self.serve_one_client()

    def shutdown(self):
        if self.socket is not None:
            self.socket.close()
            self.socket = None
        self._shutdown = True


class UpperStreamHandler(StreamRequestHandler):
    def handle(self):
        data = self.rfile.readline()
        print("{} wrote:".format(self.client_address[0]))
        print(data)
        self.wfile.write(data.upper())


def udp_stream_wrap(client, client_addr, server):
    data, socket = client
    stream = UDPStreamSocket(socket, client_addr)
    UpperStreamHandler(stream, client_addr, server)


class StreamUDPServer(UDPServer):
    # The calculated max payload size is 65507
    # Let's stay under that
    max_packet_size = 32768

    def get_request(self):
        data, client_addr = self.socket.recvfrom(
            self.max_packet_size, socket.MSG_PEEK)
        return (data, self.socket), client_addr


def main(argv):
    PORT = 7777
    BIND = '0.0.0.0'

    server = StreamUDPServer((BIND, PORT), udp_stream_wrap)
    server.handle_request()

    print('Done')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
