import socket
import time

PORT = 50003
IP = 'localhost'

if __name__ == "__main__":
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((IP, PORT))
    while True:
        data = client.recv(256)
        if not data: break
        print(f"Received {data.decode()}")