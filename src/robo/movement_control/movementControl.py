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
        self.g_bot.set_colorful_effect(0)
        self.g_bot.set_colorful_lamps(0xFF, 255, 0, 0)


    def stopRotate(self):
        self.speedz = 0 
        self.g_bot.set_car_motion(self.speedx,self.speedy,self.speedz)
        #Batteriestand auf LED
        self.g_bot.set_colorful_effect(6)

    def stopLeftRight(self):
        self.speedy = 0 
        self.g_bot.set_car_motion(self.speedx,self.speedy,self.speedz)
        #Batteriestand auf LED
        self.g_bot.set_colorful_effect(6)

    def stopForwardsBackwards(self):
        self.speedx = 0
        self.g_bot.set_car_motion(self.speedx,self.speedy,self.speedz)
        #Batteriestand auf LED
        self.g_bot.set_colorful_effect(6)

    def forwards(self):
        self.speedx = self.speed 
        self.g_bot.set_car_motion(self.speedx,self.speedy,self.speedz)
        #Batteriestand auf LED
        self.g_bot.set_colorful_effect(6)

    def backwards(self):
        self.speedx = -self.speed 
        self.g_bot.set_car_motion(self.speedx,self.speedy,self.speedz)
        #set backlights for driving backwards
        self.g_bot.set_colorful_effect(0)
        self.g_bot.set_colorful_lamps(0xFF, 255, 255, 255)

    def right(self):
        self.speedy = -self.speed 
        self.g_bot.set_car_motion(self.speedx,self.speedy,self.speedz)
        self.g_bot.set_colorful_effect(6)
        #set turnlights
        self.g_bot.set_colorful_effect(0)
        self.g_bot.set_colorful_lamps(16, 255, 204, 0)
        self.g_bot.set_colorful_lamps(15, 255, 204, 0)
        self.g_bot.set_colorful_lamps(14, 255, 204, 0)
        self.g_bot.set_colorful_lamps(13, 255, 204, 0)
        self.g_bot.set_colorful_lamps(12, 255, 204, 0)
        self.g_bot.set_colorful_lamps(11, 255, 204, 0)
        self.g_bot.set_colorful_lamps(10, 255, 204, 0)

    def left(self):
        self.speedy = self.speed 
        self.g_bot.set_car_motion(self.speedx,self.speedy,self.speedz)
        self.g_bot.set_colorful_effect(6)
                        #set turnlights
        self.g_bot.set_colorful_effect(0)
        self.g_bot.set_colorful_lamps(0, 255, 204, 0)
        self.g_bot.set_colorful_lamps(1, 255, 204, 0)
        self.g_bot.set_colorful_lamps(2, 255, 204, 0)
        self.g_bot.set_colorful_lamps(3, 255, 204, 0)
        self.g_bot.set_colorful_lamps(4, 255, 204, 0)
        self.g_bot.set_colorful_lamps(5, 255, 204, 0)

    def turnRight(self):
        self.speedz = -2 #drehen immer auf voller geschwindigkeit weil das ist langsam
        self.g_bot.set_car_motion(self.speedx,self.speedy,self.speedz)
                #set turnlights
        self.g_bot.set_colorful_effect(0)
        self.g_bot.set_colorful_lamps(16, 255, 204, 0)
        self.g_bot.set_colorful_lamps(15, 255, 204, 0)
        self.g_bot.set_colorful_lamps(14, 255, 204, 0)
        self.g_bot.set_colorful_lamps(13, 255, 204, 0)
        self.g_bot.set_colorful_lamps(12, 255, 204, 0)
        self.g_bot.set_colorful_lamps(11, 255, 204, 0)
        self.g_bot.set_colorful_lamps(10, 255, 204, 0)

    def turnLeft(self):
        self.speedz = 2 #drehen immer auf voller geschwindigkeit weil das ist langsam
        self.g_bot.set_car_motion(self.speedx,self.speedy,self.speedz)
                        #set turnlights
        self.g_bot.set_colorful_effect(0)
        self.g_bot.set_colorful_lamps(0, 255, 204, 0)
        self.g_bot.set_colorful_lamps(1, 255, 204, 0)
        self.g_bot.set_colorful_lamps(2, 255, 204, 0)
        self.g_bot.set_colorful_lamps(3, 255, 204, 0)
        self.g_bot.set_colorful_lamps(4, 255, 204, 0)
        self.g_bot.set_colorful_lamps(5, 255, 204, 0)
    
    def setSpeed(self, speed):
        speedNum = float(speed)
        self.speed = speedNum
        if self.speed > 0 and self.speedx > 0:
            self.speedx = self.speed
        if self.speed > 0 and self.speedx < 0:
            self.speedx = -self.speed
        if self.speed > 0 and self.speedy > 0:
            self.speedy = self.speed
        if self.speed > 0 and self.speedy < 0:
            self.speedy = -self.speed
        self.g_bot.set_car_motion(self.speedx,self.speedy,self.speedz)

    def turn180(self):
        self.g_bot.set_car_motion(0,0,-2)
        #set turnlights
        self.g_bot.set_colorful_effect(0)
        self.g_bot.set_colorful_lamps(16, 255, 204, 0)
        self.g_bot.set_colorful_lamps(15, 255, 204, 0)
        self.g_bot.set_colorful_lamps(14, 255, 204, 0)
        self.g_bot.set_colorful_lamps(13, 255, 204, 0)
        self.g_bot.set_colorful_lamps(12, 255, 204, 0)
        self.g_bot.set_colorful_lamps(11, 255, 204, 0)
        self.g_bot.set_colorful_lamps(10, 255, 204, 0)
        time.sleep(1.87)
        self.stopRotate()

    def beep(self):
        self.g_bot.set_beep(20)
        time.sleep(0.02)
        self.g_bot.set_beep(20)

        


"""
Nutzung
Datei im gleichen Verzeichniss oder Import ensprechend anpassen

from movementControl import MovementControl

# Objekt erstellen
controller = MovementControl()

# Methode aufrufen
controller.Stop()
"""


