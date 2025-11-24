import threading
import socket
import queue
import json

PORT_AUDIO = 50001
PORT_LIDAR = 50002
PORT_COMMANDS = 50003
IP = 'localhost'
BUFFER_SIZE = 128

class connectionHändler:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return
        self._initialized = True

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
        while True:
            data = conn.recv(BUFFER_SIZE)
            if not data: break
            self.audioQ.put(data)     
            #print(f"Received {data.decode()} on Port {PORT_AUDIO}")
        conn.close()
        s.close()

    def _getLidar(self):
        s, conn = self._openConnection(IP, PORT_LIDAR)
        while True:
            data = conn.recv(BUFFER_SIZE)
            if not data: break
            self.lidarQ.put(data)
            #print(f"Received {data.decode()} on Port {PORT_LIDAR}")
        conn.close()
        s.close()

    def _sendCommand(self):
        s, conn = self._openConnection(IP, PORT_COMMANDS)
        while True:
            cmd = self.commandQ.get()
            ##TO DO: konvertierung überprüfen            
            cmd_json = json.dumps(cmd).encode('utf-8')
            conn.send(cmd_json)

    def putCommand(self, cmd):
        self.commandQ.put(cmd)

    def getLidar(self):
        return self.lidarQ.get()
    
    def getAudio(self):
        return self.audioQ.get()

    
    
    # def processAudio(self):
    #     while True:
    #         audio_Chunk = self.audioQ.get()
    #         if audio_Chunk is None: break
    #         #Do something with Audio Data

    # def processLidar(self):
    #     while True:
    #         lidar_Scan = self.lidarQ.get()
    #         if lidar_Scan is None: break
    #         #Do something with Lidar Data

    

if __name__ == "__main__":
    conn = connectionHändler()
    while True:
        pass
#     tcp = TCP_Server()
#     commandQ = queue.Queue()
#     audioQ = queue.Queue()
#     lidarQ = queue.Queue()

#     #Receive Audio + Processing
#     print("Init Audio")
#     t1 = threading.Thread(target=tcp._getAudio, daemon=True)
#     t2 = threading.Thread(target=tcp.processAudio, daemon=True)
#     #Receive Lidar + Processing
#     print("Init Lidar")
#     t3 = threading.Thread(target=tcp._getLidar, daemon=True)
#     t4 = threading.Thread(target=tcp.processLidar, daemon=True)
#     #Send Commands
#     print("Init Commands")
#     t5 = threading.Thread(target=tcp._sendCommand, daemon=True)

#     t1.start()
#     t2.start()
#     t3.start()
#     t4.start()
#     t5.start()


#     testCommand = {
#         "type" : "movement",
#         "params" : {
#             "param" : 2077
#         }
#     }

#     commandQ.put(testCommand)

#     while True:
#        pass
    
