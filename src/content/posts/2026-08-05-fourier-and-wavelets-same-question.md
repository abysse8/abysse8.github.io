---
title: "Fourier and wavelets are the same question asked at different resolutions"
date: 2026-08-05
blurb: "Both answer one question — what basis makes this signal cheap to describe? The difference is where they're willing to be vague: Fourier in time, wavelets trade sharpness in time against sharpness in frequency."
tags: ["signal-processing", "wavelets", "fourier", "information-theory"]
hero: /posts/tf-tiling.png
draft: false
---

On day one of my wavelets class I wrote, without realizing it was the whole course: *"learning how to design the basis $\{\Phi_i\}$ so that $x = \sum c_i \Phi_i$ needs fewer coefficients."* That sentence is also the whole of Fourier analysis. Both are one move — **choose a basis that makes the signal cheap** — and they differ only in where they're willing to be vague.

## One question

Any transform writes a signal as a sum over a basis, $x = \sum_i c_i \Phi_i$, with coefficients $c_i = \langle x, \Phi_i\rangle$. Compression is: keep the big $c_i$, drop the rest. The only real choice is the basis $\{\Phi_i\}$.

- **Fourier** picks sines and cosines: perfectly sharp in *frequency*, completely spread out in *time*. Great for a steady tone; terrible for a click, because a click needs every frequency at once (this is the Gibbs ringing you see at edges).
- **Wavelets** pick little bumps at many scales: each one is localized in time *and* frequency. Fine time resolution where the signal is busy, fine frequency resolution where it's smooth.

## The uncertainty principle sets the price

You can't be perfectly sharp in both time and frequency — that's the Heisenberg–Gabor limit, the same inequality as in quantum mechanics, for the same Fourier-duality reason. Every transform is a *choice of compromise*. Fourier spends all its sharpness on frequency. Wavelets spend it adaptively: wide-in-time / narrow-in-frequency at low frequencies, narrow-in-time / wide-in-frequency at high ones — which is exactly how natural signals are built (slow backgrounds, sudden edges).

![The time–frequency plane tiled three ways — samples, Fourier, wavelets — every tile the same area.](/posts/tf-tiling.png)

Every tile has the **same area** — you can't beat the uncertainty principle, only choose the tile's *shape*. Samples are perfectly sharp in time and blind to frequency; Fourier is perfectly sharp in frequency and blind to time; wavelets give fine time where the signal is fast and fine frequency where it's slow. Same budget, three ways to spend it.

## Why this matters for compression

Natural images are piecewise-smooth: mostly flat, with sparse edges. Wavelets match that structure, so their coefficients are wildly unequal — a few large ones on the edges, near-zero everywhere else — which is exactly the condition that makes a transform worth doing. Fourier's basis doesn't localize, so a single edge lights up coefficients everywhere. Same underlying idea — a change of basis — but wavelets pick the basis that fits how the world's signals are actually shaped.
