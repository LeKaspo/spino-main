from rplidar import RPLidar
lidar = RPLidar('/dev/ttyUSB1')

info = lidar.get_info()
print(info)

health = lidar.get_health()
print(health)

'''
for i, scan in enumerate(lidar.iter_scans()):
    print('%d: Got %d measures' % (i, len(scan)))
    if i > 10:
        break
'''

for i, scan in enumerate(lidar.iter_scans()):
    if i > 3:
        break
    print(f"Scan {i}:")
    for quality, angle, distance in scan:
        print(f"  Qualität: {quality}, Winkel: {angle:.1f}°, Distanz: {distance:.1f} mm")


lidar.stop()
lidar.stop_motor()
lidar.disconnect()