"""
compress_demo.py — four ways to throw data away, same budget, different distortion.
Pure numpy + PIL (no scipy/sklearn/pywt). First-principles on purpose.

Methods (grayscale, on one image):
  1. NAIVE  : remove 10% of pixels as a centered hole. Keeps 90% of data, looks broken.
  2. DCT    : keep the largest 10% of block-DCT (8x8) coefficients. JPEG-style.
  3. PCA/KLT: keep top-k principal components (low-rank via SVD) at ~10% storage.
  4. WAVELET: keep the largest 10% of multilevel Haar coefficients.

Reports PSNR (dB, higher=better) and prints the subband coding gain G for the wavelet.
Usage: python3 compress_demo.py [input_image_path]   (omit to use a synthetic test image)
"""
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFont

KEEP = 0.10          # transform methods keep 10% of coefficients
N = 256              # working size

# ---------- load or synthesize ----------
def load(path):
    im = Image.open(path).convert("L").resize((N, N))
    return np.asarray(im, dtype=np.float64)

def synth():
    """smooth gradient + sharp shapes + high-freq texture -> shows every distortion type."""
    y, x = np.mgrid[0:N, 0:N]
    img = 128 + 80*np.sin(2*np.pi*(x+y)/380.0)          # smooth low-freq background
    img[40:110, 40:200] = 235                            # a flat bright block (sharp edges)
    r = np.hypot(x-180, y-180)
    img[r < 42] = 30                                     # a dark disk (curved edge)
    img[150:210, 30:90] = 128 + 90*np.sign(np.sin(x[150:210,30:90]*1.2))  # stripes (texture)
    return np.clip(img, 0, 255)

# ---------- metrics ----------
def psnr(a, b):
    mse = np.mean((a - b)**2)
    return 99.0 if mse == 0 else 20*np.log10(255.0/np.sqrt(mse))

# ---------- 1. naive hole ----------
def naive(img, keep):
    # keep only a centered square of area `keep`; black out the rest (deletes 1-keep of pixels)
    out = np.zeros_like(img)
    s = int(round(N*np.sqrt(keep)))
    a = (N - s)//2
    out[a:a+s, a:a+s] = img[a:a+s, a:a+s]
    return out

# ---------- 2. block DCT (8x8) ----------
def dct_matrix(n):
    r = np.arange(n)[:, None]      # frequency index (row)
    c = np.arange(n)[None, :]      # sample index (col)
    M = np.cos(np.pi*(2*c+1)*r/(2*n)) * np.sqrt(2.0/n)
    M[0, :] *= 1/np.sqrt(2)        # orthonormal DCT-II
    return M

def block_dct(img, keep):
    n = 8; D = dct_matrix(n); out = np.zeros_like(img)
    blocks, ac = [], []
    for i in range(0, N, n):
        for j in range(0, N, n):
            C = D @ img[i:i+n, j:j+n] @ D.T
            blocks.append((i, j, C))
            a = np.abs(C).copy(); a[0,0] = 0            # DC excluded from thresholding
            ac.append(a.ravel())
    # always keep every block's DC; spend the rest of the 10% budget on the largest AC coeffs
    budget_ac = max(0, int(keep*N*N) - len(blocks))
    thr = np.quantile(np.concatenate(ac), 1 - budget_ac/(N*N))
    for i, j, C in blocks:
        Ck = np.where(np.abs(C) >= thr, C, 0.0)
        Ck[0,0] = C[0,0]                                # force-keep DC
        out[i:i+n, j:j+n] = D.T @ Ck @ D
    return out

# ---------- 3. PCA / KLT (low-rank via SVD) ----------
def pca(img, keep):
    U, s, Vt = np.linalg.svd(img, full_matrices=False)
    # storage of rank-k ~ k*(2N); match to keep*N*N pixels -> k = keep*N/2
    k = max(1, int(round(keep*N/2)))
    return (U[:, :k]*s[:k]) @ Vt[:k, :]

# ---------- 4. multilevel Haar wavelet ----------
def haar_fwd(a):
    (e, o) = (a[..., 0::2], a[..., 1::2])
    return np.concatenate([(e+o)/np.sqrt(2), (e-o)/np.sqrt(2)], axis=-1)

def haar_inv(a):
    n = a.shape[-1]//2
    lo, hi = a[..., :n], a[..., n:]
    e = (lo+hi)/np.sqrt(2); o = (lo-hi)/np.sqrt(2)
    out = np.empty(a.shape); out[..., 0::2] = e; out[..., 1::2] = o
    return out

def dwt2(img, levels=4):
    c = img.copy(); size = N
    for _ in range(levels):
        c[:size,:size] = haar_fwd(c[:size,:size])           # rows
        c[:size,:size] = haar_fwd(c[:size,:size].T).T        # cols
        size //= 2
    return c

