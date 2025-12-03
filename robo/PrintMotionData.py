import threading

from Rosmaster_Lib import Rosmaster

class MotionData:

    def __init__(self):
        self.g_bot = Rosmaster()

    def start_print_motion_thread(self):
        self._print_motor_thread = threading.Thread(target= self._printMotion, args = ())
        self._print_motor_thread.start()

    def start_print_encoder_thread(self):
        self._print_encoder_thread = threading.Thread(target= self._printEncoder, args = ())
        self._print_motor_thread.start()

    def _printMotion(self):
        while True:
            x, y, z = self.g_bot.get_motion_data()
            print(x + y +z)

    def _printEncoder(self):
        while True:
            m1, m2, m3, m4 = self.g_bot.get_motor_encoder()
            print(m1 + m2 + m3 + m4)




if __name__ == "__main__":
    m = MotionData()

    try:
        m.start_print_motion_thread()
        #m.start_print_encoder_thread()
    finally:
        del m
        