"""
Written for: RIGOL TECHNOLOGIES,DP831,DP8F233600366,00.01.16
"""
from .psugeneric import PsuGeneric
from ..properties.psuproperty import PsuProperty

class RigolDP831(PsuGeneric):
    channels = 3

    def _enable_channel(self, channel):
        self._write(f":OUTP CH{channel},ON")

    def _disable_channel(self, channel):
        self._write(f":OUTP CH{channel},OFF")

    def current_limit(self, channel):
        #return float(self._ask(":CURR:PROT?"))
        return float(self._ask(f":SOUR{channel}:CURR?"))

    def voltage_limit(self, channel):
        #return float(self._ask(":VOLT:PROT?"))
        return float(self._ask(f":SOUR{channel}:VOLT?"))

    @property
    def sysinfo(self):
        return self._ask("*IDN?")

    @property
    def properties(self) -> PsuProperty:
        return PsuProperty(something=2**16)
