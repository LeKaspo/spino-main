import json
from server.connection import connectionHändler
from .undoMovement import  UndoMovement
from .core import config
from .logger import Logger

conn = connectionHändler.getInstance()
undo = UndoMovement.getInstance()
log = Logger.getInstance()

def ButtonClicked(clickedButton):
    if config.system_status["button_mode_active"] == True or clickedButton == "fullstop":
        data = {
                "type": clickedButton,
                "params": {}
            }
        sendJson(json.dumps(data))
        undo.put(clickedButton)
        log.write(clickedButton,1)

def ButtonClickedInside(clickedButton):
    match clickedButton:
        case "start":
            undo.start()
        case "undoMovement":
            undo.undoMovement()
        case "modebtn":
            config.system_status["button_mode_active"] = not config.system_status["button_mode_active"]
            print(f"tasten: {config.system_status["button_mode_active"]}")
        case "modevoice":
            config.system_status["voice_mode_active"] = not config.system_status["voice_mode_active"]
            print(f"voice: {config.system_status["voice_mode_active"]}")
        case "modegesture":
            config.system_status["gesture_mode_active"] = not config.system_status["gesture_mode_active"]
            print(f"gesture: {config.system_status["button_mode_active"]}")
        case "modelabel":
            config.system_status["label_mode_active"] = not config.system_status["label_mode_active"]
            print(f"labels: {config.system_status["label_mode_active"]}")
            
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
            sendJson(json.dumps(data))
            undo.put(command)

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
            sendJson(json.dumps(data))
            undo.put(command)

def voicecommand(command):
    if (config.system_status["voice_mode_active"] == True):
        data = {
            "type": command,
            "params": {}
        }
        sendJson(json.dumps(data))

def sendJson(json):
    conn.commandQ.put(json)
    print(json)
