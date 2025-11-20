from Rosmaster_Lib import Rosmaster # type: ignore
import time

class MovementControl:
    def __init__(self):
        self.g_bot = Rosmaster()
        self.speed = 0.5

    def fullstop(self):
        self.g_bot.set_car_motion(0,0,0)

    def stopRotate(self):
        self.g_bot.set_car_motion(0,0,0)

    def stopLeftRight(self):
        self.g_bot.set_car_motion(0,0,0)

    def stopForwardsBackwards(self):
        self.g_bot.set_car_motion(0,0,0)

    def forwards(self):
        self.g_bot.set_car_motion(self.speed,0,0)

    def backwards(self):
        self.g_bot.set_car_motion(-self.speed,0,0)

    def right(self):
        self.g_bot.set_car_motion(0,-self.speed,0)

    def left(self):
        self.g_bot.set_car_motion(0,self.speed,0)

    def turnRight(self):
        self.g_bot.set_car_motion(0,0,-self.speed)

    def turnLeft(self):
        self.g_bot.set_car_motion(0,0,self.speed)
    
    def setspeed(self, speed):
        self.speed = speed

    def turn180(self):
        self.g_bot.set_car_motion(0,0,-1)
        time.sleep(3.59)
        self.fullstop()

"""
Nutzung
Datei im gleichen Verzeichniss oder Import ensprechend anpassen

from movementControl import MovementControl

# Objekt erstellen
controller = MovementControl()

# Methode aufrufen
controller.Stop()
"""


