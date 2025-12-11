import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

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


for i, scan in enumerate(lidar.iter_scans()):
    print(scan)


lidar.stop()
lidar.stop_motor()
lidar.disconnect()