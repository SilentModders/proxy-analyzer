import io
from socketserver import _SocketWriter


class UDPStreamSocket(object):
    def __init__(self, socket, addr, data=None):
        self._sock = socket
        self.addr = addr
        self.data = data

    def send(self, data):
        return self._sock.sendto(data, self.addr)

    def sendall(self, data):
        with memoryview(data) as view, view.cast("B") as byte_view:
            amount = len(byte_view)
        if amount > 65507:
            raise ValueErrorError('Data exceeded max datagram size')
        count = self.send(data)
        if count < amount:
            raise IOError('Data exceeded max datagram size')

    def fileno(self):
        return self._sock.fileno()

    def makefile(self, mode, *args, **kwargs):
        if ('w' in mode) == ('r' in mode):  # Logical XNOR
            raise ValueError('Unsupported mode {}'.format(mode))
        if 'w' in mode:
            return _SocketWriter(self)
        if 'r' in mode:
            if 'b' in mode:
                factory = io.BytesIO
            else:
                factory = io.StringIO
            return factory(self.data)
