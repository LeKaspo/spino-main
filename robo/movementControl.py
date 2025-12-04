from Rosmaster_Lib import Rosmaster # type: ignore
import time

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
        #set turnlights
        self.g_bot.set_colorful_effect(0)
        self.g_bot.set_colorful_lamps(0xFF, 255, 255, 255)

    def right(self):
        self.speedy = -self.speed 
        self.g_bot.set_car_motion(self.speedx,self.speedy,self.speedz)
        #set turnlights
        self.g_bot.set_colorful_effect(0)
        self.g_bot.set_colorful_lamps(16, 255, 204, 0)
        self.g_bot.set_colorful_lamps(15, 255, 204, 0)
        self.g_bot.set_colorful_lamps(14, 255, 204, 0)
        self.g_bot.set_colorful_lamps(13, 255, 204, 0)
        self.g_bot.set_colorful_lamps(12, 255, 204, 0)

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

    def beeep(self):
        self.g_bot.set_beep(1)
        time.sleep(5)
        self.g_bot.set_beep(0)

    def light_battery(self):
        self.g_bot.set_colorful_effect(6)

"""
Nutzung
Datei im gleichen Verzeichniss oder Import ensprechend anpassen

from movementControl import MovementControl

# Objekt erstellen
controller = MovementControl()

# Methode aufrufen
controller.Stop()
"""


