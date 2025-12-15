import socket
import time
import queue
import pickle
import struct
import threading
import sys
from robo.lidar.mutex import Mutex

PORT = 50002

class lidarSänder:

    _instance = None
    _initialized = False
    IP = None

    def __new__(cls):
        print("Initializing new LidarSänder Singleton")
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            print("LidarSänder Singleton Already Initialized")
            return
        self._initialized = True

        #self.scanQueue = queue.Queue()
        self.lidarMutex = Mutex()
        self.lastScan = None
        
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
            print(f"Connection with {lidarSänder.IP} on Port {PORT}")
            return s
        except Exception as e:
            print(f"Unable to connect Lidar Socket: {e}")
            return None

    def _sendLidarData(self, socket):  
        try:
            while True:
                data = pickle.dumps(self.lidarMutex.read())
                if data != self.lastScan:
                    length = struct.pack('!I', len(data))
                    socket.sendall(length + data)
                    self.lastScan = data
                time.sleep(0.05)  # Send data every 50ms
        except Exception as e:
            print(f"Error while sending Lidar: {e}")
        finally:
            socket.close()

    def putLidarData(self, data):
        self.lidarMutex.write(data)
