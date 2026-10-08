"""
An op-amp is the one entry that breaks the symmetry of the circuit matrix.

A circuit at rest is a balance: at every node, current in = current out (Kirchhoff's
current law, which is charge conservation).  Written for all nodes at once it is a
matrix equation  G v = i  -- G holds the conductances, v the node voltages.

Five checks (each one has an input that would make it fail):
  1. Resistors alone give a SYMMETRIC G, and every node voltage is a weighted average
     of its neighbours -> no node can exceed the source (discrete maximum principle).
     2000 random resistor networks: max node voltage / source <= 1.
  2. An op-amp adds one row  v_out = A (v+ - v-)  that is NOT symmetric.  That one
     asymmetric entry is what lets a node exceed the source: inverting amp, gain -10.
     As A -> infinity the gain -> -Rf/Rin, error = (1 + Rf/Rin)/A  (measured vs formula).
  3. The extra power has a channel: the supply rail.  Accounting to the milliwatt.
  4. Carver Mead's transconductance amplifier: the input stage is a differential pair,
     I_out = I_b tanh(kappa dV / 2 U_T).  Linear only over ~ +-13 mV (1 %).  Put it in a
     follower and the closed loop is linear over volts -- feedback linearises the device.
  5. Dynamics.  A real op-amp has one slow pole.  Bandwidth = GBW / noise gain (measured).
     Swap the inputs (positive feedback): the matrix STILL solves to a finite answer,
     but the equilibrium is unstable -- the simulation runs to the rail.

Pure numpy + matplotlib.  Usage: python3 opamp.py   (writes opamp.png)
Sources: modified nodal analysis -- Ho, Ruehli & Brennan, IEEE Trans. Circuits Syst. 1975
(the formulation inside SPICE); transconductance amplifier -- Mead, Analog VLSI and Neural
Systems (1989), ch. 5; maximum principle for resistor networks -- Doyle & Snell, Random
Walks and Electric Networks (1984).
"""
import numpy as np


# ---------- a tiny modified-nodal-analysis (MNA) solver ----------
# Unknowns: node voltages 1..n (node 0 is ground), then one current per voltage source
# and per op-amp output.  Each component "stamps" a few numbers into the matrix.
class Circuit:
    def __init__(self, n_nodes):
        self.n = n_nodes
        self.R, self.V, self.E = [], [], []          # resistors, sources, op-amps

    def resistor(self, a, b, ohms):
        self.R.append((a, b, 1.0 / ohms))

    def vsource(self, a, volts):                     # node a held at `volts` above ground
        self.V.append((a, volts))

    def opamp(self, plus, minus, out, gain):         # v_out = gain * (v_plus - v_minus)
        self.E.append((plus, minus, out, gain))

    def matrix(self):
        m = self.n + len(self.V) + len(self.E)
        M = np.zeros((m, m), dtype=complex)
        rhs = np.zeros(m, dtype=complex)
        idx = lambda node: node - 1                  # ground (0) is dropped

        for a, b, g in self.R:                       # KCL stamps: symmetric by construction
            for p, q, s in ((a, a, g), (b, b, g), (a, b, -g), (b, a, -g)):
                if p and q:
                    M[idx(p), idx(q)] += s
        k = self.n
        for a, volts in self.V:
            M[idx(a), k] += 1; M[k, idx(a)] += 1     # symmetric pair
            rhs[k] = volts; k += 1
        for plus, minus, out, A in self.E:
            M[idx(out), k] += 1                      # op-amp injects current at out
            M[k, idx(out)] += 1                      # row: v_out - A v+ + A v- = 0
            if plus:  M[k, idx(plus)] -= A
            if minus: M[k, idx(minus)] += A          # <- these two entries have no mirror
            k += 1
        return M, rhs

    def solve(self):
        M, rhs = self.matrix()
        x = np.linalg.solve(M, rhs)
        return x[:self.n], x[self.n:]


def inverting(Rin, Rf, A, Vs=1.0, RL=1e3, positive=False):
    # node 1: input, node 2: op-amp minus input, node 3: output.  plus input at ground.
    c = Circuit(3)
    c.vsource(1, Vs)
    c.resistor(1, 2, Rin)
    c.resistor(2, 3, Rf)
    c.resistor(3, 0, RL)
    if positive:
        c.opamp(2, 0, 3, A)                          # inputs swapped -> positive feedback
    else:
        c.opamp(0, 2, 3, A)
    return c


# ---------- 1. passive networks obey the maximum principle ----------
def check_passive(trials=2000, n=8, seed=0):
    rng = np.random.default_rng(seed)
    worst, asym = 0.0, 0.0
    for _ in range(trials):
        c = Circuit(n)
        c.vsource(1, 1.0)
        for a in range(0, n + 1):                    # random graph incl. ground, always connected
            for b in range(a + 1, n + 1):
                if rng.random() < 0.4 or b == a + 1:
                    c.resistor(a, b, 10 ** rng.uniform(1, 5))
        v, _ = c.solve()
        worst = max(worst, v.real[1:].max())          # free nodes only (node 1 IS the source)
        M, _ = c.matrix()
        asym = max(asym, np.abs(M - M.T).max())
    return worst, asym


