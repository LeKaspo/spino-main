import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # geht von src/server/main/main.py aus
sys.path.append(str(ROOT))




import sys
from pathlib import Path

# Aktuelle Datei → server/main/main.py
current = Path(__file__).resolve()

# Finde den src-Ordner (automatisch für jedes Projekt)
for parent in current.parents:
    if (parent / "server").exists() or (parent / "robo").exists():
        # parent ist src/
        sys.path.insert(0, str(parent))
        break