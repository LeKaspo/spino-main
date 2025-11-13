import socket
import json

TCP_IP = '172.30.32.1'
TCP_PORT = 50069
BUFFER_SIZE = 256

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

print("Server gestartet, wartet auf Verbindung...")
conn, addr = s.accept()
print(f"Verbindung von {addr} akzeptiert.")

try:
    while True:
        data = s.recv(BUFFER_SIZE)
        command = json.dumps(data).decode('utf-8')
        print(f"Command received: {command}")
except Exception:
    print(f"Exceptio geflogen!")
finally:
    s.close