from Rosmaster_Lib import Rosmaster
import time

class MovementControl:
    def __init__(self):
        self.g_bot = Rosmaster()

    def stop(self):
        self.g_bot.set_car_motion(0,0,0)
    
    def forwards(self, speed):
        self.g_bot.set_car_motion(speed,0,0)

#passiert wenn dieses script aufgerufen wird
if __name__ == "__main__":
    controller = MovementControl()
    print("Fahrzeug fährt los...")
    controller.forwards(0.1)
    time.sleep(2)
    print("Fahrzeug wird gestoppt...")
    controller.stop()
