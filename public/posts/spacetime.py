"""
Falling is your clock taking the path of most elapsed time.  Curvature is the part of
gravity you cannot remove by falling.

Five checks (each one has an input that would make it fail):
  1. Equivalence principle -> clocks run at different rates at different heights.
     A rocket accelerating at g, no gravity anywhere, pure special relativity: pulses sent
     up from the floor arrive spread out by exactly 1 + g h / c^2.  Send them down: 1 - ...
     Pound-Rebka tower (22.5 m): g h / c^2 = 2.46e-15, measured 1965 to 1 %.
  2. Throw a ball up and catch it T later.  Of all paths between those two events, the
     one whose wristwatch shows the MOST elapsed time is the one it actually follows.
     Maximise proper time numerically -> recover the falling path (max height g T^2 / 8).
     Set g = 0 -> straight line.  Flip the clock gradient -> the path dips instead.
  3. GPS: clocks 20 200 km up run fast by 45.7 us/day (height) and slow by 7.2 us/day
     (speed): net +38.5 us/day.  Ashby, Living Reviews in Relativity 6, 1 (2003).
  4. Uniform g is NOT curvature: in free fall it vanishes.  What survives is tidal:
     two balls dropped side by side converge, two dropped one above the other separate.
     The tidal tensor at 400 km altitude has eigenvalues (-1, -1, +2) GM/r^3.
  5. Its trace is the field equation.  In vacuum: trace = 0.  Inside matter: trace =
     -4 pi G rho.  That is Newton's limit of Einstein's R_00 = 4 pi G (rho + 3p/c^2):
     mass-energy sets how much a small ball of free-falling dust shrinks.

Pure numpy + matplotlib.  Usage: python3 spacetime.py   (writes spacetime.png)
Sources: Pound & Rebka, PRL 4, 337 (1960); Pound & Snider, Phys. Rev. 140, B788 (1965);
Ashby (2003); Misner, Thorne & Wheeler, Gravitation (1973), ch. 1 and 11 (geodesic
deviation); Baez & Bunn, "The meaning of Einstein's equation", Am. J. Phys. 73, 644 (2005).
"""
import numpy as np

C = 299792458.0
GM = 3.986004418e14            # Earth, m^3/s^2
R_E = 6.371e6                  # mean radius, m


# ---------- 1. accelerating rocket, special relativity only (units c = 1) ----------
def rocket_redshift(g, h, n_pulses=20, dtau=0.05):
    # floor worldline (proper acceleration g):  t = sinh(g s)/g,  x = cosh(g s)/g
    # ceiling at fixed proper distance h above: proper acceleration 1/X with X = 1/g + h
    X = 1 / g + h
    s_emit = np.arange(n_pulses) * dtau
    if h > 0:   # floor -> ceiling, light moving +x:  x - t is conserved
        u = (np.cosh(g * s_emit) - np.sinh(g * s_emit)) / g
        # find ceiling proper time s where X (cosh - sinh)(s/X) = u, by bisection
        lo, hi = np.full_like(u, -50.0), np.full_like(u, 50.0)
        f = lambda s: X * np.exp(-s / X) - u
    else:       # emitter is the ceiling here: swap roles, send light down (-x): x + t conserved
        Xe, Xr = 1 / g + abs(h), 1 / g
        u = Xe * np.exp(s_emit / Xe)
        lo, hi = np.full_like(u, -50.0), np.full_like(u, 50.0)
        f = lambda s: u - Xr * np.exp(s / Xr)
    for _ in range(200):
        mid = (lo + hi) / 2
        go_right = f(mid) > 0
        lo, hi = np.where(go_right, mid, lo), np.where(go_right, hi, mid)
    s_recv = (lo + hi) / 2
    return np.diff(s_recv).mean() / dtau     # received spacing / emitted spacing


# ---------- 2. maximise proper time (units c = 1) ----------
# Metric of an observer held at height z in uniform gravity g (Rindler):
#   d tau^2 = (1 + g z)^2 dt^2 - dz^2
def proper_time(z, dt, g):
    zz = np.concatenate([[0.0], z, [0.0]])
    zm = (zz[1:] + zz[:-1]) / 2
    dz = np.diff(zz)
    return np.sum(np.sqrt((1 + g * zm) ** 2 * dt ** 2 - dz ** 2))


def grad(z, dt, g):
    zz = np.concatenate([[0.0], z, [0.0]])
    zm = (zz[1:] + zz[:-1]) / 2
    dz = np.diff(zz)
    L = np.sqrt((1 + g * zm) ** 2 * dt ** 2 - dz ** 2)
    dL_dzm = (1 + g * zm) * g * dt ** 2 / L
    dL_ddz = -dz / L
    # segment j depends on z_j (right end) and z_{j-1} (left end)
    gr = 0.5 * dL_dzm[:-1] + dL_ddz[:-1] + 0.5 * dL_dzm[1:] - dL_ddz[1:]
    return gr


