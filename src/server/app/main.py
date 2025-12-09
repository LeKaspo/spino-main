import sys
from pathlib import Path  

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

print(str(ROOT))

from server.app.connection import connectionHändler
import server.app.ui as ui
import server.config.config as config
import server.lidar_slam.rpslam as lidar


#from server.app.robo_start import RobotSSHController

connectionHändler.getInstance()

# controller = RobotSSHController(
#     host="192.168.10.42",
#     user="robot"
# )
# controller.run()
try:
    lidar.main()
    ui.start_ui()
except Exception as e:
    print(f"ERROR: {e}")

# start threads