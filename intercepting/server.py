#!/usr/bin/env python
import re
import sys
import traceback
from socketserver import StreamRequestHandler
from base_server import ServerProgram
from http import Request, HTTPReader
from utils import BytesWriter


class Handler(StreamRequestHandler):
    canned_500 = b'HTTP/1.1 500 E\r\nConnection: Closed\r\n\r\nGoodbye'

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

    def handle(self):
        try:
            request = HTTPReader().read_request(self.rfile)
            # print('\nRequest:')
            # print(str(request), flush=True)
            if request:
                dst_header = self.require_request_host(request)
                dst_addr = self.infer_host(dst_header)
                print('---------')
                print('To', dst_addr)
                print('---------')
                request.write(BytesWriter(sys.stdout))
                print('---------')
        finally:
            try:
                self.wfile.write(self.canned_500)
            except:
                pass
            sys.stderr.flush()
            sys.stdout.flush()


class Server(ServerProgram):
    handler = Handler


if __name__ == '__main__':
    sys.exit(Server.main(sys.argv))
