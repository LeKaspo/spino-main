from rplidar import RPLidar
import csv
import math
from datetime import datetime

lidar = RPLidar('/dev/ttyUSB1')

info = lidar.get_info()
print(f"Lidar Info: {info}")

health = lidar.get_health()
print(f"Lidar Health: {health}")

# Konfiguration
NUM_SCANS = 10
MIN_QUALITY = 10  # Mindestqualität
MAX_DISTANCE = 10000  # Maximale Distanz in mm
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
csv_filename = f'lidar_scans_{timestamp}.csv'

print(f"\nAufnahme von {NUM_SCANS} Scans...")
print(f"Filter: Qualität >= {MIN_QUALITY}, Distanz <= {MAX_DISTANCE}mm")

with open(csv_filename, 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(['scan_id', 'quality', 'angle_deg', 'distance_mm', 'x_mm', 'y_mm'])
    
    total_points = 0
    filtered_points = 0
    
    for i, scan in enumerate(lidar.iter_scans()):
        if i >= NUM_SCANS:
            break
        
        scan_points = 0
        
        for quality, angle, distance in scan:
            total_points += 1
            
            # Filter anwenden
            if quality < MIN_QUALITY or distance > MAX_DISTANCE:
                filtered_points += 1
                continue
            
            # Kartesische Koordinaten
            angle_rad = math.radians(angle)
            x = distance * math.cos(angle_rad)
            y = distance * math.sin(angle_rad)
            
            csv_writer.writerow([i, quality, round(angle, 1), round(distance, 1), 
                                round(x, 1), round(y, 1)])
            scan_points += 1
        
        print(f"Scan {i}: {scan_points} Punkte gespeichert")

print(f"\n✓ Fertig!")
print(f"  Gesamt: {total_points} Punkte")
print(f"  Gefiltert: {filtered_points} Punkte")
print(f"  Gespeichert: {total_points - filtered_points} Punkte")
print(f"  Datei: {csv_filename}")

lidar.stop()
lidar.stop_motor()
lidar.disconnect()