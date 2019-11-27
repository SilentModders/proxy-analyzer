import sys
import ssl
import socket
from socketserver import StreamRequestHandler
from threading import Thread
import traceback
from utils import UDPStreamSocket, create_service, ServiceProgram


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
            try:
                self.serve_one_client()
            except KeyboardInterrupt:
                raise
            except:
                traceback.print_exc()
                sys.stderr.flush()

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
    @staticmethod
    def _wrapper(target):
        def wrapper(*args, **kwargs):
            try:
                target(*args, **kwargs)
            except:  # Don't ask me why we need this for threads
                traceback.print_exc()
                sys.stderr.flush()
                raise

        return wrapper

    def handle_client(self, client, address):
        target = self._wrapper(super().handle_client)
        thread = Thread(target=target, args=(client, address))
        thread.start()


class TLSMixIn(object):
    certificate_path = 'private/server.pem'
    private_key_path = 'private/server.key'
    dh_params_path = 'private/dh_params.pem'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.context = ssl.create_default_context(
            purpose=ssl.Purpose.CLIENT_AUTH)
        self.context.load_cert_chain(
            self.certificate_path, self.private_key_path)
        self.context.load_dh_params(self.dh_params_path)

    def make_socket(self):
        sock = super().make_socket()
        ssock = self.context.wrap_socket(sock, server_side=True)
        return ssock


class TCPServer(ThreadingMixIn, BaseServer):
    def make_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Needed for rapid server prototyping but
        # should probably be off by default
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return sock

    def do_accept(self):
        return self.socket.accept()


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


class TLSServer(TLSMixIn, TCPServer):
    pass


def create_server(url, handler):
    servers = {
        'tcp': TCPServer,
        'udp': UDPServer,
        'tls': TLSServer,
    }
    return create_service(servers, url, handler)


class UpperStreamHandler(StreamRequestHandler):
    def handle(self):
        data = self.rfile.readline()
        print("{} wrote:".format(self.client_address[0]))
        print(data)
        self.wfile.write(data.upper())


class ServerProgram(ServiceProgram):
    handler = None

    @classmethod
    def create_server(cls, url):
        return create_server(url, cls.handler)

    @classmethod
    def run_service(cls, url):
        server = cls.create_server(url)
        server.startup()
        server.serve_forever()
        server.shutdown()
