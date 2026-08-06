"""
Learning doesn't need the true gradient — just positive correlation with it.

Three from-scratch experiments on a 2-layer net (student-teacher, MSE):
  1. Controlled-cosine sweep: replace the gradient with a surrogate g_rho at fixed
     cosine rho to the true gradient. Learns for rho>0, stalls at 0, diverges below.
  2. Feedback alignment: use a fixed RANDOM matrix B instead of W2^T in the backward
     pass. It still learns because the alignment cosine rises on its own.

Pure numpy. Usage: python3 gradient-alignment.py
"""
import numpy as np
rng = np.random.default_rng(2)
d, h, o, N = 20, 40, 5, 800
X  = rng.standard_normal((d, N))
W1t = rng.standard_normal((h, d)) / np.sqrt(d)
W2t = rng.standard_normal((o, h)) / np.sqrt(h)
Y = W2t @ np.tanh(W1t @ X)                       # fixed teacher target

def forward_back(W1, W2):
    H = np.tanh(W1 @ X); Yh = W2 @ H; d2 = Yh - Y
    loss = 0.5 * np.mean(np.sum(d2**2, 0))
    gW2 = d2 @ H.T / N
    d1  = (W2.T @ d2) * (1 - H**2); gW1_true = d1 @ X.T / N   # true backprop grad on W1
    return loss, gW1_true, gW2, H, d2

# ---- 1. controlled-correlation sweep ----
def train_rho(rho, epochs=600, lr=0.08):
    W1 = rng.standard_normal((h, d))/np.sqrt(d); W2 = rng.standard_normal((o, h))/np.sqrt(h)
    losses = []
    for _ in range(epochs):
        loss, g1, g2, H, d2 = forward_back(W1, W2)
        g = np.concatenate([g1.ravel(), g2.ravel()]); losses.append(loss)
        r = rng.standard_normal(g.size); r -= (r @ g)/(g @ g) * g
        r *= np.linalg.norm(g)/(np.linalg.norm(r)+1e-12)
        used = rho*g + np.sqrt(max(1-rho**2, 0))*r            # cos(used, g) = rho
        W1 -= lr*used[:h*d].reshape(h, d); W2 -= lr*used[h*d:].reshape(o, h)
    return losses[-1]

# ---- 2. feedback alignment ----
def train_fa(epochs=500, lr=0.08):
    W1 = rng.standard_normal((h, d))/np.sqrt(d); W2 = rng.standard_normal((o, h))/np.sqrt(h)
    B  = rng.standard_normal((h, o))/np.sqrt(o)               # fixed random feedback
    align = []
    for _ in range(epochs):
        loss, g1_true, g2, H, d2 = forward_back(W1, W2)
        g1_fa = ((B @ d2) * (1 - H**2)) @ X.T / N             # pseudo-gradient with random B
        a, b = g1_fa.ravel(), g1_true.ravel()
        align.append(a @ b / (np.linalg.norm(a)*np.linalg.norm(b) + 1e-12))
        W1 -= lr*g1_fa; W2 -= lr*g2
    return align

if __name__ == "__main__":
    print("controlled-correlation sweep — final loss:")
    for rho in [1.0, 0.5, 0.2, 0.05, 0.0, -0.2]:
        print(f"  rho = {rho:+.2f}   final loss = {train_rho(rho):.4g}")
    a = train_fa()
    print(f"\nfeedback alignment cosine: start {a[0]:+.3f}  ->  end {a[-1]:+.3f}  (emerges on its own)")