def maximise(g, T=10.0, N=200):
    dt = T / N
    z = 0.3 * np.sin(np.pi * np.arange(1, N) / N)      # deliberately wrong start (a bump)
    for _ in range(30):                                  # Newton with finite-difference Hessian
        G0 = grad(z, dt, g)
        eps = 1e-6
        H = np.empty((N - 1, N - 1))
        for i in range(N - 1):
            zp = z.copy(); zp[i] += eps
            H[:, i] = (grad(zp, dt, g) - G0) / eps
        step = np.linalg.solve(H, -G0)
        z = z + step
        if np.abs(step).max() < 1e-13:
            break
    t = np.arange(1, N) * dt
    return t, z, dt


def exact_fall(t, g, T):
    # free particle at rest in the inertial frame, seen from the Rindler frame
    X0 = np.cosh(g * T / 2) / g
    return X0 / np.cosh(g * (t - T / 2)) - 1 / g


# ---------- 3. GPS ----------
def gps():
    r = 26_561.75e3
    v = np.sqrt(GM / r)
    grav = GM / C ** 2 * (1 / R_E - 1 / r) * 86400 * 1e6
    vel = -v ** 2 / (2 * C ** 2) * 86400 * 1e6
    return grav, vel, grav + vel


# ---------- 4-5. tidal tensor = what survives free fall ----------
def accel_earth(p, rho_inside=None):
    r = np.linalg.norm(p)
    if rho_inside is not None and r < R_E:                # uniform-density ball
        return -4 / 3 * np.pi * 6.674e-11 * rho_inside * p
    return -GM * p / r ** 3


def tidal(p, field, eps=1.0):
    # T_ij = d a_i / d x_j  (relative acceleration per metre of separation)
    T = np.empty((3, 3))
    for j in range(3):
        e = np.zeros(3); e[j] = eps
        T[:, j] = (field(p + e) - field(p - e)) / (2 * eps)
    return T


def drop_pair(offset, eig, t_end=600.0, dt=0.5):
    # two balls released at rest 400 km up, separated by `offset`; leapfrog on full gravity.
    # Prediction: the linear tidal (geodesic-deviation) equation  xi'' = eig * GM/r(t)^3 * xi
    # integrated along the first ball's actual fall (r shrinks ~1500 km in 600 s).
    p0 = np.array([R_E + 400e3, 0.0, 0.0])
    P = np.array([p0, p0 + offset]); V = np.zeros_like(P)
    xi, vxi = np.linalg.norm(offset), 0.0
    sep, pred = [xi], [xi]
    a = np.array([accel_earth(q) for q in P])
    for _ in range(int(t_end / dt)):
        V += 0.5 * dt * a; vxi += 0.5 * dt * eig * GM / np.linalg.norm(P[0]) ** 3 * xi
        P += dt * V; xi += dt * vxi
        a = np.array([accel_earth(q) for q in P])
        V += 0.5 * dt * a; vxi += 0.5 * dt * eig * GM / np.linalg.norm(P[0]) ** 3 * xi
        sep.append(np.linalg.norm(P[1] - P[0])); pred.append(xi)
    return np.arange(len(sep)) * dt, np.array(sep), np.array(pred)


