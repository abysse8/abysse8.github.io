"""
Gradient descent is optimization at zero temperature.

Gradient descent + noise (Langevin) samples the Gibbs distribution exp(-L/T)
(verified to ~96%). As T->0 the distribution collapses to the global minimizer;
greedy descent (T=0) can get stuck in a local minimum that a little temperature escapes.

Pure numpy. Usage: python3 thermodynamics.py
"""
import numpy as np
rng = np.random.default_rng(5)
L  = lambda x: x**4 - 3*x**2 + 0.5*x        # double well (asymmetric)
dL = lambda x: 4*x**3 - 6*x + 0.5
xg = np.linspace(-2.3, 2.3, 400); Lg = L(xg)

def gibbs(T):
    p = np.exp(-(Lg - Lg.min())/T); return p/np.trapezoid(p, xg)

def langevin(T, walkers=4000, steps=20000, eta=0.004):
    x = rng.uniform(-2.2, 2.2, walkers)
    for _ in range(steps):
        x += -eta*dL(x) + np.sqrt(2*eta*T)*rng.standard_normal(walkers)
    return x

def gd(x0, eta=0.01, steps=3000):            # greedy gradient descent (T=0)
    x = x0
    for _ in range(steps): x -= eta*dL(x)
    return x

if __name__ == "__main__":
    # Langevin + noise samples Gibbs?
    s = langevin(1.0); h, e = np.histogram(s, 50, (-2.3, 2.3), density=True)
    ctr = 0.5*(e[:-1]+e[1:]); pg = np.interp(ctr, xg, gibbs(1.0))
    TV = 0.5*np.trapezoid(np.abs(h - pg), ctr)
    print(f"Langevin @T=1.0 vs Gibbs e^(-L/T): agreement {100*(1-TV):.0f}%")
    # global vs local minimum, and greedy descent getting stuck
    gi = np.argmin(Lg); li = np.argmin(np.where(xg > 0.4, Lg, 1e9))
    print(f"global min L={Lg[gi]:.2f} @x={xg[gi]:+.2f} | local min L={Lg[li]:.2f} @x={xg[li]:+.2f}")
    print(f"greedy GD (T=0) from x=+1.2 -> L={L(gd(1.2)):.2f} (stuck); "
          f"low-T Gibbs finds L~{np.trapezoid(L(xg)*gibbs(0.08), xg):.2f}")
