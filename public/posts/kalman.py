"""
A Kalman filter never removes noise — it weighs how much to believe each measurement.

The scalar update equals the precision-weighted average of prediction and
measurement (verified to ~2e-16). The gain K is a trust dial set by Q and R.

Pure numpy. Usage: python3 kalman.py
"""
import numpy as np
rng = np.random.default_rng(3)
N, Q, R = 140, 0.02, 1.0            # steps, process noise, measurement noise

# simulate a slow random-walk state + noisy measurements
x, xs, zs = 0.0, [], []
for _ in range(N):
    x += rng.normal(0, np.sqrt(Q)); xs.append(x); zs.append(x + rng.normal(0, np.sqrt(R)))
xs, zs = np.array(xs), np.array(zs)

# Kalman filter, and check the update == precision-weighted mean
xh, P, est, maxdiff = 0.0, 1.0, [], 0.0
for z in zs:
    xm, Pm = xh, P + Q                       # predict (Q inflates covariance, not the mean)
    K = Pm / (Pm + R)                         # gain = measurement's share of total precision
    xh = xm + K * (z - xm); P = (1 - K) * Pm  # update
    pw = (xm / Pm + z / R) / (1 / Pm + 1 / R) # fuse two Gaussians = precision-weighted mean
    maxdiff = max(maxdiff, abs(xh - pw))
    est.append(xh)
est = np.array(est)

print(f"update == precision-weighted mean?  max diff = {maxdiff:.2e}")
print(f"steady-state gain K = {K:.3f}  -> moves {K*100:.0f}% toward each measurement")
print(f"MSE raw {np.mean((zs-xs)**2):.3f} -> KF {np.mean((est-xs)**2):.3f} "
      f"({np.mean((zs-xs)**2)/np.mean((est-xs)**2):.1f}x better)")

# gain vs measurement noise — the trust dial
def steady_K(Rv, Q=0.02):
    P = 1.0
    for _ in range(500):
        Pm = P + Q; K = Pm / (Pm + Rv); P = (1 - K) * Pm
    return K
print("\ngain vs measurement noise R:")
for Rv in [0.01, 0.1, 1, 10, 100]:
    print(f"  R={Rv:6}  K={steady_K(Rv):.3f}")
