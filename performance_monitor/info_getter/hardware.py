import abc
from typing import Annotated


class GeneralHardware(abc.ABC):
    SensorValue: str = "SensorValue"

    @abc.abstractmethod
    def clear(self): ...

    @abc.abstractmethod
    def dispose(self): ...

    @abc.abstractmethod
    def update(self): ...

    def sensors(self):
        sensors_dict = {}
        for cls in self.__class__.__mro__:
            if not issubclass(cls, GeneralHardware):
                continue
            for key, value_cls in cls.__annotations__.items():
                if (
                    value_cls.__name__ == Annotated.__name__
                    and GeneralHardware.SensorValue in value_cls.__metadata__
                ):
                    sensors_dict.setdefault(key, getattr(self, key))

        return sensors_dict
