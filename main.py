#!/usr/bin/env python
import sys
from time import sleep
from threading import Thread
from examples.server import main as server
from examples.client import main as client

def main(argv):
    url = 'tls://localhost:7777'
    server_thread = Thread(target=server, args=(url, ))
    client_thread = Thread(target=client, args=(url, ))
    server_thread.start()
    client_thread.start()
    client_thread.join()
    print('', end='', flush=True)
    server_thread.join()
    
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
