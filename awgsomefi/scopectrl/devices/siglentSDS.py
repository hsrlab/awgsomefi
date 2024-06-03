from numpy._typing import NDArray
import matplotlib.pyplot as plt
import numpy as np
from awgsomefi.parameters.voltage import VoltageBound

import vxi11

from dataclasses import dataclass

@dataclass
class ScopeWave:
    # Wave points
    wave: NDArray[np.int32]
    
    # Volts
    voltage_div: float

    # Distance between samples in nanoseconds
    sample_diff: float
    
    @property
    def normalized(self):
        return self.wave * self.voltage_div


# https://siglentna.com/wp-content/uploads/dlm_uploads/2017/10/ProgrammingGuide_forSDS-1-1.pdf
class SiglentSDS:
    channels = 4

    # Distance in nanoseconds between two samples
    sample_diff = 0.2

    samples = 2800

    def __init__(self, ip):
        self.instr = vxi11.Instrument(ip)

    def _write(self, inpt):
        return self.instr.write(inpt)

    def _ask(self, inpt: bytes):
        return self.instr.ask_raw(inpt)

    def _read(self, size: int):
        return self.instr.read_raw(size)

    def channel(self, channel: int):
        if 0 < channel <= self.channels:
            return f"C{channel}: "
        raise ValueError("Channel {channel} invalid: scope has {self.channel} channels")


    def trig_normal(self):
        self._write("TRMD NORM")

    def trig_auto(self):
        self._write("TRMD AUTO")

    def get_vdiv(self, channel):
        #raw_vdiv = self._ask(f"{self.channel(channel)}VDIV?".encode())
        #raw_vdiv = self._ask(f"{self.channel(channel)}VDIV?".encode())
        #CHAN1:SCAL?
        return float(raw_vdiv.strip().split()[1][:-1])

    def waveform_setup(self, sp=1, np=0, fp=0):
        """
            Setup waveform retrieval:
            Parameters:
                sp: Sparsing. Interval between data points
                np: Number of points total. 0 sends all points
                fp: index of the first data point to display
        """
        self._write(f"WFSU SP,{sp},NP,{np},FP,{fp}")

    def get_waveform(self, scope_channel: int, plot=False) -> ScopeWave:
        #wave_data = self._ask((self.channel(scope_channel) + f"WF? DAT2").encode())
        #self._write(f"WAV:SOURce C{scope_channel}".encode())
        self._write(f"WAV:SOUR C{scope_channel}")
        wave_data = self._ask("WAV:DATA?".encode())
        #print(wave_data)
        #wave_data = wave_data[wave_data.find(b',') + 1:]

        assert wave_data[0] == ord('#')

        length_indicator = int(chr(wave_data[1])) # 9
        length = int(wave_data[2:2+length_indicator])

        data = wave_data[2+length_indicator:]

        points = [(code-255 if code > 127 else code )/25 for code in data[:-2]]

        # 2 GS/s means 0.5 nanoseconds between samples
        if plot:
            plt.plot(np.arange(0, len(points)) * self.sample_diff, points)
            plt.ylim(bottom=-0.1, top=2.5)
            plt.ylabel("Voltage (V)")
            plt.xlabel("Time (ns)")
            plt.show()

        assert data[-2:] == b'\n\n'
        #assert len(data) == length

        return ScopeWave(np.array(points, dtype=float), voltage_div=0.5, sample_diff=self.sample_diff)
