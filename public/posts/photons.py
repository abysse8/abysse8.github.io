"""
A photon is one step up the energy ladder of one mode of the electromagnetic field.

"Mode" = one way the field in a box can oscillate (a standing wave pattern), like one
string on a guitar.  Each mode behaves as a harmonic oscillator.  Classically its energy
can be anything; quantum mechanically only 0, hf, 2hf, ...  One rung = one photon.

Four checks (each one has an input that would make it fail):
  1. Count the modes in a box by brute force (integer triples) and compare with the
     formula  N(f) = 8 pi V f^3 / (3 c^3).  Ratio -> 1.
  2. Give every mode the classical average energy kT and the total energy diverges as the
     cutoff frequency grows (Rayleigh-Jeans, the "ultraviolet catastrophe").  Make the
     energy come in steps of hf and the total converges: Stefan-Boltzmann's sigma computed
     from h, c, k alone vs the CODATA value.  Set h -> 0 and it diverges again.
  3. Einstein (1909): the fluctuation of the photon number in one thermal mode is
         Var(n) = n  +  n^2
                  ^       ^
           particle term   wave term
     Computed by summing the Boltzmann distribution AND by kT^2 dE/dT (the thermodynamic
     route Einstein used).  Light is neither: it has both terms.
  4. Photon counting (Hanbury Brown & Twiss 1956): thermal light g2 = 2, laser light
     g2 = 1.  Monte Carlo with bootstrap error bars.

Pure numpy + matplotlib.  Usage: python3 photons.py   (writes photons.png)
Sources: Planck 1900; Einstein, Phys. Z. 10, 185 (1909); Hanbury Brown & Twiss, Nature 177,
27 (1956); Loudon, The Quantum Theory of Light (3rd ed., 2000), ch. 1 and 3; CODATA 2018.
"""
import numpy as np

h, c, k = 6.62607015e-34, 299792458.0, 1.380649e-23        # exact SI values since 2019
SIGMA_CODATA = 5.670374419e-8                               # W m^-2 K^-4


# ---------- 1. counting modes in a cube ----------
def count_modes(R):
    # standing waves in a cube of side L: k = pi n / L, n = (nx, ny, nz) positive integers,
    # frequency f = c |n| / 2L.  Count |n| <= R, x2 polarisations.
    n = np.arange(1, int(R) + 1)
    nx, ny = np.meshgrid(n, n, indexing="ij")
    rem = R ** 2 - nx ** 2 - ny ** 2                        # room left for nz
    nz_max = np.floor(np.sqrt(np.clip(rem, 0, None)))
    return 2 * nz_max[rem >= 1].sum()


def check_modes():
    Rs = np.array([10, 20, 50, 100, 200, 400])
    counted = np.array([count_modes(R) for R in Rs])
    formula = np.pi * Rs ** 3 / 3                           # = 8 pi V f^3 / 3 c^3 with R = 2 L f / c
    return Rs, counted, formula


# ---------- 2. energy per mode: continuous vs stepped ----------
def mean_energy_by_sum(f, T, nmax=4000):
    # average of E_n = n h f over Boltzmann weights exp(-E_n / kT), summed directly
    x = h * f / (k * T)
    n = np.arange(nmax)[:, None]
    w = np.exp(-n * x)
    return (n * h * f * w).sum(0) / w.sum(0)


def planck_mean(f, T):
    return h * f / np.expm1(h * f / (k * T))


def energy_density(T, fmax, hh=h, nf=200001):
    f = np.linspace(fmax / nf, fmax, nf)
    modes_per_vol = 8 * np.pi * f ** 2 / c ** 3             # modes per m^3 per Hz
    if hh == 0:
        E = k * T * np.ones_like(f)
    else:
        E = hh * f / np.expm1(hh * f / (k * T))
    return np.trapezoid(modes_per_vol * E, f)


