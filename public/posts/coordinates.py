"""
Intelligence is finding cheap coordinates — measured.

Represent image patches in four coordinate systems (pixels, random, DCT, PCA),
keep the top-K coefficients, and measure reconstruction loss vs K. Good
coordinates cost far less loss per coefficient — but only on structured data.
On white noise, every strategy is equal (the falsifier).

Pure numpy + PIL. Usage: python3 coordinates.py [image.jpg]
"""
import sys, numpy as np
from PIL import Image

rng = np.random.default_rng(0)
P = 8; D = P * P                      # 8x8 patches -> 64-dim vectors

def patches(img, n=4000):
    H, W = img.shape; out = []
    for y, x in zip(rng.integers(0, H-P, n), rng.integers(0, W-P, n)):
        p = img[y:y+P, x:x+P].ravel().astype(float)
        out.append(p - p.mean())     # remove DC: model structure, not brightness
    return np.array(out)

def dct_matrix(n):
    r = np.arange(n)[:, None]; c = np.arange(n)[None, :]
    M = np.cos(np.pi*(2*c+1)*r/(2*n)) * np.sqrt(2/n); M[0] *= 1/np.sqrt(2)
    return M
DCT = np.kron(dct_matrix(P), dct_matrix(P))   # separable 2D DCT basis

def strategies(Xtrain):
    """Return {name: orthonormal basis B (rows = basis vectors)}."""
    B = {}
    B["Pixels (raw coords)"] = np.eye(D)
    Q, _ = np.linalg.qr(rng.standard_normal((D, D))); B["Random basis"] = Q
    B["DCT (designed)"] = DCT
    C = np.cov(Xtrain.T); w, V = np.linalg.eigh(C)
    B["PCA (learned)"] = V[:, ::-1].T             # learned from the data itself
    return B

def loss_vs_K(X, B, Ks):
    C = X @ B.T                                    # coefficients (B orthonormal)
    curve = []
    for K in Ks:
        idx = np.argsort(-np.abs(C), 1)[:, :K]     # keep the K largest per patch
        Ck = np.zeros_like(C); np.put_along_axis(Ck, idx, np.take_along_axis(C, idx, 1), 1)
        curve.append(float(np.mean((X - Ck @ B) ** 2)))
    return curve

if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "photo.jpg"
    img = np.asarray(Image.open(src).convert("L").resize((256, 256)), float)
    X = patches(img)
    Xn = rng.integers(0, 256, (4000, D)).astype(float); Xn -= Xn.mean(1, keepdims=True)
    Ks = [1, 2, 4, 8, 16, 32, 64]
    for label, data in [("IMAGE patches", X), ("WHITE NOISE", Xn)]:
        print(f"\n{label} — loss at K=8 (of 64):")
        for name, Bmat in strategies(data).items():
            print(f"  {name:22} {loss_vs_K(data, Bmat, Ks)[Ks.index(8)]:8.1f}")
