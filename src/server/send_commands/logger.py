from threading import RLock

class Logger:

    # Singleton
    _instance = None  
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self._lock = RLock()
            self._textboxes = {1: "", 2: ""}
            self.initialized = True 
    @classmethod
    def getInstance(cls):
        return cls()    

    def clear(self, box):
        if box not in (1, 2):
            raise ValueError("box muss 1 oder 2 sein")
        with self._lock:
            self._textboxes[box] = ""
    def write(self, text, box):
        if box not in (1, 2):
            raise ValueError("box muss 1 oder 2 sein")
        with self._lock:
            self._textboxes[box] += text
            self._textboxes[box] += "&#013;"    
    def read(self, box):
        if box not in (1, 2):
            raise ValueError("box muss 1 oder 2 sein")
        with self._lock:
            return self._textboxes[box]


