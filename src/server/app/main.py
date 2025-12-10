import sys
import threading
from pathlib import Path  


ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

print(str(ROOT))

from server.app.connection import connectionHändler
import server.app.ui as ui
import server.speech.speechInput as si
import server.config.config as config
import server.gesture.gesture as gesture
import server.stream_recorder.stream_recorder as stream_recorder

recorder = stream_recorder.get_recorder()
#from server.app.robo_start import RobotSSHController

connectionHändler.getInstance()
# start robo


# controller = RobotSSHController(
#     host="192.168.10.42",
#     user="robot"
# )
# controller.run()
thread_gesture = threading.Thread(target=gesture.capture_loop, daemon=True)
thread_gesture.start()
try:
    print("Starting Stream Recorder")
    recorder.start()
    print("Starting Speech Input")
    si.start()
    print("Starting UI")
    ui.start_ui()
except Exception as e:
    print(f"ERROR: {e}")

# start threads

