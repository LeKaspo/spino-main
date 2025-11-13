import keyboard
import json 
import socket

#alternative Idee wäre keyboard.is_pressed??

### aktuell funktioniert ganz gut, jetzt muss multithreaded sein um asyncio und Tastatur gleichzeitig zu haben, und zu wissen wie man an asyncio thread loop sended

TCP_IP = '172.30.32.1'
TCP_PORT = 50069
BUFFER_SIZE = 256
MESSAGE = "Hallo Server!"

conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn.connect((TCP_IP, TCP_PORT))


keyboard.add_hotkey('w', lambda: w_press())
keyboard.add_hotkey('a', lambda: a_press())
keyboard.add_hotkey('s', lambda: s_press())
keyboard.add_hotkey('d', lambda: d_press())

def w_press():
    command = {
        "type" : 1337,
        "params" : {
            "param" : 2077,
        },
    }
    message = json.dumps(command).encode('utf-8')
    conn.send(message)
    print(f"Befehl {command} gesendet")
    
    

def a_press():
    message = "A pressed"

def s_press():
    message = "S pressed"


def d_press():
    message = "D pressed"

while True:()

