import clr
from typing import Annotated, List

from ..third_party import LHM_dll_path
from .hardware import GeneralHardware

clr.AddReference(LHM_dll_path)
from LibreHardwareMonitor import Hardware  # type: ignore
from LibreHardwareMonitor.Hardware import HardwareType, SensorType  # type: ignore


class CpuInformation(GeneralHardware):
    cpu_count: Annotated[int, GeneralHardware.SensorValue]
    cpu_name: Annotated[List[str], GeneralHardware.SensorValue]
    temperature: Annotated[List[List[float]], GeneralHardware.SensorValue]
    clock: Annotated[List[List[float]], GeneralHardware.SensorValue]
    usage: Annotated[List[List[float]], GeneralHardware.SensorValue]
    load: Annotated[List[List[float]], GeneralHardware.SensorValue]
    voltage: Annotated[List[List[float]], GeneralHardware.SensorValue]
    power: Annotated[List[float], GeneralHardware.SensorValue]

    _available_cpu: List[Hardware.IHardware]

    def __init__(self):
        self.clear()
        self.computer = Hardware.Computer()
        self.computer.IsCpuEnabled = True
        self.computer.Open()

        print("CPU Initialization:")
        self.cpu_name = []
        self._available_cpu = []
        for hardware in self.computer.Hardware:
            if hardware.HardwareType == HardwareType.Cpu:
                print(f"\tFound: {hardware.Name}")
                self._available_cpu.append(hardware)
                self.cpu_name.append(hardware.Name)
        self.cpu_count = len(self._available_cpu)

    @staticmethod
    def _get_value(value, invalid_value=65535.0) -> float:
        return value if value is not None else invalid_value

    def clear(self):
        self.temperature = []
        self.clock = []
        self.usage = []
        self.load = []
        self.voltage = []
        self.power = []

    def update(self):
        self.clear()

        for hardware in self._available_cpu:
            hardware.Update()

            total_power = 0
            temperature_read_from_core = []
            temperature_read_from_other = []
            clock = []
            load = []
            usage = []
            voltage = []

            for sensor in hardware.Sensors:
                sensor_name = str(sensor.Name).upper()
                if sensor.SensorType == SensorType.Temperature:
                    if "TJMAX" not in sensor_name:
                        if "#" in sensor_name:
                            temperature_read_from_core.append(
                                self._get_value(sensor.Value)
                            )
                        else:
                            temperature_read_from_other.append(
                                self._get_value(sensor.Value)
                            )
                elif sensor.SensorType == SensorType.Clock:
                    if "#" in sensor_name:
                        clock.append(self._get_value(sensor.Value))
                elif sensor.SensorType == SensorType.Load:
                    if "#" in sensor_name:
                        load.append(self._get_value(sensor.Value))
                    elif "TOTAL" in sensor_name:
                        usage.append(self._get_value(sensor.Value))
                elif sensor.SensorType == SensorType.Voltage:
                    if "#" in sensor_name:
                        voltage.append(self._get_value(sensor.Value))
                elif sensor.SensorType == SensorType.Power:
                    if "PACKAGE" in sensor_name:
                        total_power += self._get_value(sensor.Value)

            self.power.append(total_power)
            if temperature_read_from_core:
                self.temperature.append(temperature_read_from_core)
            else:
                self.temperature.append(temperature_read_from_other)
            self.clock.append(clock)
            self.load.append(load)
            self.usage.append(usage)
            self.voltage.append(voltage)

    def dispose(self):
        self.computer.Close()
