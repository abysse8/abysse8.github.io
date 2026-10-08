"""
Glue the line into a circle, the plane into a sphere -- and integrate over the result.

One thread, four checks (each one has an input that would make it fail):
  1. exp turns + into x.  e^{i theta} sends theta and theta + 2 pi to the same point:
     that identification (theta ~ theta + 2 pi) IS the circle  R / 2piZ.
  2. The Gaussian integral.  I^2 = int int e^{-x^2} e^{-y^2} = int int e^{-(x^2+y^2)}:
     the x -> + step makes the integrand depend on the radius only, and the 2 pi that
     appears is the length of the circle from step 1.  I = sqrt(pi).
     Falsifier: e^{-|x|^3} has no such trick -- its product is NOT radial.
     Bonus: the trapezoid rule on the whole line is exact up to aliasing (Poisson
     summation = periodising the line), predicted error 2 sqrt(pi) e^{-pi^2/h^2};
     shift the grid by a and the error picks up a factor cos(2 pi a / h).
  3. Plane + {infinity} = sphere (stereographic projection); far points crowd the pole.
  4. Knots.  A closed curve is a map out of the circle.  Gauss's linking integral is a
     double integral over circle x circle = the plane glued in both directions (a torus).
     Hopf link -> 1, unlink -> 0, torus link T(2,4) -> 2.  Periodic integrands make the
     trapezoid rule converge exponentially (Trefethen & Weideman, SIAM Review 2014).

Pure numpy + matplotlib.  Usage: python3 quotients.py   (writes quotients.png)
Sources: Gauss linking integral (Gauss 1833; Ricca & Nipoti 2011 for the history);
Gaussian integral via polar coordinates (Poisson); Poisson summation (any Fourier text).
"""
import numpy as np

TAU = 2 * np.pi


# ---------- 1. exp: (R, +) -> (circle, x), kernel 2piZ ----------
def wrap(theta):
    return np.exp(1j * theta)


def check_exp():
    a, b = 0.7, -2.3
    hom = abs(np.exp(a + b) - np.exp(a) * np.exp(b))                    # + becomes x
    same = abs(wrap(1.1) - wrap(1.1 + TAU * 3))                          # glued points
    diff = abs(wrap(1.1) - wrap(1.1 + 1.0))                              # NOT glued
    return hom, same, diff


# ---------- 2. Gaussian integral ----------
def trapz_line(f, L, h, a=0.0):
    # grid x_n = n h + a: centred on 0 when a = 0 (f is negligible beyond |x| = L)
    n = np.arange(-int(L / h) - 1, int(L / h) + 2)
    return h * f(n * h + a).sum()


def check_gaussian():
    g = lambda x: np.exp(-x ** 2)
    I = trapz_line(g, 12, 1e-3)
    # polar: int_0^{2pi} dtheta  int_0^inf e^{-r^2} r dr  = 2pi * 1/2
    r = np.linspace(0, 12, 200001)
    radial = np.trapezoid(np.exp(-r ** 2) * r, r)
    polar = TAU * radial
    # radial test: same radius, different angle
    p, q = (1.0, 0.0), (2 ** -0.5, 2 ** -0.5)
    gauss_radial = abs(g(p[0]) * g(p[1]) - g(q[0]) * g(q[1]))
    c = lambda x: np.exp(-np.abs(x) ** 3)
    cubic_radial = abs(c(p[0]) * c(p[1]) - c(q[0]) * c(q[1]))
    # Poisson prediction for the trapezoid rule on the whole line at step h
    hs = np.array([1.5, 1.25, 1.0, 0.8, 0.6, 0.5])
    err = np.array([abs(trapz_line(g, 40, h) - np.sqrt(np.pi)) for h in hs])
    pred = 2 * np.sqrt(np.pi) * np.exp(-np.pi ** 2 / hs ** 2)
    # shifted grid (a = h/3): Poisson predicts the error times cos(2 pi a / h) = -1/2
    h = 1.0
    shifted = trapz_line(g, 40, h, h / 3) - np.sqrt(np.pi)
    shifted_pred = 2 * np.sqrt(np.pi) * np.exp(-np.pi ** 2 / h ** 2) * np.cos(TAU / 3)
    return I, polar, gauss_radial, cubic_radial, hs, err, pred, shifted, shifted_pred


