from rplidar import RPLidar, RPLidarException
import time
import socket
import threading
import json 
import atexit

class RoboLidar:

    def __init__(self, port='/dev/rplidar', max_distance=300, min_distance=100, field_of_view:int=20):
        '''
        Parameters:
        - port: Serial port that the lidar is connected to.
        - max_distance: mm
        - min_distance: mm
        - field_of_view: the field of view for object detection, in degrees
        '''

        # Validate parameters
        assert (field_of_view % 2 == 0), TypeError("field_of_view needs to be an even integer")

        self.max_distance = max_distance
        self.min_distance = min_distance
        self.field_of_view = field_of_view

        # Initialise lidar
        self.lidar = RPLidar(port, timeout=5)
        info = self.lidar.get_info()
        health = self.lidar.get_health()
        print(f"Info: {info}")
        print(f"Health: {health}")
        
        # Attributes
        self.latest_obstacle = [False, False, False]
        self.latest_scan = []
        self._stop_update_thread = False
        self._stop_tcp_thread = False
        self._stop_print_thread = False

        # Ensure proper closing of the lidar
        atexit.register(self.cleanup)

    def start_working_thread(self):
        '''
        Call this method once to continuously update self.latest_scan and self.latest_obstacle.
        '''
        self._update_thread = threading.Thread(target=self._update, args=(self.max_distance, self.min_distance))
        self._update_thread.start()

    def start_tcp_tread(self, ip, port):
        '''
        Call this method once, to start sending the self.latest_scan() to a remote socket continuously.
        Parameters:
        - ip: IP address of the target machine
        - port: Port on the target machine
        '''
        self._tcp_thread = threading.Thread(target=self._send_lidar_data, args=(ip, port))
        self._tcp_thread.start()

    def start_print_thread(self):
        self._print_thread = threading.Thread(target=self._print_scan, args=())
        self._print_thread.start()

    def _update(self, max_distance:int, min_distance:int): 
        """
        Yields true if lidar detects an object in fornt, to the left, and to the right of the robot. (10° window)
        This action is calibrated with max- and min_distance. If the lidar detects an object closer than max_distance, but further away than min_distance, it yields true.
        Parameters:
        - max_distance: mm
        - min_distance: mm
        """
        print("in update")
        iterator = self.lidar.iter_scans()
        for scan in iterator:
            if self._stop_update_thread:
                break
            
            # Update latest_scan
            self.latest_scan = scan
            # [{"quality": quality, "angle": angle, "distance": distance} for quality, angle, distance in scan] # JSON-compatible list of dictionaries

            fow = self.field_of_view / 2

            # Update latest_obstacle
            left, center, right = False, False, False
            for measure in scan:
                quality, angle, distance = measure
                # object detection right
                if angle >= 90 - fow and angle <= 90 + fow:
                    right = distance <= max_distance and distance >= min_distance
                # object detection center
                elif angle >= -fow and angle <= fow:
                    center = distance <= max_distance and distance >= min_distance
                # object detection left
                elif angle >= 270 - fow and angle <= 270 + fow:
                    left = distance <= max_distance and distance >= min_distance
            
            self.latest_obstacle = [left, center, right]

    def _send_lidar_data(self, ip='192.168.0.229', port=50003):
        """
        Continuously sends latest scan data over a TCP connection.
        Parameters:
        - ip: IP address of the target machine
        - port: Port on the target machine
        """
        while True:
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
            with client:
                try:
                    while not self._stop_tcp_thread:
                        # Convert latest_scan to JSON string aa
                        data = json.dumps(self.latest_scan)
                        client.sendall(self.latest_scan.encode('utf-8'))
                        time.sleep(0.1)  # Send data every 100ms
                except Exception as e:
                    print(f"Error in sending data: {e}")

    def _print_scan(self):
        while not self._stop_print_thread:
            print(self.latest_obstacle)
            time.sleep(1)


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
        robolidar.start_tcp_tread("192.168.0.229", 50002)
        print("Started tcp thread")
        
        '''
        robolidar.start_print_thread()
        print("Started printing thread")
        '''
        
    finally:
        del robolidar

if __name__ == "__main__":
    main()
