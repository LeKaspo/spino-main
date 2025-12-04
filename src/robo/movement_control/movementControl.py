import sys
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from robo.ext_libs.Rosmaster_Lib import Rosmaster

class MovementControl:
    def __init__(self):
        self.g_bot = Rosmaster()
        self.speedx = 0
        self.speedy = 0
        self.speedz = 0 
        self.speed = 0.5

    def fullstop(self):
        self.speedx = 0
        self.speedy = 0
        self.speedz = 0 
        self.g_bot.set_car_motion(self.speedx,self.speedy,self.speedz)

    def stopRotate(self):
        self.speedz = 0 
        self.g_bot.set_car_motion(self.speedx,self.speedy,self.speedz)
        

    def stopLeftRight(self):
        self.speedy = 0 
        self.g_bot.set_car_motion(self.speedx,self.speedy,self.speedz)

    def stopForwardsBackwards(self):
        self.speedx = 0
        self.g_bot.set_car_motion(self.speedx,self.speedy,self.speedz)

    def forwards(self):
        self.speedx = self.speed 
        self.g_bot.set_car_motion(self.speedx,self.speedy,self.speedz)

    def backwards(self):
        self.speedx = -self.speed 
        self.g_bot.set_car_motion(self.speedx,self.speedy,self.speedz)

    def right(self):
        self.speedy = -self.speed 
        self.g_bot.set_car_motion(self.speedx,self.speedy,self.speedz)

    def left(self):
        self.speedy = self.speed 
        self.g_bot.set_car_motion(self.speedx,self.speedy,self.speedz)

    def turnRight(self):
        self.speedz = -1 #drehen immer auf voller geschwindigkeit weil das ist langsam
        self.g_bot.set_car_motion(self.speedx,self.speedy,self.speedz)

    def turnLeft(self):
        self.speedz = 1 #drehen immer auf voller geschwindigkeit weil das ist langsam
        self.g_bot.set_car_motion(self.speedx,self.speedy,self.speedz)
    
    def setSpeed(self, speed):
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


