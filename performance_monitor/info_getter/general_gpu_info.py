import clr
from typing import Annotated, List

from ..third_party import LHM_dll_path
from .hardware import GeneralHardware

clr.AddReference(LHM_dll_path)
from LibreHardwareMonitor import Hardware  # type: ignore
from LibreHardwareMonitor.Hardware import HardwareType, SensorType  # type: ignore


class GeneralGpuInformation(GeneralHardware):
    gpu_count: Annotated[int, GeneralHardware.SensorValue]
    gpu_names: Annotated[List[str], GeneralHardware.SensorValue]
    available_memory: Annotated[List[int], GeneralHardware.SensorValue]
    used_memory: Annotated[List[int], GeneralHardware.SensorValue]
    memory_usage: Annotated[List[float], GeneralHardware.SensorValue]
    usage: Annotated[List[float], GeneralHardware.SensorValue]
    power: Annotated[List[float], GeneralHardware.SensorValue]
    available_power: Annotated[List[float], GeneralHardware.SensorValue]
    temperature: Annotated[List[float], GeneralHardware.SensorValue]
    core_clock: Annotated[List[float], GeneralHardware.SensorValue]
    memory_clock: Annotated[List[float], GeneralHardware.SensorValue]

    _available_gpu: List[Hardware.IHardware]

    def __init__(self):
        self.clear()

        self.computer = Hardware.Computer()
        self.computer.IsGpuEnabled = True
        self.computer.Open()

        print("General GPU Initialization:")
        self.gpu_names = []
        self._available_gpu = []
        for hardware in self.computer.Hardware:
            if hardware.HardwareType != HardwareType.GpuNvidia:
                self._available_gpu.append(hardware)
                self.gpu_names.append(hardware.Name)
                print(f"\tFound: {hardware.Name}")

        self.gpu_count = len(self._available_gpu)

    @staticmethod
    def _safe_value(value, default=0):
        return value if value is not None else default

    @staticmethod
    def _to_bytes_from_mib(value_mib: float) -> int:
        return int(value_mib * 1024 * 1024)

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

        for gpu in self._available_gpu:
            gpu.Update()

            available_memory = 0
            used_memory = 0
            usage = 0
            power = 0
            temperature = 0
            core_clock = 0
            memory_clock = 0

            for sensor in gpu.Sensors:
                sensor_name = str(sensor.Name).upper()
                s_type = sensor.SensorType

                if s_type == SensorType.Temperature and "GPU" in sensor_name:
                    temperature = self._safe_value(sensor.Value)
                elif s_type == SensorType.Clock:
                    if "CORE" in sensor_name:
                        core_clock = self._safe_value(sensor.Value)
                    elif "MEMORY" in sensor_name:
                        memory_clock = self._safe_value(sensor.Value)
                elif s_type == SensorType.Load:
                    if "CORE" in sensor_name or "GPU" in sensor_name:
                        usage = self._safe_value(sensor.Value)
                    elif "MEMORY" in sensor_name:
                        memory_usage = self._safe_value(sensor.Value)
                elif s_type == SensorType.Power:
                    if (
                        "TOTAL" in sensor_name
                        or "GPU" in sensor_name
                        or "CORE" in sensor_name
                    ):
                        power = self._safe_value(sensor.Value)
                elif s_type in (SensorType.SmallData, SensorType.Data):
                    if "MEMORY TOTAL" in sensor_name:
                        available_memory = self._to_bytes_from_mib(
                            self._safe_value(sensor.Value)
                        )
                    elif "MEMORY USED" in sensor_name:
                        used_memory = self._to_bytes_from_mib(
                            self._safe_value(sensor.Value)
                        )

            if available_memory > 0 and used_memory >= 0:
                memory_usage = (used_memory / available_memory) * 100
            else:
                memory_usage = 0

            self.available_memory.append(available_memory)
            self.used_memory.append(used_memory)
            self.memory_usage.append(memory_usage)
            self.usage.append(usage)
            self.power.append(power)
            # todo: support available power if possible, currently set as 0
            self.available_power.append(power)
            self.temperature.append(temperature)
            self.core_clock.append(core_clock)
            self.memory_clock.append(memory_clock)

    def dispose(self):
        if hasattr(self, "computer"):
            self.computer.Close()
