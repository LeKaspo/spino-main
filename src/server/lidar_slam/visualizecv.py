import math
import numpy as np
import cv2
import threading
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))
from server.app.connection import connectionHändler


WINDOW_SIZE = 10
SCALE = 10

def visualize():
        conn = connectionHändler.getInstance()

        last_scan = None
        
        try:    
            while True:
                
                scan = conn.getLidar()

                if scan != last_scan:
            
                    # Create a black image
                    img = np.zeros((WINDOW_SIZE, WINDOW_SIZE, 3), dtype=np.uint8)
                    # Create a mask for line detection (single channel)
                    mask = np.zeros((WINDOW_SIZE, WINDOW_SIZE), dtype=np.uint8)

                    # Draw center point
                    center_x, center_y = WINDOW_SIZE // 2, WINDOW_SIZE // 2
                    cv2.circle(img, (center_x, center_y), 5, (0, 0, 255), -1)

                    for quality, angle, distance in scan:
                        if distance > 0:
                            # Convert angle to radians
                            angle_rad = math.radians(angle)

                            # Polar to Cartesian
                            x = distance * math.cos(angle_rad)
                            y = distance * math.sin(angle_rad)

                            # Map to image coordinates
                            px = int(center_x + x * SCALE)
                            py = int(center_y + y * SCALE)

                            if 0 <= px < WINDOW_SIZE and 0 <= py < WINDOW_SIZE:
                                # Draw all points in green
                                cv2.circle(img, (px, py), 2, (0, 255, 0), -1)
        except KeyboardInterrupt as e:
             print("keyboard interrupt visualize")

        

def main():
    thread = threading.Thread(target=visualize, daemon=True)
    thread.start()

if __name__ == "__name__":
    main()