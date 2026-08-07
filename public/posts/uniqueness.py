"""
One initial condition, infinitely many futures.

dy/dx = 3 y^(2/3), y(0)=0 violates the Lipschitz condition at y=0, so Picard's
uniqueness theorem does not apply: y=0, y=x^3, and y=(x-a)^3 for any a>=0 all
solve it. A numerical solver returns just one -- and a 1e-15 change in the start
(below roundoff) flips the future. A Lipschitz equation is immune.

Pure numpy. Usage: python3 uniqueness.py
"""
import numpy as np
X = np.linspace(0, 5, 400)

def rk4(f, y0):
    y, out = y0, []
    for i in range(len(X)):
        out.append(y)
        if i == len(X) - 1: break
        h = X[i+1] - X[i]
        k1 = f(y); k2 = f(y + h/2*k1); k3 = f(y + h/2*k2); k4 = f(y + h*k3)
        y += h/6*(k1 + 2*k2 + 2*k3 + k4)
    return np.array(out)

f_nonlipschitz = lambda y: 3*np.sign(y)*abs(y)**(2/3)   # slope 2 y^(-1/3) -> unbounded at 0
f_lipschitz    = lambda y: 1.0 - y                       # bounded slope

if __name__ == "__main__":
    print("exact solutions of y'=3y^(2/3), y(0)=0:  y=0,  y=x^3,  y=(x-a)^3 for any a>=0")
    print(f"\nsolver value at x=5:")
    print(f"  non-Lipschitz, y0=0      -> {rk4(f_nonlipschitz, 0.0)[-1]:.3f}   (stays at zero)")
    print(f"  non-Lipschitz, y0=1e-15  -> {rk4(f_nonlipschitz, 1e-15)[-1]:.1f}   (takes off!)")
    print(f"  Lipschitz,     y0=0      -> {rk4(f_lipschitz, 0.0)[-1]:.4f}")
    print(f"  Lipschitz,     y0=1e-15  -> {rk4(f_lipschitz, 1e-15)[-1]:.4f}   (identical: uniqueness)")
