#!/usr/bin/env python
import sys
from socketserver import StreamRequestHandler
from base_server import create_server


class UpperStreamHandler(StreamRequestHandler):
    def handle(self):
        data = self.rfile.readline()
        print("{} wrote:".format(self.client_address[0]))
        print(data)
        self.wfile.write(data.upper())


def main(argv):
    server = create_server('tls://localhost:7777', UpperStreamHandler)
    server.startup()
    server.serve_forever()
    server.shutdown()

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
