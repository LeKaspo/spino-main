# Spino

This is a Spionaustier repo

![Picture of Roboter](https://cdn11.bigcommerce.com/s-yo2n39m6g3/images/stencil/1280x1280/products/2785/11421/71Xrm2EZF7L__50140.1723978723.jpg?c=2?imbypass=on)

Camera stream starten:
Auf roboter robo/start_camera.sh ausführen
Auf Laptop: server/ui/ui.py ausführen mit python -m server.ui.ui
  Dann im Browser öffnen


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