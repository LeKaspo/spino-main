# Spino einrichten

## Sparse Checkout einrichten

Sparse Checkout erlaubt es, nur bestimmte Ordner des Repositories lokal auszuwählen.

```bash
# Sparse Checkout aktivieren
git config core.sparseCheckout true

# Gewünschte Ordner definieren, z. B. nur den client-Ordner
echo "client/" >> .git/info/sparse-checkout

# Daten abrufen und auschecken
git pull origin main

# Nun ist lokal nur der client-Ordner sichtbar.
```

## Virtuelle Umgebung einrichten

```bash
# Virtuelle Umgebung erstellen
python -m venv spino_venv

# Virtuelle Umgebung aktivieren (Linux/Mac)
source spino_venv/bin/activate

# Abhängigkeiten installieren
pip install -r requirements.txt
```
