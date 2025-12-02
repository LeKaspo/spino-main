from rplidar import RPLidar
from LidarSlam import RoboLidar


def LidarSlamSend(self):
    LIDAR_DEVICE            = '/dev/rplidar'

    lidar = RPLidar(LIDAR_DEVICE)

    info = lidar.get_info()
    print(info)

    health = lidar.get_health()
    print(health)


    iterator = self.lidar.iter_scans()
    for scan in iterator:
        if self._stop_update_thread:
            break
            



    lidar.stop()
    lidar.stop_motor()
    lidar.disconnect()