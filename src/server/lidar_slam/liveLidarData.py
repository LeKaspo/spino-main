import threading
import time
import numpy as np
import matplotlib.pyplot as plt

import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from server.app.connection import connectionHändler