import threading
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

import server.send_commands.sendcommands as sendcommands
from server.send_commands.undoMovement import  UndoMovement
import random
import time
import server.config.config as config

class Roaming:
    
    # Singleton
    _instance = None  
    _singleton_lock = threading.Lock()
    
    def __new__(cls):
        with cls._singleton_lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if getattr(self, "initialized", False):
            return
        self.initialized = True

        self.started = False
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self.undo = UndoMovement.getInstance()

    @classmethod
    def getInstance(cls):
        return cls()
    
    # start thread
    def start(self):
        with self._lock:
            if self.started:
                return False, "free roam allready activated"
            self._stop_event.clear()
            try:
                self._thread = threading.Thread(
                    target=self.loop,
                    name="RoamingLoop",
                    daemon=True
                )
                self._thread.start()
                self.started = True
                return True, "Spino is now free"
            except Exception:
                self._thread = None
                self.started = False
                return False, "free roam could not be started"

    #stop thread, be aware spino will end its current loop before stopping
    def stop(self):
        with self._lock:
            if not self.started:
                return False, "free roam allready deactivated"
            self._stop_event.set()
            thread = self._thread
        if thread is not None:
            thread.join(timeout=0.5)
        with self._lock:
            self._thread = None
            self.started = False
        return True, "Spino is not free anymore"

    
    def loop(self):
        try:
            # drive slowly to reduce crash potential
            sendcommands.sendJson({"type": "setSpeed", "params": {"val1": 0.2}})
            config.system_status["cur_speed"] = 0.2
            while not self._stop_event.is_set():
                if self.is_stopped():
                    self.emergency_halt()
                    self._stop_event.set()
                self.undo.start()
                # drive forwards and turn and than come back
                for _ in range(3):
                    if self._stop_event.is_set() or self.is_stopped(): #alwys check for emergency stop
                        self.emergency_halt()
                        self._stop_event.set()
                        break
                    if self.send_if_free({"type": "forwards", "params": {}}):
                        self.undo.put("forwards")
                    if self.wait_or_stopped(self.getRandTime()):
                        self.emergency_halt()
                        self._stop_event.set()
                        break
                    dir = self.getRandDir()
                    if self.send_if_free({"type": dir, "params": {}}):
                        self.undo.put(dir)
                    if self.wait_or_stopped(self.getRandTime()):
                        self.emergency_halt()
                        self._stop_event.set()
                        break
                    if self.send_if_free({"type": "stopRotate", "params": {}}):
                        self.undo.put("stopRotate")
                    if self.wait_or_stopped(self.getRandTime()):
                        self.emergency_halt()
                        self._stop_event.set()
                        break
                    if self.send_if_free({"type": "stopForwardsBackwards", "params": {}}):
                        self.undo.put("stopForwardsBackwards")
                if self._stop_event.is_set() or self.is_stopped():
                    break
                self.undo.undoMovement()
        finally:
            with self._lock:
                self._thread = None
                self.started = False

    # helper funktions 
    def getRandTime(self):
        return random.uniform(0.1, 1)
    
    def getRandDir(self):
        return random.choice(["turnLeft", "turnRight"])
    
    def is_stopped(self) -> bool:
            return bool(config.system_status.get("stop_flag", False))

    def wait_or_stopped(self, seconds: float) -> bool:
        remaining = seconds
        step = min(0.05, seconds)
        while remaining > 0:
            if self._stop_event.is_set() or self.is_stopped():
                return True
            if self._stop_event.wait(timeout=step):
                return True
            remaining -= step
        return self.is_stopped() or self._stop_event.is_set()

    def send_if_free(self, msg: dict) -> bool:
        if self.is_stopped() or self._stop_event.is_set():
            return False
        sendcommands.sendJson(msg)
        return True
    
    def emergency_halt(self):
        sendcommands.sendJson({"type": "fullstop", "params": {}})