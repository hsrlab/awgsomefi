from awgsomefi.oceangen.polynomial.interpolation import Polynomial

from dataclasses import dataclass
import numpy as np


@dataclass
class GlitchParams:
    period: int # nanoseconds
    norm_ts: list[float] # Range from 0 to 100. See `Polynomial.DOMAIN`
    voltages: list[float]


    @classmethod
    def from_segments(cls, segments: list[float], voltages: list[float], final_offset: int):
        ts = np.cumsum(segments)
        period = ts[-1] + final_offset
        norm_ts = np.interp(ts, [0, period], Polynomial.DOMAIN)
        return cls(period, norm_ts.tolist(), voltages)
