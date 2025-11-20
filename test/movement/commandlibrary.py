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
    "message": tst.somefunctionality
}

execute_command("message", dict)
