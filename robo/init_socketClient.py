import socket

TCP_IP = '192.168.0.165'
TCP_PORT = 50069
BUFFER_SIZE = 1024
MESSAGE = "Hallo Server!"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))

print(f"Nachricht an Server gesendet: {MESSAGE}")
s.send(MESSAGE.encode())

data = s.recv(BUFFER_SIZE)
s.close()

print(f"Empfangene Antwort: {data.decode()}")