def idwt2(c, levels=4):
    sizes = [N//(2**(levels-1-i)) for i in range(levels)]
    out = c.copy()
    for size in sizes:
        out[:size,:size] = haar_inv(out[:size,:size].T).T
        out[:size,:size] = haar_inv(out[:size,:size])
    return out

def wavelet(img, keep):
    c = dwt2(img)
    thr = np.quantile(np.abs(c).ravel(), 1-keep)
    ck = np.where(np.abs(c) >= thr, c, 0.0)
    return idwt2(ck)

# ---------- 5. CDF 9/7 wavelet (JPEG2000) via the lifting scheme ----------
# Predict/update lifting: exactly invertible for ANY coefficients, because the
# inverse just replays the four steps backwards with the signs flipped.
_A, _B, _G, _D = -1.586134342059924, -0.052980118572961, 0.882911075530934, 0.443506852043971
_K = 1.230174104914001

def _f97_rows(A):                                  # transform each row (last axis), even length
    s, d = A[:, 0::2].copy(), A[:, 1::2].copy()
    d = d + _A*(s + np.roll(s,-1,1))               # predict 1
    s = s + _B*(d + np.roll(d, 1,1))               # update 1
    d = d + _G*(s + np.roll(s,-1,1))               # predict 2
    s = s + _D*(d + np.roll(d, 1,1))               # update 2
    return np.concatenate([s*_K, d/_K], 1)         # scale -> [low | high]; low-pass kept large

def _i97_rows(A):
    n = A.shape[1]//2
    s, d = A[:, :n].copy()/_K, A[:, n:].copy()*_K
    s = s - _D*(d + np.roll(d, 1,1))
    d = d - _G*(s + np.roll(s,-1,1))
    s = s - _B*(d + np.roll(d, 1,1))
    d = d - _A*(s + np.roll(s,-1,1))
    out = np.empty((A.shape[0], 2*n)); out[:,0::2]=s; out[:,1::2]=d
    return out

def dwt97(img, levels=4):
    c = img.copy(); size = N
    for _ in range(levels):
        c[:size,:size] = _f97_rows(c[:size,:size])          # rows
        c[:size,:size] = _f97_rows(c[:size,:size].T).T       # cols
        size //= 2
    return c

def idwt97(c, levels=4):
    out = c.copy()
    for size in [N//(2**(levels-1-i)) for i in range(levels)]:
        out[:size,:size] = _i97_rows(out[:size,:size].T).T
        out[:size,:size] = _i97_rows(out[:size,:size])
    return out

def wavelet97(img, keep):
    c = dwt97(img)
    thr = np.quantile(np.abs(c).ravel(), 1-keep)
    return idwt97(np.where(np.abs(c) >= thr, c, 0.0))

def coding_gain(img):
    """G = arithmetic mean / geometric mean of the 4 first-level subband variances."""
    c = img.copy()
    c = haar_fwd(c); c = haar_fwd(c.T).T
    h = N//2
    LL, LH, HL, HH = c[:h,:h], c[:h,h:], c[h:,:h], c[h:,h:]
    v = np.array([np.var(b) for b in (LL, LH, HL, HH)]) + 1e-9
    return v.mean()/np.exp(np.mean(np.log(v)))

# ---------- assemble side-by-side ----------
def strip(imgs, labels, cols=3):
    pad, lab = 8, 22
    tiles = []
    for a, txt in zip(imgs, labels):
        t = Image.fromarray(np.clip(a,0,255).astype(np.uint8), "L").convert("RGB")
        canvas = Image.new("RGB", (N, N+lab), (255,255,255))
        canvas.paste(t, (0, lab))
        ImageDraw.Draw(canvas).text((4, 4), txt, fill=(0,0,0))
        tiles.append(canvas)
    rows = (len(tiles)+cols-1)//cols
    W = cols*N + (cols+1)*pad
    H = rows*(N+lab) + (rows+1)*pad
    out = Image.new("RGB", (W, H), (255,255,255))
    for i, t in enumerate(tiles):
        r, c = divmod(i, cols)
        out.paste(t, (pad + c*(N+pad), pad + r*(N+lab+pad)))
    return out

if __name__ == "__main__":
    img = load(sys.argv[1]) if len(sys.argv) > 1 else synth()
    keep = float(sys.argv[3]) if len(sys.argv) > 3 else KEEP
    pct = int(round((1-keep)*100))
    outs, labels = [img], ["original"]
    for fn, name in [
        (lambda x: naive(x, keep),    f"naive: keep center {int(keep*100)}%"),
        (lambda x: pca(x, keep),      "PCA / low-rank"),
        (lambda x: block_dct(x, keep),"DCT (JPEG)"),
        (lambda x: wavelet(x, keep),  "Haar wavelet (crude)"),
        (lambda x: wavelet97(x, keep),"CDF 9/7 wavelet (JPEG2000)"),
    ]:
        r = fn(img); outs.append(r)
        labels.append(f"{name}  PSNR {psnr(img, r):.1f}dB")
    print(f"subband coding gain G = {coding_gain(img):.2f}  (=> {0.5*np.log2(coding_gain(img)):.2f} bits/sample)")
    for l in labels[1:]: print("  ", l)
    strip(outs, labels).save(sys.argv[2] if len(sys.argv) > 2 else "compare.png")
    print("saved compare.png")
