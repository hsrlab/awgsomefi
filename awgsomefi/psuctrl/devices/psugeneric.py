from abc import ABC, abstractmethod
from ..properties.psuproperty import PsuProperty
import vxi11

from functools import wraps

class PsuGeneric(ABC):
    channels = 0

    class protect:
        def __call__(self, func):
            @wraps(func)
            def wrapper(self, channel, *args, **kwargs):
                if (self.current_limit(channel) <= self.upper_current and
                    self.voltage_limit(channel) <= self.upper_voltage):

                    return func(self, channel, *args, **kwargs)

                raise ValueError(f"Channel '{channel}' protections not within configured bounds")
            return wrapper


    def __init__(self, ip, upper_voltage=5, upper_current=1, *args, **kwargs):
        self.instr = vxi11.Instrument(ip)
        self.upper_voltage = upper_voltage
        self.upper_current = upper_current

    def _write(self, inpt):
        return self.instr.write(inpt)

    def _ask(self, inpt):
        return self.instr.ask(inpt)

    @abstractmethod
    def current_limit(self, channel):
        pass

    @abstractmethod
    def voltage_limit(self, channel):
        pass

    @abstractmethod
    def _enable_channel(self, channel):
        pass

    @abstractmethod
    def _disable_channel(self, channel):
        pass

    @property
    @abstractmethod
    def sysinfo(self):
        pass

    @property
    @abstractmethod
    def properties(self) -> PsuProperty:
        pass

    @protect()
    def enable_channel(self, channel):
        self._enable_channel(channel)

    def disable_channel(self, channel):
        self._disable_channel(channel)

    @classmethod
    def get_psu(cls, model, *args, **kwargs):
        for psu in cls.__subclasses__():
            if model in psu.__name__:
                return psu(*args, **kwargs)
        return None
