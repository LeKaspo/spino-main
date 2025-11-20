import socket
import queue
import json
import threading
import time
from executor import CommandExecutor

PORT = 50003
IP = 'localhost'

def getCommands():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((IP, PORT))
    while True:
        data = client.recv(256)
        if not data: break
        #Decode JSON Command-Format
        command_json = json.loads(data.decode('utf-8'))
        commandQ.put(command_json)

def execCommands():
    while True:
        print("Waiting for Commands")
        command = commandQ.get()
        #Execute the Commands from the Q
        commandExc.executeCommand(command)
        


if __name__ == "__main__":
    commandQ = queue.Queue()
    commandExc = CommandExecutor()
    
    print("Starting Command Threads")
    t1 = threading.Thread(target=getCommands, daemon=True)
    t2 = threading.Thread(target=execCommands, daemon=True)

    t1.start()
    t2.start()

    while True:
        pass
   