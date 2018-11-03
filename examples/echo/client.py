#!/usr/bin/env python
import sys
from socketserver import StreamRequestHandler
from base_client import ClientProgram


class Handler(StreamRequestHandler):
    def handle(self):
        self.wfile.write(sys.stdin.readline().encode())
        data = self.rfile.readline()
        print(data.decode())


class Client(ClientProgram):
    handler = Handler


if __name__ == '__main__':
    sys.exit(Client.main(sys.argv))
