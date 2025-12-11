import threading
 
class Mutex:
    def __init__(self, default = None):
        self.__data = default
        self.__readers = 0
        self.__counter_lock = threading.Lock()
        self.__resource_lock = threading.Lock()
        self.__acquire_write = threading.Lock()
 
    def write(self, data):
       with self.__acquire_write:
            with self.__resource_lock:
                self.__data = data
 
    def read(self):
        self.__acquire_write.acquire()
        self.__acquire_write.release()
        with self.__counter_lock:
            self.__readers +=1
            if self.__readers == 1:
                self.__resource_lock.acquire()
        ret = self.__data
        with self.__counter_lock:
            self.__readers -=1
            if self.__readers == 0:
                self.__resource_lock.release()
        return ret
 