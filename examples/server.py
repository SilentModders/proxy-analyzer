#!/usr/bin/env python
import sys
from socketserver import StreamRequestHandler
from base_server import ServerProgram


class UpperStreamHandler(StreamRequestHandler):
    def handle(self):
        while(True):
            data = self.rfile.readline()
            print(data, flush=True)
            if not data:
                return


class UpperServer(ServerProgram):
    handler = UpperStreamHandler


if __name__ == '__main__':
    sys.exit(UpperServer.main(sys.argv))
