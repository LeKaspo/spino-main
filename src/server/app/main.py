import sys
from pathlib import Path  
import threading

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from server.app.connection import connectionHändler
import server.app.ui as ui
import server.gesture.gesture as gesture

connectionHändler.getInstance()
#start robo
ui.start_ui()

# start threads

t = threading.Thread(target=gesture.capture_loop, daemon=True)
t.start()