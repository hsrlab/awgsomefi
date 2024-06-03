import skopt
import shap

from scipy.interpolate import CubicHermiteSpline
from scipy.signal import stft

import glob

import matplotlib.pyplot as plt

from skopt.plots import plot_objective, plot_convergence

from numpy.polynomial.chebyshev import Chebyshev
import numpy as np

import matplotlib as mpl
rc_fonts = {
    "font.family": "serif",
    "font.size": 32,
    "text.usetex": True,
    "text.latex.preamble": r"""
    \usepackage{libertine}
    \usepackage{amsmath}
    \usepackage[libertine]{newtxmath}
    """
}

mpl.rcParams.update(rc_fonts)


def load_data(filename):
    return skopt.load(filename)


def plot_chebyshev():
    a,b,c,d = [52.234091724866374, 149.99999999999912, 247.76590827513243, 2.627008538016581e-8]
    poly = Chebyshev.interpolate(lambda x: 3 + (d*x*(-12*a*b*c + 6*(b*c + a*(b + c))*x - 4*(a + b + c)*x**2 + 3*x**3))/12, 4)
    xs = np.linspace(0, 300, 1000)
    ys = poly(xs)

    plt.grid(color="gray")
    plt.rc('axes', axisbelow=True)
    plt.title("Chebyshev Polynomial")
    plt.xlabel("Glitch Time (ns)")
    plt.ylabel("Voltage (V)")
    plt.plot(xs, ys)

def plot_chebyshev_derivative():
    a,b,c,d = [52.234091724866374, 149.99999999999912, 247.76590827513243, 2.627008538016581e-8]
    poly = Chebyshev.interpolate(lambda x: 3 + (d*x*(-12*a*b*c + 6*(b*c + a*(b + c))*x - 4*(a + b + c)*x**2 + 3*x**3))/12, 4).deriv()
    xs = np.linspace(0, 300, 1000)
    ys = poly(xs)

    plt.grid(color="gray")
    plt.rc('axes', axisbelow=True)
    plt.title("Chebyshev Polynomial Derivative")
    plt.xlabel("Glitch Time (ns)")
    plt.ylabel("Slew Rate (V/ns)")
    plt.plot(xs, ys)

def fft_chebyshev():
    a,b,c,d = [52.234091724866374, 149.99999999999912, 247.76590827513243, 2.627008538016581e-8]
    poly = Chebyshev.interpolate(lambda x: 3 + (d*x*(-12*a*b*c + 6*(b*c + a*(b + c))*x - 4*(a + b + c)*x**2 + 3*x**3))/12, 4).deriv()
    xs = np.linspace(0, 300, 1000)
    ys = poly(xs).astype(float)

    fourier = np.fft.fft(ys)
    freq = np.fft.fftfreq(len(ys), xs[1] - xs[0])
    plt.plot(freq, np.abs(fourier))

def fft_spline():
    primary_xs = np.linspace(0, 100, 5)
    poly = CubicHermiteSpline(primary_xs, [3, 1.9, 2.5, 1.9, 3], np.zeros(5))

    xs = np.arange(0, 100, 0.01)

    ys = np.sin(2 * np.pi * 10 * xs) + np.sin(2 * np.pi * 20 * xs)
    #ys = poly(xs).astype(float)
    #f, t, Zxx = stft(ys, 1/0.01)
    #print(f.shape)
    #print(t.shape)
    #print(Zxx.shape)
    #plt.pcolormesh(t, f, np.abs(Zxx))

    fourier = np.fft.fft(ys)
    freq = np.fft.fftfreq(len(ys), d=xs[1] - xs[0])

    plt.plot(freq, np.abs(fourier))
    plt.xlim(0, 30)
    #plt.plot(xs, ys)

def plot_spline_derivative(params=[3, 1.9, 2.5, 1.9, 3], length=300):
    primary_xs = np.linspace(0, length, 5)
    poly = CubicHermiteSpline(primary_xs, params, np.zeros(5)).derivative()
    xs = np.linspace(0, length, 1000)
    ys = poly(xs)

    plt.grid(color="gray")
    plt.rc('axes', axisbelow=True)
    plt.title("Polynomial Spline Derivative")
    plt.xlabel("Glitch Time (ns)")
    plt.ylabel("Slew Rate (V/ns)")
    plt.plot(xs, ys)

