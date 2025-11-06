from Rosmaster_Lib import Rosmaster
import time

class MovementControl:
    def __init__(self):
        self.g_bot = Rosmaster()
        self.speedX = 0
        self.speedY = 0
        self.speedZ = 0

    def stop(self):
        self.g_bot.set_car_motion(0,0,0)
    
    def drive(self):
        self.g_bot.set_car_motion(self.speedX, self.speedY, self.speedZ)
    
    def setSpeedX(self, speed):
        self.setSpeedX = speed

    def setSpeedY(self, speed):
        self.setSpeedY = speed

    def setSpeedZ(self, speed):
        self.setSpeedZ = speed

    def forwards(self):
        self.setSpeedX(0.1)
        self.drive

#passiert wenn dieses script aufgerufen wird
if __name__ == "__main__":
    controller = MovementControl()
    print("Fahrzeug fährt los...")
    controller.forwards()
    time.sleep(2)
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


