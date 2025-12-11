import threading

from robo.ext_libs.Rosmaster_Lib import Rosmaster

class MotionData:

    def __init__(self):
        self.g_bot = Rosmaster()
        self.stop_print_motion = False
        self.stop_print_encoder = False


    def start_print_motion_thread(self):
        self._print_motor_thread = threading.Thread(target= self._printMotion, args = ())
        self._print_motor_thread.start()

    def start_print_encoder_thread(self):
        self._print_encoder_thread = threading.Thread(target= self._printEncoder, args = ())
        self._print_motor_thread.start()

    def _printMotion(self):
        while not self.stop_print_motion:
            x, y, z = self.g_bot.get_motion_data()
            print(f"{x} + {y} + {z}")

    def _printEncoder(self):
        while self.stop_print_encoder:
            m1, m2, m3, m4 = self.g_bot.get_motor_encoder()
            print(f"{m1} + {m2} + {m3} + {m4}")




if __name__ == "__main__":
    while True:
        pass
        