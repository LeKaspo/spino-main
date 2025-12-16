import threading
import getpass
import sys
from pathlib import Path  

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from server.app.connection import connectionHändler
from server.app.robo_start import RobotSSHController
import server.app.ui as ui
import server.speech.speechInput as si
import server.config.config as config
import server.gesture.gesture as gesture
import server.lidar_slam.rpslam as lidar
import server.lidar_slam.obstacle_detection as obstacleDetection
import server.lidar_slam.visualizecv as lidarStream
import server.stream_recorder.stream_recorder as stream_recorder

    

try:
    # initialize connection handler singleton
    connectionHändler.getInstance()

    # start robo
    password = getpass.getpass("SSH Passwort für jetson eingeben: ")
    controller = RobotSSHController(
        serverIP=config.setup_data["ip_address"],
        password=password
    )
    controller.run()
    controller.ready.wait()

    recorder = stream_recorder.get_recorder()

    # start inputs and ui in separate threads
    print("Starting Lidar Input")
    obstacleDetection.main()
    print("Starting Gesture Input")
    gesture.start()
    print("Starting Stream Recorder")
    recorder.start()
    print("Starting Speech Input")
    si.start()
    ui.start_ui()
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(0)
