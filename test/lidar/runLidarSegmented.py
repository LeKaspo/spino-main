from rplidar import RPLidar

def sector(angle, sectors=16):
    '''Teilt 360° in gleich große Sektoren, gibt Index zurück'''
    sector_angle = 360 / sectors
    return int(angle // sector_angle)

lidar = RPLidar('/dev/ttyUSB1')

info = lidar.get_info()
print(info)

health = lidar.get_health()
print(health)

lidar.motor_speed(1023)

print("Heheheha")

SECTORS = 16

for i, scan in enumerate(lidar.iter_scans()):
    if i > 0:  # Nur einmal ausgeben für Übersicht
        break
    print(f"Scan {i}:")
    # Initialisiere pro Sektor: (Abstand, Qualität, Winkel)
    results = [(float('inf'), 0, 0) for _ in range(SECTORS)]
    for quality, angle, distance in scan:
        idx = sector(angle, SECTORS)
        # Speichere den Wert, falls der Abstand kleiner ist als bisher
        if distance < results[idx][0]:
            results[idx] = (distance, quality, angle)
    # Ausgabe pro Sektor
    for idx, (distance, quality, angle) in enumerate(results):
        if distance != float('inf'):
            print(f"  Sektor {idx:2d}: Abstand {distance:8.1f} mm | Winkel {angle:6.1f}° | Qualität {quality:3d}")
        else:
            print(f"  Sektor {idx:2d}: Kein Wert")

lidar.stop()
lidar.stop_motor()
lidar.disconnect()