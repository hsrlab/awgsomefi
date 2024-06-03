#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
from z3 import *


TOTAL_T = 10**9 # 10^6 microseconds

RES = 10**2
MAX_V = 2**128# Vertical Resultion
#MAX_SLEW = 10**100000 # 2500V/us Volts/second

cs = Ints('c1 c2 c3 c4')
e = Int('e')
c1, c2, c3, c4 = cs

samples = [int(x) for x in np.linspace(0, TOTAL_T, num=RES, dtype=int)]
#samples = [RealVal(x) for x in np.linspace(0, TOTAL_T, num=RES)]
#possible_y = set([RealVal(x) for x in np.linspace(0, MAX_V, num=2**16)])

n = int(10**9/6)
n2 = int(10**9 * 1/3)
s = Solver()

#s.add(c4*n2**4 + c3*n2**3 + c2*n2**2 + c1*n2 > MAX_V * 11/12)
#s.add(c4*n**4 + c3*n**3 + c2*n**2 + c1*n > MAX_V * 11/12)
s.add(e >= -5, e <= 5)
s.add(c4 > 0, TOTAL_T**4*c4 + TOTAL_T**3*c3 + TOTAL_T**2*c2 + TOTAL_T*c1 + e == 0) # ROOTS
s.add([And([c4*x**4 + c3*x**3 + c2*x**2 + c1*x >= 0, c4*x**4 + c3*x**3 + c2*x**2 + c1*x <= MAX_V]) for x in samples])
   # 4*c4*x**3 + 3*c3*x**2 + 2*c2*x + c1 > -MAX_SLEW, 4*c4*x**3 + 3*c3*x**2 + 2*c2*x + c1 < MAX_SLEW]) for x in samples])


# https://theory.stanford.edu/%7Enikolaj/programmingz3.html#sec-blocking-evaluations
def all_smt(s, initial_terms):
    def block_term(s, m, t):
        s.add(t != m.eval(t, model_completion=True))
    def fix_term(s, m, t):
        s.add(t == m.eval(t, model_completion=True))
    def all_smt_rec(terms):
        if sat == s.check():
           m = s.model()
           yield m
           for i in range(len(terms)):
               s.push()
               block_term(s, m, terms[i])
               for j in range(i):
                   fix_term(s, m, terms[j])
               yield from all_smt_rec(terms[i:])
               s.pop()   
    yield from all_smt_rec(list(initial_terms))


gen = all_smt(s, cs)

#xs = np.linspace(0, TOTAL_T, num=RES)
#xs = np.linspace(0, TOTAL_T, num=RES, dtype=int)
xs = samples
#xs = [x.as_fraction() for x in samples]
for m in gen:
    print(m)
    poly = [m.eval(c4*x**4 + c3*x**3 + c2*x**2 + c1*x) for x in samples]
    slew = [m.eval(4*c4*x**3 + 3*c3*x**2 + 2*c2*x + c1) for x in samples]
    plt.plot([xs[0], xs[-1]], 2*[MAX_V])
    plt.plot(xs, poly)
    plt.plot(xs, slew)
    plt.show()
