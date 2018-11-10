#!/usr/bin/env python
import sys
from base_client import ClientProgram, ClientPipe
from utils import BytesWriter, BytesReader


def main(argv):
    url = argv[1]
    pipe_in = BytesReader(sys.stdin)
    pipe_out = BytesWriter(sys.stdout)

    class Client(ClientProgram):
        handler = ClientPipe(pipe_in, pipe_out).make_handler

    Client().run_service(url)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
