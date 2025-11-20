import socket
import time

PORT = 50002
IP = 'localhost'

if __name__ == "__main__":
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((IP, PORT))
    while True:
        client.send("Lidar Data".encode())
        time.sleep(10)

