import sys
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from robo.movement_control.movementControl import MovementControl

class CommandExecutor:
    
    def __init__(self):
        mc = MovementControl()
        self.command_dict = {
            "fullstop" : mc.fullstop,
            "stopRotate" : mc.stopRotate,
            "stopLeftRight" : mc.stopLeftRight,
            "stopForwardsBackwards" : mc.stopForwardsBackwards,
            "forwards" : mc.forwards,
            "backwards" : mc.backwards,
            "right" : mc.right,
            "left" : mc.left,
            "turnRight" : mc.turnRight,
            "turnLeft" : mc.turnLeft,
            "setSpeed" : mc.setSpeed,
            "turn180" : mc.turn180
        }
        
    def executeCommand(self, commandString):      
        try:
            if isinstance(commandString, str):
                #print("Loading Command to JSON")
                command = json.loads(commandString)
            #print(f"Typ vom Command {type(command)}")
            command_type = command["type"]
            command_params = list(command["params"].values())
            
            if (command_params == []):
                self.command_dict[command_type]()
            else:
                self.command_dict[command_type](*command_params)
        except Exception as e:
            print(f"Error while executing Command: {e}")