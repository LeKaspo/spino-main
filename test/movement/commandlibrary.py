#import json
#from enum import Enum
#from movementControl import MovementControl as con
from helper import tester as tst

# This file shortens the command calls, you call the function with the command you want to execute and it returns you the string to send to the robbi

def execute_command(what_command, dicti):
    dicti[what_command]()

def printsmth():
    print("hat geklappt")

dict = {
    "movement": tst.somefunctionality
}

command = {
        "type" : "movement",
        "params" : {
            "param" : 2077
        }
    }

command_type = command["type"]
print(command_type) 

command_param = command["params"]
print(command_param)



execute_command(command_type, dict)
