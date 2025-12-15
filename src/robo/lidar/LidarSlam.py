import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from robo.ext_libs.rplidar import RPLidar, RPLidarException
from robo.sockets.sendLidar import lidarSänder
from robo.lidar.mutex import Mutex
import threading
import atexit

class RoboLidar:

    def __init__(self, port='/dev/rplidar'):
        '''
        Parameters:
        - port: Serial port that the lidar is connected to.
        - max_distance: mm
        - min_distance: mm
        - field_of_view: the field of view for object detection, in degrees
        '''

        self.sender = lidarSänder.getInstance()

        self.lidarMutex = Mutex()
        
        self.prev_scan = None

        # Initialise lidar
        self.lidar2 = RPLidar('/dev/rplidar')
        self.lidar2.stop()
        self.lidar2.stop_motor()
        self.lidar2.disconnect()

        self.lidar = RPLidar(port, timeout=5)
        info = self.lidar.get_info()
        health = self.lidar.get_health()
        print(f"Info: {info}")
        print(f"Health: {health}")
        
        # Attributes
        self._stop_update_thread = False
        self._stop_tcp_thread = False
        self._stop_object_detection_thread = False

        # Ensure proper closing of the lidar
        atexit.register(self.cleanup)

    def start_working_thread(self):
        '''
        Call this method once to continuously update self.latest_scan and self.latest_obstacle.
        '''
        self._update_thread = threading.Thread(target=self._update)
        self._update_thread.start()

    def start_tcp_thread(self):
        '''
        Call this method once, to start sending the self.latest_scan() to a remote socket continuously.
        Parameters:
        - ip: IP address of the target machine
        - port: Port on the target machine
        '''
        self._tcp_thread = threading.Thread(target=self._send_lidar_data)
        self._tcp_thread.start()

    def start_object_detection_thread(self):
        self._object_detection_thread = threading.Thread(target=self._object_detection, args=())
        self._object_detection_thread.start()

    def _update(self): 
        while True:
            try:
                for i, scan in enumerate(self.lidar.iter_scans(scan_type="express")): 
                    if self._stop_update_thread:
                        break
            
                    # Update latest_scan
                    #if i % 1 == 0:
                    self.lidarMutex.write(scan)
            except RPLidarException:
                self.lidar.clean_input()

    def _send_lidar_data(self):
        """
        Continuously sends latest scan data over a TCP connection.
        Parameters:
        - ip: IP address of the target machine
        - port: Port on the target machine
        """
        while True:
            try:
                while not self._stop_tcp_thread:
                    scan = self.lidarMutex.read()
                    if scan != self.prev_scan:
                        self.prev_scan = scan
                        self.sender.putLidarData(scan)

            except Exception as e:
                print(f"Error in sending LidarData: {e}")

    def cleanup(self):
        """Cleanup resources when the program exits."""
        try:
            self.lidar.stop()
            self.lidar.stop_motor()
            self.lidar.clean_input()
            self.lidar.disconnect()
            print("Lidar safely disconnected.")
        except RPLidarException as e:
            print(f"Error during lidar cleanup: {e}")

    def __del__(self):
        self.cleanup()

def main():
    robolidar = RoboLidar('/dev/rplidar')
    try:
        
        print("Starting Lidar Threads")
        robolidar.start_working_thread()
        robolidar.start_tcp_thread()
        
        '''
        robolidar.start_object_detection_thread()
        print("Started object detection thread")
        '''
        
    finally:
        del robolidar