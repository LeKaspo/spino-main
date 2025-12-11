import threading
import time
import numpy as np
import matplotlib.pyplot as plt

import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from server.app.connection import connectionHändler
 
# ========== ANGEPASSTE BEREICHE ==========
MIN_QUALITY = 5
MIN_DISTANCE = 100   # 10 cm (vorher 200 = 20 cm)
MAX_DISTANCE = 3000  # 3 Meter
# =========================================
 
lidar_points = []
lidar_lock = threading.Lock()
 
def lidar_data_collector(connector):
    global lidar_points
   
    print("🔍 LIDAR SAMMLER GESTARTET")
    print(f"   Min Distanz: {MIN_DISTANCE/10:.1f} cm")
    print(f"   Max Distanz: {MAX_DISTANCE/10:.1f} cm")
   
    while True:
        try:
            lidar_data = connector.getLidar()
           
            #if lidar_data and isinstance(lidar_data, list):
            current_points = []
               
            for measurement in lidar_data:
                if len(measurement) >= 3:
                        #quality = float(measurement[0])
                        angle_deg = float(measurement[1])
                        distance_mm = float(measurement[2])
                        #quality >= MIN_QUALITY and
                       
                        if MIN_DISTANCE <= distance_mm <= MAX_DISTANCE:
                            # Korrigierte Transformation
                            angle_rad = np.radians(angle_deg)
                            x = distance_mm * np.sin(angle_rad)
                            y = distance_mm * np.cos(angle_rad)
                           
                            current_points.append({
                                'angle': angle_deg,
                                'distance': distance_mm,
                                'x': x,
                                'y': y
                            })
               
                with lidar_lock:
                    lidar_points = current_points
           
            time.sleep(0.05)
           
        except Exception as ex:
            print(f"Fehler: {ex}")
            time.sleep(0.5)
 
