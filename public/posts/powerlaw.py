"""
The slow tail you can't fake.

A power-law tail 1/t cannot be built from a finite sum of decaying exponentials
(they peel off) — it needs a continuum of modes down to zero rate:
    1/t = integral_0^inf e^(-lambda t) d lambda.
Consequence via Green-Kubo: transport coefficient = integral of C(t). For the
hydrodynamic long-time tail C(t) ~ t^(-d/2), that integral converges in 3D but
diverges (log) in 2D -> no finite viscosity in two dimensions.

Pure numpy. Usage: python3 powerlaw.py
"""
import numpy as np
t = np.logspace(-1, 2.5, 300)
g = 1.0 / t                                    # the slow power-law tail

def fit_with_exponentials(K, t_fit=30):
    lam = np.logspace(-1.3, 1.0, K)            # K relaxation rates (fast modes)
    E = np.exp(-np.outer(t, lam))              # basis of decaying exponentials
    m = t <= t_fit
    a, *_ = np.linalg.lstsq(E[m], g[m], rcond=None)
    return E @ a

print("fit 1/t with K exponentials, then look past the fit window (t=100):")
i = np.argmin(np.abs(t - 100))
for K in (1, 3, 10):
    print(f"  K={K:2d}: 1/t={g[i]:.4f}  exp-fit={fit_with_exponentials(K)[i]:+.4f}  (collapses)")
print("exact: 1/t = ∫_0^inf e^(-λt) dλ  -> a continuum of modes with weight down to λ=0")

# Green-Kubo: transport coefficient = ∫ C(t) dt, for the long-time tail C~t^(-d/2)
def transport(power, T):
    tt = np.linspace(1.0, T, 4000); return np.trapezoid(tt**(-power), tt)
print("\ntransport integral ∫C(t)dt up to T=1e4:")
print(f"  3D  C~t^(-3/2): {transport(1.5, 1e4):.3f}  (converges -> finite viscosity)")
print(f"  2D  C~t^(-1)  : {transport(1.0, 1e4):.3f}  (diverges ~log T -> NO finite viscosity)")
