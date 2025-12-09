import sys
from pathlib import Path  
import threading

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

print(str(ROOT))

from server.app.connection import connectionHändler
import server.app.ui as ui
import server.config.config as config
import server.gesture.gesture as gesture

#from server.app.robo_start import RobotSSHController

connectionHändler.getInstance()

# controller = RobotSSHController(
#     host="192.168.10.42",
#     user="robot"
# )
# controller.run()

ui.start_ui()

# start threads

t = threading.Thread(target=gesture.capture_loop, daemon=True)
t.start()