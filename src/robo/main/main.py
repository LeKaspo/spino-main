import sys
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

camera_script = ROOT / "robo" / "main" / "start_camera.sh"
sendLidar = ROOT / "robo" / "sockets" / "sendLidar.py"
sendAudio = ROOT / "robo" / "sockets" / "sendAudio.py"
get_commands = ROOT / "robo" / "sockets" / "getCommands.py"


processes = []

IP = sys.argv[1]


try:
    p1 = subprocess.Popen(["bash", str(camera_script)])
    processes.append(p1)

    # p_audio = subprocess.Popen(["python", str(sendAudio)])
    # processes.append(p_audio)

    # p_lidar = subprocess.Popen(["python", str(sendLidar)])
    # processes.append(p_lidar)

    p_commands = subprocess.Popen(["python", str(get_commands), IP])
    processes.append(p_commands)

    for p in processes:
        p.wait()
except Exception as e:
    print(f"Error in main.py: {e}")

print("Disconnected and Shutdown")