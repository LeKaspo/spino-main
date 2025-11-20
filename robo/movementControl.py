from Rosmaster_Lib import Rosmaster
import time
import sys
import select


class MovementControl:
    def __init__(self):
        self.g_bot = Rosmaster()

    def stop(self):
        self.g_bot.set_car_motion(0,0,0)
        print("debug stop")

    def forwards(self):
        self.g_bot.set_car_motion(0.5,0,0)

    def backwards(self):
        self.g_bot.set_car_motion(-0.5,0,0)

    def right(self):
        self.g_bot.set_car_motion(0,-0.5,0)

    def left(self):
        self.g_bot.set_car_motion(0,0.5,0)

    def turnright(self):
        self.g_bot.set_car_motion(0,0,-0.5)

    def turnleft(self):
        self.g_bot.set_car_motion(0,0,0.5)


#passiert wenn dieses script aufgerufen wird
if __name__ == "__main__":
    controller = MovementControl()
    controller.g_bot.set_pid_param(kp=0.2, ki=0.3, kd=0.2, forever=False)
    print(controller.g_bot.get_motion_pid () )
    running = True
    print("Steuerung mit W/A/S/D, Drehen mit Q/E, Beenden mit X")
    while running:
        if select.select([sys.stdin], [], [], 0.1)[0]:
            key = sys.stdin.read(1)
            if key == 'w':
                controller.forwards()
            elif key == 'a':
                controller.left()
            elif key == 's':
                controller.backwards()
            elif key == 'd':
                controller.right()
            elif key == 'q':
                controller.turnleft()
            elif key == 'e':
                controller.turnright()
            elif key == 'x':
                running = False
            else:
                controller.stop()
           
        
        target_speed = 0.5 
        a_x, a_y, a_z = controller.g_bot.get_motion_data()
        print(f"Zielgeschwindigkeit: {target_speed:.2f} m/s")
        print(f"Aktuelle geschwindigkeit: ax={a_x:.2f}, ay={a_y:.2f}, az={a_z:.2f}")

        #if a_x != 0 or a_y != 0 or a_z != 0:
         #   print(f"Zielgeschwindigkeit: {target_speed:.2f} m/s")
          #  print(f"Aktuelle geschwindigkeit: ax={a_x:.2f}, ay={a_y:.2f}, az={a_z:.2f}")




"""
Nutzung
Datei im leichen Vrrzeichniss oder Import ensprechend anpassen

from movement_control import MovementControl

# Objekt erstellen
controller = MovementControl()

# Methode aufrufen
controller.Stop()
"""


