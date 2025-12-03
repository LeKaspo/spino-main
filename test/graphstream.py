import socket
import threading
import io
import time
import math
import matplotlib.pyplot as plt

HOST = '0.0.0.0'
PORT = 8080

def mjpeg_stream(conn):
    conn.send(b"HTTP/1.1 200 OK\r\n")
    conn.send(b"Content-Type: multipart/x-mixed-replace; boundary=frame\r\n\r\n")

    # daten für mein beispiel
    x_values = [i * 0.1 for i in range(100)]
    frame_count = 0

    while True:
        #mehr sachen für mein beispiel, also hier slam einfügen
        y_values = [math.sin(x + frame_count * 0.1) for x in x_values]
        frame_count += 1
        fig, ax = plt.subplots()
        ax.plot(x_values, y_values)
        ax.set_ylim(-1.5, 1.5)
        ax.set_title(f"Frame {frame_count}")

    
        buf = io.BytesIO()
        plt.savefig(buf, format='jpeg')
        plt.close(fig)
        buf.seek(0)
        frame = buf.read()

        # MJPEG-Frame senden
        conn.send(b"--frame\r\n")
        conn.send(b"Content-Type: image/jpeg\r\n\r\n")
        conn.send(frame)
        conn.send(b"\r\n")
        time.sleep(0.1)  # ~10 FPS

def start_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(5)
    print(f"Server läuft auf http://{HOST}:{PORT}/")

    while True:
        conn, addr = s.accept()
        print(f"Verbindung von {addr}")
        threading.Thread(target=mjpeg_stream, args=(conn,)).start()

if __name__ == "__main__":
    start_server()

