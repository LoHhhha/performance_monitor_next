import abc
from typing import Annotated, get_origin as get_origin_cls


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
                break
            for key, value_cls in cls.__annotations__.items():
                if (
                    get_origin_cls(value_cls) is Annotated
                    and GeneralHardware.SensorValue in value_cls.__metadata__
                ):
                    sensors_dict[key] = getattr(self, key)

        return {"type": self.__class__.__name__, "sensors": sensors_dict}