# ---------- 2. inverting amplifier: gain vs open-loop gain A ----------
def check_gain(Rin=1e3, Rf=1e4):
    As = 10.0 ** np.arange(1, 8)
    gain = np.array([inverting(Rin, Rf, A).solve()[0][2].real for A in As])
    exact = -(Rf / Rin) / (1 + (1 + Rf / Rin) / As)
    M, _ = inverting(Rin, Rf, 1e5).matrix()
    return As, gain, exact, np.abs(M - M.T).max()


# ---------- 3. where the power comes from ----------
def check_power(Rin=1e3, Rf=1e4, RL=1e3, Vs=1.0, rail=15.0):
    v, cur = inverting(Rin, Rf, 1e6, Vs, RL).solve()
    v1, v2, v3 = v.real
    i_out = -cur[1].real                             # current the op-amp sources into node 3
    p_in = Vs * (v1 - v2) / Rin                      # what the signal source delivers
    p_load = v3 ** 2 / RL
    p_rf = (v2 - v3) ** 2 / Rf
    p_rail = rail * abs(i_out)                       # output swings negative: pulled from -15 V
    p_stage = (rail - abs(v3)) * abs(i_out)          # burned in the output transistor
    return p_in, p_load, p_rf, p_rail, p_stage


# ---------- 4. Mead's transconductance amplifier ----------
UT, KAPPA, VE = 0.02585, 0.7, 50.0                   # thermal voltage, gate coupling, Early voltage
A_MEAD = VE * KAPPA / (2 * UT)                       # small-signal voltage gain (~677)


def mead_open(dv):
    return np.tanh(KAPPA * dv / (2 * UT))            # I_out / I_bias


def mead_follower(vin):
    # solve v_out = VE * tanh(kappa (vin - v_out) / 2UT) by bisection (monotone in v_out)
    lo, hi = np.full_like(vin, -VE), np.full_like(vin, VE)
    for _ in range(200):
        mid = (lo + hi) / 2
        f = mid - VE * np.tanh(KAPPA * (vin - mid) / (2 * UT))
        lo, hi = np.where(f > 0, lo, mid), np.where(f > 0, mid, hi)
    return (lo + hi) / 2


def nonlinearity(x, y):
    p = np.polyfit(x, y, 1)
    return np.abs(y - np.polyval(p, x)).max() / np.ptp(y)


def check_mead():
    dv = np.linspace(-0.0128, 0.0128, 201)
    i = mead_open(dv)
    ol = nonlinearity(dv, i)
    droop = mead_open(np.array(0.0128)) / (KAPPA * 0.0128 / (2 * UT))   # actual / small-signal line
    vin = np.linspace(0.0, 2.0, 201)
    vout = mead_follower(vin)
    cl = nonlinearity(vin, vout)
    track = (vin - vout)[-1]
    return ol, droop, cl, track


# ---------- 5. dynamics: one slow pole ----------
A0, FP = 1e5, 10.0                                   # DC gain, pole frequency -> GBW = 1 MHz


def f3db(Rin, Rf):
    f = np.logspace(1, 8, 4000)
    H = np.array([abs(inverting(Rin, Rf, A0 / (1 + 1j * fi / FP)).solve()[0][2]) for fi in f])
    target = H[0] / np.sqrt(2)
    k = np.argmax(H < target)
    return np.exp(np.interp(np.log(target), np.log(H[[k, k - 1]]), np.log(f[[k, k - 1]]))), f, H


def simulate(positive, Rin=1e3, Rf=1e4, Vs=0.1, rail=15.0, T=2e-4, dt=1e-9):
    # tau dv/dt = -v + A0 (v+ - v-),  v- (or v+) = beta v + (1 - beta) Vs
    tau, beta = 1 / (2 * np.pi * FP), Rin / (Rin + Rf)
    v, out = 0.0, []
    for _ in range(int(T / dt)):
        fb = beta * v + (1 - beta) * Vs
        diff = fb if positive else -fb
        v = np.clip(v + dt / tau * (-v + A0 * diff), -rail, rail)
        out.append(v)
    pole = (A0 * beta - 1) / tau if positive else -(1 + A0 * beta) / tau
    return np.array(out), pole


