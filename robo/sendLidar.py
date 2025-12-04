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
    try:
        while True:
            client.send("Lidar Data".encode())
            time.sleep(10)
    except Exception as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("Programm closed")
    finally:
        client.close()

if __name__ == "__main__":
    scanQueue = queue.Queue()