from rplidar import RPLidar

LIDAR_DEVICE            = '/dev/rplidar'

lidar = RPLidar(LIDAR_DEVICE)
stopLidar = False

info = lidar.get_info()
print(info)

health = lidar.get_health()
print(health)


iterator = lidar.iter_scans()
scan = oldscan = next(iterator)

while (not stopLidar):
    scan = next(iterator)

    if scan != oldscan:
        print(f"Schicke Scan")
        

    else:
        print("No new Scan")



lidar.stop()
lidar.stop_motor()
lidar.disconnect()