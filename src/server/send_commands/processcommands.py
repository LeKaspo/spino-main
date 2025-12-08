import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

import server.send_commands.sendcommands as sendcommands
from server.send_commands.undoMovement import  UndoMovement


def ButtonClicked(clickedButton):
    data = {
            "type": clickedButton,
            "params": {}
        }
    sendcommands.sendJson(json.dumps(data))
    undo = UndoMovement.getInstance()
    undo.put(clickedButton)

def ButtonClickedInside(clickedButton):
    undo = UndoMovement.getInstance()
    match clickedButton:
        case "start":
            undo.start()
        case "undoMovement":
            undo.undoMovement()

def ButtonPress(pressedButton):
    commands = {
        "w": "forwards",
        "a": "left",
        "s": "backwards",
        "d": "right",
        "q": "turnLeft",
        "e": "turnRight"
    }
    command = commands.get(pressedButton, "unknownCommand")

    if command != "unkownCommand":        
        data = {
                "type": command,
                "params": {}
            }
        sendcommands.sendJson(json.dumps(data))
    
        undo = UndoMovement.getInstance()
        undo.put(command)

def ButtonRelease(releasedButton):
    commands = {
        "w": "stopForwardsBackwards",
        "s": "stopForwardsBackwards",
        "a": "stopLeftRight",
        "d": "stopLeftRight",
        "q": "stopRotate",
        "e": "stopRotate"
    }
    command = commands.get(releasedButton, "unknownCommand")

    if command != "unkownCommand":        
        data = {
                "type": command,
                "params": {}
            }
        sendcommands.sendJson(json.dumps(data))

        undo = UndoMovement.getInstance()
        undo.put(command)

def voicecommand(command):
    commandList = {"forwards", "backwards", "left", "right", "turnLeft", "turnRight", "fullstop", "turn180"}
    commandParamsList = {"setSpeedSlower",}
    if command in commandList:
        data = {
                "type": command,
                "params": {}
            }
        sendcommands.sendJson(json.dumps(data))
        print("Sent voice command:", command)
    elif command in commandParamsList:
        params = {}
        commandClean = ""
        match command:
            case "setSpeedSlower":
                commandClean = "setSpeed"
                params = {0.2}
            case "setSpeedFaster":
                commandClean = "setSpeed"
                params = {0.8}
        data = {
                "type": commandClean,
                "params": params
            }
        sendcommands.sendJson(json.dumps(data))
        print("Sent voice command:", command, "with params:", params)
    else :
        print("Unknown voice command:", command)
    

