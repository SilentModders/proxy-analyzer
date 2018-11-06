#!/usr/bin/env python
import sys
from socketserver import StreamRequestHandler
from base_server import ServerProgram


class Handler(StreamRequestHandler):
    def handle(self):
        data = self.rfile.readline()
        data = data.lower().strip()
        if data == b'do you have a geiger counter?':
            msg = b'Mine is in the shop.\n'
        else:
            msg = b'...\n'
        self.wfile.write(msg)


class Server(ServerProgram):
    handler = Handler


if __name__ == '__main__':
    sys.exit(Server.main(sys.argv))
