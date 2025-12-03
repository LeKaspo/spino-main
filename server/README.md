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



# Windows Laptop als Server verwenden (Socket Connection)

- **Voraussetzungen:**
    - Der Windows-Laptop und Spino müssen im selben Netzwerk/Routernetzwerk sein.
    - Derzeit muss die IP Adresse des Laptops manuell in getCommands, sendAudio, sendLidar und in connection eingetragen werden

- **Netzwerk einrichten:**
    - Windows-Netzwerktyp auf **"Privat"** stellen (Netzwerk- und Interneteinstellungen).

- **Firewall freigeben:**
    - **Windows Defender Firewall mit erweiterter Sicherheit** als Administrator öffnen.
    - Zu **"Eingehende Regeln"** navigieren und **neue Regel erstellen**:
        - Typ: **Port**
        - Protokoll: **TCP**
        - Gewünschten Port eingeben (z.B. 50050)
        - **Verbindung zulassen** auswählen
        - Aussagekräftige Beschreibung vergeben

- **Abschließend:**
    - Den PC neustarten, damit alle Einstellungen angewendet werden.

# Sprachaktivierung

- **Voraussetzungen:**
    - Verbindung zum Roboter
    - Alle für die Sprachaktivierung erforderlichen Libraries im venv
    - Einen Ordner namens "models" in spino-main erstellen
    - Modell "faster-whisper-tiny" von https://huggingface.co/Systran/faster-whisper-tiny herunterladen und in den models ordner verschieben
    - Andere Faster-Whisper Modelle gehen natürlich auch, aber dann müssen die commands angepasst werden

- **Ausführen:**
```bash
# Standard ausführung Deutsch:
python3 server\speechInput.py --model tiny --language de
# Ausführung Englisch:
python3 server\speechInput.py --model tiny --language en
# Wenn Modell nicht gefunden:
python3 server\speechInput.py --model tiny --language de --model-path "pathToModel"
# Für weitere Hilfe und Ausführliche Doku:
python3 server\speechInput.py --help
```
- **Befehle hinzufügen:**
    - in speechInput.py in COMMANDS:
        - name = an den Spino gesendeter Command mittels sendcommands.voicecommand
        - phrases = die Phrasen, die den Command triggern

