import pynvml
from typing import Annotated, Tuple, List

from .hardware import GeneralHardware


class NvidiaGpuInformation(GeneralHardware):
    gpu_count: Annotated[int, GeneralHardware.SensorValue]
    gpu_names: Annotated[List[str], GeneralHardware.SensorValue] = []
    available_memory: Annotated[List[int], GeneralHardware.SensorValue]
    used_memory: Annotated[List[int], GeneralHardware.SensorValue]
    memory_usage: Annotated[List[float], GeneralHardware.SensorValue]
    usage: Annotated[List[float], GeneralHardware.SensorValue]
    power: Annotated[List[float], GeneralHardware.SensorValue]
    available_power: Annotated[List[float], GeneralHardware.SensorValue]
    temperature: Annotated[List[float], GeneralHardware.SensorValue]
    core_clock: Annotated[List[float], GeneralHardware.SensorValue]
    memory_clock: Annotated[List[float], GeneralHardware.SensorValue]

    _handles: List[Tuple[str, pynvml.struct_c_nvmlDevice_t]]

    def __init__(self):
        self.clear()

        print("Nvidia GPU Initialization:")
        self.gpu_count = 0
        self._handles = []
        try:
            pynvml.nvmlInit()
        except Exception as e:
            print(f"\tCould not found Nvidia GPU, due to {e}")
        self.gpu_count = pynvml.nvmlDeviceGetCount()
        for gpu_id in range(self.gpu_count):
            gpu_handle = pynvml.nvmlDeviceGetHandleByIndex(gpu_id)
            gpu_name = pynvml.nvmlDeviceGetName(gpu_handle)
            self._handles.append(gpu_handle)
            self.gpu_names.append(gpu_name)
            print(f"\tFound: {gpu_name}")

    def clear(self):
        self.available_memory = []
        self.used_memory = []
        self.memory_usage = []
        self.usage = []
        self.power = []
        self.available_power = []
        self.temperature = []
        self.core_clock = []
        self.memory_clock = []

    def update(self):
        self.clear()

        for gpu_handle in self._handles:
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(gpu_handle)
            self.available_memory.append(mem_info.total)
            self.used_memory.append(mem_info.used)
            self.memory_usage.append((mem_info.used / mem_info.total) * 100)
            self.usage.append(pynvml.nvmlDeviceGetUtilizationRates(gpu_handle).gpu)
            self.power.append(pynvml.nvmlDeviceGetPowerUsage(gpu_handle) / 1000)
            self.available_power.append(pynvml.nvmlDeviceGetEnforcedPowerLimit(gpu_handle) / 1000)
            self.temperature.append(pynvml.nvmlDeviceGetTemperatureV(gpu_handle, 0))
            self.core_clock.append(pynvml.nvmlDeviceGetClockInfo(gpu_handle, 0))
            self.memory_clock.append(pynvml.nvmlDeviceGetClockInfo(gpu_handle, 2))

    @classmethod
    def dispose(cls):
        try:
            pynvml.nvmlShutdown()
        except Exception as e:
            print(f"Could not shutdown Nvidia GPU, due to {e}")
