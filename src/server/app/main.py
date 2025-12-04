import sys
from pathlib import Path  

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from server.app.connection import connectionHändler
import server.app.ui as ui

connectionHändler.getInstance()
#start robo
ui.start_ui()

# start threads