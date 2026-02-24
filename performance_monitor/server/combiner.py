import threading
from typing import Any, Dict, List

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
    _lock: threading.Lock

    def __init__(self):
        super().__init__(
            getters_dict={
                "time": TimeInformation,
                "cpu": CpuInformation,
                "gpu": GeneralGpuInformation,
                "nv_gpu": NvidiaGpuInformation,
                "memory": MemoryInformation,
                "network": NetworkInformation,
                "frame_time": FrameTimeInformation,
            }
        )
        self._lock = threading.Lock()

    def get_info(self) -> List[Dict[str, Any]]:
        with self._lock:
            self._update()
            return list(getter.sensors() for getter in self.available_getters)
