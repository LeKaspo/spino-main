import sys
from pathlib import Path  

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

print(str(ROOT))

from server.app.connection import connectionHändler
import server.app.ui as ui
import server.config.config as config
import server.lidar_slam.rpslam as lidar
import server.lidar_slam.visualize_lidar as visualize


#from server.app.robo_start import RobotSSHController

print("Starting Sockets")
connectionHändler.getInstance()

# controller = RobotSSHController(
#     host="192.168.10.42",
#     user="robot"
# )
# controller.run()
try:
    print("Starting Lidar")
    visualize.main()
    print("Starting UI")
    ui.start_ui()
except Exception as e:
    print(f"ERROR: {e}")

# start threads