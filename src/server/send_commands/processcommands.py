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
    data = {
            "type": command,
            "params": {}
        }
    sendcommands.sendJson(json.dumps(data))

def gesture_command(gesture):
    gesture_commands = {
        "fist_normal": "fullstop",
        "fist_rotated_left": "turnLeft",
        "fist_rotated_right": "turnRight",
        "palm_normal": "forwards",
        "palm_rotated_left": "left",
        "palm_rotated_right": "right",
        "back_normal": "backwards",
        "back_rotated_left": "left", 
        "back_rotated_right": "right"
    }
    command = gesture_commands.get(gesture, "unknownCommand")

    if command != "unkownCommand":        
        data = {
                "type": command,
                "params": {}
            }
        sendcommands.sendJson(json.dumps(data))
    

