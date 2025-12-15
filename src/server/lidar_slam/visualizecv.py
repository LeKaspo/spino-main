import math
import numpy as np
import cv2
import threading
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))
from server.app.connection import connectionHändler

WINDOW_SIZE = 800
SCALE = 0.5

def visualize():
    conn = connectionHändler.getInstance()
    frame_count = 0
    fps_clock = time.time()
    fps = 0
    
    try:    
        while True:
            scan = conn.getLidar()
            
            if not scan or len(scan) == 0:
                time.sleep(0.01)  # Nicht zu lang warten!
                continue
            
            frame_count += 1
            
            # Create a black image
            img = np.zeros((WINDOW_SIZE, WINDOW_SIZE, 3), dtype=np.uint8)

            # Draw center point
            center_x, center_y = WINDOW_SIZE // 2, WINDOW_SIZE // 2
            cv2.circle(img, (center_x, center_y), 5, (0, 0, 255), -1)

            point_count = 0
            for quality, angle, distance in scan:
                if distance > 0:
                    angle_rad = math.radians(angle)
                    x = distance * math.cos(angle_rad)
                    y = distance * math.sin(angle_rad)

                    px = int(center_x + x * SCALE)
                    py = int(center_y + y * SCALE)

                    if 0 <= px < WINDOW_SIZE and 0 <= py < WINDOW_SIZE:
                        cv2.circle(img, (px, py), 2, (0, 255, 0), -1)
                        point_count += 1

            # FPS berechnen
            if frame_count % 30 == 0:
                fps = 30 / (time.time() - fps_clock)
                fps_clock = time.time()

            # Info auf dem Fenster anzeigen
            cv2.putText(img, f"Frame: {frame_count} | Points: {point_count} | FPS: {fps:.1f}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            # ✅ WICHTIG: Fenster JEDES FRAME aktualisieren!
            cv2.imshow('LiDAR Visualization', img)
            
            # ✅ WICHTIG: Kleine Wartezeit für GUI Events
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("\n✓ Programm beendet")
    except Exception as e:
        print(f"✗ Fehler: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cv2.destroyAllWindows()

def main():
    print("🚀 Starte kontinuierliche LiDAR Visualisierung...")
    print("   Drücke 'q' zum Beenden")
    
    # ✅ WICHTIG: daemon=False damit das Fenster offen bleibt
    thread = threading.Thread(target=visualize, daemon=False)
    thread.start()
    
    try:
        while thread.is_alive():
            thread.join(0.1)
    except KeyboardInterrupt:
        print("\n🛑 Beende...")

if __name__ == "__main__":
    main()