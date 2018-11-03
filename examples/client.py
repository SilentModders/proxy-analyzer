#!/usr/bin/env python
import sys
from socketserver import StreamRequestHandler
from base_client import create_client


class HelloHandler(StreamRequestHandler):
    def handle(self):
        print('Connected to {}:{}'.format(*self.client_address))
        self.wfile.write(b'Hello!\n')
        data = self.rfile.readline().strip()
        print(data)


def main(argv):
    client = create_client('tls://localhost:7777', HelloHandler)
    client.startup()
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
