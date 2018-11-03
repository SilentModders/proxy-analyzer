#!/usr/bin/env python
import sys
from socketserver import StreamRequestHandler
from base_server import ServerProgram


class UpperStreamHandler(StreamRequestHandler):
    def handle(self):
        data = self.rfile.readline()
        print("{} wrote:".format(self.client_address[0]))
        print(data)
        self.wfile.write(data.upper())


class UpperServer(ServerProgram):
    handler = UpperStreamHandler


if __name__ == '__main__':
    sys.exit(UpperServer.main(argv))
