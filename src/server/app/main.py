import sys
from pathlib import Path  

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

print(str(ROOT))

from server.app.connection import connectionHändler
import server.app.ui as ui
import server.config.config as config
import server.lidar_slam.rpslam as lidar
import server.lidar_slam.obstacle_detection as obstacleDetection
import server.lidar_slam.visualizecv as lidarStream


#from server.app.robo_start import RobotSSHController

print("Starting Sockets")
connectionHändler.getInstance()

# controller = RobotSSHController(
#     host="192.168.10.42",
#     user="robot"
# )
# controller.run()
try:
    print("Start Obstacle Detection")
    obstacleDetection.main()
    print("Start Lidar Stream")
    lidarStream.main()
    print("Starting Slam")
    #lidar.main()
    print("Starting UI")
    ui.start_ui()
except Exception as e:
    print(f"ERROR: {e}")

# start threads