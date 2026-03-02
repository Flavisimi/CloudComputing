import re
from urllib.parse import urlparse, parse_qs

routes = []

def route(method, pattern):
    def wrapper(func):
        routes.append((method, re.compile(f"^{pattern}$"), func))
        return func
    return wrapper

def dispatch(method, full_path, body):
    parsed = urlparse(full_path)
    path = parsed.path
    query_params = {k: v[0] for k, v in parse_qs(parsed.query).items()}

    for m, pattern, handler in routes:
        match = pattern.match(path)
        if m == method and match:
            return handler(body, query_params=query_params, **match.groupdict())

    from http_utils import error_response
    return error_response(404, "Route not found", f"{method} {path} does not match any endpoint")