# lidar_server.py
# Läuft auf Raspberry Pi, sendet Lidar-Daten über Netzwerk

from test.lidar.BreezySlam.rplidar import RPLidar
import socket
import json
import math
import time

class LidarServer:
    """
    Sendet Lidar-Scans über TCP Socket
    """
    
    def __init__(self, port='/dev/ttyUSB1', tcp_port=5000):
        self.lidar = RPLidar(port)
        self.tcp_port = tcp_port
        self.running = False
        
    def scan_to_dict(self, scan):
        """Konvertiert Scan zu übertragbarem Format"""
        points = []
        
        for quality, angle, distance in scan:
            if quality > 10 and distance > 0:
                # Berechne kartesische Koordinaten
                angle_rad = math.radians(angle)
                x = distance * math.cos(angle_rad)
                y = distance * math.sin(angle_rad)
                
                points.append({
                    'x': round(x, 1),
                    'y': round(y, 1),
                    'distance': round(distance, 1),
                    'angle': round(angle, 1),
                    'quality': quality
                })
        
        return points
    
    def start_server(self):
        """Startet TCP Server und sendet Scans"""
        print("Starte Lidar Server...")
        
        # Lidar Info
        info = self.lidar.get_info()
        print(f"Lidar Info: {info}")
        
        # Socket erstellen
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Binde an alle Interfaces
        server_socket.bind(('0.0.0.0', self.tcp_port))
        server_socket.listen(1)
        
        # Hole lokale IP
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        print(f"Server läuft auf {local_ip}:{self.tcp_port}")
        print(f"Auf Windows verbinden mit: python lidar_client.py {local_ip}")
        print("Warte auf Client-Verbindung...")
        
        try:
            # Warte auf Client
            client_socket, client_address = server_socket.accept()
            print(f"Client verbunden: {client_address}")
            
            self.running = True
            scan_count = 0
            
            # Sende Scans
            for scan in self.lidar.iter_scans():
                if not self.running:
                    break
                
                scan_count += 1
                
                # Konvertiere Scan
                points = self.scan_to_dict(scan)
                
                # Erstelle Nachricht
                message = {
                    'scan_id': scan_count,
                    'timestamp': time.time(),
                    'num_points': len(points),
                    'points': points
                }
                
                # Serialisiere zu JSON
                json_data = json.dumps(message)
                
                # Sende Länge + Daten
                try:
                    # Sende zuerst die Länge (4 Bytes)
                    length = len(json_data)
                    client_socket.sendall(length.to_bytes(4, byteorder='big'))
                    
                    # Dann die Daten
                    client_socket.sendall(json_data.encode('utf-8'))
                    
                    if scan_count % 10 == 0:
                        print(f"📤 Scan {scan_count} gesendet: {len(points)} Punkte")
                
                except (BrokenPipeError, ConnectionResetError):
                    print("Client getrennt")
                    break
        
        except KeyboardInterrupt:
            print("\n Server gestoppt (Ctrl+C)")
        
        finally:
            print("Cleanup...")
            self.running = False
            
            try:
                client_socket.close()
            except:
                pass
            
            server_socket.close()
            self.lidar.stop()
            self.lidar.stop_motor()
            self.lidar.disconnect()
            
            print("Server beendet")


if __name__ == "__main__":
    server = LidarServer(port='/dev/ttyUSB1', tcp_port=5000)
    server.start_server()