def check_energy(T=5772.0):
    f = np.array([1e13, 1e14, 5e14, 1e15])
    direct = mean_energy_by_sum(f, T)
    formula = planck_mean(f, T)
    fmax_list = [1e15, 2e15, 4e15, 8e15]
    rj = [energy_density(T, fm, hh=0) for fm in fmax_list]
    pl = [energy_density(T, fm) for fm in fmax_list]
    sigma = c * pl[-1] / (4 * T ** 4)
    # "h -> 0" sweep: shrink h, sigma grows without bound at fixed cutoff
    h_sweep = [h, h / 10, h / 100]
    sig_h = [c * energy_density(T, 8e15, hh=hh) / (4 * T ** 4) for hh in h_sweep]
    # Wien peak of the spectrum per unit frequency: f^3 / (e^x - 1) peaks at x = 2.8214
    ff = np.linspace(1e12, 2e15, 400001)
    peak_x = h * ff[np.argmax(ff ** 3 / np.expm1(h * ff / (k * T)))] / (k * T)
    return f, direct, formula, fmax_list, rj, pl, sigma, sig_h, peak_x


# ---------- 3. Einstein's fluctuation formula ----------
def check_fluctuations():
    xs = np.array([0.05, 0.5, 1.0, 2.0, 5.0])                # hf / kT
    rows = []
    for x in xs:
        n = np.arange(20000)
        p = np.exp(-n * x); p /= p.sum()
        mean = (n * p).sum()
        var = (n ** 2 * p).sum() - mean ** 2
        # thermodynamic route: Var(E) = k T^2 dE/dT, in units of (hf)^2.  With x = hf/kT,
        # T d/dT = -x d/dx, so Var(n) = -dn/dx.  Central difference:
        d = 1e-5
        nbar = lambda y: 1 / np.expm1(y)
        thermo = -(nbar(x + d) - nbar(x - d)) / (2 * d)
        rows.append((x, mean, var, mean + mean ** 2, thermo))
    return rows


# ---------- 4. photon counting statistics ----------
def g2(counts):
    n = counts.astype(float)
    return (n * (n - 1)).mean() / n.mean() ** 2


def check_counting(nbar=4.0, N=200000, B=200, seed=1):
    rng = np.random.default_rng(seed)
    thermal = rng.geometric(1 / (1 + nbar), N) - 1           # Bose-Einstein = geometric, mean nbar
    laser = rng.poisson(nbar, N)
    out = {}
    for name, s in (("thermal", thermal), ("laser", laser)):
        boots = [g2(s[rng.integers(0, N, N)]) for _ in range(B)]
        out[name] = (g2(s), *np.percentile(boots, [2.5, 97.5]), s)
    return out


