import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

import server.send_commands.sendcommands as sendcommands
from server.send_commands.undoMovement import  UndoMovement
import server.config.config as config
from .logger import Logger

#get instances from utility singeltons
undo = UndoMovement.getInstance()
log = Logger.getInstance()

#handle diffrent kinds of buttons
def ButtonClicked(clickedButton, param = None):
    if config.system_status["button_mode_active"] == True or clickedButton == "fullstop" or clickedButton == "setSpeed":
        if param is not None: # if relevant sent param and update system_status
            data = {
                    "type": clickedButton,
                    "params": {"val1" : param}
                }
            log.write(f"{clickedButton}: {param}", 1)
            undo.put(clickedButton, param)
            if clickedButton == "setSpeed":
                config.system_status["cur_speed"] = float(param)
        else:
            data = {
                    "type": clickedButton,
                    "params": {}
                }
            log.write(clickedButton,1)
            undo.put(clickedButton)
        sendcommands.sendJson(json.dumps(data))
        
def ButtonClickedInside(clickedButton):
    msg = ""
    match clickedButton:
        case "start":
            undo.start()
            msg = "start record route"
        case "undoMovement":
            undo.undoMovement()
            msg = "Spino is comming back"
        case "safevideo":
            # TODO: methoden aufruf wür das video speichern
            msg = "video safed"
        case "modebtn":
            config.system_status["button_mode_active"] = not config.system_status["button_mode_active"]
            msg = "button control active" if config.system_status["button_mode_active"] else "button control deactivated"
        case "modevoice":
            config.system_status["voice_mode_active"] = not config.system_status["voice_mode_active"]
            msg = "voice control active" if config.system_status["voice_mode_active"] else "voice control deactivated"
        case "modegesture":
            config.system_status["gesture_mode_active"] = not config.system_status["gesture_mode_active"]
            msg = "gesture control active" if config.system_status["gesture_mode_active"] else "gesture control deactivated"
        case "modelabel":
            config.system_status["label_mode_active"] = not config.system_status["label_mode_active"]
            msg = "label recognition active" if config.system_status["label_mode_active"] else "label recognition deactivated"
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

# handle commands from other inputs
def voicecommand(command):
    if (config.system_status["voice_mode_active"] == True):
        data = {
            "type": command,
            "params": {}
        }
        sendcommands.sendJson(json.dumps(data))
        log.write(f"from voice input: {command}",1)

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
        log.write(f"from gesture input: {command}",1)