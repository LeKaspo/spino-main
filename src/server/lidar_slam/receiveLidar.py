import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from server.app.connection import connectionHändler

conn = connectionHändler.getInstance()


try:
    while True:
        scan = conn.getLidar()
        print(scan)
except KeyboardInterrupt:
    print("Closed receivedLidarProgram")
except Exception as e:
    print(f"Error while Program: {e}")
finally:
    print("finally")