if __name__ == "__main__":
    Rs, counted, formula = check_modes()
    print("1. modes in a cube: brute-force count vs 8 pi V f^3 / 3 c^3")
    for R, n, fm in zip(Rs, counted, formula):
        print(f"   |n| <= {R:4d}   counted {n:14.0f}   formula {fm:14.0f}   ratio {n / fm:.5f}   (1 - ratio) x R = {(1 - n / fm) * R:.3f}")
    print("   the shortfall is the walls: Weyl's law for a box predicts (1 - ratio) x R -> 9/4 = 2.250")

    f, direct, formula_e, fmax_list, rj, pl, sigma, sig_h, peak_x = check_energy()
    print("\n2. energy per mode at T = 5772 K (the Sun's surface)")
    for fi, d, p in zip(f, direct, formula_e):
        print(f"   f = {fi:.0e} Hz   summed {d / (k * 5772):.6f} kT   Planck formula {p / (k * 5772):.6f} kT   classical 1 kT")
    print("   total energy density (J/m^3) as the frequency cutoff grows:")
    for fm, a, b in zip(fmax_list, rj, pl):
        print(f"     cutoff {fm:.0e} Hz   classical {a:10.3e}   stepped {b:10.3e}")
    print(f"   sigma from h, c, k  = {sigma:.6e}   CODATA {SIGMA_CODATA:.6e}   rel. diff {abs(sigma / SIGMA_CODATA - 1):.1e}")
    print(f"   same, h/10 and h/100 (cutoff 8e15): {sig_h[1]:.3e}, {sig_h[2]:.3e}  <- shrink the step, lose the answer")
    print(f"   spectrum peak at hf/kT = {peak_x:.4f}  (Wien: 2.8214)")

    print("\n3. Einstein 1909: Var(n) = n + n^2  (particle + wave)")
    for x, mean, var, pred, thermo in check_fluctuations():
        print(f"   hf/kT = {x:4.2f}   n = {mean:8.4f}   Var summed {var:10.4f}   n+n^2 {pred:10.4f}   "
              f"kT^2 dE/dT {thermo:10.4f}   particle share {mean / var:.2f}")

    res = check_counting()
    print("\n4. photon counting, mean 4 photons per window, 200 000 windows")
    for name, (g, lo, hi, _) in res.items():
        print(f"   {name:7s}  g2 = {g:.4f}   95% CI [{lo:.4f}, {hi:.4f}]   (theory {'2' if name == 'thermal' else '1'})")
    lam = 633e-9
    print(f"\n   scale: one 633 nm photon = {h * c / lam / 1.602176634e-19:.3f} eV; a 1 mW HeNe laser emits {1e-3 / (h * c / lam):.2e} photons/s")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 4, figsize=(15, 3.8))

    ax[0].semilogx(Rs, counted / formula, "o-")
    ax[0].axhline(1, color="k", lw=0.8)
    ax[0].set_xlabel("radius in mode-number space (= 2Lf/c)"); ax[0].set_ylabel("counted / formula")
    ax[0].set_title("standing waves in a box:\ncount them, get f³", fontsize=9)

    T = 5772.0
    ff = np.linspace(1e12, 2.5e15, 2000)
    dens = 8 * np.pi * ff ** 2 / c ** 3
    ax[1].plot(ff / 1e15, dens * planck_mean(ff, T) * 1e15, label="energy in steps of hf (Planck)")
    ax[1].plot(ff / 1e15, dens * k * T * 1e15, "k--", label="continuous energy (kT per mode)")
    ax[1].set_ylim(0, 1.6 * (dens * planck_mean(ff, T)).max() * 1e15)
    ax[1].set_xlabel("frequency (PHz)"); ax[1].set_ylabel("energy density (J m⁻³ PHz⁻¹)")
    ax[1].set_title("T = 5772 K: steps tame the\nultraviolet catastrophe", fontsize=9); ax[1].legend(fontsize=7)

    nb = np.logspace(-2, 2, 200)
    ax[2].loglog(nb, nb + nb ** 2, "k", label="total Var(n)")
    ax[2].loglog(nb, nb, "C0--", label="particle term n̄")
    ax[2].loglog(nb, nb ** 2, "C1--", label="wave term n̄²")
    for x, mean, var, _, _ in check_fluctuations():
        ax[2].plot(mean, var, "ro", ms=4)
    ax[2].set_xlabel("mean photons per mode n̄"); ax[2].set_ylabel("Var(n)")
    ax[2].set_title("Einstein 1909: light fluctuates\nlike particles AND waves", fontsize=9); ax[2].legend(fontsize=7)

    bins = np.arange(0, 25)
    for name, col in (("thermal", "C1"), ("laser", "C0")):
        ax[3].hist(res[name][3], bins=bins, density=True, alpha=0.5, color=col,
                   label=f"{name}: g2 = {res[name][0]:.3f}")
    ax[3].set_xlabel("photons counted per window"); ax[3].set_ylabel("probability")
    ax[3].set_title("same mean (4), different light:\nbunched vs random arrivals", fontsize=9); ax[3].legend(fontsize=7)

    fig.tight_layout()
    fig.savefig("photons.png", dpi=150)
    print("\nwrote photons.png")
