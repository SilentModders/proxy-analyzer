BREAK = b'\r\n'


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
    max_data_length = 1048576

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

    def read_data(self, rfile, length):
        length = min(self.max_data_length, length)
        return rfile.read(length)

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
                request.data = self.read_data(rfile, length)
        return request
