import time
import psutil
from typing import Annotated

from .hardware import GeneralHardware


class NetworkInformation(GeneralHardware):
    upload: Annotated[float, GeneralHardware.SensorValue]
    download: Annotated[float, GeneralHardware.SensorValue]

    _prev_time: float
    _prev_bytes_sent: float
    _prev_bytes_recv: float

    def __init__(self):
        self.clear()

        self._prev_time = -1
        self._prev_bytes_sent = -1
        self._prev_bytes_recv = -1

        print("Network Initialization:")
        for dev_name, values in psutil.net_if_stats().items():
            print(f"\tFound: {dev_name}, {values.speed}M")

    def clear(self):
        self.upload = 0
        self.download = 0

    def update(self):
        self.clear()

        net_info = psutil.net_io_counters()
        current_time = time.time()
        if self._prev_time >= 0:
            self.upload = (net_info.bytes_sent - self._prev_bytes_sent) / (
                current_time - self._prev_time
            )
            self.download = (net_info.bytes_recv - self._prev_bytes_recv) / (
                current_time - self._prev_time
            )

        self._prev_time = current_time
        self._prev_bytes_sent = net_info.bytes_sent
        self._prev_bytes_recv = net_info.bytes_recv

    def dispose(self):
        pass