# ---------- 3. plane + {inf} -> sphere ----------
def to_sphere(x, y):
    s = x ** 2 + y ** 2
    return np.stack([2 * x, 2 * y, s - 1]) / (s + 1)


def to_plane(X, Y, Z):
    return X / (1 - Z), Y / (1 - Z)


def check_sphere():
    rng = np.random.default_rng(0)
    x, y = rng.normal(size=(2, 1000)) * 3
    P = to_sphere(x, y)
    on_sphere = np.max(np.abs(np.linalg.norm(P, axis=0) - 1))
    xb, yb = to_plane(*P)
    roundtrip = np.max(np.hypot(xb - x, yb - y))
    far = [np.linalg.norm(to_sphere(np.array(R), np.array(0.0)) - np.array([0, 0, 1])) for R in (10, 100, 1000)]
    return on_sphere, roundtrip, far


# ---------- 4. linking number over circle x circle ----------
def linking(c1, c2, N):
    t = np.arange(N) * TAU / N                     # periodic grid: no endpoint, equal weights
    T, S = np.meshgrid(t, t, indexing="ij")
    r1, d1 = c1(T)
    r2, d2 = c2(S)
    diff = r1 - r2
    num = np.einsum("i...,i...->...", diff, np.cross(d1, d2, axis=0))
    den = np.linalg.norm(diff, axis=0) ** 3
    return (num / den).sum() * (TAU / N) ** 2 / (4 * np.pi)


def circle(cx=0.0):
    return lambda t: (np.stack([cx + np.cos(t), np.sin(t), 0 * t]),
                      np.stack([-np.sin(t), np.cos(t), 0 * t]))


def circle_xz(cx):
    return lambda s: (np.stack([cx + np.cos(s), 0 * s, np.sin(s)]),
                      np.stack([-np.sin(s), 0 * s, np.cos(s)]))


def torus_curve(phase, R=2.0, r=1.0, q=2):
    # goes once the long way (phi = t) and q times around the tube (theta = q t + phase)
    def c(t):
        th = q * t + phase
        pos = np.stack([(R + r * np.cos(th)) * np.cos(t), (R + r * np.cos(th)) * np.sin(t), r * np.sin(th)])
        dth = q
        vel = np.stack([-r * np.sin(th) * dth * np.cos(t) - (R + r * np.cos(th)) * np.sin(t),
                        -r * np.sin(th) * dth * np.sin(t) + (R + r * np.cos(th)) * np.cos(t),
                        r * np.cos(th) * dth])
        return pos, vel
    return c


def trefoil(t):
    pos = np.stack([np.sin(t) + 2 * np.sin(2 * t), np.cos(t) - 2 * np.cos(2 * t), -np.sin(3 * t)])
    vel = np.stack([np.cos(t) + 4 * np.cos(2 * t), -np.sin(t) + 4 * np.sin(2 * t), -3 * np.cos(3 * t)])
    return pos, vel


def check_knots():
    hopf, unlink = (circle(), circle_xz(1.0)), (circle(), circle_xz(5.0))
    t24 = (torus_curve(0.0), torus_curve(np.pi))
    Ns = [8, 16, 32, 64, 128, 256]
    conv = {name: [linking(*pair, N) for N in Ns] for name, pair in
            [("Hopf", hopf), ("unlink", unlink), ("T(2,4)", t24)]}
    closed = np.linalg.norm(trefoil(np.array(0.0))[0] - trefoil(np.array(TAU))[0])
    return Ns, conv, closed


