import sys
import threading
from pathlib import Path  

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from server.app.connection import connectionHändler
import server.app.ui as ui
import server.speech.speechInput as si

connectionHändler.getInstance()
# start robo
ui_thread = threading.Thread(target=ui.start_ui, name="UIThread", daemon=False)
speech_thread = threading.Thread(target=si.main, name="SpeechThread", daemon=False)

ui_thread.start()
speech_thread.start()

ui_thread.join()
speech_thread.join()

# start threads