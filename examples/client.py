#!/usr/bin/env python
import sys
from socketserver import StreamRequestHandler
from base_client import ClientProgram


class HelloHandler(StreamRequestHandler):
    def handle(self):
        print('Connected to {}:{}'.format(*self.client_address))
        self.wfile.write(b'Hello!\n')
        data = self.rfile.readline().strip()
        print(data)


class HelloClient(ClientProgram):
    handler = HelloHandler


if __name__ == '__main__':
    sys.exit(HelloClient.main(argv))
