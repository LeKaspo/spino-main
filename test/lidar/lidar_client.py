# lidar_client.py
# Läuft auf Windows PC, empfängt und visualisiert Daten

import socket
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque
import sys

class LidarClient:
    """
    Empfängt Lidar-Scans und visualisiert sie
    """
    
    def __init__(self, server_ip, server_port=5000, num_scans=5):
        self.server_ip = server_ip
        self.server_port = server_port
        self.num_scans = num_scans
        
        # Buffer für letzte N Scans
        self.scan_buffer = deque(maxlen=num_scans)
        
        # Socket
        self.socket = None
        self.connected = False
        
        # Statistiken
        self.scan_count = 0
        self.total_points = 0
        
        # Plot Setup
        self.fig, self.ax = plt.subplots(figsize=(12, 12))
        
        # Ein Scatter-Plot für alle Scans (gleiche Farbe)
        self.scatter = self.ax.scatter([], [], s=5, c='blue', alpha=0.6, label='Scans')
        
        # Sensor-Position
        self.sensor_plot = self.ax.scatter([0], [0], c='red', s=300, 
                                          marker='x', label='Sensor', zorder=10)
        
        # Plot-Einstellungen
        self.ax.set_xlim(-5000, 5000)
        self.ax.set_ylim(-5000, 5000)
        self.ax.set_xlabel('X (mm)', fontsize=12)
        self.ax.set_ylabel('Y (mm)', fontsize=12)
        self.ax.set_title('Live Lidar Stream (Letzte 5 Scans)', 
                         fontsize=14, fontweight='bold')
        self.ax.grid(True, alpha=0.3)
        self.ax.legend(loc='upper right', fontsize=10)
        self.ax.set_aspect('equal')
        
        # Info-Text
        self.text = self.ax.text(0.02, 0.98, '', transform=self.ax.transAxes,
                                verticalalignment='top', fontsize=11,
                                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
    
    def connect(self):
        """Verbindet mit Server"""
        print(f"🔌 Verbinde mit {self.server_ip}:{self.server_port}...")
        
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_ip, self.server_port))
            self.connected = True
            print("Verbunden!")
            return True
        
        except Exception as e:
            print(f"Verbindung fehlgeschlagen: {e}")
            return False
    
    def receive_scan(self):
        """Empfängt einen Scan vom Server"""
        try:
            # Empfange Länge (4 Bytes)
            length_bytes = self.socket.recv(4)
            if not length_bytes:
                return None
            
            length = int.from_bytes(length_bytes, byteorder='big')
            
            # Empfange Daten
            data = b''
            while len(data) < length:
                chunk = self.socket.recv(min(length - len(data), 4096))
                if not chunk:
                    return None
                data += chunk
            
            # Parse JSON
            message = json.loads(data.decode('utf-8'))
            
            return message
        
        except Exception as e:
            print(f"Empfangsfehler: {e}")
            self.connected = False
            return None
    
    def update_plot(self, frame):
        """Update-Funktion für Animation"""
        if not self.connected:
            return [self.scatter, self.sensor_plot, self.text]
        
        # Empfange Scan
        scan_data = self.receive_scan()
        
        if scan_data is None:
            self.connected = False
            self.text.set_text('Verbindung verloren')
            return [self.scatter, self.sensor_plot, self.text]
        
        # Extrahiere Punkte
        points = scan_data['points']
        
        if len(points) > 0:
            # Konvertiere zu NumPy Array
            xy_points = np.array([[p['x'], p['y']] for p in points])
            
            # Füge zum Buffer hinzu
            self.scan_buffer.append(xy_points)
            
            # Statistiken
            self.scan_count = scan_data['scan_id']
            self.total_points += len(points)
            
            # Kombiniere alle Scans im Buffer
            all_points = np.vstack(list(self.scan_buffer))
            
            # Update Scatter-Plot
            self.scatter.set_offsets(all_points)
            
            # Update Text
            avg_points = self.total_points / self.scan_count if self.scan_count > 0 else 0
            
            self.text.set_text(
                f'Scan #{self.scan_count}\n'
                f'Aktuelle Punkte: {len(points)}\n'
                f'Gesamt im Plot: {len(all_points)}\n'
                f'Buffer: {len(self.scan_buffer)}/{self.num_scans}\n'
                f'Ø Punkte/Scan: {avg_points:.0f}'
            )
        
        return [self.scatter, self.sensor_plot, self.text]
    
    def start(self):
        """Startet Visualisierung"""
        if not self.connect():
            return
        
        print("Starte Visualisierung...")
        print("Schließe das Fenster zum Beenden")
        
        # Animation starten
        anim = FuncAnimation(self.fig, self.update_plot, 
                           interval=50,  # 50ms Update
                           blit=True,
                           cache_frame_data=False)
        
        plt.show()
        
        # Cleanup
        self.disconnect()
    
    def disconnect(self):
        """Trennt Verbindung"""
        print("\nTrenne Verbindung...")
        self.connected = False
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        
        print("Getrennt")


if __name__ == "__main__":
    # IP-Adresse vom Raspberry Pi
    if len(sys.argv) > 1:
        server_ip = sys.argv[1]
    else:
        # Standard: Localhost (für Tests)
        server_ip = input("Raspberry Pi IP-Adresse: ")
    
    client = LidarClient(server_ip=server_ip, server_port=5000, num_scans=5)
    client.start()