import socket
import time
import queue
import pickle
import struct
import threading

PORT = 50002
IP = '192.168.0.78'
class lidarSänder:

    _instance = None
    _initialized = False

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

        sendThread = threading.Thread(target=self._sendLidarData, daemon=True)
        sendThread.start()

    @staticmethod
    def getInstance():
        if lidarSänder._instance is None:
            lidarSänder._instance = lidarSänder()
        return lidarSänder._instance

    def _sendLidarData(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((IP, PORT))
        try:
            while True:
                data = pickle.dumps(self.scanQueue.get())
                print(len(data))
                length = struct.pack('!I', len(data))
                client.sendall(length + data)
                time.sleep(0.5)  # Send data every 500ms
        except Exception as e:
            print(f"Error: {e}")
        except KeyboardInterrupt:
            print("Programm closed")
        finally:
            client.close()

    def putLidarData(self, data):
        self.scanQueue.put(data)
