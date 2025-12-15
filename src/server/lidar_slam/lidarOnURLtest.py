import io
import time
import numpy as np
import threading
import matplotlib
import matplotlib.pyplot as plt
from flask import Flask, Response
import sys
from pathlib import Path

matplotlib.use('Agg')

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))
from server.app.connection import connectionHändler

app = Flask(__name__)

# Globaler Frame Buffer
current_frame = None
frame_lock = threading.Lock()

def generate_frames():
    """Generiere MJPEG Frames"""
    global current_frame
    
    conn_lidar = connectionHändler.getInstance()
    frame_count = 0
    
    while True:
        try:
            scan = conn_lidar.getLidar()
            
            if not scan or len(scan) == 0:
                time.sleep(0.01)
                continue
            
            frame_count += 1
            
            fig, ax = plt.subplots(figsize=(10, 10), facecolor='black')
            ax.set_facecolor('black')
            
            x_points, y_points, distances = [], [], []
            
            for quality, angle, distance in scan:
                angle_rad = np.radians(angle)
                x = (distance / 1000) * np.cos(angle_rad)
                y = (distance / 1000) * np.sin(angle_rad)
                x_points.append(x)
                y_points.append(y)
                distances.append(distance)
            
            scatter = ax.scatter(x_points, y_points, c=distances, cmap='hot',
                                s=120, alpha=0.95, vmin=0, vmax=8000,
                                edgecolors='white', linewidth=0.5)
            
            ax.set_xlim(-15, 15)
            ax.set_ylim(-15, 15)
            ax.set_aspect('equal')
            ax.grid(True, alpha=0.2, color='white', linestyle='--', linewidth=0.5)
            ax.set_xlabel('X (m)', color='white', fontsize=12, fontweight='bold')
            ax.set_ylabel('Y (m)', color='white', fontsize=12, fontweight='bold')
            ax.tick_params(colors='white', labelsize=10)
            
            for spine in ax.spines.values():
                spine.set_edgecolor('white')
            
            ax.set_title(f'Lidar 2D View | Frame #{frame_count}',
                        color='white', fontsize=14, fontweight='bold', pad=20)
            
            cbar = plt.colorbar(scatter, ax=ax, label='Distance (mm)')
            cbar.ax.tick_params(colors='white')
            cbar.ax.yaxis.label.set_color('white')
            
            buf = io.BytesIO()
            plt.savefig(buf, format='jpeg', facecolor='black')
            plt.close(fig)
            buf.seek(0)
            
            with frame_lock:
                current_frame = buf.read()
            
            time.sleep(0.05)
            
        except Exception as e:
            print(f"Fehler: {e}")
            time.sleep(0.1)

def mjpeg_generator():
    """Generator für MJPEG Stream"""
    while True:
        with frame_lock:
            if current_frame:
                frame = current_frame
            else:
                time.sleep(0.01)
                continue
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n'
               b'Content-Length: ' + str(len(frame)).encode() + b'\r\n\r\n'
               + frame + b'\r\n')

@app.route('/stream')
def stream():
    """MJPEG Stream"""
    return Response(mjpeg_generator(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

def main():
    # Starte Frame-Generator
    generator_thread = threading.Thread(target=generate_frames, daemon=True)
    generator_thread.start()
    
    print("Server läuft auf http://192.168.0.78:50010/stream")
    app.run(host='192.168.0.78', port=50010, debug=False, threaded=True)