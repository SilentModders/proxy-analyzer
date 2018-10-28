#!/usr/bin/env python
import sys
import ssl
import socket


def main(argv):
    PORT = 7777
    ADDR = 'localhost'

    hostname = ADDR
    context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)
    context.load_verify_locations('private/cert.pem')
    with socket.create_connection((ADDR, PORT)) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            ssock.send(b"Hello\n")
            print(ssock.recv(1024))

    print('Done')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
