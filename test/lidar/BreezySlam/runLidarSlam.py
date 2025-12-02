from rplidar import RPLidar

LIDAR_DEVICE            = '/dev/rplidar'

lidar = RPLidar(LIDAR_DEVICE)
stopLidar = False

info = lidar.get_info()
print(info)

health = lidar.get_health()
print(health)


iterator = lidar.iter_scans()
scan = next(iterator)

while (not stopLidar):
    if scan != next(iterator):
        print(f"Schicke Scan")

        scan = next(iterator)

    else:
        print("No new Scan")



lidar.stop()
lidar.stop_motor()
lidar.disconnect()