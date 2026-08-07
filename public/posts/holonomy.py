"""
The field strength is a commutator: F = [D_mu, D_nu].

Parallel-transport a vector around a closed loop on a unit sphere and it returns
rotated by exactly the enclosed curvature (area). On a flat plane, zero. That
leftover rotation (the holonomy) is the failure of the two transport directions
to commute — the field strength / curvature.

Pure numpy. Usage: python3 holonomy.py
"""
import numpy as np
u = lambda v: v/np.linalg.norm(v)
def rodrigues(v, k, th): return v*np.cos(th) + np.cross(k, v)*np.sin(th) + k*np.dot(k, v)*(1-np.cos(th))
def transport(v, p, q):                        # parallel transport v as base moves p->q on sphere
    p, q = u(p), u(q); ax = np.cross(p, q); s = np.linalg.norm(ax)
    return v if s < 1e-12 else rodrigues(v, ax/s, np.arctan2(s, np.dot(p, q)))
sph = lambda th, ph: np.array([np.sin(th)*np.cos(ph), np.sin(th)*np.sin(ph), np.cos(th)])

def holonomy(th1, th2, ph1, ph2, n=400):
    P = ([sph(th1, ph) for ph in np.linspace(ph1, ph2, n)] +
         [sph(th, ph2) for th in np.linspace(th1, th2, n)] +
         [sph(th2, ph) for ph in np.linspace(ph2, ph1, n)] +
         [sph(th, ph1) for th in np.linspace(th2, th1, n)])
    p0 = P[0]
    e1 = u(np.array([np.cos(th1)*np.cos(ph1), np.cos(th1)*np.sin(ph1), -np.sin(th1)]))
    e2 = np.cross(p0, e1); v = e1.copy()
    for i in range(len(P)-1): v = transport(v, P[i], P[i+1])
    v = transport(v, P[-1], P[0])
    return float(np.arctan2(np.dot(v, e2), np.dot(v, e1)))

area = lambda th1, th2, ph1, ph2: (ph2-ph1)*(np.cos(th1)-np.cos(th2))  # solid angle on unit sphere

if __name__ == "__main__":
    print("enclosed area | holonomy (rotation) | ratio   [unit sphere, curvature K=1]")
    for th2 in [0.5, 0.8, 1.1, 1.4, 1.7, 2.0]:
        A = area(0.4, th2, 0.0, 1.2); H = holonomy(0.4, th2, 0.0, 1.2)
        print(f"  {A:.3f}         {H:+.3f}            {H/A:+.3f}")
    print("flat plane: holonomy = 0 for any loop (transports commute -> no field strength)")