def visualize_loop():
    """Visualisierung mit 10 cm Minimum"""
   
    plt.ion()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
   
    # Setup Polar
    ax1 = plt.subplot(121, projection='polar')
    ax1.set_title('LIDAR Polar View (10 cm - 3 m)', fontsize=14, fontweight='bold')
    ax1.set_theta_zero_location('N')
    ax1.set_theta_direction(-1)
    ax1.set_ylim(0, MAX_DISTANCE)
   
    # Setup Kartesisch
    ax2 = plt.subplot(122)
    ax2.set_title('LIDAR Draufsicht (10 cm - 3 m)', fontsize=14, fontweight='bold')
    ax2.set_xlabel('X (mm) → RECHTS', fontsize=12)
    ax2.set_ylabel('Y (mm) → VORNE', fontsize=12)
    ax2.set_xlim(-MAX_DISTANCE, MAX_DISTANCE)
    ax2.set_ylim(-MAX_DISTANCE, MAX_DISTANCE)
    ax2.grid(True, alpha=0.3)
    ax2.set_aspect('equal')
   
    # Zeichne Mindestabstand-Kreis (10 cm)
    circle_min = plt.Circle((0, 0), MIN_DISTANCE, color='red', fill=False,
                            linestyle='--', linewidth=2, alpha=0.5, label=f'Min {MIN_DISTANCE/10:.0f} cm')
   
    # Zeichne Maximalabstand-Kreis (3 m)
    circle_max = plt.Circle((0, 0), MAX_DISTANCE, color='blue', fill=False,
                            linestyle='--', linewidth=2, alpha=0.3, label=f'Max {MAX_DISTANCE/10:.0f} cm')
   
    plt.tight_layout()
   
    frame = 0
    colorbar_added = False
   
    while True:
        try:
            frame += 1
           
            with lidar_lock:
                points = lidar_points.copy()
           
            # Clear
            ax1.clear()
            ax2.clear()
           
            # Re-setup Polar
            ax1.set_title(f'LIDAR Polar View (Frame {frame})', fontsize=14, fontweight='bold')
            ax1.set_theta_zero_location('N')
            ax1.set_theta_direction(-1)
            ax1.set_ylim(0, MAX_DISTANCE)
           
            # Re-setup Kartesisch
            ax2.set_title(f'LIDAR Draufsicht (Frame {frame})', fontsize=14, fontweight='bold')
            ax2.set_xlabel('X (mm) → RECHTS', fontsize=12)
            ax2.set_ylabel('Y (mm) → VORNE', fontsize=12)
            ax2.set_xlim(-MAX_DISTANCE, MAX_DISTANCE)
            ax2.set_ylim(-MAX_DISTANCE, MAX_DISTANCE)
            ax2.grid(True, alpha=0.3)
            ax2.set_aspect('equal')
           
            # Roboter-Position
            ax2.plot(0, 0, 'ro', markersize=20, label='Roboter', zorder=10)
           
            # Mindest- und Maximalabstand-Kreise
            circle_min = plt.Circle((0, 0), MIN_DISTANCE, color='red', fill=False,
                                    linestyle='--', linewidth=2, alpha=0.5)
            circle_max = plt.Circle((0, 0), MAX_DISTANCE, color='blue', fill=False,
                                    linestyle='--', linewidth=1, alpha=0.3)
            ax2.add_patch(circle_min)
            ax2.add_patch(circle_max)
           
            # Richtungs-Pfeile
            arrow_len = MAX_DISTANCE * 0.3
           
            # VORNE = +Y (0°)
            ax2.arrow(0, 0, 0, arrow_len, head_width=150, head_length=200,
                     fc='red', ec='red', alpha=0.6, linewidth=3, zorder=5)
            ax2.text(0, arrow_len + 250, 'VORNE\n(0°)', ha='center',
                    fontsize=12, fontweight='bold', color='red')
           
            # RECHTS = +X (90°)
            ax2.arrow(0, 0, arrow_len, 0, head_width=150, head_length=200,
                     fc='blue', ec='blue', alpha=0.6, linewidth=3, zorder=5)
            ax2.text(arrow_len + 250, 0, 'RECHTS\n(90°)', ha='left',
                    fontsize=12, fontweight='bold', color='blue')
           
            # HINTEN = -Y (180°)
            ax2.arrow(0, 0, 0, -arrow_len, head_width=150, head_length=200,
                     fc='green', ec='green', alpha=0.6, linewidth=3, zorder=5)
            ax2.text(0, -arrow_len - 250, 'HINTEN\n(180°)', ha='center',
                    fontsize=12, fontweight='bold', color='green')
           
            # LINKS = -X (270°)
            ax2.arrow(0, 0, -arrow_len, 0, head_width=150, head_length=200,
                     fc='orange', ec='orange', alpha=0.6, linewidth=3, zorder=5)
            ax2.text(-arrow_len - 250, 0, 'LINKS\n(270°)', ha='right',
                    fontsize=12, fontweight='bold', color='orange')
           
            if len(points) > 0:
                angles = [p['angle'] for p in points]
                distances = [p['distance'] for p in points]
                x_coords = [p['x'] for p in points]
                y_coords = [p['y'] for p in points]
               
                # Plot Polar
                ax1.scatter([np.radians(a) for a in angles], distances,
                           c=distances, cmap='plasma', s=40, alpha=0.8,
                           vmin=MIN_DISTANCE, vmax=MAX_DISTANCE)
               
                # Plot Kartesisch
                scatter = ax2.scatter(x_coords, y_coords,
                                     c=distances, cmap='plasma', s=40, alpha=0.8,
                                     vmin=MIN_DISTANCE, vmax=MAX_DISTANCE, zorder=3)
               
                # Colorbar (nur einmal hinzufügen)
                if not colorbar_added:
                    cbar = plt.colorbar(scatter, ax=ax2, label='Distanz (mm)')
                    cbar.ax.set_ylabel('Distanz (mm)', fontsize=10)
                    colorbar_added = True
               
                # Nächster Punkt
                min_idx = distances.index(min(distances))
                nearest_angle = angles[min_idx]
                nearest_dist = distances[min_idx]
                nearest_x = x_coords[min_idx]
                nearest_y = y_coords[min_idx]
               
                # Markiere nächsten Punkt
                ax2.plot(nearest_x, nearest_y, 'r*', markersize=20, zorder=15)
               
                # Zähle Punkte in verschiedenen Bereichen
                very_close = sum(1 for d in distances if d < 200)  # < 20 cm
                close = sum(1 for d in distances if 200 <= d < 500)  # 20-50 cm
                medium = sum(1 for d in distances if 500 <= d < 1000)  # 50-100 cm
                far = sum(1 for d in distances if d >= 1000)  # > 100 cm
               
                # Statistiken
                stats = f"Punkte: {len(points)}\n"
                stats += f"  < 20cm: {very_close}\n"
                stats += f"  20-50cm: {close}\n"
                stats += f"  50-100cm: {medium}\n"
                stats += f"  > 100cm: {far}\n"
                stats += f"\nMin: {min(distances)/10:.1f} cm\n"
                stats += f"Max: {max(distances)/10:.1f} cm\n"
                stats += f"Avg: {sum(distances)/len(distances)/10:.1f} cm\n"
                stats += f"\n🎯 NÄCHSTER:\n"
                stats += f"Winkel: {nearest_angle:.1f}°\n"
                stats += f"Dist: {nearest_dist/10:.1f} cm\n"
                stats += f"X: {nearest_x/10:.1f} cm\n"
                stats += f"Y: {nearest_y/10:.1f} cm"
               
                ax2.text(0.02, 0.98, stats, transform=ax2.transAxes,
                        va='top', fontsize=9,
                        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9))
            else:
                ax2.text(0.5, 0.5, '⚠️ Keine Daten!\nWarte auf Lidar...',
                        transform=ax2.transAxes, ha='center', va='center',
                        fontsize=14, fontweight='bold',
                        bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
           
            # Legende mit Kreisen
            legend_elements = [
                plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='r',
                          markersize=10, label='Roboter'),
                plt.Line2D([0], [0], color='red', linestyle='--', linewidth=2,
                          label=f'Min {MIN_DISTANCE/10:.0f} cm'),
                plt.Line2D([0], [0], color='blue', linestyle='--', linewidth=1,
                          label=f'Max {MAX_DISTANCE/10:.0f} cm')
            ]
            ax2.legend(handles=legend_elements, loc='upper right', fontsize=9)
           
            plt.pause(0.1)
           
        except KeyboardInterrupt:
            print("\n[Visualisierung] Beendet")
            break
        except Exception as ex:
            print(f"Visualisierung Fehler: {ex}")
            import traceback
            traceback.print_exc()
            time.sleep(0.5)
 
def main():

    conn = connectionHändler.getInstance()
   
    print("="*80)
    print("🔍 LIDAR VISUALISIERUNG (10 CM MINIMUM)")
    print("="*80)
    print(f"\n📏 Messbereich:")
    print(f"   Minimum: {MIN_DISTANCE/10:.1f} cm (10 cm)")
    print(f"   Maximum: {MAX_DISTANCE/10:.1f} cm (3 Meter)")
    print("\n📊 Koordinaten-System:")
    print("   0° (VORNE)  = +Y Achse")
    print("   90° (RECHTS) = +X Achse")
    print("   180° (HINTEN) = -Y Achse")
    print("   270° (LINKS)  = -X Achse")
    print("="*80)

    threading.Thread(target=lidar_data_collector, args=(conn,), daemon=True).start()
   
    time.sleep(3)
   
    print("\n📊 Öffne Fenster...")
    print("💡 Du kannst jetzt Objekte ab 10 cm Entfernung sehen!")
    print("💡 Der rote gestrichelte Kreis zeigt die 10 cm Grenze")
   
    try:
        #threading.Thread(target=visualize_loop, daemon=True)
        visualize_loop()
    except KeyboardInterrupt:
        print("\n[Main] Programm beendet")