def plot_spline(params=[3, 1.9, 2.5, 1.9, 3], length=300):
    primary_xs = np.linspace(0, length, 5)
    poly = CubicHermiteSpline(primary_xs, params, np.zeros(5))
    xs = np.linspace(0, length, 1000)
    ys = poly(xs)

    plt.grid(color="gray")
    plt.rc('axes', axisbelow=True)
    plt.title("Polynomial Spline")
    plt.xlabel("Glitch Time (ns)")
    plt.ylabel("Voltage (V)")
    plt.plot(xs, ys)


def plot_twin_spline(params=[3, 0.8, 2.5, 0.8, 3], primary_xs=[0, 25, 50, 57, 100], length=200, name=None):
    fig, ax1 = plt.subplots(figsize=(16, 8))
    ax2 = ax1.twinx()

    primary_xs = np.interp(primary_xs, [0, 100], [0, length])

    poly = CubicHermiteSpline(primary_xs, params, np.zeros_like(primary_xs))
    deriv = poly.derivative()
    xs = np.linspace(0, length, 100000)
    ys1 = poly(xs)
    ys2 = deriv(xs)

    ax1.plot(xs, ys1, color="tab:red", label="Glitch Waveform", linewidth=3)
    ax2.plot(xs, ys2, color="tab:blue", linestyle="dashed", label="Glitch Waveform Derivative", linewidth=3)

    ax1.tick_params(axis="y", labelcolor="tab:red", labelsize=20)
    ax2.tick_params(axis="y", labelcolor="tab:blue", labelsize=20)
    ax1.tick_params(axis="x", labelsize=20)

    ax1.set_ylabel("Voltage (V)", color="tab:red", fontsize=24, fontweight='bold')
    ax2.set_ylabel("Slew Rate (V/ns)", color="tab:blue", fontsize=24, fontweight='bold')
    ax1.set_xlabel("Glitch Time (ns)", fontsize=24, fontweight='bold')
    #ax1.grid(color="gray")

    if name is not None:
        ax1.set_title(name)

    #ax2.set_ylim(-0.20, 0.20)
    #ax1.set_ylim(0.60, 3.00)
    #plt.show()
    #plt.savefig("/home/lstas/prop/spline_overshoot_plot_full.pdf", bbox_inches="tight")
    #np.save("dataset/waveforms/spline_waveform.npy", ys1)

def plot_twin_cheb():
    fig, ax1 = plt.subplots(figsize=(16, 8))
    ax2 = ax1.twinx()

    a,b,c,d = [31.60292980231234, 100.00000000000043, 168.39707019768815, 3.107126368465046e-7]
    length = 200
    poly = Chebyshev.interpolate(lambda x: 3 + (d*x*(-12*a*b*c + 6*(b*c + a*(b + c))*x - 4*(a + b + c)*x**2 + 3*x**3))/12, 4)
    deriv = poly.deriv()

    xs = np.linspace(0, length, 100000)
    ys1 = poly(xs)
    ys2 = deriv(xs)

    ax1.plot(xs, ys1, color="tab:red", label="Glitch Waveform", linewidth=3)
    ax2.plot(xs, ys2, linestyle="dashed", color="tab:blue", label="Glitch Waveform Derivative", linewidth=3)

    ax1.tick_params(axis="y", labelcolor="tab:red", labelsize=20)
    ax2.tick_params(axis="y", labelcolor="tab:blue", labelsize=20)
    ax1.tick_params(axis="x", labelsize=20)

    ax1.set_ylabel("Voltage (V)", color="tab:red", fontsize=24, fontweight='bold')
    ax2.set_ylabel("Slew Rate (V/ns)", color="tab:blue", fontsize=24, fontweight='bold')
    ax1.set_xlabel("Glitch Time (ns)", fontsize=24, fontweight='bold')

    ax2.set_ylim(-0.20, 0.20)
    #ax1.set_ylim(1.75, 3.05)
    #plt.show()
    #plt.savefig("/home/lstas/prop/cheb_overshoot_plot_full.pdf", bbox_inches="tight")
    np.save("dataset/waveforms/cheb_waveform.npy", ys1)


