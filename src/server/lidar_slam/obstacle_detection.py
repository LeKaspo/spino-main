from server.app.connection import connectionHändler
import threading
import time
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))


class Object_Detector:
        
        def __init__(self, max_distance=300, min_distance=100, field_of_view:int=20):

            # Validate parameters
            assert (field_of_view % 2 == 0), TypeError("field_of_view needs to be an even integer")

            self.max_distance = max_distance
            self.min_distance = min_distance
            self.field_of_view = field_of_view
            
            self.latest_obstacle = [False, False, False]

            self._stop_object_detection_thread = False

            self.start_object_detection_thread()

        
        def start_object_detection_thread(self):
            self._object_detection_thread = threading.Thread(target=self._object_detection, args=())
            self._object_detection_thread.start()
            
        def get_scan(self, scan):
            self.scan = scan
                
            fow = self.field_of_view / 2

            # Update latest_obstacle
            left, center, right = False, False, False
            for measure in self.scan:
                quality, angle, distance = measure
                # object detection right
                if angle >= 90 - fow and angle <= 90 + fow:
                    right = distance <= self.max_distance and distance >= self.min_distance
                    # object detection center
                elif angle >= -fow and angle <= fow:
                        center = distance <= self.max_distance and distance >= self.min_distance
               # object detection left
                elif angle >= 270 - fow and angle <= 270 + fow:
                    left = distance <= self.max_distance and distance >= self.min_distance

            self.latest_obstacle = [left, center, right]



        def _object_detection(self):
            while not self._stop_object_detection_thread:
                if self.latest_obstacle[0] or self.latest_obstacle[1] or self.latest_obstacle[2]:
                    print("Clear Queue and Fullstop")
                time.sleep(0.25)

            