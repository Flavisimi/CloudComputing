import socket
import threading
from router import dispatch
import controllers
HOST = "0.0.0.0"
PORT = 8080

def receive(conn):
    data = b""

    while b"\r\n\r\n" not in data:
        chunk = conn.recv(1024)
        if not chunk:
            break
        data += chunk

    header, body = data.split(b"\r\n\r\n", 1)

    header_lines = header.decode().split("\r\n")
    method, path, _ = header_lines[0].split(" ")

    content_length = 0
    for line in header_lines[1:]:
        if "Content-Length" in line:
            content_length = int(line.split(":")[1].strip())

    while len(body) < content_length:
        body += conn.recv(1024)

    return method, path, body.decode()

def client(conn):
    try:
        method, path, body = receive(conn)
        response = dispatch(method, path, body)
        conn.sendall(response)
    except Exception as e:
        error = f"HTTP/1.1 500 Internal Server Error\r\n\r\n{str(e)}"
        conn.sendall(error.encode())
    finally:
        conn.close()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print("API running on 8080")
    while True:
        conn, _ = s.accept()
        threading.Thread(target=client, args=(conn,)).start()