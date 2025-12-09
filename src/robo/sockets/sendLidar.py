import socket
import time
import queue
import pickle
import struct
import threading
import sys

PORT = 50002

class lidarSänder:

    _instance = None
    _initialized = False
    IP = None

    def __new__(cls):
        print("New Object")
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        print("Initialize Singleton")
        if hasattr(self, "_initialized") and self._initialized:
            print("Singleton Already Initialized")
            return
        self._initialized = True

        self.scanQueue = queue.Queue()
        
        socket = self.connectSocket()
        if socket == None:
            sys.exit(0)

        sendThread = threading.Thread(target=self._sendLidarData, args=(socket,), daemon=True)
        sendThread.start()

    @staticmethod
    def getInstance():
        if lidarSänder._instance is None:
            lidarSänder._instance = lidarSänder()
        return lidarSänder._instance
    
    @staticmethod
    def setIP(IP):
        lidarSänder.IP = IP

    def connectSocket(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((lidarSänder.IP, PORT))
            return s
        except Exception as e:
            print(f"Unable to connect Lidar Socket: {e}")
            return None

    def _sendLidarData(self, socket):  
        try:
            while True:
                data = pickle.dumps(self.scanQueue.get())
                print(len(data))
                length = struct.pack('!I', len(data))
                socket.sendall(length + data)
                time.sleep(0.5)  # Send data every 500ms
        except Exception as e:
            print(f"Error: {e}")
        finally:
            socket.close()

    def putLidarData(self, data):
        self.scanQueue.put(data)
