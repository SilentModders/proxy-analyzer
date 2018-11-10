import io
import re


class SocketWriter(io.BufferedIOBase):
    """
    Lifted straight from cpython.
    Allows file writing on non-stream sockets
    """

    def __init__(self, sock):
        self._sock = sock

    def writable(self):
        return True

    def write(self, b):
        self._sock.sendall(b)
        with memoryview(b) as view:
            return view.nbytes

    def fileno(self):
        return self._sock.fileno()


class UDPStreamSocket(object):
    def __init__(self, socket, addr, data=None, self_close=False):
        self._sock = socket
        self.addr = addr
        self.data = data
        self.self_close = self_close

    def __enter__(self):
        pass

    def __exit__(self, exc_type, value, traceback):
        self.close()

    def close(self):
        if self.self_close:
            self._sock.close()

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
            return SocketWriter(self)
        if 'r' in mode:
            if self.data is not None:
                if 'b' in mode:
                    factory = io.BytesIO
                else:
                    factory = io.StringIO
                return factory(self.data)
            else:
                return self._sock.makefile(mode)


def parse_scheme(url):
    scheme_rx = r'(?P<protocol>[^:/]+)://(?P<host>[^:/]+):(?P<port>[\d]+)/?'
    match = re.match(scheme_rx, url)
    if not match:
        msg = 'Invalid network scheme {}'.format(url)
        msg += ', valid example: tls://www.example.com:443'
        raise ValueError(msg)
    else:
        return (
            match.group('protocol'), match.group('host'), match.group('port')
        )


def create_service(services, url, handler):
    protocol, host, port = parse_scheme(url)
    protocol = protocol.lower()
    port = int(port)
    if protocol not in services:
        msg = 'Unsupported protocol {}'.format(protocol)
        msg += ', choices are: {}'.format(servers.keys())
        raise ValueError(msg)
    else:
        return services[protocol]((host, port), handler)


class ServiceProgram(object):
    @classmethod
    def run_service(cls, url):
        raise NotImplementedError

    @classmethod
    def main(cls, argv):
        if len(argv) < 2:
            print('Usage: {0} protocol-url\n\teg: {0} {1}'.format(
                argv[0], 'tls://localhost:443'
            ))
            return 1
        cls.run_service(argv[1])
        return 0


class BytesWriter(object):
    """
    For printing byte strings
    """

    def __init__(self, fp):
        self.fp = fp

    def write(self, data):
        self.fp.write(data.decode())
        self.fp.flush()


class IterStream(object):
    def __init__(self, iterator):
        self.iterator = iterator
        self.buffer = b''

    def read(self, size):
        while len(self.buffer) < size:
            try:
                self.buffer += next(self.iterator)
            except StopIteration:
                break

        data = self.buffer[:size]
        self.buffer = self.buffer[size:]
        return data
