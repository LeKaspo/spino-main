import sys
from pathlib import Path
import socket
import queue
import json
import threading
import struct
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from robo.movement_control.executor import CommandExecutor

IP = sys.argv[1]
PORT = 50003


def connect():
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((IP, PORT))
        print(f"Connection with {IP} on Port {PORT}")
        return client
    except Exception as e:
        print(f"Unable to connect: {e}")
        return None


def getCommands(client):
    try:
        while True:
            pre = client.recv(4)
            data_len = struct.unpack("!I", pre)[0]
            data = client.recv(data_len)
            if not data: break

            command_string = data.decode('utf-8')
            command_json = json.loads(command_string)

            print(f"Command Received: {command_json}")
            if isinstance(command_json, str):
                command_json = json.loads(command_json)

            if command_json["type"] == "fullstop":
                emergencyStop()
            else:
                commandQ.put(command_json)
    except Exception as e:
        print(f"Error in getCommands: {e}")
    finally:
        emergencyStop()
        client.close()
        commandQ.put("STOP")
        print("getCommands Thread was stopped")


def execCommands():
    print("Waiting for Commands to execute")
    try:
        while True:
            command = commandQ.get()
            if command == "STOP":
                print("execCommands Thread was stopped")
                break
            commandExc.executeCommand(command)
    
    except Exception as e:
        print(f"Error in execCommands: {e}")


def emergencyStop():
    with commandQ.mutex:
        commandQ.queue.clear()
    fullstop = {"type": "fullstop", "params": {}}
    commandExc.executeCommand(fullstop)
    print("Emergency Stop")


if __name__ == "__main__":
    commandQ = queue.Queue()
    commandExc = CommandExecutor()

    client = connect()
    if client == None:
        sys.exit(0)


    print("Starting Command Threads")
    t1 = threading.Thread(target=getCommands, args=(client,), daemon=True)
    t2 = threading.Thread(target=execCommands, daemon=True)

    t1.start()
    t2.start()

    try:
        t1.join()
        t2.join()
    except KeyboardInterrupt:
        emergencyStop()
        sys.exit(0)
   