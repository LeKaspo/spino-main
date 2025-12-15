import server.send_commands.sendcommands as sendcommands
import threading
import time
import sys
import json
from pathlib import Path
import server.config.config as config
from server.app.connection import connectionHändler
ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))


class Object_Detector:
        
        def __init__(self, max_distance=400, min_distance=100, field_of_view:int=20):

            # Validate parameters
            assert (field_of_view % 2 == 0), TypeError("field_of_view needs to be an even integer")

            self.max_distance = max_distance
            self.min_distance = min_distance
            self.field_of_view = field_of_view
            
            self.latest_obstacle = [False, False, False]
            self.previous_obstacle = []

            self.prev_scan = None

            self._stop_object_detection_thread = False

            self.conn = connectionHändler.getInstance()

        def start_update_scan_thread(self):
            self._update_scan_thread = threading.Thread(target=self._get_scan, args=())
            self._update_scan_thread.start()
        
        def start_object_detection_thread(self):
            self._object_detection_thread = threading.Thread(target=self._object_detection, args=())
            self._object_detection_thread.start()
            
        def _get_scan(self):
            while True:
                scan = self.conn.getLidar()
                if scan != self.prev_scan:
                    
                    self.prev_scan = scan

                    fow = self.field_of_view / 2

                    # Update latest_obstacle
                    left, center, right = False, False, False
                    for measure in scan:
                        quality, angle, distance = measure
                        # object detection right
                        if angle >= 90 - fow and angle <= 90 + fow and not right:
                            right = distance <= self.max_distance and distance >= self.min_distance
                        # object detection center
                        elif angle >= -fow and angle <= fow and not center:
                                center = distance <= self.max_distance and distance >= self.min_distance
                        # object detection left
                        elif angle >= 270 - fow and angle <= 270 + fow and not left:
                            left = distance <= self.max_distance and distance >= self.min_distance

                    self.latest_obstacle = [left, center, right]



        def _object_detection(self):
            while not self._stop_object_detection_thread:
                if ((self.latest_obstacle[0] or self.latest_obstacle[1] or self.latest_obstacle[2])): # and self.latest_obstacle is not self.previous_obstacle
                    data = {
                    "type": "fullstop",
                    "params": {}
                    }
                    sendcommands.sendJson(json.dumps(data))
                    #config.system_status["stop_flag"] = True
                    #self.previous_obstacle = self.latest_obstacle
                time.sleep(0.05)

def main():
    detector = Object_Detector()

    detector.start_update_scan_thread()
    detector.start_object_detection_thread()

