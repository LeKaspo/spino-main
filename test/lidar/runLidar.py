from rplidar import RPLidar
lidar = RPLidar('/dev/ttyUSB1')

info = lidar.get_info()
print(info)

health = lidar.get_health()
print(health)

'''
for i, scan in enumerate(lidar.iter_scans()):
    if i > 3:
        break
    print(f"Scan {i}:")
    for quality, angle, distance in scan:
        print(f"  Qualität: {quality}, Winkel: {angle:.1f}°, Distanz: {distance:.1f} mm")
'''

iterator = lidar.iter_scans()
scan = next(iterator)
print(type(scan))

i = 0

while i < 20:
    if scan != next(iterator):

        scan = next(iterator)

        items = [item for item in next(iterator)]

        distances = [item[2] for item in items]
        angles    = [item[1] for item in items]

        
        for distances, angles in scan:
            print(f"Winkel: {angles:.1f}°, Distanz: {distances:.1f} mm")
        
    print(f"Schicke next Scan")
    i += 1

lidar.stop()
lidar.stop_motor()
lidar.disconnect()