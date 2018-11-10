#!/usr/bin/env python
import re
import sys
import traceback
from socketserver import StreamRequestHandler
from base_server import ServerProgram, TLSServer
from base_client import ClientProgram, ClientPipe
from http import Request, HTTPReader
from utils import BytesWriter


class Handler(StreamRequestHandler):
    canned_500 = b'HTTP/1.1 500 E\r\nConnection: Closed\r\n\r\nGoodbye'

    def connect_upstream(self, url, pipe_rfile, pipe_wfile):
        class Client(ClientProgram):
            handler = ClientPipe(pipe_rfile, pipe_wfile).make_handler

        Client().run_service(url)

    def require_request_host(self, request):
        hosts = request.headers.get(b'host', [])
        if not hosts:
            raise ValueError('"host" header is required')
        elif len(hosts) > 1:
            raise ValueError('"host" may only appear once')
        else:
            return hosts[0]

    def infer_host(self, host_header):
        parts = host_header.split(b':')
        if len(parts) > 2 or len(parts) < 1:
            raise ValueError('Malformed host: {}'.format(host_header))
        elif len(parts) == 1:
            host = parts[0]
            port = self.server.bind[1]
        elif len(parts) == 2:
            host, port = parts
            try:
                port = int(port)
            except ValueError:
                raise ValueError(
                    'Invalid port on host header: {}'.format(host_header)
                )

        return host.strip().decode(), port

    def infer_protocol(self):
        isTLS = isinstance(self.server, TLSServer)
        return 'tls' if isTLS else 'tcp'

    def handle(self):
        wrote_response = False
        try:
            request = HTTPReader().read_request(self.rfile)
            # print('\nRequest:')
            # print(str(request), flush=True)
            if request:
                dst_header = self.require_request_host(request)
                dst_host, dst_port = self.infer_host(dst_header)
                dst_proto = self.infer_protocol()
                dst_url = '{}://{}:{}'.format(dst_proto, dst_host, dst_port)
                print('----------------------')
                print(dst_url)
                print('----------------------')
                # HACK
                request.headers[b'connection'] = [b'close']
                self.connect_upstream(dst_url, request.as_file(), self.wfile)
                wrote_response = True
        finally:
            try:
                if not wrote_response:
                    self.wfile.write(self.canned_500)
            except:
                pass


class Server(ServerProgram):
    handler = Handler


if __name__ == '__main__':
    sys.exit(Server.main(sys.argv))
