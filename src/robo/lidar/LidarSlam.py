import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from robo.ext_libs.rplidar import RPLidar, RPLidarException
from robo.sockets.sendLidar import lidarSänder
import time
import threading
import atexit

IP_ADRESS = '192.168.0.78'

class RoboLidar:

    def __init__(self, port='/dev/rplidar', max_distance=300, min_distance=100, field_of_view:int=20):
        '''
        Parameters:
        - port: Serial port that the lidar is connected to.
        - max_distance: mm
        - min_distance: mm
        - field_of_view: the field of view for object detection, in degrees
        '''

        self.sender = lidarSänder.getInstance()
        

        # Validate parameters
        assert (field_of_view % 2 == 0), TypeError("field_of_view needs to be an even integer")

        self.max_distance = max_distance
        self.min_distance = min_distance
        self.field_of_view = field_of_view

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
        self.latest_scan = []
        self.last_scan = []
        self._stop_update_thread = False
        self._stop_tcp_thread = False
        self._stop_object_detection_thread = False

        # Ensure proper closing of the lidar
        atexit.register(self.cleanup)

    def start_working_thread(self):
        '''
        Call this method once to continuously update self.latest_scan and self.latest_obstacle.
        '''
        self._update_thread = threading.Thread(target=self._update, args=(self.max_distance, self.min_distance))
        self._update_thread.start()

    def start_tcp_thread(self):
        '''
        Call this method once, to start sending the self.latest_scan() to a remote socket continuously.
        Parameters:
        - ip: IP address of the target machine
        - port: Port on the target machine
        '''
        print("Hello im in the start_tcp_thread")
        self._tcp_thread = threading.Thread(target=self._send_lidar_data)
        self._tcp_thread.start()

    def start_object_detection_thread(self):
        self._object_detection_thread = threading.Thread(target=self._object_detection, args=())
        self._object_detection_thread.start()

    def _update(self, max_distance:int, min_distance:int): 
        """
        Yields true if lidar detects an object in fornt, to the left, and to the right of the robot. (10° window)
        This action is calibrated with max- and min_distance. If the lidar detects an object closer than max_distance, but further away than min_distance, it yields true.
        Parameters:
        - max_distance: mm
        - min_distance: mm
        """
        print("in update")
        while True:
            try:
                for i, scan in enumerate(self.lidar.iter_scans()): #scan_type='express'
                    if self._stop_update_thread:
                        break
            
                    # Update latest_scan
                    #if i % 2 == 0:
                    self.latest_scan = scan
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
            '''
            while True:
                try:
                    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    client.connect((ip, port))
                    print(f"Lidar Connected to {ip}:{port}")
                    break
                except ConnectionRefusedError:
                    print("Lidar Connection refused. Retrying in 2 seconds...")
                    time.sleep(2)
                except Exception as e:
                    print(f"Error while trying to connect {e}")
                    client.close()
                    return
            '''
            try:
                while not self._stop_tcp_thread:
                    if self.latest_scan != self.last_scan:

                        self.last_scan = self.latest_scan

                        #filtered_scan = [measure for measure in self.latest_scan if (measure[1] >= 270 or measure[1] <= 90)]
                        self.sender.putLidarData(self.latest_scan)

            except Exception as e:
                print(f"Error in sending data: {e}")

    def _object_detection(self):
        while not self._stop_object_detection_thread:
            if self.latest_obstacle[0] or self.latest_obstacle[1] or self.latest_obstacle[2]:
                print("Clear Queue and Fullstop")
            time.sleep(0.5)


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
    robolidar = RoboLidar('/dev/rplidar', field_of_view=40)
    try:
        robolidar.start_working_thread()
        print("Started working thread")

        robolidar.start_tcp_thread()
        print("Started tcp thread")
        
        '''
        robolidar.start_object_detection_thread()
        print("Started object detection thread")
        '''
        
    finally:
        del robolidar

if __name__ == "__main__":
    main()
