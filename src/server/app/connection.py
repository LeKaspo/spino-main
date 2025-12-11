import threading
import socket
import queue
import json
import struct
import time
import pickle

PORT_AUDIO = 50001
PORT_LIDAR = 50002
PORT_COMMANDS = 50003
IP = '192.168.0.31'

class connectionHändler:
    
    _instance = None
    _initialized = False

    def __new__(cls):
        print("Initializing new Connection Singleton")
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            print("Connection Singleton Already Initialized")
            return
        self._initialized = True

        self.commandQ = queue.Queue()
        #self.audioQ = queue.Queue()
        self.lidarQ = queue.Queue()

        print("Starting Connection Threads")
        #t1 = threading.Thread(target=self._getAudio, daemon=True)
        t2 = threading.Thread(target=self._getLidar, daemon=True)
        t3 = threading.Thread(target=self._sendCommand, daemon=True)

        #t1.start()
        t2.start()
        t3.start()

    @staticmethod
    def getInstance():
        if connectionHändler._instance is None:
            connectionHändler._instance = connectionHändler()
        return connectionHändler._instance

    @staticmethod
    def _openConnection(IP, PORT):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind((IP, PORT))
            s.listen(1)
            print(f"Listening on Port {PORT}")
            conn, _ = s.accept()
            print(f"Connection on Port {PORT}")
            return s, conn
        except Exception as e:
            print(f"Error while opening Socket: {e}")

    def _getAudio(self):
        s, conn = self._openConnection(IP, PORT_AUDIO)
        try:
            while True:
                data = conn.recv()
                if not data: break
                self.audioQ.put(data)     
        except Exception as e:
            print(f"Error while getting Audio: {e}")
        finally:
            conn.close()
            s.close()

    def recv_all(self, sock, n):
        """Helper function to receive exactly n bytes"""
        data = bytearray()
        while len(data) < n:
            packet = sock.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return data

    def _getLidar(self):
        s, conn = self._openConnection(IP, PORT_LIDAR)
        try:
            while True:
                length_data = conn.recv(4)
                length = struct.unpack('!I', length_data)[0]
                data = self.recv_all(conn, length)
                realdata = pickle.loads(data)
                self.lidarQ.put(realdata)
        except Exception as e:
            print(f"Error while getting Lidar: {e}")
        finally:
            conn.close()
            s.close()

    def _sendCommand(self):
        s, conn = self._openConnection(IP, PORT_COMMANDS)
        try:
            while True:
                cmd = self.commandQ.get()       
                cmd_json = json.dumps(cmd).encode('utf-8')
                cmd_len = len(cmd_json)
                pre_len = struct.pack("!I", cmd_len)
                conn.sendall(pre_len + cmd_json)
        except Exception as e:
            print(f"Error while sending Command: {e}")
        finally:
            conn.close()
            s.close()

    def putCommand(self, cmd):
        self.commandQ.put(cmd)

    def getLidar(self):
        return self.lidarQ.get()
    
    def getAudio(self):
        return self.audioQ.get()