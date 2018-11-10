#!/usr/bin/env python
import sys
from base_client import ClientPipe
from base_client import ClientProgram, ClientPipe
from utils import IterStream, BytesWriter


def byte_reader(stream):
    def _wrapper(stream):
        while True:
            data = next(stream)
            if data:
                yield data.encode()

    return IterStream(_wrapper(stream))


def main(argv):
    url = argv[1]
    pipe_in = byte_reader(sys.stdin)
    pipe_out = BytesWriter(sys.stdout)

    class Client(ClientProgram):
        handler = ClientPipe(pipe_in, pipe_out).make_handler

    Client().run_service(url)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
