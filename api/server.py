import socket
import threading
from router import dispatch
import controllers

HOST = "0.0.0.0"
PORT = 8080

def receive(conn):
    data = b""
    while b"\r\n\r\n" not in data:
        chunk = conn.recv(4096)
        if not chunk:
            break
        data += chunk

    if b"\r\n\r\n" not in data:
        raise ValueError("Malformed HTTP request: missing header terminator")

    header_raw, body = data.split(b"\r\n\r\n", 1)
    header_lines = header_raw.decode(errors="replace").split("\r\n")

    try:
        method, path, _ = header_lines[0].split(" ", 2)
    except ValueError:
        raise ValueError(f"Malformed request line: {header_lines[0]!r}")

    content_length = 0
    for line in header_lines[1:]:
        if line.lower().startswith("content-length:"):
            try:
                content_length = int(line.split(":", 1)[1].strip())
            except ValueError:
                raise ValueError("Invalid Content-Length header")

    while len(body) < content_length:
        chunk = conn.recv(4096)
        if not chunk:
            break
        body += chunk

    return method, path, body.decode(errors="replace")


def client(conn):
    try:
        method, path, body = receive(conn)
        response = dispatch(method, path, body)
        conn.sendall(response)
    except Exception as e:
        from http_utils import error_response
        conn.sendall(error_response(500, "Internal server error", str(e)))
    finally:
        conn.close()


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    print(f"API running on {PORT}")
    while True:
        conn, _ = s.accept()
        threading.Thread(target=client, args=(conn,), daemon=True).start()