import socket

TCP_IP = '172.30.32.1'
TCP_PORT = 50069
BUFFER_SIZE = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

print("Server gestartet, wartet auf Verbindung...")
conn, addr = s.accept()
print(f"Verbindung von {addr} akzeptiert.")

while True:
    data = conn.recv(BUFFER_SIZE)
    if not data:
        break
    print(f"Empfangene Daten: {data.decode()}")
    conn.send(data)  # Sendet die empfangenen Daten zurück

conn.close()
print("Verbindung geschlossen.")