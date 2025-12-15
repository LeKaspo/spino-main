import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from server.app.connection import connectionHändler

conn = connectionHändler.getInstance()

# send json to the robot, contains a command and possiblx params
def sendJson(json):
    conn.commandQ.put(json)
