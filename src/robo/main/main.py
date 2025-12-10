import sys
from pathlib import Path
import subprocess
import atexit
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from robo.sockets.sendLidar import lidarSänder
import robo.lidar.LidarSlam as LidarSlam

camera_script = ROOT / "robo" / "main" / "start_camera.sh"
sendAudio = ROOT / "robo" / "sockets" / "sendAudio.py"
get_commands = ROOT / "robo" / "sockets" / "getCommands.py"


processes = []
try:
    IP = sys.argv[1]
except Exception as e:
    print(f"You have to give an IP as argument to the main script")
    sys.exit(0)

def cleanup():
    """Automatically Executed when programm stops"""
    print("\nStopping Processes...")
    for p in processes:
        p.terminate()
    for p in processes:
        try:
            p.wait(timeout=2)
        except subprocess.TimeoutExpired:
            p.kill()
    print("All Processes stopped")

atexit.register(cleanup)

try:
    print("="*20)
    print("Starting Camera Stream")
    p1 = subprocess.Popen(["bash", str(camera_script)])
    processes.append(p1)
    time.sleep(1)

    #Audio sending was not implemented :(
    #p_audio = subprocess.Popen(["python", str(sendAudio)])
    #processes.append(p_audio)

    print("="*20)
    print("Starting Lidar Connection")
    lidarSänder.setIP(IP)
    lidarSänder.getInstance()
    time.sleep(1)

    print("="*20)
    print("Starting SLAM")
    LidarSlam.main()
    time.sleep(1)

    print("="*20)
    print("Starting Command Connection")
    p_commands = subprocess.Popen(["python", str(get_commands), IP])
    processes.append(p_commands)
    time.sleep(1)

    for p in processes:
        p.wait()
except KeyboardInterrupt:
    print("Programm stopped by Keyboard Interrupt")
    sys.exit(0)
except Exception as e:
    print(f"Error in main.py: {e}")