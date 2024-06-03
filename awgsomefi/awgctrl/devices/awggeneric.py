from abc import ABC, abstractmethod
from functools import wraps
from typing import Dict, List

import inspect
from awgsomefi.parameters.voltage import VoltageBound
import vxi11

from ..parameters import ArbWave, SquareWave, OperationMode, SineWave, PulseWave

ChannelID = int

class AwgGeneric(ABC):
    channels = 0

    channel_voltages: Dict[int, VoltageBound] = {}

    """
    Generic Methods
    """
    def __init__(self, setup_params, ip):
        self.instr = vxi11.Instrument(ip)
        self.protect_on()
        self.quick_setup(setup_params)

    def _write(self, inpt):
        return self.instr.write(inpt)

    def _ask(self, inpt):
        return self.instr.ask(inpt)

    def _ask_raw(self, inpt: bytes):
        return self.instr.ask_raw(inpt)

    def _write_raw(self, inpt: bytes):
        return self.instr.write_raw(inpt)

    """
    Device-specifc Methods
    """
    @abstractmethod
    def setup_arbitrary(self, channel: ChannelID, name: str,  wave: ArbWave, mode: OperationMode = OperationMode.BURST):
        pass

    @abstractmethod
    def set_trig_delay(self, channel: ChannelID, length):
        pass

    @abstractmethod
    def setup_square(self, channel: ChannelID, wave: SquareWave, mode: OperationMode = OperationMode.SWEEP):
        pass

    @abstractmethod
    def setup_sine(self, channel: ChannelID, wave: SineWave):
        pass

    @abstractmethod
    def setup_dc(self, channel: ChannelID, voltage: float):
        pass

    @abstractmethod
    def setup_pulse(self, channel: ChannelID, pulse: PulseWave):
        pass

    @abstractmethod
    def get_channel_wave(self, channel: ChannelID):
        pass

    @abstractmethod
    def set_load(self, channel: ChannelID, **kwargs):
        pass

    @abstractmethod
    def set_operation_mode(self, channel: ChannelID, mode: OperationMode):
        pass

    @abstractmethod
    def reset(self):
        pass

    @abstractmethod
    def protect_on(self):
        pass

    @abstractmethod
    def wait_complete(self):
        pass

    @abstractmethod
    def combine_channels(self, channel: ChannelID):
        pass

    @abstractmethod
    def set_polarity_normal(self, channel: ChannelID):
        pass

    @abstractmethod
    def set_polarity_invert(self, channel: ChannelID):
        pass

    @abstractmethod
    def enable_channel(self, channel: ChannelID):
        pass

    @abstractmethod
    def disable_channel(self, channel: ChannelID):
        pass

    @property
    @abstractmethod
    def sysinfo(self):
        pass

    @property
    @abstractmethod
    def properties(self) -> Dict:
        pass


    @classmethod
    def get_awg(cls, model, setup_params, *args, **kwargs):
        for awg in cls.__subclasses__():
            if model in awg.__name__:
                return awg(setup_params=setup_params, *args, **kwargs)
        return None

    def quick_setup(self, channels: List[Dict]):
        for channel in channels:
            channel_id = channel["channel_id"]
            print("Setting up channel", channel)
            # Set voltage for the channel
            voltage = VoltageBound(**channel['voltage'])
            if "opamp_gain" in channel:
                gain = channel['opamp_gain']

                if gain < 0:
                    self.set_polarity_invert(channel_id)
                else:
                    self.set_polarity_normal(channel_id)
                voltage /= abs(gain)
            else:
                self.set_polarity_normal(channel_id)

            self.channel_voltages[channel_id] = voltage

            # Set load for the channel
            if "load" not in channel or channel["load"] == "hiZ":
                self.set_load(channel_id, hiZ=True)
            else:
                self.set_load(channel_id, resistance=channel['load'])

        return self.channel_voltages

