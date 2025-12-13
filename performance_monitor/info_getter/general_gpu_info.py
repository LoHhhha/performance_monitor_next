import clr
from typing import Annotated, List

from ..third_party import LHM_dll_path
from .hardware import GeneralHardware

clr.AddReference(LHM_dll_path)
from LibreHardwareMonitor import Hardware
from LibreHardwareMonitor.Hardware import HardwareType, SensorType


class GeneralGpuInformation(GeneralHardware):
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

    def __init__(self):
        self.clear()
        self._gpus: List[Hardware.IHardware] = []

        self.computer = Hardware.Computer()
        self.computer.IsGpuEnabled = True
        self.computer.Open()

        print("General GPU Initialization:")
        for hardware in self.computer.Hardware:
            if hardware.HardwareType != HardwareType.GpuNvidia:
                self._gpus.append(hardware)
                print(f"\tFound: {hardware.Name}")

        self.gpu_count = len(self._gpus)

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

        for gpu in self._gpus:
            gpu.Update()
            self.gpu_names.append(gpu.Name)

            metrics = {
                "available_memory": 0,
                "used_memory": 0,
                "memory_usage": 0,
                "usage": 0,
                "power": 0,
                "available_power": 0,
                "temperature": 0,
                "core_clock": 0,
                "memory_clock": 0,
            }

            for sensor in gpu.Sensors:
                sensor_name = str(sensor.Name).upper()
                s_type = sensor.SensorType

                if s_type == SensorType.Temperature and "GPU" in sensor_name:
                    metrics["temperature"] = self._safe_value(sensor.Value)
                elif s_type == SensorType.Clock:
                    if "CORE" in sensor_name:
                        metrics["core_clock"] = self._safe_value(sensor.Value)
                    elif "MEMORY" in sensor_name:
                        metrics["memory_clock"] = self._safe_value(sensor.Value)
                elif s_type == SensorType.Load:
                    if "CORE" in sensor_name or "GPU" in sensor_name:
                        metrics["usage"] = self._safe_value(sensor.Value)
                    elif "MEMORY" in sensor_name:
                        metrics["memory_usage"] = self._safe_value(sensor.Value)
                elif s_type == SensorType.Power:
                    if "TOTAL" in sensor_name or "GPU" in sensor_name or "CORE" in sensor_name:
                        metrics["power"] = self._safe_value(sensor.Value)
                elif s_type in (SensorType.SmallData, SensorType.Data):
                    if "MEMORY TOTAL" in sensor_name:
                        metrics["available_memory"] = self._to_bytes_from_mib(
                            self._safe_value(sensor.Value)
                        )
                    elif "MEMORY USED" in sensor_name:
                        metrics["used_memory"] = self._to_bytes_from_mib(
                            self._safe_value(sensor.Value)
                        )

            if metrics["available_memory"] > 0 and metrics["used_memory"] >= 0:
                metrics["memory_usage"] = (metrics["used_memory"] // metrics["available_memory"]) * 100

            self.available_memory.append(metrics["available_memory"])
            self.used_memory.append(metrics["used_memory"])
            self.memory_usage.append(metrics["memory_usage"])
            self.usage.append(metrics["usage"])
            self.power.append(metrics["power"])
            self.available_power.append(metrics["available_power"])
            self.temperature.append(metrics["temperature"])
            self.core_clock.append(metrics["core_clock"])
            self.memory_clock.append(metrics["memory_clock"])

    def dispose(self):
        if hasattr(self, "computer"):
            self.computer.Close()
