import json

STATUS_TEXT = {
    200: "OK",
    201: "Created",
    400: "Bad Request",
    404: "Not Found",
    500: "Internal Server Error"
}

def json_response(data, status=200):
    body = json.dumps(data, default=str)
    return (
        f"HTTP/1.1 {status} {STATUS_TEXT.get(status,'')}\r\n"
        f"Content-Type: application/json\r\n"
        f"Content-Length: {len(body)}\r\n\r\n"
        f"{body}"
    ).encode()