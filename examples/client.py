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


def client_service(url):
    return create_client(url, HelloHandler)


def main(argv):
    if len(argv) < 2:
        print('Usage: {0} protocol-url\n\teg: {0} {1}'.format(
            argv[0], 'tls://localhost:443'
        ))
        return 1
    client = client_service(argv[1])
    client.startup()
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
