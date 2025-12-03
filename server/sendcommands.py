import json

try:
    from server.connection import connectionHändler
except ImportError:
    from connection import connectionHändler

conn = connectionHändler.getInstance()

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
    commandList = {"forwards", "backwards", "left", "right", "turnLeft", "turnRight", "fullstop", "turn180"}
    commandParamsList = {"setSpeedSlower",}
    if command in commandList:
        data = {
                "type": command,
                "params": {}
            }
        sendJson(json.dumps(data))
        print("Sent voice command:", command)
    elif command in commandParamsList:
        params = {}
        commandClean = ""
        match command:
            case "setSpeedSlower":
                commandClean = "setSpeed"
                params = {"speed": 0.2}
            case "setSpeedFaster":
                commandClean = "setSpeed"
                params = {"speed": 0.8}
        data = {
                "type": commandClean,
                "params": params
            }
        sendJson(json.dumps(data))
        print("Sent voice command:", command, "with params:", params)
    else :
        print("Unknown voice command:", command)
    

def sendJson(json):
    conn.commandQ.put(json)
    #print(json)