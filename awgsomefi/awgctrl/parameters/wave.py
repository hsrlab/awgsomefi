from dataclasses import dataclass, field
from typing import List

@dataclass
class CommonWave:
    frequency: int # Hertz

    @classmethod
    def from_period(cls, period: int, *args, **kwargs):
        """
        Unit of period is nano seconds
        """
        frequency = int(1/(period * 1e-9))
        return cls(*args, frequency=frequency, **kwargs)

@dataclass
class ArbWave(CommonWave):
    phase: float = 0
    waveform: List[int] = field(default_factory=list)

@dataclass
class SquareWave(CommonWave):
    phase: float = 0
    duty: int = 50 # %

@dataclass
class SineWave(CommonWave):
    phase: float = 0

@dataclass
class PulseWave(CommonWave):
    fall: float # Nanoseconds: [8.4, 20] range for SDG
    delay: float = 0 # Seconds
