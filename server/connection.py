import threading
import socket
import queue
import json

PORT_AUDIO = 50001
PORT_LIDAR = 50002
PORT_COMMANDS = 50003
IP = '192.168.0.229'
BUFFER_SIZE = 128

class connectionHändler:
    
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

        print("Starting Sockets")
        self.commandQ = queue.Queue()
        self.audioQ = queue.Queue()
        self.lidarQ = queue.Queue()

        t1 = threading.Thread(target=self._getAudio, daemon=True)
        t2 = threading.Thread(target=self._getLidar, daemon=True)
        t3 = threading.Thread(target=self._sendCommand, daemon=True)
        t1.start()
        t2.start()
        t3.start()

    @staticmethod
    def getInstance():
        if connectionHändler._instance is None:
            connectionHändler._instance = connectionHändler()
        return connectionHändler._instance

    @staticmethod
    def _openConnection(IP, PORT):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((IP, PORT))
        s.listen(1)
        print(f"Listening on Port {PORT}")
        conn, _ = s.accept()
        print(f"Connection on Port {PORT}")
        return s, conn

    def _getAudio(self):
        s, conn = self._openConnection(IP, PORT_AUDIO)
        try:
            while True:
                data = conn.recv(BUFFER_SIZE)
                if not data: break
                self.audioQ.put(data)     
        except Exception as e:
            print(f"Error while getting Audio: {e}")
        except KeyboardInterrupt:
            print("Closed getAudio Thread")
        finally:
            conn.close()
            s.close()

    def _getLidar(self):
        s, conn = self._openConnection(IP, PORT_LIDAR)
        try:
            while True:
                data = conn.recv(BUFFER_SIZE)
                if not data: break
                self.lidarQ.put(data)
        except Exception as e:
            print(f"Error while getting Lidar: {e}")
        except KeyboardInterrupt:
            print("Closed getLidarThread")
        finally:
            conn.close()
            s.close()

    def _sendCommand(self):
        s, conn = self._openConnection(IP, PORT_COMMANDS)
        try:
            while True:
                cmd = self.commandQ.get()       
                print(f"command sent: {cmd}")  
                cmd_json = json.dumps(cmd).encode('utf-8')
                conn.send(cmd_json)
        except Exception as e:
            print(f"Error while sending Command: {e}")
        except KeyboardInterrupt:
            print("Closed sendCommand Thread")
        finally:
            conn.close()
            s.close()

    def putCommand(self, cmd):
        self.commandQ.put(cmd)

    def getLidar(self):
        return self.lidarQ.get()
    
    def getAudio(self):
        return self.audioQ.get()


print("Initializing conn Object")
conn = connectionHändler.getInstance()
print("object initailized")
conn2 = connectionHändler.getInstance()

print(conn == conn2)

if __name__ == "__main__":
    while True:
        pass

