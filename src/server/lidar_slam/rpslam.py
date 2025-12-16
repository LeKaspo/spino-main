#!/usr/bin/env python3

'''
rpslam.py : BreezySLAM Python with SLAMTECH RP A1 Lidar
                 
Copyright (C) 2018 Simon D. Levy

This code is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as 
published by the Free Software Foundation, either version 3 of the 
License, or (at your option) any later version.

This code is distributed in the hope that it will be useful,     
but WITHOUT ANY WARRANTY without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License 
along with this code.  If not, see <http://www.gnu.org/licenses/>.
'''
import sys
from pathlib import Path
import threading
ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from server.app.connection import connectionHändler
import server.config.config as config

def main():
    print("Starting Lidar Thread")
    t = threading.Thread(target=BreezySlam,daemon=True)
    t.start()


def BreezySlam():
    conn = connectionHändler.getInstance()

    MAP_SIZE_PIXELS         = 500
    MAP_SIZE_METERS         = 10



    # Ideally we could use all 250 or so samples that the RPLidar delivers in one 
    # scan, but on slower computers you'll get an empty map and unchanging position
    # at that rate.
    MIN_SAMPLES   = 10

    try:
        from breezyslam.algorithms import RMHC_SLAM # type: ignore
        from breezyslam.sensors import RPLidarA1 as LaserModel # type: ignore
        from roboviz import MapVisualizer # type: ignore
    except Exception as e:
        print(f"Breezy Import failed: {e}")
        print("Install BreezySLAM and Visualize as stated in docs")
        sys.exit(0)


    # Create an RMHC SLAM object with a laser model and optional robot model
    slam = RMHC_SLAM(LaserModel(), MAP_SIZE_PIXELS, MAP_SIZE_METERS)

    # Set up a SLAM display
    viz = MapVisualizer(MAP_SIZE_PIXELS, MAP_SIZE_METERS, 'SLAM')

    # Initialize an empty trajectory
    trajectory = []

    # Initialize empty map
    mapbytes = bytearray(MAP_SIZE_PIXELS * MAP_SIZE_PIXELS)

    # We will use these to store previous scan in case current scan is inadequate
    previous_distances = None
    previous_angles    = None

    prev_scan = None

    while True:
        if config.system_status["slam_active"]:
            # Extract (quality, angle, distance) triples from current scan
            scan = conn.getLidar()
            if scan != prev_scan:
                prev_scan = scan
                items = [item for item in scan]

                # Extract distances and angles from triples
                distances = [item[2] for item in items]
                angles    = [(180-item[1])%360 for item in items]

            # Update SLAM with current Lidar scan and scan angles if adequate
            if len(distances) > MIN_SAMPLES:
                slam.update(distances, scan_angles_degrees=angles)
                previous_distances = distances.copy()
                previous_angles    = angles.copy()

            # If not adequate, use previous
            elif previous_distances is not None:
                slam.update(previous_distances, scan_angles_degrees=previous_angles)

            # Get current robot position
            x, y, theta = slam.getpos()

                # Get current map bytes as grayscale
            slam.getmap(mapbytes)

            # Display map and robot pose, exiting gracefully if user closes it
            if not viz.display(x/1000., y/1000., theta, mapbytes):
                print("Exiting SLAM Thread")
                exit(0)
