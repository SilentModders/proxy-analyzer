#!/usr/bin/env python
import re
import sys
import traceback
from socketserver import StreamRequestHandler
from base_server import ServerProgram

BREAK = b'\r\n'


class BytesWriter(object):
    def __init__(self, fp):
        self.fp = fp

    def write(self, data):
        self.fp.write(data.decode())


class Request(object):
    def __init__(self, method, url, http_ver=None, headers=None, data=None):
        self.method = method
        self.url = url
        self.http_ver = http_ver or b'HTTP/1.1'
        self.headers = headers or {}
        self.data = data

    def write(self, wfile):
        lines = [b'%s %s %s' % (self.method, self.url, self.http_ver)]
        for key, values in self.headers.items():
            for value in values:
                lines.append(b'%s: %s' % (key, value))
        lines += [b'', b'']
        wfile.write(BREAK.join(lines))
        if self.data:
            wfile.write(self.data)
        wfile.write(BREAK)

    def __str__(self):
        data = '{} {} {}'.format(
            self.method.decode(), self.url.decode(), self.http_ver.decode()
        )
        for key, value in self.headers.items():
            data += '\n{}: {}'.format(
                key.decode(), [_.decode() for _ in value]
            )
        return data


class HTTPReader(object):
    # FIXME: This all needs done with byte level IO
    # There are several over performance offenses
    max_header_lines = 32
    max_data_lines = 1024

    def read_head(self, rfile):
        request = b''
        headers = 0
        while(headers < self.max_header_lines):
            line = rfile.readline()
            # print(line, flush=True)
            request += line
            if not line or line == BREAK:
                break
            headers += 1
        return request

    def parse_method_line(self, line):
        words = line.split(b' ')
        if len(words) != 3:
            raise ValueError('Invalid method line')
       # TODO: Use namedtuple?
        return {
            'method': words[0].strip(),
            'url': words[1].strip(),
            'http_ver': words[2].strip(),
        }

    def parse_header(self, header):
        parts = header.split(b':', 1)
        if len(parts) != 2:
            raise ValueError('Invalid header')
        # TODO: Use namedtuple?
        return {
            'key': parts[0].strip(),
            'value': parts[1].strip(),
        }

    def parse_head(self, data):
        data = [_ for _ in data.split(BREAK) if _]
        if not data:
            return None
        method_line_data = self.parse_method_line(data[0])
        method = method_line_data['method']
        url = method_line_data['url']
        http_ver = method_line_data['http_ver']
        headers = {}
        if len(data) > 1:
            for header in data[1:]:
                header_data = self.parse_header(header)
                key = header_data['key'].lower()
                value = header_data['value']
                headers[key] = headers.get(key, []) + [value]
        return Request(method, url, http_ver, headers)

    def read_data(self, rfile):
        data = b''
        lines = 0
        while(lines < self.max_data_lines):
            line = rfile.readline()
            data += line
            if not line:
                return data
            lines += 1

    def read_request(self, rfile):
        head = self.read_head(rfile)
        request = self.parse_head(head)
        if not request:
            return None
        length_headers = request.headers.get(b'content-length', [])
        if length_headers:
            if len(length_headers) > 1:
                raise ValueError('"content-length" may only appear once')
            else:
                try:
                    length = int(length_headers[0])
                except ValueError:
                    raise ValueError('Invalid "content-length"')
                request.data = self.read_data(rfile)
        return request


class Handler(StreamRequestHandler):
    canned_500 = b'HTTP 500 E\r\nConnection: Closed\r\n\r\nGoodbye'

    def require_request_host(self, request):
        hosts = request.headers.get(b'host', [])
        if not hosts:
            raise ValueError('"host" header is required')
        elif len(hosts) > 1:
            raise ValueError('"host" may only appear once')
        else:
            return hosts[0]

    def infer_host(self, host_header):
        parts = host_header.split(b':')
        if len(parts) > 2 or len(parts) < 1:
            raise ValueError('Malformed host: {}'.format(host_header))
        elif len(parts) == 1:
            host = parts[0]
            port = self.server.bind[1]
        elif len(parst) == 2:
            host, port = parts
        return host, port

    def handle(self):
        try:
            request = HTTPReader().read_request(self.rfile)
            # print('\nRequest:')
            # print(str(request), flush=True)
            if request:
                dst_header = self.require_request_host(request)
                dst_addr = self.infer_host(dst_header)
                print('---------')
                print('To', dst_addr)
                print('---------')
                request.write(BytesWriter(sys.stdout))
                print('---------')
        finally:
            try:
                self.wfile.write(self.canned_500)
            except:
                pass
            sys.stderr.flush()
            sys.stdout.flush()


class Server(ServerProgram):
    handler = Handler


if __name__ == '__main__':
    sys.exit(Server.main(sys.argv))
