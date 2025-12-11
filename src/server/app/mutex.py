import threading

class mutex:
    
    def __init__(self):
        self._list = []
        self._lock = threading.Lock()
    
    def write(self, new_list):
        with self._lock:
            self._list = new_list
    
    def read(self):
        with self._lock:
            return self._list