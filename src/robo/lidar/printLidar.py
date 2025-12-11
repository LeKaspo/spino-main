from robo.ext_libs.rplidar import RPLidar, RPLidarException

lidar2 = RPLidar('/dev/rplidar')
lidar2.stop()
lidar2.stop_motor()
lidar2.disconnect()

lidar = RPLidar('/dev/rplidar')

info = lidar.get_info()
print(info)

health = lidar.get_health()
print(health)


while True:
            try:
                print("Try enumerate")
                for i, scan in enumerate(lidar.iter_scans()):
            
                    # Update latest_scan
                    if i % 5 == 0:
                        print(scan)
            except RPLidarException:
                print("Rplidar Exception")
                lidar.clean_input()

lidar.stop()
lidar.stop_motor()
lidar.disconnect()