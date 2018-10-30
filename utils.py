class UDPStreamSocket(object):
    def __init__(self, socket, addr):
        self._sock = socket
        self.addr = addr

    def send(self, data):
        return self._sock.sendto(data, self.addr)

    def makefile(self, mode, bufsize):
        return self._sock.makefile(mode, bufsize)

    def sendall(self, data):
        count = 0
        with memoryview(data) as view, view.cast("B") as byte_view:
            amount = len(byte_view)
            while count < amount:
                    count += self.send(byte_view[count:])
