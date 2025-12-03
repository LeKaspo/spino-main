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
        self.speedz = -1 
        self.g_bot.set_car_motion(self.speedx,self.speedy,self.speedz)

    def turnLeft(self):
        self.speedz = 1 
        self.g_bot.set_car_motion(self.speedx,self.speedy,self.speedz)
    
    def setSpeed(self, speed):
        self.speed = speed
        if self.speed > 0 and self.speedx > 0:
            self.speedx = self.speed
        if self.speed > 0 and self.speedx < 0:
            self.speedx = -self.speed
        if self.speed > 0 and self.speedy > 0:
            self.speedy = self.speed
        if self.speed > 0 and self.speedy < 0:
            self.speedy = -self.speed
        

    def turn180(self):
        self.g_bot.set_car_motion(0,0,-1)
        time.sleep(3.59)
        self.fullstop()

    def test(self):
        #should start to beep
        self.set_beep(1)
        time.sleep(2)
        #should stop beeping
        self.set_beep(0)
        time.sleep(1)
        #should beep for 0.2 seconds
        self.set_beep(200)
        time.sleep(3)
        #should stop beeping
        self.set_beep(0)
        time.sleep(1)
        #should light up red
        self.set_colorful_effect(0)
        self.set_colorful_lamps(0xFF, 255, 0, 0)
        time.sleep(2)
        #middle lamp should light up blue
        self.set_colorful_lamps(7, 0, 0, 255)
        time.sleep(2)
        #should display power level
        self.set_colorful_effect(6)
        time.sleep(5)
        #whatever running light does
        self.set_colorful_effect(1)
        time.sleep(5)
        self.set_colorful_effect(0)
        


"""
Nutzung
Datei im gleichen Verzeichniss oder Import ensprechend anpassen

from movementControl import MovementControl

# Objekt erstellen
controller = MovementControl()

# Methode aufrufen
controller.Stop()
"""


