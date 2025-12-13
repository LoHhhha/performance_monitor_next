import time
from typing import Tuple, List, Optional

from ..utils import settings
from ..utils import strings
from ..utils import tools
from ..info_getter import CpuInformation
from ..info_getter import MemoryInformation
from ..info_getter import NetworkInformation
from ..info_getter import NvidiaGpuInformation
from ..info_getter import GeneralGpuInformation
from ..info_getter import TimeInformation


class Combiner:
    time: TimeInformation
    cpu: CpuInformation
    nv_gpu: Optional[NvidiaGpuInformation]
    gpu: Optional[GeneralGpuInformation]
    memory: MemoryInformation
    network: NetworkInformation

    def __init__(
            self,
            general_gpu_enable: bool = True,
            nv_gpu_enable: bool = True,
    ):
        print("Collecting Information...")
        self.time = TimeInformation()
        self.cpu = CpuInformation()
        if general_gpu_enable:
            self.gpu = GeneralGpuInformation()
        else:
            self.gpu = None
        if nv_gpu_enable:
            self.nv_gpu = NvidiaGpuInformation()
        else:
            self.nv_gpu = None
        self.memory = MemoryInformation()
        self.network = NetworkInformation()

        print("Initialization Complete.")
        time.sleep(2)

    def get_total_power(self) -> float:
        return (
                self.cpu.power +
                (tools.get_sum(self.nv_gpu.power) if self.nv_gpu else 0) +
                (tools.get_sum(self.gpu.power) if self.gpu else 0)
        )

    def outline_info(self) -> Tuple[str, List[Tuple[str, str]]]:
        return strings.outline_name, tools.get_table([
            tools.get_tuple(
                strings.total_power,
                f"{self.get_total_power():.0f}{settings.power_postfix}"
            ),
            tools.get_tuple(
                strings.boot_time,
                str(self.time.boot_time).split('.')[0]
            ),
            tools.get_tuple(
                strings.cur_time,
                self.time.time.strftime(settings.time_fmt)
            ),
        ])

    def memory_info(self) -> Tuple[str, List[Tuple[str, str]]]:
        return strings.memory_name, tools.get_table([
            tools.get_tuple(
                strings.memory_usage,
                tools.get_rate_display(self.memory.physical_memory_usage),
            ),
            tools.get_tuple(
                strings.memory_detail,
                tools.get_max_display(
                    f"{self.memory.used_physical_memory // settings.byte2mb:.0f}",
                    f"{self.memory.total_physical_memory // settings.byte2mb:.0f}",
                    settings.mb_postfix
                ),
            ),
            tools.get_tuple(
                strings.memory_swap_detail,
                tools.get_max_display(
                    f"{self.memory.used_swap_memory // settings.byte2mb:.0f}",
                    f"{self.memory.total_swap_memory // settings.byte2mb:.0f}",
                    settings.mb_postfix
                ),
            ),
        ])

    def cpu_info(self) -> Tuple[str, List[Tuple[str, str]]]:
        return self.cpu.cpu_name[0], tools.get_table([
            tools.get_tuple(
                strings.cpu_clock,
                f"{tools.get_max(self.cpu.clock):.0f}{settings.clock_postfix}"
            ),
            tools.get_tuple(
                strings.cpu_voltage,
                f"{tools.get_max(self.cpu.voltage):.3f}{settings.voltage_postfix}"
            ),
            tools.get_tuple(
                strings.cpu_power,
                f"{self.cpu.power:.0f}{settings.power_postfix}"
            ),
            tools.get_tuple(
                strings.cpu_temperature,
                tools.get_temperature_display(tools.get_max(self.cpu.temperature), "cpu")
            ),
            tools.get_tuple(
                strings.cpu_usage,
                tools.get_rate_display(tools.get_avg(self.cpu.usage))
            ),
            tools.get_tuple(
                strings.cpu_max_thread_usage,
                tools.get_rate_display(tools.get_max(self.cpu.load))
            ),
            tools.get_tuple(
                strings.cpu_thread_usage,
                tools.get_each_usage(self.cpu.load)
            ),
        ])

    @classmethod
    def gpu_info(cls, gpu_info) -> List[Tuple[str, List[Tuple[str, str]]]]:
        return list([(gpu_info.gpu_names[gpu_idx], tools.get_table([
            tools.get_tuple(
                strings.gpu_clock,
                f"{gpu_info.core_clock[gpu_idx]:.0f}{settings.clock_postfix}"
            ),
            tools.get_tuple(
                strings.gpu_memory_clock,
                f"{gpu_info.memory_clock[gpu_idx]:.0f}{settings.clock_postfix}"
            ),
            tools.get_tuple(
                strings.gpu_power,
                tools.get_max_display(
                    f"{gpu_info.power[gpu_idx]:.0f}",
                    f"{gpu_info.available_power[gpu_idx]:.0f}",
                    settings.power_postfix
                ),
            ),
            tools.get_tuple(
                strings.gpu_memory_detail,
                tools.get_max_display(
                    f"{gpu_info.used_memory[gpu_idx] // settings.byte2mb:.0f}",
                    f"{gpu_info.available_memory[gpu_idx] // settings.byte2mb:.0f}",
                    settings.mb_postfix
                ),
            ),
            tools.get_tuple(
                strings.gpu_temperature,
                tools.get_temperature_display(gpu_info.temperature[gpu_idx], f"gpu-{gpu_idx}")
            ),
            tools.get_tuple(
                strings.gpu_usage,
                tools.get_rate_display(gpu_info.usage[gpu_idx])
            ),
            tools.get_tuple(
                strings.gpu_memory_usage,
                tools.get_rate_display(gpu_info.memory_usage[gpu_idx])
            ),
        ])) for gpu_idx in range(gpu_info.gpu_count)])

    def network_info(self) -> Tuple[str, List[Tuple[str, str]]]:
        return strings.network, tools.get_table([
            tools.get_tuple(
                strings.upload,
                f"{self.network.upload / settings.byte2mb:.2f}{settings.mb_per_postfix}"
            ),
            tools.get_tuple(
                strings.download,
                f"{self.network.download / settings.byte2mb:.2f}{settings.mb_per_postfix}"
            )
        ])

    def get_info(self) -> List[Tuple[str, List[Tuple[str, str]]]]:
        self.update()

        return [
            self.outline_info(),
            self.memory_info(),
            self.cpu_info(),
            *(self.gpu_info(self.nv_gpu) if self.nv_gpu else []),
            *(self.gpu_info(self.gpu) if self.gpu else []),
            self.network_info(),
        ]

    def update(self):
        self.time.update()
        self.cpu.update()
        if self.gpu:
            self.gpu.update()
        if self.nv_gpu:
            self.nv_gpu.update()
        self.memory.update()
        self.network.update()