def plot_spline_data(data):
    params = [3] + data.x[1:] + [3]
    length = data.x[0]
    print(data.x)
    plot_spline(params, length)
    plt.show()
    plot_spline_derivative(params, length)


def show_best_glitch(data, label=""):
    print(data.fun)
    data = data.x
    primary_xs = np.linspace(0, data[0], 5)
    poly = CubicHermiteSpline(primary_xs, [3, data[1], data[2], data[3], 3], np.zeros(5))
    xs = np.linspace(0, data[0], 1000)
    ys = poly(xs)

    plt.rcParams["figure.figsize"] = (16,8)
    plt.xticks(np.linspace(0, data[0], 11))

    #colors = ["", "red", "green", "purple"]
    #for i in range(1, len(primary_xs) - 1):
        #plt.arrow(primary_xs[i], poly(primary_xs[i]), 0,  0.15, width=0.6, head_length=0.1, length_includes_head=True, color=colors[i])
        #plt.arrow(primary_xs[i], poly(primary_xs[i]), 0, -0.15, width=0.6, head_length=0.1, length_includes_head=True, color=colors[i])
    plt.scatter(primary_xs[1:-1], poly(primary_xs[1:-1]), color="purple", s=10, linewidths=8, zorder=100)

    plt.tick_params(axis="y", labelsize=32)
    plt.tick_params(axis="x", labelsize=32)

    #plt.grid(color="gray")
    plt.rc('axes', axisbelow=True)
    plt.xlabel(r"\textbf{Glitch Time (ns)}", fontsize="32")
    plt.ylabel(r"\textbf{Voltage (V)}", fontsize="32")
    plt.plot(xs, ys, linewidth=3, label=label)
    plt.ylim((0, 3.2))
    plt.yticks(np.arange(0, 3.1, 0.5))
    #plt.savefig("/home/lstas/prop/best_glitch.pdf", bbox_inches="tight")

def show_convergence(data):
    plt.rcParams["figure.figsize"] = (16,8)

    plot_convergence(data)
    plt.title("")
    plt.ylabel("Probability of Glitch Failing", fontsize="24", fontweight="bold")
    plt.xlabel("Waveforms Tried", fontsize="24", fontweight="bold")

    plt.tick_params(axis="y", labelsize=20)
    plt.tick_params(axis="x", labelsize=20)

    plt.savefig("/home/lstas/prop/covergence.pdf", bbox_inches="tight")

def show_dependence(data):
    #ax = plot_objective(data, dimensions=["Glitch Time (ns)", "First Minimum (V)", "Middle Peak (V)", "Last Minimum (V)"], sample_source="expected_minimum", minimum="expected_minimum", n_points=80)
    ax = plot_objective(data, sample_source="expected_minimum", minimum="expected_minimum", n_points=80)
    #ax1 = plot_objective(data, dimensions=["Glitch Time (ns)", "First Minimum (V)", "Middle Peak (V)", "Last Minimum (V)"], sample_source="random", minimum="expected_minimum")
    fig = ax[0, 0].get_figure()
    #fig.suptitle("Glitch Parameter Dependence Matrix")
    #fig.set_size_inches((10, 20))
    plt.show()
    #fig.savefig("/home/lstas/prop/dep_matrix.pdf")
    #return fig, ax


# even_w_2022-11-22 13:41:59.856331.gz : good bound
# even_w_2022-11-22 14:25:30.800383.gz : tuned bound

old = "dataset/spline_proposal_2023-01-16 13:11:10.668659.gz"
best = "dataset/spline_proposal_2023-01-16 14:37:35.551630.gz"
depends = "dataset/spline_proposal_2023-01-16 14:54:35.134613.gz"
wv = "dataset/spline_wv_2023-01-19 13:26:53.201399.gz"

best_twoglitch = "dataset/spline_w_pos_2023-02-03 08:20:22.297606.gz"
best_oneglitch = "dataset/spline_w_pos_2023-02-03 08:39:44.537175.gz"

best_nec = "dataset/spline_nec_leak3rd2023-05-09 19:09:18.937252.gz"

