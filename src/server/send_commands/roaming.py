import threading
import server.send_commands.sendcommands as sendcommands
from server.send_commands.undoMovement import  UndoMovement
import random
import time

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
    
    def start(self):
        with self._lock:
            if self.started:
                return False, "Roaming war bereits aktiv."
            self._stop_event.clear()
            try:
                self._thread = threading.Thread(
                    target=self.loop,
                    name="RoamingLoop",
                    daemon=True
                )
                self._thread.start()
                self.started = True
                return True, "Spino ist jetzt in Freilandhaltung."
            except Exception:
                self._thread = None
                self.started = False
                return False, "Roaming konnte nicht gestartet werden."



    def stop(self):
        with self._lock:
            if not self.started:
                return False, "Roaming war bereits inaktiv."
            self._stop_event.set()
            thread = self._thread
        if thread is not None:
            thread.join(timeout=0.5)
        with self._lock:
            self._thread = None
            self.started = False
        return True, "Spino ist jetzt nicht mehr in Freilandhaltung."


    def loop(self):
        sendcommands.sendJson({"type": "setSpeed", "params": {0.2} })
        while not self._stop_event.is_set():
            self.undo.start()
            for _ in range(3):
                sendcommands.sendJson({"type": "forwards", "params": {0} })
                self.undo.put("forwards")
                time.sleep(self.getRandTime())
                dir = self.getRandDir()
                sendcommands.sendJson({"type": dir, "params": {0} })
                self.undo.put(dir)
                time.sleep(self.getRandTime())
                sendcommands.sendJson({"type": "stopForwardsBackwards", "params": {0} })
                self.undo.put("stopForwardsBackwards")
            self.undo.undoMovement()
            
    def getRandTime():
        return random.uniform(0.1, 1)
    
    def getRandDir():
        return random.choice(["turnLeft", "turnRight"])

        

