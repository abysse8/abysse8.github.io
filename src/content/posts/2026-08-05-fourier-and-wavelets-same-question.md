---
title: "Fourier and wavelets are the same question asked at different resolutions"
date: 2026-08-05
blurb: "Both answer one question — what basis makes this signal cheap to describe? The difference is where they're willing to be vague: Fourier in time, wavelets trade sharpness in time against sharpness in frequency."
tags: ["signal-processing", "wavelets", "fourier", "information-theory"]
draft: true
---

*Draft — pull the derivation from my Fall-2023 filter-bank notes; add a time-frequency tiling figure.*

On day one of my wavelets class I wrote, without realizing it was the whole course: *"learning how to design the basis $\{\Phi_i\}$ so that $x = \sum c_i \Phi_i$ needs fewer coefficients."* That sentence is also the whole of Fourier analysis. Both are one move — **choose a basis that makes the signal cheap** — and they differ only in where they're willing to be vague.

## One question

Any transform writes a signal as a sum over a basis, $x = \sum_i c_i \Phi_i$, with coefficients $c_i = \langle x, \Phi_i\rangle$. Compression is: keep the big $c_i$, drop the rest. The only real choice is the basis $\{\Phi_i\}$.

- **Fourier** picks sines and cosines: perfectly sharp in *frequency*, completely spread out in *time*. Great for a steady tone; terrible for a click, because a click needs every frequency at once (this is the Gibbs ringing you see at edges).
- **Wavelets** pick little bumps at many scales: each one is localized in time *and* frequency. Fine time resolution where the signal is busy, fine frequency resolution where it's smooth.

## The uncertainty principle sets the price

You can't be perfectly sharp in both time and frequency — that's the Heisenberg–Gabor limit, the same inequality as in quantum mechanics, for the same Fourier-duality reason. Every transform is a *choice of compromise*. Fourier spends all its sharpness on frequency. Wavelets spend it adaptively: wide-in-time / narrow-in-frequency at low frequencies, narrow-in-time / wide-in-frequency at high ones — which is exactly how natural signals are built (slow backgrounds, sudden edges).

## Why this matters for compression

Natural images are piecewise-smooth: mostly flat, with sparse edges. Wavelets match that structure, so their coefficients are wildly unequal — which, as the [coding-gain post](/posts/) showed, is precisely the condition for large $G$. Fourier's basis doesn't localize, so a single edge lights up coefficients everywhere. Same underlying idea — a change of basis — but wavelets pick the basis that fits how the world's signals are actually shaped.
