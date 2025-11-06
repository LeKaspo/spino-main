from Rosmaster_Lib import Rosmaster
import time

class MovementControl:
    def __init__(self):
        self.g_bot = Rosmaster()

    def stop(self):
        self.g_bot.set_car_motion(0,0,0)

    def forwards(self):
        self.g_bot.set_car_motion(0.1,0,0)

    def backwards(self):
        self.g_bot.set_car_motion(-0.1,0,0)

    def right(self):
        self.g_bot.set_car_motion(0,-0.1,0)

    def left(self):
        self.g_bot.set_car_motion(0,0.1,0)

    def turnleft(self):
        self.g_bot.set_car_motion(0,0,-0.1)

    def turnleft(self):
        self.g_bot.set_car_motion(0,0,0.1)


#passiert wenn dieses script aufgerufen wird
if __name__ == "__main__":
    controller = MovementControl()
    controller.right()
    time.wait(2)
    controller.left()
    time.wait(2)
    controller.turnright()
    time.wait(2)
    controller.turnleft()
    time.wait(2)
    print("Fahrzeug wird gestoppt...")
    controller.stop()


"""
Nutzung
Datei im leichen Vrrzeichniss oder Import ensprechend anpassen

from movement_control import MovementControl

# Objekt erstellen
controller = MovementControl()

# Methode aufrufen
controller.Stop()
"""


