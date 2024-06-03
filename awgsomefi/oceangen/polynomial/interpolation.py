import numpy as np
from numpy.polynomial import Chebyshev as P
from scipy.interpolate import CubicSpline, CubicHermiteSpline

from copy import deepcopy

from awgsomefi.awgctrl.parameters import Resolution
from awgsomefi.parameters import VoltageBound

import matplotlib.pyplot as plt



class Polynomial:
    """
    Represents evaluatable polynomial


    To be instantiated primarily using a `PolynomialFactory` instance
    """

    DOMAIN = (0, 100)

    def __init__(self, p, resolution, voltage) -> None:
        self.p = p
        self.resolution = resolution
        self.voltage = voltage

    @classmethod
    def chebyshev_from_points(cls, xs: np.ndarray, ys: np.ndarray, resolution: Resolution, voltage: VoltageBound):
        """
        Parameters
        ----------

        xs: NDArray[float]
            x values to interpolate. x should be within the DOMAIN
        ys: NDArray[float]
            y values to interpolate. y refers to the voltage setting
        resolution: Resolution
            Vertical/Horizontal resolution of the AWG

        voltage: VoltageBound
            The normal voltage as well as low/high bounds for the glitch

        Example
        -------
        p = Polynomial([25, 50, 75], [.3, 2.5, 1], Resolution(16, 12), VoltageBound(0, 3.3, 3.3))
        x = np.arange((1 << 12) - 1)
        plt.plot(x, p(x))
        plt.show()
        """

        # Set the function later
        xs_padded = [cls.DOMAIN[0]] + list(xs) + [cls.DOMAIN[1]]
        ys_padded = [voltage.norm] + list(ys) + [voltage.norm]
        degree = len(xs_padded) - 1 # Degree of interpolation
        p, (resid, rank, sv, rcond) = P.fit(resolution.rescale_horizontal(xs_padded, cls.DOMAIN), ys_padded, degree, domain=cls.DOMAIN, full=True)

        return cls(p, resolution, voltage)

    @classmethod
    def hermite_spline_from_points(cls, xs, ys, resolution: Resolution, voltage: VoltageBound, *, dydx=None):
        xs_padded = [cls.DOMAIN[0]] + list(xs) + [cls.DOMAIN[1]]
        ys_padded = [voltage.norm] + list(ys) + [voltage.norm]

        if dydx is None:
            dydx = np.zeros_like(xs_padded)

        spline = CubicHermiteSpline(resolution.rescale_horizontal(xs_padded, cls.DOMAIN), ys_padded, dydx)

        return cls(spline, resolution, voltage)

    @classmethod
    def spline_from_points(cls, xs, ys, configuration, resolution: Resolution, voltage: VoltageBound):
        xs_padded = [cls.DOMAIN[0]] + list(xs) + [cls.DOMAIN[1]]
        ys_padded = [voltage.norm] + list(ys) + [voltage.norm]

        spline = CubicSpline(resolution.rescale_horizontal(xs_padded, cls.DOMAIN), ys_padded, bc_type=configuration)

        return cls(spline, resolution, voltage)

    def __call__(self, x):
        """ Evaluate polynomial """
        return self.resolution.rescale_vertical(self.p(x), [self.voltage.low, self.voltage.high])

    def __neg__(self):
        """ Much better to invert the AWG polarity than to use this """
        newp = deepcopy(self)
        newp.p = -self.p
        return newp

    def eval_all(self, plot=False):
        eval_xs = np.arange(self.resolution.horizontal+1)
        points = self(eval_xs).astype(int)

        if plot:
            plt.ylim([-self.resolution.vertical//2, self.resolution.vertical//2])
            plt.xlim([0, self.resolution.horizontal])
            plt.plot(eval_xs, points)
            #plt.show()

        return eval_xs, points

class PolynomialFactory:
    """
    Helps create waveforms given a constant device resolution and voltages
    """

    def __init__(self, resolution: Resolution, voltage: VoltageBound) -> None:
        self.resolution = resolution
        self.voltage = voltage

    def interpolate_chebyshev(self, xs: np.ndarray, ys: np.ndarray) -> Polynomial:
        return Polynomial.chebyshev_from_points(xs, ys, self.resolution, self.voltage)

    def interpolate_spline(self, xs: np.ndarray, ys: np.ndarray, configuration) -> Polynomial:
        """
        For meaning of `configuration` see the documentation for `bc_type`:
        `https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.CubicSpline.html`
        """

        return Polynomial.spline_from_points(xs, ys, configuration, self.resolution, self.voltage)

    def interpolate_hermite_spline(self, xs: np.ndarray, ys: np.ndarray, dydx=None) -> Polynomial:
        return Polynomial.hermite_spline_from_points(xs, ys, self.resolution, self.voltage, dydx=dydx)

    def from_function(self, p) -> Polynomial:
        """
        If function p(x) is already defined correctly and you just want to lift it to a Polynomial class
        """
        return Polynomial(p, self.resolution, self.voltage)

    def random_chebyshev(self, degree) -> Polynomial:
        """
        Interpolate random voltages on chebyshev_nodes
        """
        rng = np.random.default_rng()
        xs = self.get_chebyshev_nodes(degree - 1)
        ys = rng.uniform(low=self.voltage.low, high=self.voltage.high, size=len(xs))

        return self.interpolate_chebyshev(xs, ys)

    def get_equispaced_points(self, inner_points_count: int):
        """
        Returns an array of equispaced points to be used for interpolation

        Parameters
        ----------

        inner_points_count: int
            number of inner interpolation points used for determining the waveform.
            Note: the fixed point at the start and end at Vcc doesn't count!

        """
        lower_bound, upper_bound = Polynomial.DOMAIN
        points = np.linspace(lower_bound, upper_bound, inner_points_count + 2)
        return points[1:-1]

    def get_chebyshev_nodes(self, inner_points_count: int):
        """
        Returns an array of points at Chebyshev nodes (of the first kind).
        Useful for interpolating Chebyshev polynomials in a stable way (avoiding oscillations)

        Parameters
        ----------

        inner_points_count: int
            number of inner interpolation points used for determining the waveform.
            Note: the fixed point at the start and end at Vcc doesn't count!

        """
        cheb1 = np.polynomial.chebyshev.chebpts1(inner_points_count + 2)
        points = np.interp(cheb1, [-1, 1], Polynomial.DOMAIN)

        return points[1:-1]
