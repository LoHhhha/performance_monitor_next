from datetime import datetime
from typing import Annotated
import psutil

from .hardware import GeneralHardware


class TimeInformation(GeneralHardware):
    time: Annotated[float, GeneralHardware.SensorValue]
    boot_time: Annotated[float, GeneralHardware.SensorValue]

    def __init__(self):
        self.clear()

    def clear(self):
        self.time = 0.0
        self.boot_time = 0.0

    def dispose(self):
        pass

    def update(self):
        self.clear()

        self.time = datetime.now().timestamp()
        self.boot_time = self.time - psutil.boot_time()
