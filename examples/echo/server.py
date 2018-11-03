#!/usr/bin/env python
import sys
from socketserver import StreamRequestHandler
from base_server import ServerProgram


class Handler(StreamRequestHandler):
    def handle(self):
        data = self.rfile.readline()
        self.wfile.write(data)


class Server(ServerProgram):
    handler = Handler


if __name__ == '__main__':
    sys.exit(Server.main(sys.argv))
