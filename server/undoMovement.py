import datetime
import sendcommands
import time

class UndoMovement:
    def __init__(self):
        self.stack = []
        lastTime = 0
        self.x
        self.y
        self.z
        self.lastx
        self.lasty
        self.lastz
        

    def start(self):
        self.stack = []
        self.stack.append({0, 0 , 0 , 0})

    def put(self, command):
        match command:
            case "forwards" | "backwards" | "stopForwardsBackwards":
                self.x = self.last.x
                self.lastx = command
            case "left" | "right" | "stopLeftRight":
                self.y = self.last.y
                self.lasty = command
            case "turnLeft" | "turnRight" |  "stopRotate":
                self.z = self.last.xz
                self.lastz = command
            case "fullStop":
                self.x = self.last.x
                self.lastx = command
                self.y = self.last.y
                self.lasty = command
                self.z = self.last.xz
                self.lastz = command
                
        if (self.lastTime == 0):
            self.lastTime = datetime.now()
        else:
            time = datetime.now()
            difference = self.lastTime - time
            duration = difference.total_seconds()
            self.lastTime = time

            self.stack.append({duration, self.x , self.y , self.z})

    def undoMovement(self):
        while not bool(self.stack):
            commands = self.stack.pop()
            for i in range(1, 3): 
                data = {
                    "type": commands[i],
                    "params": {}
                }
                sendcommands(data)
            time.sleep(commands[0])

    






        
        