def nec_promise():
    toffsetpromise = 84
    periodpromise = 1752
    xspromise = [0, 465.12842465753425, 1131.2671232876712, 1757.6712328767123, 2451.8578767123286, 2945.034246575343, 3510.6678082191784, 4094]
    yspromise = np.array([180.20486177386047, 215.57675077124918, 126.74941706270315, 90.70129309192006, 57.81752498710887, 59.71370131121669]) * 5
    yspromise /= 1000
    xspromise = np.interp(xspromise, [0, 4094], [0, 100])

    yspromise = [1.8] + yspromise.tolist() + [1.8]

    plot_twin_spline(params=yspromise, primary_xs=xspromise, length=periodpromise)
    plt.show()


def nec_new():
    xsnew = [0, 234, 299, 213, 255, 231, 273]
    ysnew = np.array([0.1678330206398118, 0.22072976436429156, 0.18231235398310666, 0.07846777771048857, 0.08652150089080485, 0.05256824131202503]) * 5
    xsnew = np.cumsum(xsnew)
    periodnew = xsnew[-1] + 250
    xsnew = np.append(xsnew, periodnew)
    xsnew = np.interp(xsnew, [0, periodnew], [0, 100])
    print(xsnew)

    ysnew = [1.8] + ysnew.tolist() + [1.8]

    plot_twin_spline(params=ysnew, primary_xs=xsnew, length=periodnew)
    plt.savefig("/home/lstas/Documents/StanMsThesis/figures/78k0r-best-glitch.pdf", bbox_inches="tight")
    #plt.show()


def nec_bad():
    xsbad = [0, 234, 299, 213, 255, 231, 273]
    ysbad = np.array([0.0678330206398118, 0.32072976436429156, 0.28231235398310666, 0.07846777771048857, 0.26652150089080485, 0.05256824131202503]) * 5
    xsbad = np.cumsum(xsbad)
    periodbad = xsbad[-1] + 250
    xsbad = np.append(xsbad, periodbad)
    xsbad = np.interp(xsbad, [0, periodbad], [0, 100])

    ysbad = [1.8] + ysbad.tolist() + [1.8]
    print(ysbad)

    print(xsbad, ysbad)
    print(len(xsbad), len(ysbad))
    plot_twin_spline(params=ysbad, primary_xs=xsbad, length=periodbad)
    plt.show()



#data = load_data(best_nec)
#plt.plot(data.func_vals)

#show_best_glitch(load_data(depends), "Best found glitch")
#plt.ylim((0, 3))
#plt.show()
#nec_new()
#nec_bad()
#nec_promise()

for filepath, name in zip([best_oneglitch, best_twoglitch], ["Single Instruction Skip", "Double Instruction Skip"]):
    data = load_data(filepath)

    #fft_chebyshev()
    #fft_spline()
    #plot_twin_spline([3] + data.x[1:4] + [3], [0] + data.x[4:] + [100], length=data.x[0], name=name)
    #print(name)
    #print(data.fun)
    #print(data.x)
    #print()
    #plot_twin_cheb()
    #plot_twin_spline()
    #plot_twin_cheb()
    #plt.show()

    #plot_twin_cheb()
    #plot_spline()
    #plot_spline_derivative()
    #plt.ylim(-0.06, 0.06)
    #plot_spline_data(data)
    #plot_chebyshev_derivative()

    #plot_spline_derivative()
    #show_dependence(data)

    #print(data.x)
    #plt.tight_layout()
    show_best_glitch(data, label=name)
    plt.legend(prop=dict(weight='bold', size=24))
    #show_convergence(data)
    #fig, ax = show_dependence(data)
    #print(data.fun)

    #generate_spline(*data.x, plot=True)
    #plt.show()

    #if int(data.fun*100) == 57:
    #    model = data.models[-1]
    #    print(model)

    #    X_train = np.array([np.array(x) for x in data.x_iters])
    #    print(model.predict(X_train))
    #    quit()
    #    explainer = shap.KernelExplainer(model.predict, X_train)

    #    test = np.array([[200, 0.8, 1.8, 0.8]])
    #    values = explainer(test)
    #    #vals = explainer(np.array(data.x_iters))
    #    #plot_objective(data)
    #    break
    #print(data.fun)
    #print(data)
    

#plt.show()
plt.tight_layout()
plt.savefig("/home/lstas/Documents/StanMsThesis/figures_practice/stmglitch-single-double.pdf", bbox_inches="tight")