if __name__ == "__main__":
    g = 0.1
    print("1. rocket accelerating at g, no gravity (c = 1, g = 0.1)")
    for h in (1.0, 2.0, -1.0):
        r = rocket_redshift(g, h)
        print(f"   pulses sent {'up' if h > 0 else 'down'} {abs(h):.0f}: spacing ratio = {r:.10f}   "
              f"predicted {(1 + g * h) if h > 0 else 1 / (1 + g * abs(h)):.10f}")
    print(f"   Pound-Rebka tower, h = 22.5 m: g h / c^2 = {9.81 * 22.5 / C ** 2:.3e}  "
          f"(Pound & Snider 1965: measured / predicted = 0.9990 +- 0.0076)")

    T = 10.0
    print("\n2. maximise wristwatch time between (t=0, z=0) and (t=10, z=0), c = 1")
    paths = {}
    for gg in (0.02, 0.0, -0.02):
        t, z, dt = maximise(gg, T)
        paths[gg] = (t, z)
        if gg != 0:
            ex = exact_fall(t, gg, T)
            print(f"   g = {gg:+.2f}: max height {z.max() if gg > 0 else z.min():+.6f}   exact free fall "
                  f"{ex.max() if gg > 0 else ex.min():+.6f}   Newton g T^2/8 = {gg * T ** 2 / 8:+.6f}   "
                  f"max path error {np.abs(z - ex).max():.1e}")
        else:
            print(f"   g =  0.00: max |height| {np.abs(z).max():.1e}   (straight line: no clock gradient, no fall)")
    gg = 0.02
    t, z = paths[gg]
    dt = T / (len(z) + 1)
    scales = np.linspace(0, 2, 41)
    taus = np.array([proper_time(a * z, dt, gg) for a in scales])
    print(f"   scale the path by a: tau(a=0) = {taus[0]:.10f}, tau(a=1) = {taus[20]:.10f}, tau(a=2) = {taus[40]:.10f}")
    print(f"   best a = {scales[np.argmax(taus)]:.2f}  (climbing gains clock rate, moving costs it; the fall balances them)")

    grav, vel, net = gps()
    print(f"\n3. GPS clock vs ground clock: height {grav:+.1f} us/day, speed {vel:+.1f} us/day, net {net:+.1f} us/day")
    print(f"   uncorrected, that is {net * 1e-6 * C / 1e3:.1f} km of ranging error per day")

    p = np.array([R_E + 400e3, 0.0, 0.0])
    r = np.linalg.norm(p)
    Tt = tidal(p, accel_earth)
    eig = np.sort(np.linalg.eigvalsh((Tt + Tt.T) / 2))
    print(f"\n4. tidal tensor 400 km up, in units of GM/r^3 = {GM / r ** 3:.3e} s^-2:")
    print(f"   eigenvalues {np.round(eig / (GM / r ** 3), 5)}   (predicted -1, -1, +2)")
    Tu = tidal(p, lambda q: np.array([-9.81, 0.0, 0.0]))
    print(f"   uniform field g = 9.81: max |tidal| = {np.abs(Tu).max():.1e}  <- removable by falling: no curvature")
    t1, s_side, p_side = drop_pair(np.array([0.0, 10.0, 0.0]), -1)
    t2, s_up, p_up = drop_pair(np.array([10.0, 0.0, 0.0]), +2)
    print("   two balls 10 m apart, 600 s of free fall (full-gravity simulation vs linear tidal equation):")
    print(f"     side by side:        {s_side[-1]:.4f} m   tidal prediction {p_side[-1]:.4f} m")
    print(f"     one above the other: {s_up[-1]:.4f} m   tidal prediction {p_up[-1]:.4f} m")

    rho = 3 * GM / 6.674e-11 / (4 * np.pi * R_E ** 3)
    inside = tidal(np.array([R_E / 2, 0, 0]), lambda q: accel_earth(q, rho), eps=1.0)
    print(f"\n5. trace of the tidal tensor (= Newton's limit of R_00, up to sign and c^2):")
    print(f"   vacuum, 400 km up:          {np.trace(Tt):+.2e} s^-2   (vs single eigenvalue {GM / r ** 3:.2e})")
    print(f"   inside uniform Earth (rho = {rho:.0f} kg/m^3): {np.trace(inside):+.4e}   -4 pi G rho = {-4 * np.pi * 6.674e-11 * rho:+.4e}")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 4, figsize=(15, 3.8))

    for gg, col in ((0.02, "C0"), (0.0, "k"), (-0.02, "C3")):
        t, z = paths[gg]
        ax[0].plot(t, z, color=col, label=f"clock gradient g = {gg:+.2f}")
    ax[0].plot(paths[0.02][0], exact_fall(paths[0.02][0], 0.02, T), "y--", lw=1.2, label="exact free fall")
    ax[0].set_xlabel("t"); ax[0].set_ylabel("height z")
    ax[0].set_title("path of maximum wristwatch time\nbetween two fixed events", fontsize=9); ax[0].legend(fontsize=7)

    ax[1].plot(scales, (taus - taus[0]) * 1e3, "o-", ms=3)
    ax[1].axvline(1, color="k", lw=0.8)
    ax[1].set_xlabel("path height × a  (a = 1 is the fall)"); ax[1].set_ylabel("τ − τ(stay put)  (×10⁻³)")
    ax[1].set_title("too low: clock in slow region\ntoo high: clock pays for speed", fontsize=9)

    ax[2].bar(["height", "speed", "net"], [grav, vel, net], color=["C0", "C3", "k"])
    ax[2].axhline(0, color="k", lw=0.6)
    ax[2].set_ylabel("µs per day vs ground")
    ax[2].set_title("GPS satellite clocks\n(Ashby 2003: +45.7, −7.2, +38.5)", fontsize=9)

    ax[3].plot(t1, s_side, label="side by side: converge")
    ax[3].plot(t2, s_up, label="one above other: separate")
    ax[3].plot(t1, p_side, "k:", lw=1)
    ax[3].plot(t2, p_up, "k:", lw=1, label="tidal-tensor prediction")
    ax[3].set_xlabel("seconds of free fall"); ax[3].set_ylabel("separation (m)")
    ax[3].set_title("curvature = what falling can't remove\n(eigenvalues −1, −1, +2 · GM/r³)", fontsize=9)
    ax[3].legend(fontsize=7)

    fig.tight_layout()
    fig.savefig("spacetime.png", dpi=150)
    print("\nwrote spacetime.png")
