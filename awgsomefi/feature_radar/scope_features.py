import numpy as np
from awgsomefi.oceangen.polynomial.interpolation import Polynomial

from awgsomefi.scopectrl import SiglentSDS
from awgsomefi.parameters import VoltageBound
from awgsomefi.scopectrl import ScopeWave

import matplotlib.pyplot as plt

class ScopeFeatureExtractor:

    def __init__(self, expectation: Polynomial) -> None:
        self.expectation = expectation
        self.waveforms: list[ScopeWave] = []
        self.extractors = [
                    self.extract_bounds,
                    self.extract_duration
                ]

    def extract(self):
        points = np.average(np.array([w.normalized for w in self.waveforms]), axis=0)
        ex = ScopeWave(points, 1, 0.5)
        for extractor in self.extractors:
            print(extractor.__name__, extractor(ex))

    def add_scope_waveform(self, scope: SiglentSDS, channel: int):
        self.add_waveform(scope.get_waveform(channel))

    def add_waveform(self, waveform: ScopeWave):
        self.waveforms.append(waveform)

    def plot_waveforms(self):
        if len(self.waveforms) == 0:
            raise ValueError("Add at least 1 waveform")

        points = np.average(np.array([w.normalized for w in self.waveforms]), axis=0)
        plt.plot(np.arange(0, len(points)) * self.waveforms[0].sample_diff, points)
        plt.ylim(bottom=-0.1, top=2.5)
        plt.ylabel("Voltage (V)")
        plt.xlabel("Time (ns)")
        plt.show()

    def extract_duration(self, waveform: ScopeWave):
        wave = waveform.wave
        voltage = self.expectation.voltage
        start = np.argmax(wave < voltage.norm - 0.05)
        delta = np.argmax(wave[start:] > voltage.norm - 0.01)

        return delta * waveform.sample_diff
    
    def extract_bounds(self, waveform: ScopeWave):
        print(waveform.wave)
        wave = waveform.normalized
        low = np.min(wave)
        high = np.max(wave)
        norm = np.average(np.concatenate((wave[:10], wave[-10:])))
        voltage = VoltageBound(low, high, norm)

        # TODO: add delta_voltage
        return voltage
