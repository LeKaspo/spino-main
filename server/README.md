# Server einrichten

## Virtuelle Umgebung einrichten

```bash
# Virtuelle Umgebung erstellen
python -m venv spino_venv

# Virtuelle Umgebung aktivieren (Windows)
.\spino_venv\Scripts\activate

# Abhängigkeiten installieren
pip install -r requirements.txt
```

## Drive Spino and see Cameraview


On Linux Laptop, check if you have entered the right IP-Adresses in the sript. Activate the venv (spino_venv) on the laptop, start the connection.py. 

Then start the Robbi and its scripts (as described in the README)

Then go onto the website where the flask server is run and you can see the camerastream and control the movement of the spino.


# Using Windows Laptop as a Server

## Prerequisites:
- The Windows laptop and Spino must be on the same network/router network.
- Currently, the laptop's IP address must be manually entered in getCommands, sendAudio, sendLidar, and in connection

## Set up network:
- Set Windows network type to **"Private"** (Network and Internet settings).

## Configure firewall:
- Open **Windows Defender Firewall with Advanced Security** as administrator.
- Navigate to **"Inbound Rules"** and **create new rule**:
    - Type: **Port**
    - Protocol: **TCP**
    - Enter desired ports
    - Currently we are using ports 50001, 50002, 50003
    - Select **Allow the connection**
    - Provide a meaningful description

## Finally:
- Restart the PC so that all settings are applied.

