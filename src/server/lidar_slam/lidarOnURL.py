import socket
import threading
import io
import time
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))
from server.app.connection import connectionHändler

HOST = '192.168.0.78'
PORT = 50010

def mjpeg_stream(conn):
    """Streame Lidar-Visualisierung als MJPEG"""
    conn.send(b"HTTP/1.1 200 OK\r\n")
    conn.send(b"Content-Type: multipart/x-mixed-replace; boundary=frame\r\n\r\n")
    
    conn_lidar = connectionHändler.getInstance()
    frame_count = 0
    
    while True:
        try:
            scan = conn_lidar.getLidar()
            
            if not scan or len(scan) == 0:
                continue
            
            frame_count += 1
            
            # Matplotlib Figure erstellen
            fig, ax = plt.subplots(figsize=(10, 10), facecolor='black')
            ax.set_facecolor('black')
            
            x_points, y_points, distances = [], [], []
            
            for quality, angle, distance in scan:
                angle_rad = np.radians(angle)
                x = (distance / 1000) * np.cos(angle_rad)
                y = (distance / 1000) * np.sin(angle_rad)
                x_points.append(x)
                y_points.append(y)
                distances.append(distance)
            
            # Scatter Plot
            scatter = ax.scatter(x_points, y_points, c=distances, cmap='hot',
                                s=120, alpha=0.95, vmin=0, vmax=8000,
                                edgecolors='white', linewidth=0.5)
            
            # Achsen konfigurieren
            ax.set_xlim(-15, 15)
            ax.set_ylim(-15, 15)
            ax.set_aspect('equal')
            
            ax.grid(True, alpha=0.2, color='white', linestyle='--', linewidth=0.5)
            ax.set_xlabel('X (m)', color='white', fontsize=12, fontweight='bold')
            ax.set_ylabel('Y (m)', color='white', fontsize=12, fontweight='bold')
            ax.tick_params(colors='white', labelsize=10)
            
            for spine in ax.spines.values():
                spine.set_edgecolor('white')
            
            ax.set_title(f'Lidar 2D View | Frame #{frame_count}',
                        color='white', fontsize=14, fontweight='bold', pad=20)
            
            # Colorbar
            cbar = plt.colorbar(scatter, ax=ax, label='Distance (mm)')
            cbar.ax.tick_params(colors='white')
            cbar.ax.yaxis.label.set_color('white')
            
            # In JPEG konvertieren
            buf = io.BytesIO()
            plt.savefig(buf, format='jpeg', facecolor='black')
            plt.close(fig)
            buf.seek(0)
            frame = buf.read()
            
            # MJPEG-Frame senden
            conn.send(b"--frame\r\n")
            conn.send(b"Content-Type: image/jpeg\r\n\r\n")
            conn.send(frame)
            conn.send(b"\r\n")
            
            time.sleep(0.05)  
            
        except Exception as e:
            print(f"Error: {e}")
            break
    
    conn.close()

def start_server():
    """Starte MJPEG HTTP Server"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(5)
    print(f"Lidar Server läuft auf http://localhost:{PORT}/")
    print(f"Öffne im Browser: http://localhost:{PORT}/")
    
    
    try:
        while True:
            conn, addr = s.accept()
            print(f"Browser verbunden von {addr}")
            clientThread = threading.Thread(target=mjpeg_stream, args=(conn,), daemon=True)
            clientThread.start()
            
    except KeyboardInterrupt:
        print("\n\nFahre Server herunter...")
        s.close()
        print("Server beendet!")
        sys.exit(0)

def main():
    start_server()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProgramm beendet!")
        sys.exit(0)