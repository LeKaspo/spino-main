import sys
import threading
from pathlib import Path  
import threading

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

print(str(ROOT))

from server.app.connection import connectionHändler
import server.app.ui as ui
import server.speech.speechInput as si
import server.config.config as config
import server.gesture.gesture as gesture

#from server.app.robo_start import RobotSSHController

connectionHändler.getInstance()
# start robo
ui_thread = threading.Thread(target=ui.start_ui, name="UIThread", daemon=False)
speech_thread = threading.Thread(target=si.main, name="SpeechThread", daemon=False)

ui_thread.start()
speech_thread.start()

ui_thread.join()
speech_thread.join()

# controller = RobotSSHController(
#     host="192.168.10.42",
#     user="robot"
# )
# controller.run()
thread_gesture = threading.Thread(target=gesture.capture_loop, daemon=True)
thread_gesture.start()

ui.start_ui()

# start threads

