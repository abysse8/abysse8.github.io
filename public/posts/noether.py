"""
Break the symmetry, lose the law (Noether).

Two unit-mass particles on a line, coupled by a spring, integrated with velocity
Verlet (symplectic). Break space-translation symmetry -> momentum drifts (energy
holds). Break time-translation symmetry -> energy drifts (momentum holds).

Pure numpy. Usage: python3 noether.py
"""
import numpy as np

def run(force, energy, T=60, dt=0.005):
    q = np.array([-1.0, 1.2]); p = np.array([0.3, -0.1]); P = []; E = []
    for i in range(int(T/dt)):
        t = i*dt
        P.append(p.sum()); E.append(energy(q, p, t))
        ph = p + force(q, t)*dt/2
        q = q + ph*dt
        p = ph + force(q, t + dt)*dt/2
    return np.array(P), np.array(E)

k, Om, w = 4.0, 1.5, 2.2
spread = lambda x: float(x.max() - x.min())

# A: translation-invariant + time-independent  -> P and E conserved
fA = lambda q, t: np.array([-k*(q[0]-q[1]), +k*(q[0]-q[1])])
eA = lambda q, p, t: 0.5*p@p + 0.5*k*(q[0]-q[1])**2
# B: fixed external trap breaks translation -> momentum not conserved
fB = lambda q, t: np.array([-k*(q[0]-q[1]) - Om**2*q[0], +k*(q[0]-q[1]) - Om**2*q[1]])
eB = lambda q, p, t: 0.5*p@p + 0.5*k*(q[0]-q[1])**2 + 0.5*Om**2*(q@q)
# C: time-dependent spring breaks time-translation -> energy not conserved
kt = lambda t: k*(1 + 0.5*np.sin(w*t))
fC = lambda q, t: np.array([-kt(t)*(q[0]-q[1]), +kt(t)*(q[0]-q[1])])
eC = lambda q, p, t: 0.5*p@p + 0.5*kt(t)*(q[0]-q[1])**2

if __name__ == "__main__":
    for name, f, e in [("both symmetries", fA, eA), ("no translation (trap)", fB, eB),
                       ("explicit time (H(t))", fC, eC)]:
        P, E = run(f, e)
        print(f"{name:24}  dP={spread(P):.2e}   dE={spread(E):.2e}")
