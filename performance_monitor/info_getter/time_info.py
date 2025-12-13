from datetime import datetime, timedelta
import psutil

from .hardware import GeneralHardware


class TimeInformation(GeneralHardware):
    time: datetime
    boot_time: timedelta

    def __init__(self):
        self.clear()

    def clear(self):
        self.time = datetime.now()
        self.boot_time = timedelta()

    def dispose(self):
        pass

    def update(self):
        self.clear()

        self.time = datetime.now()
        self.boot_time = self.time - datetime.fromtimestamp(psutil.boot_time())
