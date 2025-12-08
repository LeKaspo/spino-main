# Server einrichten

## Virtuelle Umgebung einrichten

```bash
# Virtuelle Umgebung erstellen
python -m venv spino_venv

# Virtuelle Umgebung aktivieren (Windows)
.\spino_venv\Scripts\activate

# Abhängigkeiten installieren
pip install -r requirements_server.txt
```

## Drive Spino and see Cameraview


On Linux Laptop, check if you have entered the right IP-Adresses in the sript. Activate the venv (spino_venv) on the laptop, start the connection.py. 

Then start the Robbi and its scripts (as described in the README)

Then go onto the website where the flask server is run and you can see the camerastream and control the movement of the spino.

# Using Windows Laptop as a Server

## Prerequisites

- The Windows laptop and Spino must be on the same network/router network.
- Currently, the laptop's IP address must be manually entered in getCommands, sendAudio, sendLidar, and in connection

## Set up network

- Set Windows network type to **"Private"** (Network and Internet settings).

## Configure firewall

- Open **Windows Defender Firewall with Advanced Security** as administrator.
- Navigate to **"Inbound Rules"** and **create new rule**:
- - Type: **Port**
- - Protocol: **TCP**
- - Enter desired ports
- - Currently we are using ports 50001, 50002, 50003
- - Select **Allow the connection**
- - Provide a meaningful description

## Finally:
- Restart the PC so that all settings are applied.

# Voice activation

- **Prerequisites:**
    - Connection to the robot
    - All libraries required for voice activation installed in the venv
    - Create a folder named "models" in `spino-main\server`
    - Download the model "faster-whisper-tiny" from https://huggingface.co/Systran/faster-whisper-tiny and move it into the `models` folder
    - Other Faster-Whisper models also work, but then the commands must be adjusted accordingly

- **Execution:**
```bash
# cd to spino-main
# Default run in German:
python3 src\server\speech\speechInput.py --model tiny --language de
# Run in English:
python3 src\server\speech\speechInput.py --model tiny --language en
# When the model is not found:
python3 src\server\speech\speechInput.py --model tiny --language de --model-path "pathToModel"
# For more help and detailed documentation:
python3 src\server\speech\speechInput.py --help
```
- **Add commands:**
    - In `speechInput.py`, under `COMMANDS`:
        - `name` = command sent to Spino via `sendcommands.voicecommand`
        - `phrases` = the phrases that trigger the command

