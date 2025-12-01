from Rosmaster_Lib import Rosmaster # type: ignore
import time

class MovementControl:
    def __init__(self):
        self.g_bot = Rosmaster()
        self.speedx = 0
        self.speedy = 0
        self.speedz = 0 #drehen immer auf voller geschwindigkeit weil das ist langsam
        self.speed = 0.5

    def fullstop(self):
        self.speedx = 0
        self.speedy = 0
        self.speedz = 0
        print(f"command executed: fullstop x: {self.speedx}, y: {self.speedy}, z: {self.speedz}")
        self.g_bot.set_car_motion(self.speedx,self.speedy,self.speedz)

    def stopRotate(self):
        self.speedz = 0
        print(f"command executed: stopRotate z: {self.speedz}")
        self.g_bot.set_car_motion(self.speedx,self.speedy,self.speedz)
        

    def stopLeftRight(self):
        self.speedy = 0
        print(f"command executed: stopLeftright y: {self.speedy}")
        self.g_bot.set_car_motion(self.speedx,self.speedy,self.speedz)

    def stopForwardsBackwards(self):
        self.speedx = 0
        print(f"command executed: stopForwardsbackwards x: {self.speedx}")
        self.g_bot.set_car_motion(self.speedx,self.speedy,self.speedz)

    def forwards(self):
        self.speedx = self.speed
        print(f"command executed: forwards x: {self.speedx}")
        self.g_bot.set_car_motion(self.speedx,self.speedy,self.speedz)

    def backwards(self):
        self.speedx = -self.speed
        print(f"command executed: backwards x: {self.speedx}")
        self.g_bot.set_car_motion(self.speedx,self.speedy,self.speedz)

    def right(self):
        self.speedy = -self.speed
        print(f"command executed: right y: {self.speedy}")
        self.g_bot.set_car_motion(self.speedx,self.speedy,self.speedz)

    def left(self):
        self.speedy = self.speed
        print(f"command executed: left y: {self.speedy}")
        self.g_bot.set_car_motion(self.speedx,self.speedy,self.speedz)

    def turnRight(self):
        self.speedz = -1
        print(f"command executed:turnRight  z: {self.speedz}")
        self.g_bot.set_car_motion(self.speedx,self.speedy,self.speedz)

    def turnLeft(self):
        self.speedz = 1
        print(f"command executed: turnLeft z: {self.speedz}")
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


