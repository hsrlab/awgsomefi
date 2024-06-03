from dataclasses import dataclass

@dataclass
class VoltageBound:
    """ Voltage configurations for the glitch """
    low:  float
    high: float
    norm: float

    @property
    def delta(self):
        return self.high - self.low

    @property
    def amplitude(self):
        return self.delta

    @property
    def offset(self):
        return (self.high + self.low)/2
    
    # Division helpful for OPAMP gain compensation
    def __div__(self, other: int):
        if other > 0:
            low = self.low / other
            high = self.high / other
        elif other < 0:
            low  = self.high / other
            high = self.low / other
        else:
            raise ZeroDivisionError("Can't have OPAMP amplification of 0")
        norm = self.norm / other

        return VoltageBound(low, high, norm)
    
    def __mul__(self, other: int):
        if other >= 0:
            low = self.low * other
            high = self.high * other
        else:
            low  = self.high * other
            high = self.low * other

        norm = self.norm * other

        return VoltageBound(low, high, norm)



    __truediv__ = __div__
