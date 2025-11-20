import threading
import socket
import time
import queue

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

def getLidar():
    s, conn = openConnection(PORT_LIDAR)
    while True:
        data = conn.recv(BUFFER_SIZE)
        if not data: break
        print(f"Received {data.decode()} on Port {PORT_LIDAR}")
    conn.close()
    s.close() 

def sendCommand():
    s, conn = openConnection(PORT_COMMANDS)
    while True:
        conn.send("Command".encode())
        time.sleep(3)


if __name__ == "__main__":
    
    stop_event = threading.Event()

    #Receive Audio
    print("Starting Audio")
    t1 = threading.Thread(target=getAudio, args=(), daemon=True)
    #Receive Lidar
    print("Starting Lidar")
    t2 = threading.Thread(target=getLidar, args=(), daemon=True)
    #Send Commands
    print("Starting Commands")
    t3 = threading.Thread(target=sendCommand, args=(), daemon=True)
    
    t1.start()
    t2.start()
    t3.start()
    
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        stop_event.set()
        t1.join()
        t2.join()
        t3.join()
        