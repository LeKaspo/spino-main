from movementControl import MovementControl as mc
import json

class CommandExecutor:
    
    def __init__(self):
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
        
    def executeCommand(self, command):
        if isinstance(command, str):
            command = json.loads(command)
        print(f"Typ vom Command {type(command)}")
        command_type = command["type"]
        command_params = list(command["params"].values())
        
        if (command_params == []):
            self.command_dict[command_type]()
        else:
            self.command_dict[command_type](*command_params)