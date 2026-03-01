import re
from urllib.parse import urlparse

routes = []

def route(method, pattern):
    def wrapper(func):
        routes.append((method, re.compile(pattern), func))
        return func
    return wrapper

def dispatch(method, full_path, body):
    parsed = urlparse(full_path)
    path = parsed.path

    for m, pattern, handler in routes:
        match = pattern.match(path)
        if m == method and match:
            return handler(body, **match.groupdict())

    return b"HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\n\r\n"