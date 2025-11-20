import socket
import time

PORT = 50001
IP = 'localhost'

if __name__ == "__main__":
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((IP, PORT))
    while True:
        client.send("Audio Data".encode())
        time.sleep(10)