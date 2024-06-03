import numpy as np
import matplotlib.pyplot as plt
from ssqueezepy import ssq_cwt, ssq_stft, cwt
from scipy.interpolate import CubicHermiteSpline
from ssqueezepy.visuals import plot, imshow
from matplotlib import cm


def viz(x, Tx, Wx):
    plt.imshow(np.abs(Wx), aspect='auto', cmap='turbo')
    plt.show()
    plt.imshow(np.abs(Tx), aspect='auto', vmin=0, vmax=.2, cmap='turbo')
    plt.show()

# Define poly signal
#ys1 = [3, 0, 1, 0, 1, 0, 3]
#ys2 = [500, 0, 200, 0, 200, 0, 200, 0, 200, 0, 500]
#ys3 = [3, 0, 1, 0, 1, 0, 1, 0, 3]
##ys3 = [500, 0, 200, 100, 300, 200, 500]
##ys = [500, 0, 200, 0, 200, 0, 200, 0, 200, 0, 200, 0, 500]
##ys = [500, 0, 500]
#
#def get_spline(ys):
#    primary_xs = np.linspace(0, 1/1000, len(ys))
#    poly = CubicHermiteSpline(primary_xs, ys, np.zeros(len(ys)))
#    return poly
#
#poly1 = get_spline(ys1)
#poly2 = get_spline(ys2)
#poly3 = get_spline(ys3)#lambda x: 100*np.sin(1000 * x * 2 * np.pi)# + np.sin(x*50) + np.sin(x*100)
##poly4 = get_spline(ys4)
#
##%%# Define signal ####################################
#N = 10000
#t = np.linspace(0, 1/1000, N, endpoint=True)
#t2 = np.linspace(0, 4 * np.pi, 2*N, endpoint=False)
#xo = np.cos(2 * np.pi * 2  * t)
#xo += xo[::-1]  # add self reflected
#x = xo + np.sqrt(2) * np.random.randn(N)  # add noise
#plt.plot(poly(t))
#plt.show()
#quit()



x1 = np.load("./waveforms/cheb_glitch.npy")
x2 = np.load("./waveforms/spline_glitch.npy")

N = len(x1)
t = np.linspace(0, 200e-9, N)

#x1 = poly1(t)
##x2 = poly2(t)
#x3 = poly3(t)
#x4 = poly4(t)
#x = np.hstack((x, x))
plt.plot(t, x1)
#plt.plot(t, x2)
plt.plot(t, x2)
#plt.plot(t, 24)
plt.show()
quit()

#help(cwt)
#Wx, scales = cwt(x)
Tx, _, ssq_freqs, *_ = ssq_cwt(x1, t=np.linspace(0, 200e-9, N, True))
Tx2, _, ssq_freqs, *_ = ssq_cwt(x2, t=np.linspace(0, 200e-9, N, True))
#Tx = np.sum(np.abs(Tx), axis=1)

filt = (ssq_freqs <  10**7)

ssq_freqs = ssq_freqs[filt]
Tx = Tx[filt]
Tx2 = Tx2[filt]

#plt.pcolormesh(t, ssq_freqs, np.abs(Tx))
plt.pcolormesh(t, ssq_freqs, np.abs(Tx))
plt.show()

#ax = plt.figure().add_subplot(projection='3d')
#ax.plot_surface(ssq_freqs[:, None], t[None, :], np.abs(Tx2))
#ax.plot_surface(ssq_freqs[:, None], t[None, :], np.abs(Tx2), cmap=cm.coolwarm)
#ax.set_xlim((0, 10000))
#plt.show()
#
##imshow(Tx, abs=1, title="abs(SSWT)", yticks=ssq_freqs, show=1)
#
#Tx, _, ssq_freqs, *_ = ssq_cwt(x2, t=np.linspace(0, 1/1000, N, True))
#Tx = np.sum(np.abs(Tx), axis=1)
#plt.plot(ssq_freqs, np.abs(Tx))
##imshow(Tx, abs=1, title="abs(SSWT)", yticks=ssq_freqs, show=1)
#
#Tx, _, ssq_freqs, *_ = ssq_cwt(x3, t=np.linspace(0, 1/1000, N, True))
#Tx = np.sum(np.abs(Tx), axis=1)
#plt.plot(ssq_freqs, np.abs(Tx))
#
##print(len(scales))
##plt.xlim((0, 10000))
#plt.show()
#
#plt.xlim((0, 0.5*10**8))
#
#fourier = np.fft.fft(x1)
#freq = np.fft.fftfreq(len(x1), d=t[1] - t[0])
#plt.plot(freq, np.abs(fourier))
#
#fourier = np.fft.fft(x2)
#freq = np.fft.fftfreq(len(x2), d=t[1] - t[0])
#plt.plot(freq, np.abs(fourier))

#fourier = np.fft.fft(x3)
#freq = np.fft.fftfreq(len(x3), d=t[1] - t[0])
#plt.plot(freq, np.abs(fourier))

#fourier = np.fft.fft(x4)
#freq = np.fft.fftfreq(len(x3), d=t[1] - t[0])
#plt.plot(freq, np.abs(fourier))

