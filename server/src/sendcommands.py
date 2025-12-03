import json
#from connection import connectionHändler

#conn = connectionHändler.getInstance()

def ButtonClicked(clickedButton):
    data = {
            "type": clickedButton,
            "params": {}
        }
    sendJson(json.dumps(data))


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

def voicecommand(command):
    data = {
            "type": command,
            "params": {}
        }
    sendJson(json.dumps(data))
    
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
        sendJson(json.dumps(data))


def sendJson(json):
    print("Sending command:", json)
    #conn.commandQ.put(json)
    #print(json)