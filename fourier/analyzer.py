from scipy.interpolate import CubicHermiteSpline
from scipy.signal import stft
from scipy import signal

import ssqueezepy

import glob

import matplotlib.pyplot as plt

from numpy.polynomial.chebyshev import Chebyshev
import numpy as np

def fft_spline():
    primary_xs = np.linspace(0, 100, 5)
    poly = CubicHermiteSpline(primary_xs, [3, 1.9, 2.5, 1.9, 3], np.zeros(5))

    sample_rate = 1/10**2

    xs = np.arange(0, 1, sample_rate)

    primary_xs = np.linspace(0, 1, 5)
    poly = CubicHermiteSpline(primary_xs, [3, 1.0, 2.5, 1.0, 3], np.zeros(5))

    print(1/sample_rate * np.pi)

    #ys = np.sin(2 * np.pi * 10**5 * xs)# + np.sin(2 * np.pi * 20 * xs)
    ys = poly(xs).astype(float)
    print(np.max(ys))
    #f, t, Zxx = stft(ys, 1/0.01)
    #print(f.shape)
    #print(t.shape)
    #print(Zxx.shape)
    #plt.pcolormesh(t, f, np.abs(Zxx))

    #fourier = np.fft.fft(ys)
    #freq = np.fft.fftfreq(len(ys), d=xs[1] - xs[0])
    #print(xs[1] - xs[0])

    f, t, Zxx = signal.stft(ys, sample_rate)
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')
    plt.pcolormesh(t, f, np.abs(Zxx), vmin=0, vmax=3, shading='gouraud')
    plt.show()

    #plt.plot(freq, np.abs(fourier))
    #plt.xlim(0)


help(ssqueezepy.cwt)
#fft_spline()
plt.show()