if __name__ == "__main__":
    hom, same, diff = check_exp()
    print("1. exp turns + into x")
    print(f"   |e^(a+b) - e^a e^b|              = {hom:.1e}")
    print(f"   |e^(i 1.1) - e^(i(1.1 + 6 pi))|   = {same:.1e}   (glued: theta ~ theta + 2 pi)")
    print(f"   |e^(i 1.1) - e^(i 2.1)|           = {diff:.3f}     (not glued -- this would be 0 if the check were vacuous)")

    I, polar, gr, cr, hs, err, pred, sh, shp = check_gaussian()
    print("\n2. Gaussian integral")
    print(f"   line integral   = {I:.15f}")
    print(f"   2 pi * 1/2      = {polar:.15f}   sqrt -> {np.sqrt(polar):.15f}")
    print(f"   sqrt(pi)        = {np.sqrt(np.pi):.15f}")
    print(f"   radial? e^-x^2 e^-y^2 at (1,0) vs (.71,.71): diff = {gr:.1e}")
    print(f"   radial? e^-|x|^3 product, same two points:    diff = {cr:.3f}  <- no polar trick")
    print("   trapezoid on the whole line, step h: measured error vs Poisson prediction 2 sqrt(pi) e^(-pi^2/h^2)")
    for h, e, p in zip(hs, err, pred):
        print(f"     h = {h:4.2f}   measured {e:.2e}   predicted {p:.2e}")
    print(f"   grid shifted by h/3 (h = 1): signed error {sh:+.3e}, predicted x cos(2pi/3): {shp:+.3e}")

    on, rt, far = check_sphere()
    print("\n3. plane + {inf} = sphere")
    print(f"   max | |P| - 1 |      = {on:.1e}   (images lie on the sphere)")
    print(f"   max round-trip error = {rt:.1e}")
    print(f"   distance to north pole for |p| = 10, 100, 1000: {', '.join(f'{d:.4f}' for d in far)}  (~ 2/|p|)")

    Ns, conv, closed = check_knots()
    print("\n4. linking number = (1/4 pi) double integral over circle x circle")
    print(f"   trefoil closes up: |gamma(0) - gamma(2 pi)| = {closed:.1e}")
    for name, vals in conv.items():
        print(f"   {name:7s} " + "  ".join(f"N={N}: {v:+.10f}" for N, v in zip(Ns, vals) if N in (8, 32, 128, 256)))

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(14, 3.8))

    ax = fig.add_subplot(1, 4, 1)
    th = np.linspace(-3 * TAU, 3 * TAU, 600)
    z = wrap(th)
    ax.scatter(z.real, z.imag, c=np.mod(th, TAU), cmap="twilight", s=6)
    for k in range(-3, 4):
        w = wrap(0.9 + TAU * k)
        ax.plot(w.real, w.imag, "ko", ms=6 - abs(k))
    ax.set_aspect("equal"); ax.set_title("line → circle: θ ~ θ+2π\n7 glued copies of θ=0.9 land on one point", fontsize=9)
    ax.set_xticks([]); ax.set_yticks([])

    ax = fig.add_subplot(1, 4, 2)
    ax.semilogy(hs, err, "o-", label="measured")
    ax.semilogy(hs, pred, "k--", label="Poisson: 2√π e^{-π²/h²}")
    ax.set_xlabel("step h"); ax.set_ylabel("|trapezoid − √π|")
    ax.set_title("∫e^{-x²}: error is aliasing\nfrom periodising the line", fontsize=9); ax.legend(fontsize=7)

    ax = fig.add_subplot(1, 4, 3, projection="3d")
    for c0 in np.linspace(-4, 4, 17):
        s = np.linspace(-40, 40, 800)
        ax.plot(*to_sphere(np.full_like(s, c0), s), lw=0.6, color="C0")
        ax.plot(*to_sphere(s, np.full_like(s, c0)), lw=0.6, color="C1")
    ax.scatter([0], [0], [1], color="k", s=20)
    ax.set_title("plane grid on the sphere\nevery line runs to ∞ = north pole", fontsize=9)
    ax.set_axis_off()

    ax = fig.add_subplot(1, 4, 4)
    for name, vals in conv.items():
        target = {"Hopf": 1, "unlink": 0, "T(2,4)": 2}[name]
        ax.semilogy(Ns, np.maximum(np.abs(np.abs(vals) - target), 1e-16), "o-", label=f"{name} → {target}")
    ax.set_xscale("log", base=2); ax.set_xlabel("grid points per circle N")
    ax.set_ylabel("| |Lk| − integer |")
    ax.set_title("linking integral over circle×circle\nperiodic ⇒ exponential convergence", fontsize=9)
    ax.legend(fontsize=7)

    fig.tight_layout()
    fig.savefig("quotients.png", dpi=150)
    print("\nwrote quotients.png")
