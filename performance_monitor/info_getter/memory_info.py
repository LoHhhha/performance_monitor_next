import psutil
from typing import Annotated

from .hardware import GeneralHardware


class MemoryInformation(GeneralHardware):
    physical_memory_usage: Annotated[float, GeneralHardware.SensorValue]
    total_physical_memory: Annotated[int, GeneralHardware.SensorValue]
    total_swap_memory: Annotated[int, GeneralHardware.SensorValue]
    used_physical_memory: Annotated[int, GeneralHardware.SensorValue]
    used_swap_memory: Annotated[int, GeneralHardware.SensorValue]

    def __init__(self):
        self.clear()

        print("Memory Initialization:")
        print(f"\tTotal Physical Memory: {psutil.virtual_memory().total}")
        print(f"\tTotal Swap Memory: {psutil.swap_memory().total}")

    def clear(self):
        self.physical_memory_usage = 0
        self.total_physical_memory = 0
        self.total_swap_memory = 0
        self.used_physical_memory = 0
        self.used_swap_memory = 0

    def update(self):
        self.clear()

        phy = psutil.virtual_memory()
        swap = psutil.swap_memory()

        self.physical_memory_usage = phy.percent
        self.total_physical_memory = phy.total
        self.total_swap_memory = swap.total
        self.used_physical_memory = phy.used
        self.used_swap_memory = swap.used

    def dispose(self):
        pass