if __name__ == "__main__":
    worst, asym_p = check_passive()
    print("1. resistors only (2000 random networks, source = 1 V)")
    print(f"   highest FREE node voltage seen = 1 {worst - 1:+.1e} V   (maximum principle: <= 1, up to roundoff)")
    print(f"   max |G - G^T|                  = {asym_p:.1e}     (symmetric)")

    As, gain, exact, asym_a = check_gain()
    print("\n2. add one op-amp: inverting amp, Rin = 1k, Rf = 10k (ideal gain -10)")
    print(f"   max |M - M^T| with op-amp      = {asym_a:.1e}   (the op-amp row has no mirror)")
    for A, g, e in zip(As, gain, exact):
        print(f"   A = {A:8.0e}   gain = {g:+.6f}   formula -10/(1+11/A) = {e:+.6f}   |error vs -10| = {abs(g + 10):.2e}")

    p_in, p_load, p_rf, p_rail, p_stage = check_power()
    print("\n3. power accounting (Vs = 1 V, load 1k, rails +-15 V)")
    print(f"   signal source delivers         = {p_in * 1e3:7.2f} mW")
    print(f"   load receives                  = {p_load * 1e3:7.2f} mW   ({p_load / p_in:.0f}x the input)")
    print(f"   -15 V rail delivers            = {p_rail * 1e3:7.2f} mW")
    print(f"   = load {p_load * 1e3:.2f} + Rf {p_rf * 1e3:.2f} + output stage {p_stage * 1e3:.2f} = {(p_load + p_rf + p_stage) * 1e3:.2f} mW")

    ol, droop, cl, track = check_mead()
    print(f"\n4. Mead transconductance amp (kappa = {KAPPA}, U_T = {UT * 1e3:.2f} mV, small-signal gain {A_MEAD:.0f})")
    print(f"   open loop at 12.8 mV: output / small-signal line = {droop:.4f}  (1 % low)")
    print(f"   open loop over +-12.8 mV: deviation from best straight line = {ol:.1e} of span")
    print(f"   follower over 0..2 V:     deviation from best straight line = {cl:.1e} of span")
    print(f"   follower tracking error at 2 V = {track * 1e3:.2f} mV  (predicted 2/(1+A) = {2 / (1 + A_MEAD) * 1e3:.2f} mV)")

    print(f"\n5. one-pole op-amp, A0 = 1e5, pole {FP:.0f} Hz -> gain-bandwidth 1 MHz")
    curves = {}
    for Rf in (1e3, 1e4, 1e5):
        fc, f, H = f3db(1e3, Rf)
        ng = 1 + Rf / 1e3
        curves[Rf] = (f, H)
        print(f"   |gain| = {Rf / 1e3:5.0f}   noise gain {ng:5.0f}   -3 dB at {fc / 1e3:8.2f} kHz   GBW/NG = {1e6 / ng / 1e3:8.2f} kHz")
    neg, pole_n = simulate(False)
    pos, pole_p = simulate(True)
    dc_pos = inverting(1e3, 1e4, A0, Vs=0.1, positive=True).solve()[0][2].real
    print(f"   negative feedback: pole {pole_n:+.3e} /s -> settles to {neg[-1]:+.4f} V (matrix says {inverting(1e3, 1e4, A0, Vs=0.1).solve()[0][2].real:+.4f})")
    print(f"   positive feedback: pole {pole_p:+.3e} /s -> runs to   {pos[-1]:+.4f} V (matrix says {dc_pos:+.4f} -- a balance, not a stable state)")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 4, figsize=(15, 3.8))

    ax[0].loglog(As, np.abs(gain + 10), "o", label="measured |gain − (−10)|")
    ax[0].loglog(As, np.abs(exact + 10), "k--", label="formula 10 − 10/(1+11/A)")
    ax[0].set_xlabel("open-loop gain A"); ax[0].set_ylabel("gain error")
    ax[0].set_title("feedback: closed-loop gain stops\ndepending on A", fontsize=9); ax[0].legend(fontsize=7)

    dv = np.linspace(-0.15, 0.15, 400)
    ax[1].plot(dv * 1e3, mead_open(dv), label="tanh(κΔV/2U_T)")
    ax[1].plot(dv * 1e3, KAPPA * dv / (2 * UT), "k--", lw=0.8, label="small-signal line")
    ax[1].axvspan(-12.8, 12.8, color="C2", alpha=0.15, label="linear to 1 %")
    ax[1].set_ylim(-1.3, 1.3); ax[1].set_xlabel("ΔV (mV)"); ax[1].set_ylabel("I_out / I_bias")
    ax[1].set_title("Mead's diff pair: open loop\nlinear over ±13 mV only", fontsize=9); ax[1].legend(fontsize=7)

    vin = np.linspace(0, 2, 200)
    ax[2].plot(vin, (vin - mead_follower(vin)) * 1e3, "C3", label="measured Vin − Vout")
    ax[2].plot(vin, vin / (1 + A_MEAD) * 1e3, "k--", lw=0.8, label="Vin / (1 + A)")
    ax[2].set_xlabel("Vin (V)"); ax[2].set_ylabel("tracking error (mV)")
    ax[2].set_title("same device as a follower: error is a\nstraight 0.15 % over 2 V (nonlinearity 2e-7)", fontsize=9)
    ax[2].legend(fontsize=7)

    for Rf, (f, H) in curves.items():
        ax[3].loglog(f, H, label=f"|gain| {Rf / 1e3:.0f}")
    ax[3].loglog(f, 1e6 / f, "k:", lw=0.8, label="GBW / f")
    ax[3].set_ylim(0.1, 300); ax[3].set_xlabel("frequency (Hz)"); ax[3].set_ylabel("|closed-loop gain|")
    ax[3].set_title("gain × bandwidth = constant", fontsize=9); ax[3].legend(fontsize=7)

    fig.tight_layout()
    fig.savefig("opamp.png", dpi=150)
    print("\nwrote opamp.png")
