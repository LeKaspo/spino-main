import sys
from pathlib import Path  

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from server.app.connection import connectionHändler
import server.app.ui as ui
from server.app.robo_start import RobotSSHController

controller = RobotSSHController(
    host="192.168.10.42",
    user="robot"
)

connectionHändler.getInstance()
controller.run()
ui.start_ui()

# start threads