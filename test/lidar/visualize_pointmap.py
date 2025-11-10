import csv
import math
import matplotlib.pyplot as plt
import subprocess
# Dateiname der zu plottenden CSV:
csv_filename = "lidar_scans_1.csv"  # Hier anpassen!

proc = subprocess.Popen("path", )

proc.kill()

xs = []
ys = []

# CSV einlesen und Polarkoordinaten in XY umrechnen
with open(csv_filename, 'r') as csvfile:
    csv_reader = csv.DictReader(csvfile)
    for row in csv_reader:
        angle = float(row['angle_deg'])
        distance = float(row['distance_mm'])
        # Negative oder 0-Abstände ignorieren
        if distance <= 0:
            continue
        radians = math.radians(angle)
        y = distance * math.cos(radians)
        x = distance * math.sin(radians)
        xs.append(x)
        ys.append(y)

# Punktwolke plotten
plt.figure(figsize=(8, 8))
plt.scatter(xs, ys, s=2, c='blue')
plt.gca().set_aspect('equal', adjustable='datalim')
plt.xlabel("x [mm]")
plt.ylabel("y [mm]")
plt.title("Lidar Punktwolke aus CSV")
plt.grid(True)
plt.show()