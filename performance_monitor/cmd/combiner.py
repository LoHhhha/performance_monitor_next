from datetime import datetime
import time
from typing import Optional, Tuple, List

from . import settings, tools
from ..assets import strings
from ..info_getter import (
    TimeInformation,
    CpuInformation,
    GeneralGpuInformation,
    NvidiaGpuInformation,
    MemoryInformation,
    NetworkInformation,
    FrameTimeInformation,
    Combiner as BaseCombiner,
)


class Combiner(BaseCombiner):
    time: TimeInformation
    cpu: CpuInformation
    gpu: Optional[GeneralGpuInformation]
    nv_gpu: Optional[NvidiaGpuInformation]
    memory: MemoryInformation
    network: NetworkInformation
    frame_time: FrameTimeInformation

    def __init__(
        self,
        general_gpu_enable: bool = True,
        nv_gpu_enable: bool = True,
    ):
        super().__init__(
            getters_dict={
                "time": TimeInformation,
                "cpu": CpuInformation,
                "gpu": GeneralGpuInformation if general_gpu_enable else None,
                "nv_gpu": NvidiaGpuInformation if nv_gpu_enable else None,
                "memory": MemoryInformation,
                "network": NetworkInformation,
                "frame_time": FrameTimeInformation,
            }
        )
        time.sleep(2)

    def _get_total_power(self) -> float:
        return (
            tools.get_sum(self.cpu.power)
            + (tools.get_sum(self.nv_gpu.power) if self.nv_gpu else 0)
            + (tools.get_sum(self.gpu.power) if self.gpu else 0)
        )

    def _get_fps_str(self) -> str:
        if self.frame_time.fps is None or self.frame_time.fps_1_low is None:
            fps = strings.error_value
        else:
            fps = f"{self.frame_time.fps}({self.frame_time.fps_1_low})"
        return fps

    def outline_info(self) -> Tuple[str, List[Tuple[str, str]]]:
        time_datetime = datetime.fromtimestamp(self.time.time)
        return strings.outline_name, tools.get_table(
            [
                tools.get_tuple(
                    strings.time,
                    tools.get_pair_display(
                        time_datetime.strftime("%H:%M:%S"),
                        time_datetime.strftime("%a %b.%d"),
                        sep="",
                        clip_able=False,
                    ),
                ),
                tools.get_tuple(
                    strings.fps,
                    tools.get_pair_display(
                        self._get_fps_str(),
                        (
                            self.frame_time.target_process
                            if self.frame_time.target_process
                            else "UNKNOWN"
                        ),
                        sep="@ ",
                    ),
                ),
                tools.get_tuple(
                    strings.total_power,
                    tools.get_trend_display(
                        self._get_total_power(),
                        trend_id="total_power",
                        prefix=settings.power_postfix,
                        lowest=20,
                        highest=180,
                    ),
                ),
            ]
        )

    def memory_info(self) -> Tuple[str, List[Tuple[str, str]]]:
        return strings.memory_name, tools.get_table(
            [
                tools.get_tuple(
                    strings.memory_usage,
                    tools.get_rate_display(self.memory.physical_memory_usage),
                ),
                tools.get_tuple(
                    strings.memory_detail,
                    tools.get_pair_display(
                        f"{self.memory.used_physical_memory // settings.byte2mb:.0f}",
                        f"{self.memory.total_physical_memory // settings.byte2mb:.0f}",
                        settings.mb_postfix,
                    ),
                ),
                tools.get_tuple(
                    strings.memory_swap_detail,
                    tools.get_pair_display(
                        f"{self.memory.used_swap_memory // settings.byte2mb:.0f}",
                        f"{self.memory.total_swap_memory // settings.byte2mb:.0f}",
                        settings.mb_postfix,
                    ),
                ),
            ]
        )

    def cpu_info(self) -> List[Tuple[str, List[Tuple[str, str]]]]:
        return list(
            (
                self.cpu.cpu_name[cpu_idx],
                tools.get_table(
                    [
                        tools.get_tuple(
                            strings.cpu_clock,
                            f"{tools.get_max(self.cpu.clock[cpu_idx]):.0f}{settings.clock_postfix}",
                        ),
                        tools.get_tuple(
                            strings.cpu_voltage,
                            f"{tools.get_max(self.cpu.voltage[cpu_idx]):.3f}{settings.voltage_postfix}",
                        ),
                        tools.get_tuple(
                            strings.cpu_power,
                            f"{self.cpu.power[cpu_idx]:.0f}{settings.power_postfix}",
                        ),
                        tools.get_tuple(
                            strings.cpu_temperature,
                            tools.get_trend_display(
                                tools.get_max(self.cpu.temperature[cpu_idx]),
                                trend_id=f"cpu-{cpu_idx}",
                                prefix=settings.temperature_postfix,
                                lowest=30,
                                highest=100,
                            ),
                        ),
                        tools.get_tuple(
                            strings.cpu_usage,
                            tools.get_rate_display(
                                tools.get_avg(self.cpu.usage[cpu_idx])
                            ),
                        ),
                        tools.get_tuple(
                            strings.cpu_max_thread_usage,
                            tools.get_rate_display(
                                tools.get_max(self.cpu.load[cpu_idx])
                            ),
                        ),
                        tools.get_tuple(
                            strings.cpu_thread_usage,
                            tools.get_each_usage(self.cpu.load[cpu_idx]),
                            clip_val=False,
                        ),
                    ]
                ),
            )
            for cpu_idx in range(self.cpu.cpu_count)
        )

    @classmethod
    def gpu_info(
        cls, gpu_info, sub_class: str = "general"
    ) -> List[Tuple[str, List[Tuple[str, str]]]]:
        return list(
            [
                (
                    gpu_info.gpu_names[gpu_idx],
                    tools.get_table(
                        [
                            tools.get_tuple(
                                strings.gpu_clock,
                                f"{gpu_info.core_clock[gpu_idx]:.0f}{settings.clock_postfix}",
                            ),
                            tools.get_tuple(
                                strings.gpu_memory_clock,
                                f"{gpu_info.memory_clock[gpu_idx]:.0f}{settings.clock_postfix}",
                            ),
                            tools.get_tuple(
                                strings.gpu_power,
                                tools.get_pair_display(
                                    f"{gpu_info.power[gpu_idx]:.0f}",
                                    f"{gpu_info.available_power[gpu_idx]:.0f}",
                                    settings.power_postfix,
                                ),
                            ),
                            tools.get_tuple(
                                strings.gpu_memory_detail,
                                tools.get_pair_display(
                                    f"{gpu_info.used_memory[gpu_idx] // settings.byte2mb:.0f}",
                                    f"{gpu_info.available_memory[gpu_idx] // settings.byte2mb:.0f}",
                                    settings.mb_postfix,
                                ),
                            ),
                            tools.get_tuple(
                                strings.gpu_temperature,
                                tools.get_trend_display(
                                    gpu_info.temperature[gpu_idx],
                                    trend_id=f"gpu-{sub_class}-{gpu_idx}",
                                    prefix=settings.temperature_postfix,
                                    lowest=30,
                                    highest=100,
                                ),
                            ),
                            tools.get_tuple(
                                strings.gpu_usage,
                                tools.get_rate_display(gpu_info.usage[gpu_idx]),
                            ),
                            tools.get_tuple(
                                strings.gpu_memory_usage,
                                tools.get_rate_display(gpu_info.memory_usage[gpu_idx]),
                            ),
                        ]
                    ),
                )
                for gpu_idx in range(gpu_info.gpu_count)
            ]
        )

    def network_info(self) -> Tuple[str, List[Tuple[str, str]]]:
        return strings.network, tools.get_table(
            [
                tools.get_tuple(
                    strings.upload,
                    tools.get_byte_speed_display(self.network.upload),
                ),
                tools.get_tuple(
                    strings.download,
                    tools.get_byte_speed_display(self.network.download),
                ),
            ]
        )

    def get_info(self) -> List[Tuple[str, List[Tuple[str, str]]]]:
        self._update()

        return [
            self.outline_info(),
            self.memory_info(),
            *self.cpu_info(),
            *(self.gpu_info(self.nv_gpu, sub_class="nv") if self.nv_gpu else []),
            *(self.gpu_info(self.gpu, sub_class="general") if self.gpu else []),
            self.network_info(),
        ]
