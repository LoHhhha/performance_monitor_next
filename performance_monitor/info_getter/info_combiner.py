from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from . import GeneralHardware


class Combiner(ABC):
    available_getters: List[GeneralHardware]

    def __init__(
        self,
        getters_dict: Dict[str, Optional[GeneralHardware]],
    ):
        print("Collecting Meta Information...")

        self.available_getters = []
        for name, getter_cls in getters_dict.items():
            if getter_cls is None:
                setattr(self, name, None)
                continue
            getter = getter_cls()
            setattr(self, name, getter)
            self.available_getters.append(getter)

        print("Initialization Complete.")

    @abstractmethod
    def get_info(self) -> Any: ...

    def _update(self):
        for getter in self.available_getters:
            getter.update()

    def dispose(self):
        for getter in self.available_getters:
            getter.dispose()
        print("All resources released.")
