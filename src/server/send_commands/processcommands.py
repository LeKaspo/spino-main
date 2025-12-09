import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

import server.send_commands.sendcommands as sendcommands
from server.send_commands.undoMovement import  UndoMovement
from server.send_commands.roaming import  Roaming
import server.config.config as config
from .logger import Logger

undo = UndoMovement.getInstance()
log = Logger.getInstance()
roam = Roaming.getInstance

def ButtonClicked(clickedButton, param = None):
    if config.system_status["button_mode_active"] == True or clickedButton == "fullstop":
        if param is not None:
            data = {
                    "type": clickedButton,
                    "params": param
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
        case "moderoaming":
            if config.system_status.get("roaming_mode_active") is False:
                ok, msg = roam.start()
                if ok:
                    config.system_status["roaming_mode_active"] = True
            else:
                ok, msg = roam.stop()
                if ok:
                    config.system_status["roaming_mode_active"] = False
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

        if command != "unkownCommand":        
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

        if command != "unkownCommand":        
            data = {
                    "type": command,
                    "params": {}
                }
            sendcommands.sendJson(json.dumps(data))
            undo.put(command)
            log.write(command,1)

def voicecommand(command):
    if (config.system_status["voice_mode_active"] == True):
        data = {
            "type": command,
            "params": {}
        }
        sendcommands.sendJson(json.dumps(data))
        log.write(command,1)

    
