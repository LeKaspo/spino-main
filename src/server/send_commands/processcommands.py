import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

import server.send_commands.sendcommands as sendcommands
from server.send_commands.undoMovement import  UndoMovement
import server.config.config as config
from .logger import Logger

undo = UndoMovement.getInstance()
log = Logger.getInstance()


def ButtonClicked(clickedButton, param = None):
    if config.system_status["button_mode_active"] == True or clickedButton == "fullstop":
        if param is not None:
            data = {
                    "type": clickedButton,
                    "params": {"val1" : param}
                }
            log.write(f"{clickedButton}: {param}", 1)
        else:
            data = {
                    "type": clickedButton,
                    "params": {}
                }
            log.write(clickedButton,1)
        sendcommands.sendJson(json.dumps(data))
        undo.put(clickedButton)

def ButtonClickedInside(clickedButton):
    msg = ""
    match clickedButton:
        case "start":
            undo.start()
            msg = "starte Routen Aufnahme"
        case "undoMovement":
            undo.undoMovement()
            msg = "Spino kommt zurück"
        case "modebtn":
            config.system_status["button_mode_active"] = not config.system_status["button_mode_active"]
            msg = "Tastensteuerung (de)aktiviert"
        case "modevoice":
            config.system_status["voice_mode_active"] = not config.system_status["voice_mode_active"]
            msg = "Sprachsteuerung (de)aktiviert"
        case "modegesture":
            config.system_status["gesture_mode_active"] = not config.system_status["gesture_mode_active"]
            msg = "Gestensteuerung (de)aktiviert"
        case "modelabel":
            config.system_status["label_mode_active"] = not config.system_status["label_mode_active"]
            msg = "LabelerkennungsModus (de)aktiviert"
    log.write(msg,1)
            
def ButtonPress(pressedButton):
    if (config.system_status["button_mode_active"] == True):
        commands = {
            "w": "forwards",
            "a": "left",
            "s": "backwards",
            "d": "right",
            "q": "turnLeft",
            "e": "turnRight"
        }
        command = commands.get(pressedButton, "unknownCommand")

        if command != "unknownCommand":        
            data = {
                    "type": command,
                    "params": {}
                }
            sendcommands.sendJson(json.dumps(data))
            undo.put(command)
            log.write(command,1)

def ButtonRelease(releasedButton):
    if (config.system_status["button_mode_active"] == True):
        commands = {
            "w": "stopForwardsBackwards",
            "s": "stopForwardsBackwards",
            "a": "stopLeftRight",
            "d": "stopLeftRight",
            "q": "stopRotate",
            "e": "stopRotate"
        }
        command = commands.get(releasedButton, "unknownCommand")

        if command != "unknownCommand":        
            data = {
                    "type": command,
                    "params": {}
                }
            sendcommands.sendJson(json.dumps(data))
            undo.put(command)
            log.write(command,1)


def voicecommand(command):
    if (config.system_status["voice_mode_active"] == True):
        commandList = {"forwards", "backwards", "left", "right", "turnLeft", "turnRight", "fullstop", "turn180" }
        commandParamsList = {"setSpeedSlower", "setSpeedFaster", "resetSpeed"}
        if command in commandList:
            data = {
                    "type": command,
                    "params": {}
                }
            sendcommands.sendJson(json.dumps(data))
            log.write(command,1)
            print("Sent voice command:", command)
        elif command in commandParamsList:
            params = {}
            commandClean = ""
            match command:
                case "setSpeedSlower":
                    commandClean = "setSpeed"
                    params = {"val1" : 0.2}
                case "setSpeedFaster":
                    commandClean = "setSpeed"
                    params = {"val1" : 0.8}
                case "resetSpeed":
                    commandClean = "setSpeed"
                    params = {"val1" : 0.5}
            data = {
                    "type": commandClean,
                    "params": params
                }
            sendcommands.sendJson(json.dumps(data))
            log.write(command,1)
            print("Sent voice command:", command, "with params:", params)
        else :
            print("Unknown voice command:", command)
    else:
        print("Voice mode is not active. Ignoring voice command:", command)

    
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
