from test.lidar.BreezySlam.rplidar import RPLidar
lidar = RPLidar('/dev/ttyUSB1')

info = lidar.get_info()
print(info)

health = lidar.get_health()
print(health)


iterator = lidar.iter_scans()
scan = next(iterator)
print(type(scan))

i = 0

while i < 20:
    if scan != next(iterator):
        print(f"Schicke Scan")

        scan = next(iterator)

        items = [item for item in next(iterator)]

        distances = [item[2] for item in items]
        angles    = [item[1] for item in items]

        for distances, angles in scan:
            print(f"Winkel: {angles:.1f}°, Distanz: {distances:.1f} mm")
        
        i += 1
    else:
        print("No new Scan")



lidar.stop()
lidar.stop_motor()
lidar.disconnect()