---
title: "I deleted 90% of my baby photo five different ways. Only one left a hole."
date: 2026-07-31
blurb: "Every compression method throws away about the same amount of information. What separates a good codec from a bad one is where it's allowed to put the damage."
tags: ["signal-processing", "compression", "wavelets", "information-theory"]
hero: /posts/compression-delete90.png
code: /posts/compress_demo.py
draft: false
---

This is me at one year old. Then I deleted **90%** of the picture — five different ways. One method left almost nothing. The other four rebuilt me from a tenth of the data. Same amount deleted every time — the only thing that changed was *what* got thrown away.

![Same photo, 90% deleted five ways: naive spatial deletion collapses while PCA, DCT and wavelets survive.](/posts/compression-delete90.png)

That's the whole secret of data compression, and it took me embarrassingly long to see it: compression isn't about **how much** you lose. It's about **where you get to hide the error.**

## Same budget, five verdicts

| method | PSNR | what the error looks like |
|---|---|---|
| naive — delete pixels | **4.5 dB** | a black frame, a sliver of face left. Total, local loss. |
| PCA / low-rank | 28.7 dB | soft but recognizable — the broad patterns survive |
| Haar wavelet (crudest one) | 37.6 dB | clean, error diffused into smooth regions |
| DCT — the transform inside JPEG | 39.8 dB | sharp, but blocking + ringing at the edges |
| CDF 9/7 — the wavelet inside JPEG2000 | **40.3 dB** | visually perfect |

PSNR (peak signal-to-noise ratio) is decibels of fidelity — higher is better, and it's a log scale, so 4.5 vs 40.3 is not "nine times worse," it's a different universe. The naive method deleted the *least useful* 90% — a solid block of pixels — and lost the image. The wavelet deleted the *least noticeable* 90% and lost nothing you can see.

## Push it to 98% and the second lesson appears

![At 98% deleted, JPEG's DCT blocks fracture while the wavelets hold together.](/posts/compression-delete98.png)

At a brutal 98% deleted, even the good methods strain — and now the gap between JPEG and JPEG2000 becomes *visible*. The DCT's 8×8 blocks fracture (29.8 dB) while the wavelets hold together (30.7 / 31.7 dB). That's not luck: JPEG2000 replaced JPEG's block-DCT with exactly this wavelet **because** it degrades gracefully instead of shattering.

## Why wavelets win

Each wavelet basis function is localized in **space and frequency at once** — it says "detail of this scale, near this spot." Throw away the small coefficients and you remove fine detail exactly in the flat regions where nothing was happening. The error migrates to the smooth cheeks where the eye doesn't look, and the sharp edges — the large coefficients — survive.

Contrast the two failures:

- A **pixel** is perfectly localized in space but spread across all frequency. Delete pixels and you get a hole — local, catastrophic.
- A **cosine** (Fourier / DCT) is perfectly localized in frequency but spread across all space. Truncate one and its error smears everywhere — ringing near edges, and block-by-block coding to contain it.
- A **wavelet** sits between the two, which is the whole point.

## The part I actually love

By PSNR, the wavelet only *barely* beats JPEG at 90% — 40.3 vs 39.8. But your eye isn't close; the wavelet is obviously cleaner. **A single number ranked them nearly equal while hiding the only thing that mattered — where the error went.** That's the trap of compressing quality into one scalar: it can't see a distortion *profile*. This is why "how much error" is the wrong question and "where is the error allowed to land" is the right one.

## Everything from scratch

No libraries beyond numpy — the DCT matrix, the PCA (via SVD), the Haar transform, and the CDF 9/7 lifting scheme are all hand-written. Two bugs got caught by the numbers before any eye could: a non-orthonormal DCT matrix (reconstruction was garbage), and an inverted wavelet scaling that made "keep the largest coefficients" throw away the wrong ones. The metric earning its keep.

```python
# CDF 9/7 wavelet (JPEG2000) via the lifting scheme — exactly invertible,
# because the inverse just replays the four steps backwards with flipped signs.
def _f97_rows(A):                       # transform each row, even length
    s, d = A[:, 0::2].copy(), A[:, 1::2].copy()
    d = d + _A*(s + np.roll(s,-1,1))    # predict 1
    s = s + _B*(d + np.roll(d, 1,1))    # update 1
    d = d + _G*(s + np.roll(s,-1,1))    # predict 2
    s = s + _D*(d + np.roll(d, 1,1))    # update 2
    return np.concatenate([s*_K, d/_K], 1)   # scale -> [low | high]
```

[Full script (numpy + PIL, ~150 lines)](/posts/compress_demo.py) — run it on any image of your own.

*Next in this thread: the one number that predicts, before you compress anything, whether a signal will compress at all.*
