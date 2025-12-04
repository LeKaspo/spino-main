import time
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from server.send_commands.undoMovement import sendcommands
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
            self.last_x = 0
            self.last_y = 0
            self.last_z = 0
            self.initialized = True 
    
    @classmethod
    def getInstance(cls):
        return cls()

    # quasi initialisierung für startpunkt der aufnahme
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

    # hinzufügen zum stack mit umdrehen der richtung und aufzeichnung der dauer
    def put(self, command):
        now = time.perf_counter()
        if self.last_time is not None:
            duration = now - self.last_time
            self.stack.append({
                "duration": duration,
                "x": self.last_x,
                "y": self.last_y,
                "z": self.last_z,
                "special": None 
            })
        self.last_time = now

        match command:
            case "forwards":
                self.last_x = -1
            case "backwards":
                self.last_x = 1
            case "stopForwardsBackwards":
                self.last_x = 0
            case "left" :
                self.last_y = -1
            case "right":
                self.last_y = 1
            case "stopLeftRight":
                self.last_y = 0
            case "turnLeft":
                self.last_z = -1
            case  "turnRight":
                self.last_z = 1
            case "stopRotate":
                self.last_z = 0
            case "fullStop":
                self.last_x = 0
                self.last_y = 0
                self.last_z = 0
            case "turn180":
                self.stack.append({
                    "duration": 3.59,
                    "x": 0,
                    "y": 0,
                    "z": 0,
                    "special": "turn180"
                })
                self.last_time = None

    # stack abarbeiten
    def undoMovement(self):
        curx = 0
        cury = 0 
        curz = 0
        while self.stack:
            state = self.stack.pop()

            #special commands anders bearbeiten
            if state.get("special") is not None:
                print (state.get("special"))
                sendcommands.sendJson(json.dumps({"type": state.get("special"), "params": {}}))
                time.sleep(state["duration"])
            else:
                if state["x"] != curx:
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
                # nur warten wenn auch gefahren wird
                if state["x"] != 0 or state["y"] != 0 or state["z"] != 0:   
                    time.sleep(state["duration"])


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
    






        
        
