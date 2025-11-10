from Rosmaster_Lib import Rosmaster
import time
import sys
import select


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

    def turnright(self):
        self.g_bot.set_car_motion(0,0,0.1)


#passiert wenn dieses script aufgerufen wird
if __name__ == "__main__":
    controller = MovementControl()
    running = True
    print("Steuerung mit W/A/S/D, Drehen mit Q/E, Beenden mit X")
    while running:
        if select.select([sys.stdin], [], [], 0.1)[0]:
            key = sys.stdin.read(1)
            match key:
                case 'w':
                    controller.forwards()
                case 'a':
                    controller.left()
                case 's':
                    controller.backwards()
                case 'd':
                    controller.right()
                case 'q':
                    controller.turnleft()
                case 'e':
                    controller.turnright()
                case 'x':
                    running = False
                case _:
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


