# Spino einrichten

## Sparse Checkout einrichten

Sparse Checkout erlaubt es, nur bestimmte Ordner des Repositories lokal auszuwählen.

```bash
git clone --no-checkout https://github.com/LeKaspo/spino-main.git
cd spino-main

git sparse-checkout init

git sparse-checkout set --no-cone "/*" '!server/'

git checkout main
```

## Virtuelle Umgebung einrichten

```bash
# Virtuelle Umgebung erstellen
python -m venv spino_venv

# Virtuelle Umgebung aktivieren (Linux/Mac)
source spino_venv/bin/activate
# Auf Windows (Eingabeaufforderung):
spino_venv\Scripts\activate.bat
# Auf Windows (Powershell):
spino_venv\Scripts\Activate.ps1

# Abhängigkeiten installieren
pip install -r requirements_robo.txt
```

## To Startup and let the Spino drive

Controller on Laptop side must be started first!

 SSH onto the spino, activate the venv (camera-venv), and execute the main.sh in this folder.
