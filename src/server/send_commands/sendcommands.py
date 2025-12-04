import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from server.app.connection import connectionHändler
from server.send_commands.undoMovement import  UndoMovement

conn = connectionHändler.getInstance()

def ButtonClicked(clickedButton):
    data = {
            "type": clickedButton,
            "params": {}
        }
    sendJson(json.dumps(data))
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
        sendJson(json.dumps(data))
    
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
        sendJson(json.dumps(data))

        undo = UndoMovement.getInstance()
        undo.put(command)

def voicecommand(command):
    data = {
            "type": command,
            "params": {}
        }
    sendJson(json.dumps(data))
    
def sendJson(json):
    conn.commandQ.put(json)
    print(json)
