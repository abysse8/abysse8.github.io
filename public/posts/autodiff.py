"""
Autodiff isn't symbolic and isn't finite differences.

A ~20-line forward-mode autodiff (dual numbers: value + derivative) returns exact
derivatives (zero error, no step size). Finite differences fight a step-size
tradeoff and bottom out near 1e-11. And reverse-mode autodiff gets a full
n-dimensional gradient in ~2 passes vs 2n evaluations -- the reason backprop exists.

Pure numpy. Usage: python3 autodiff.py
"""
import numpy as np

class D:                                   # dual number: a = value, b = derivative
    def __init__(s, a, b=0.0): s.a, s.b = a, b
    def __add__(s, o): o = o if isinstance(o, D) else D(o); return D(s.a + o.a, s.b + o.b)
    def __mul__(s, o): o = o if isinstance(o, D) else D(o); return D(s.a * o.a, s.a * o.b + s.b * o.a)
    def __pow__(s, n): return D(s.a ** n, n * s.a ** (n - 1) * s.b)
def sin(x): return D(np.sin(x.a), np.cos(x.a) * x.b)
def exp(x): return D(np.exp(x.a), np.exp(x.a) * x.b)

f  = lambda x: sin(x ** 2) + exp(x) + x ** 3      # build it once from x -> it's in the graph
fv = lambda x: np.sin(x ** 2) + np.exp(x) + x ** 3

if __name__ == "__main__":
    x0 = 1.3
    true = 2 * x0 * np.cos(x0 ** 2) + np.exp(x0) + 3 * x0 ** 2
    ad = f(D(x0, 1.0)).b                           # seed derivative of x with 1
    print(f"autodiff  f'({x0}) = {ad:.15f}   error = {abs(ad - true):.1e}")
    best = min(abs((fv(x0 + h) - fv(x0 - h)) / (2 * h) - true) for h in np.logspace(-1, -14, 40))
    print(f"finite differences, best over all h: error = {best:.1e}  (autodiff: {abs(ad-true):.1e})")
    print("\ncost of a full n-dim gradient:  finite diff = 2n evals ;  reverse-mode autodiff = ~2, any n")
    for n in [1, 100, 10_000, 1_000_000]:
        print(f"  n={n:>9}:  finite diff {2*n:>10} evals   |   autodiff ~2")
