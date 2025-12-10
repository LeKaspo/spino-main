from threading import RLock, Condition

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
            self._version = {1: 0, 2: 0}
            self._cv = Condition(self._lock)
            self.initialized = True 
    @classmethod
    def getInstance(cls):
        return cls()    

    # clear a log box
    def clear(self, box):
        if box not in (1, 2):
            raise ValueError("box muss 1 oder 2 sein")
        with self._lock:
            self._textboxes[box] = ""
    # write to the log box
    def write(self, text, box):
        if box not in (1, 2):
            raise ValueError("box muss 1 oder 2 sein")
        with self._lock:
            self._textboxes[box] += text + "\n"
            self._version[box] += 1  # increment version, important for reading
            self._cv.notify_all()  
    # read from the log box
    def read_with_version(self, box):
        if box not in (1, 2):
            raise ValueError("box muss 1 oder 2 sein")
        with self._lock:
            return self._textboxes[box], self._version[box]


