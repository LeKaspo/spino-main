import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from server.app.connection import connectionHändler

conn = connectionHändler.getInstance()

def sendJson(json):
    conn.commandQ.put(json)
    print(json)
