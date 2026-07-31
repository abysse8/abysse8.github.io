"""
sparse_coding.py — Olshausen & Field (1996), from scratch in numpy.

Claim to demonstrate: give a dumb optimizer nothing but (a) patches of natural
photos and (b) a pressure to explain each patch with FEW active units, and the
basis functions it invents come out looking like V1 receptive fields —
localized, oriented, multi-scale edge detectors. Nobody puts edges in.

Objective, per patch x:   min_a  ||x - Phi a||^2  +  lambda * ||a||_1
   reconstruction error (distortion)  +  sparsity (how many neurons fire = rate)
Learn Phi by alternating: infer sparse a (ISTA), then nudge Phi toward the
residual and renormalize. Pure numpy + PIL.
"""
import glob, sys, numpy as np
from PIL import Image

rng = np.random.default_rng(0)          # fixed seed: reproducible receptive fields
P      = 16                             # patch side (16x16 -> elongated Gabors)
DIM    = P*P
NATOMS = 256                            # dictionary size (16x16 grid to display)
NPATCH = 40000
BATCH  = 100
ITERS  = 6000
LAM    = float(sys.argv[1]) if len(sys.argv) > 1 else 0.8   # sparsity weight
ETA    = float(sys.argv[2]) if len(sys.argv) > 2 else 1.5   # dictionary learning rate
INFER  = 70                             # ISTA iterations per batch

# ---------- 1. sample patches from natural photos ----------
paths = sorted(glob.glob("/home/j3/Documents/gmail-archive/curated/gallery/*.jpg"))[:40]
imgs = []
for p in paths:
    try:
        im = np.asarray(Image.open(p).convert("L").resize((256,256)), float)/255.0
        imgs.append(im)
    except Exception:
        pass
print(f"loaded {len(imgs)} images")

patches = np.empty((NPATCH, DIM))
for i in range(NPATCH):
    im = imgs[rng.integers(len(imgs))]
    r, c = rng.integers(0, 256-P, size=2)
    pat = im[r:r+P, c:c+P].ravel()
    patches[i] = pat - pat.mean()       # remove DC (per-patch brightness)

# ---------- 2. ZCA whitening, top-K only (flatten 1/f^2 WITHOUT amplifying noise) ----------
# Full whitening boosts the smallest-variance (highest-frequency) directions, which
# are mostly noise -> noisy filters. Keeping only the top-K principal components drops
# those noise directions before whitening. That's what exposes clean edges.
KEEP_PC = 180
cov = patches.T @ patches / NPATCH
w, V = np.linalg.eigh(cov)              # ascending
idx = np.argsort(-w)[:KEEP_PC]          # top-K by variance
w, V = np.maximum(w[idx], 1e-8), V[:, idx]
whiten = V @ np.diag(1/np.sqrt(w)) @ V.T
X = patches @ whiten                    # whitened patches (rows), noise directions removed
X /= X.std()                            # unit scale so LAM is meaningful

# ---------- 3. learn the dictionary ----------
Phi = rng.standard_normal((DIM, NATOMS))
Phi /= np.linalg.norm(Phi, axis=0, keepdims=True)

def soft(z, t):                         # soft-threshold = the L1 proximal operator
    return np.sign(z) * np.maximum(np.abs(z) - t, 0.0)

for it in range(ITERS):
    xb = X[rng.integers(NPATCH, size=BATCH)].T      # (DIM, BATCH)
    L = np.linalg.norm(Phi, 2)**2                   # ISTA step = 1/Lipschitz
    step = 1.0/L
    a = np.zeros((NATOMS, BATCH))
    for _ in range(INFER):                          # ISTA: sparse inference
        a = soft(a + step*(Phi.T @ (xb - Phi @ a)), step*LAM)
    eta = ETA / (1 + it/1200)                       # anneal learning rate -> it settles
    Phi += (eta/BATCH) * (xb - Phi @ a) @ a.T       # gradient step on reconstruction
    Phi /= np.linalg.norm(Phi, axis=0, keepdims=True)  # keep atoms unit-norm
    if it % 500 == 0:
        rec = np.mean((xb - Phi @ a)**2)
        act = np.mean(np.abs(a) > 1e-3)
        print(f"iter {it:4d}  recon {rec:.3f}  active {100*act:4.1f}%")

# ---------- 4. tile the learned receptive fields into one image ----------
side = int(np.sqrt(NATOMS))
pad = 1
tile = np.ones((side*(P+pad)+pad, side*(P+pad)+pad)) * 0.5
order = np.argsort(-np.linalg.norm(Phi, axis=0))     # (all unit norm; stable order)
for k, idx in enumerate(order):
    f = Phi[:,idx].reshape(P,P)
    f = (f - f.min())/(np.ptp(f)+1e-9)               # normalize each filter to [0,1]
    r, c = divmod(k, side)
    y, x = pad + r*(P+pad), pad + c*(P+pad)
    tile[y:y+P, x:x+P] = f
Image.fromarray((tile*255).astype(np.uint8)).resize((side*(P+pad)*4,)*2, Image.NEAREST)\
     .save("receptive_fields.png")
print("saved receptive_fields.png")
