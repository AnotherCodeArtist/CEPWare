import threading
import time


class Counter(threading.Thread):
    def __init__(self, interval=1):
        threading.Thread.__init__(self)
        self.interval = interval
        self.value = 0
        self.alive = False

    def run(self):
        self.alive = True
        while self.alive:
            time.sleep(self.interval)
            self.value += self.interval

    def peek(self):
        return self.value

    def finish(self):
        self.alive = False
        return self.value