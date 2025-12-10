import time
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

import server.send_commands.sendcommands as sendcommands
import server.config.config as config

class UndoMovement:
    # Singleton
    _instance = None  
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.stack = []
            self.last_time = 0
            self.last_x = 0 # remeber each direction to enable driving in multiple directions at once
            self.last_y = 0
            self.last_z = 0
            self.last_speed = 0.0
            self.started = False
            self.initialized = True 
    
    @classmethod
    def getInstance(cls):
        return cls()

    # start the route recording
    def start(self):
        self.stack = []
        self.stack.append({
                "duration": 0.0,
                "x": 0,
                "y": 0,
                "z": 0,
                "special": None
            })
        self.last_time = None
        self.last_x = 0
        self.last_y = 0
        self.last_z = 0
        self.last_speed = config.system_status["cur_speed"] 
        self.started = True

    # add a command to the stack with timestamp
    def put(self, command):
        now = time.perf_counter()
        if self.last_time is not None: #if its not the first command (since special command)
            duration = now - self.last_time
            self.stack.append({
                "duration": duration,
                "x": self.last_x,
                "y": self.last_y,
                "z": self.last_z,
                "special": None,
                "var": 0 
            })
        self.last_time = now

        match command:
            case "forwards":
                self.last_x = 1
            case "backwards":
                self.last_x = -1
            case "stopForwardsBackwards":
                self.last_x = 0
            case "left" :
                self.last_y = 1
            case "right":
                self.last_y = -1
            case "stopLeftRight":
                self.last_y = 0
            case "turnLeft":
                self.last_z = 1
            case  "turnRight":
                self.last_z = -1
            case "stopRotate":
                self.last_z = 0
            case "fullStop":
                self.last_x = 0
                self.last_y = 0
                self.last_z = 0
            case "turn180":
                self.stack.append({
                    "duration": 1.8657,
                    "x": 0,
                    "y": 0,
                    "z": 0,
                    "special": "turn180",
                    "var": 0
                })
                self.last_time = None
            case "setSpeed":
                self.stack.append({
                    "duration": 0,
                    "x": 0,
                    "y": 0,
                    "z": 0,
                    "special": "setSpeed",
                    "var": self.last_speed
                })
                self.last_speed = config.system_status["cur_speed"]
                self.last_time = None

    # undo the movement by following the instruction from the stack
    def undoMovement(self):
        if (self.started):
            sendcommands.sendJson(json.dumps({"type": "turn180", "params": {}})) # turning arround to drive forwards
            time.sleep(1.8657)
            curx = 0
            cury = 0 
            curz = 0
            while self.stack:
                state = self.stack.pop()
                
                if state.get("special") is not None: #handle special commands
                    param = {"var1" : state.get("var")} if state.get("var") != 0 else {}
                    sendcommands.sendJson(json.dumps({"type": state.get("special"), "params": param}))
                    time.sleep(state["duration"])
                else:
                    if state["x"] != curx: # send apropriate commands if it changed
                        command_x = self.get_command(state["x"], 'x')
                        sendcommands.sendJson(json.dumps({"type": command_x, "params": {}}))
                        curx = state["x"]
                    if state["y"] != cury:
                        command_y = self.get_command(state["y"], 'y')
                        sendcommands.sendJson(json.dumps({"type":command_y, "params": {}}))
                        cury = state["y"]
                    if state["z"] != curz:
                        command_z = self.get_command(state["z"], 'z')
                        sendcommands.sendJson(json.dumps({"type": command_z, "params": {}}))
                        curz = state["z"]
                    # only wait the duration if the robot is actually driving
                    if state["x"] != 0 or state["y"] != 0 or state["z"] != 0:   
                        time.sleep(state["duration"])
            self.started = False

    # get the command name
    def get_command(self, command, axis):
        mapx = {
            -1: "backwards",
            1: "forwards",
            0: "stopForwardsBackwards" }
        mapy = {
           -1: "right",
            1: "left",
            0: "stopLeftRight"
        }
        mapz = {
            -1: "turnRight",
            1: "turnLeft",
            0: "stopRotate"
        }
        match axis:
            case 'x':
                return mapx.get(command)
            case 'y':
                return mapy.get(command)
            case 'z':
                return mapz.get(command)  