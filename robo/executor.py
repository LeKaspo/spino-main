from movementControl import MovementControl as mc

class CommandExecutor:
    
    def __init__(self):
        self.command_dict = {
            "stop" : mc.stop,
            "forwards" : mc.forwards,
            "backwards" : mc.backwards,
            "right" : mc.right,
            "left" : mc.left,
            "turnright" : mc.turnright,
            "turnleft" : mc.turnleft
        }
        pass
        
    def executeCommand(self, command):
        command_type = command["type"]
        command_params = list(command["params"].values())
        
        if (command_params == []):
            self.command_dict[command_type]()
        else:
            self.command_dict[command_type](*command_params)     


# if __name__ == "__main__":
#     #testing Stuff
#     jason = {
#         "type" : "movement",
#         "params" : {}
#     }

#     cmdExc = CommandExecutor()
#     cmdExc.executeCommand(jason)
