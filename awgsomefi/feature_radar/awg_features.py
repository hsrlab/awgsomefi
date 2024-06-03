import numpy as np
from dataclasses import dataclass

from awgsomefi.oceangen.polynomial import Polynomial

import matplotlib.pyplot as plt

@dataclass
class WShape:
    lean: bool
    midpeak: int
    delta: int

@dataclass
class UShape:
    pass

Shape = WShape | UShape

def extract_oob(points_orig, poly: Polynomial):
    """
    Counts number of points of polynomial outside of our allowed glitch range

    Separates result into a tuple of points outside of upper bound and lower bound
    """
    oobupper = np.count_nonzero(points_orig == poly.resolution.vertical//2)
    ooblower = np.count_nonzero(points_orig == -poly.resolution.vertical//2)

    return oobupper, ooblower


def extract_shape(points_orig, poly: Polynomial, plot=False) -> Shape:
    """
    Attempts to extract visual "shape" of polynomial according to its derivative.

    Returns result as a Shape type, which gives additional details to nature of shape.
    """
    deriv = poly.p.deriv(1)
    eval_xs = np.arange(poly.resolution.horizontal)
    points = deriv(eval_xs).astype(float)

    roots = deriv.roots()
    roots = roots.real[abs(roots.imag)<1e-5]

    lowerbound = np.argmax(points_orig < (poly.resolution.vertical//2 - 1));
    upperbound = np.argmax(np.flip(points_orig) < (poly.resolution.vertical//2 - 1));
    peaks = np.count_nonzero(((lowerbound < roots) & (roots < len(points_orig) - upperbound)))

    shape = None
    if peaks > 2:
        print("W-wave")
        left, mid, right = poly(roots[0]), poly(roots[1]), poly(roots[2])
        delta = abs(right - left)
        if left > right + 10000:
            print("Lean-left", delta)
        elif right > left + 10000:
            print("Lean-right", delta)
        else:
            print("Even", delta)

        shape = WShape(np.sign(right - left), max(abs(left - mid), abs(right - mid)), delta)

    else:
        print("U-wave")
        shape = UShape()

    if plot:
        plt.plot(eval_xs, points)
        plt.show()

    return shape
