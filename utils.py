import io


class UDPStreamSocket(object):
    def __init__(self, socket, addr, data=None):
        self._sock = socket
        self.addr = addr
        self.data = data

    def send(self, data):
        return self._sock.sendto(data, self.addr)

    def sendall(self, data):
        count = 0
        with memoryview(data) as view, view.cast("B") as byte_view:
            amount = len(byte_view)
            while count < amount:
                    count += self.send(byte_view[count:])

    def makefile(self, mode, *args, **kwargs):
        if 'w' in mode:
            raise ValueError('UDP stream writing is not supported')
        elif 'r' in mode:
            if 'b' in mode:
                factory = io.BytesIO
            else:
                factory = io.StringIO
            return factory(self.data)
        else:
            raise ValueError('Unsupported mode {}'.format(mode))
