import threading
import socket
import time
import queue
import json

PORT_AUDIO = 50001
PORT_LIDAR = 50002
PORT_COMMANDS = 50003
IP = 'localhost'
BUFFER_SIZE = 128

def openConnection(PORT):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((IP, PORT))
    s.listen(1)
    print(f"Listening on Port {PORT}")
    conn, _ = s.accept()
    print(f"Connection on Port {PORT}")
    return s, conn

def getAudio():
    s, conn = openConnection(PORT_AUDIO)
    while True:
        data = conn.recv(BUFFER_SIZE)
        if not data: break     
        print(f"Received {data.decode()} on Port {PORT_AUDIO}")
    conn.close()
    s.close()

def processAudio():
    while True:
        audio_Chunk = audioQ.get()
        if audio_Chunk is None: break
        #Do something with Audio Data

def getLidar():
    s, conn = openConnection(PORT_LIDAR)
    while True:
        data = conn.recv(BUFFER_SIZE)
        if not data: break
        print(f"Received {data.decode()} on Port {PORT_LIDAR}")
    conn.close()
    s.close() 

def processLidar():
    while True:
        lidar_Scan = lidarQ.get()
        if lidar_Scan is None: break
        #Do something with Lidar Data

def sendCommand():
    s, conn = openConnection(PORT_COMMANDS)
    while True:
        cmd = commandQ.get()
        cmd_json = json.dumps(cmd).encode('utf-8')
        conn.send(cmd_json)
        time.sleep(3)


if __name__ == "__main__":
    
    commandQ = queue.Queue()
    audioQ = queue.Queue()
    lidarQ = queue.Queue()

    #Receive Audio + Processing
    print("Init Audio")
    t1 = threading.Thread(target=getAudio, daemon=True)
    t2 = threading.Thread(target=processAudio, daemon=True)
    #Receive Lidar + Processing
    print("Init Lidar")
    t3 = threading.Thread(target=getLidar, daemon=True)
    t4 = threading.Thread(target=processLidar, daemon=True)
    #Send Commands
    print("Init Commands")
    t5 = threading.Thread(target=sendCommand, daemon=True)

    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t5.start()

    testCommand = {
        "type" : "movement",
        "params" : {
            "param" : 2077
        }
    }

    commandQ.put(testCommand)

    while True:
       pass
    
