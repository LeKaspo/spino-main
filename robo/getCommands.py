import socket
import queue
import json
import threading
import struct
from executor import CommandExecutor

PORT = 50003
IP = '192.168.0.229'

def getCommands():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((IP, PORT))
    try:
        while True:
            pre = client.recv(4)
            data_len = struct.unpack("!I", pre)
            print(f"receiving data of length {data_len}")
            data = client.recv(data_len)
            if not data: break
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
    except Exception as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("Programm closed")
    finally:
        client.close()
        fullstop = {
                "type": "fullstop",
                "params": {}
            }
        commandQ.put(fullstop)

def execCommands():
    while True:
        print("Waiting for Commands")
        command = commandQ.get()
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
   