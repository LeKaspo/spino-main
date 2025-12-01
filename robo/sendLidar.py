import socket
import time
import queue
import json
import threading

PORT = 50002
IP = '192.168.0.229'

def sendLidarData():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((IP, PORT))
    while True:
        client.send("Lidar Data".encode())
        time.sleep(10)

if __name__ == "__main__":
    scanQueue = queue.Queue()