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
    if len(argv) < 2:
        print('Usage: {0} protocol-url\n\teg: {0} {1}'.format(
            argv[0], 'tls://localhost:443'
        ))
        return 1
    server = create_server(argv[1], UpperStreamHandler)
    server.startup()
    server.serve_forever()
    server.shutdown()

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
