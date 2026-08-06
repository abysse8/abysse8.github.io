"""
Timing is the information a rate code throws away.

Two encodings of a stimulus s, two readouts (spike count vs spike timing),
mutual information (bits) of each. When s is in the RATE, count reads it. When s
is in the TIMING (count decoupled from s), the count readout gets ~0 bits — blind.

Pure numpy. Usage: python3 timing.py
"""
import numpy as np
rng = np.random.default_rng(7)

def MI(sd, yd, sbins, ybins):                # mutual info (bits) by binning
    Pxy, _, _ = np.histogram2d(sd, yd, bins=[sbins, ybins]); Pxy /= Pxy.sum()
    Px = Pxy.sum(1, keepdims=True); Py = Pxy.sum(0, keepdims=True); m = Pxy > 0
    return float(np.sum(Pxy[m] * np.log2(Pxy[m] / (Px * Py)[m])))

N, W, sig = 300_000, 1.0, 0.10
s = rng.uniform(0, 1, N); sb = np.linspace(0, 1, 21)

def rate_code(W_win):                        # stimulus sets the RATE
    rho = 2 + 18*s
    n  = rng.poisson(rho * W_win)            # count encodes s
    t1 = np.minimum(rng.exponential(1/rho), W_win)
    return MI(s, n, sb, np.arange(0, n.max()+2)-0.5), MI(s, t1, sb, np.linspace(0, W_win, 41))

def timing_code(mu0):                        # stimulus sets the TIMES; count decoupled from s
    n = np.clip(rng.poisson(mu0, N), 1, None)             # count independent of s
    meant = s*W + rng.standard_normal(N)*sig/np.sqrt(n)    # mean spike time encodes s
    return MI(s, n, sb, np.arange(0, n.max()+2)-0.5), MI(s, meant, sb, np.linspace(-0.2, 1.2, 41))

if __name__ == "__main__":
    print("INFO IN THE RATE:   μ   count-MI   timing-MI")
    for W_win in [0.1, 0.5, 2.0]:
        c, t = rate_code(W_win); print(f"   {np.mean((2+18*0.5)*W_win):6.1f}   {c:.3f}     {t:.3f}")
    print("\nINFO IN THE TIMING (count decoupled from s):   μ   count-MI   timing-MI")
    for mu0 in [1, 4, 16]:
        c, t = timing_code(mu0); print(f"   {mu0:6.1f}   {c:.3f}     {t:.3f}   <- count is blind")
