import ssl
import socket
from socketserver import StreamRequestHandler
from utils import UDPStreamSocket, create_service, ServiceProgram


class BaseClient(object):
    def __init__(self, endpoint, handler):
        self.hostname, self.port = endpoint
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


def create_client(url, handler):
    clients = {
        'tcp': TCPClient,
        'udp': UDPClient,
        'tls': TLSClient,
    }
    return create_service(clients, url, handler)


class ClientProgram(ServiceProgram):
    handler = None

    @classmethod
    def create_client(cls, url):
        return create_client(url, cls.handler)

    @classmethod
    def run_service(cls, url):
        client = cls.create_client(url)
        client.startup()
