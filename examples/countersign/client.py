#!/usr/bin/env python
import sys
from socketserver import StreamRequestHandler
from base_client import ClientProgram


class Handler(StreamRequestHandler):
    def handle(self):
        self.wfile.write(b'Do you have a Geiger counter?\n')
        data = self.rfile.readline().strip()
        print(data)


class Client(ClientProgram):
    handler = Handler


if __name__ == '__main__':
    sys.exit(Client.main(sys.argv))
