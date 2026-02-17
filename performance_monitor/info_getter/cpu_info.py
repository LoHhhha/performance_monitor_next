import clr
from typing import Annotated, List

from ..third_party import LHM_dll_path
from .hardware import GeneralHardware

clr.AddReference(LHM_dll_path)
from LibreHardwareMonitor import Hardware
from LibreHardwareMonitor.Hardware import HardwareType, SensorType


class CpuInformation(GeneralHardware):
    cpu_name: Annotated[List[str], GeneralHardware.SensorValue]
    temperature: Annotated[List[float], GeneralHardware.SensorValue]
    clock: Annotated[List[float], GeneralHardware.SensorValue]
    usage: Annotated[List[float], GeneralHardware.SensorValue]
    load: Annotated[List[float], GeneralHardware.SensorValue]
    voltage: Annotated[List[float], GeneralHardware.SensorValue]
    power: Annotated[float, GeneralHardware.SensorValue]

    def __init__(self):
        self.clear()
        self.computer = Hardware.Computer()
        self.computer.IsCpuEnabled = True
        self.computer.Open()

        print("CPU Initialization:")
        for hardware in self.computer.Hardware:
            print(f"\tFound: {hardware.Name}")

    @staticmethod
    def get_value(value, invalid_value=65535.0) -> float:
        return value if value is not None else invalid_value

    def clear(self):
        self.cpu_name = []
        self.temperature = []
        self.clock = []
        self.usage = []
        self.load = []
        self.voltage = []
        self.power = 0

    def update(self):
        self.clear()

        # self.computer.Update()
        for hardware in self.computer.Hardware:
            hardware.Update()
            if hardware.HardwareType == HardwareType.Cpu:
                self.cpu_name.append(hardware.Name)

                for sensor in hardware.Sensors:
                    if sensor.SensorType == SensorType.Temperature:
                        if "#" in sensor.Name:
                            self.temperature.append(self.get_value(sensor.Value))
                    elif sensor.SensorType == SensorType.Clock:
                        if "#" in sensor.Name:
                            self.clock.append(self.get_value(sensor.Value))
                    elif sensor.SensorType == SensorType.Load:
                        if "#" in sensor.Name:
                            self.load.append(self.get_value(sensor.Value))
                        elif "TOTAL" in str(sensor.Name).upper():
                            self.usage.append(self.get_value(sensor.Value))
                    elif sensor.SensorType == SensorType.Voltage:
                        if "#" in sensor.Name:
                            self.voltage.append(self.get_value(sensor.Value))
                    elif sensor.SensorType == SensorType.Power:
                        if "CPU PACKAGE" in str(sensor.Name).upper():
                            self.power += self.get_value(sensor.Value)

    def dispose(self):
        self.computer.Close()
