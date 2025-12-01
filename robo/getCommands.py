import socket
import queue
import json
import threading
import time
from executor import CommandExecutor

PORT = 50003
IP = '192.168.0.229'

def getCommands():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((IP, PORT))
    while True:
        data = client.recv(256)
        if not data: break
        #Decode JSON Command-Format
        print("Bytes")
        print(type(data))
        print(data)
        command_string = data.decode('utf-8')
        print("String")
        print(type(command_string))
        print(command_string)
        command_json = json.loads(command_string)
        print("JSON")
        print(type(command_json))
        print(command_json)
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
   