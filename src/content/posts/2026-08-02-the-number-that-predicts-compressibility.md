---
title: "The one number that tells you if a signal will compress — before you compress it"
date: 2026-08-02
blurb: "Coding gain G is the ratio of the arithmetic to the geometric mean of the subband energies. It says, in advance, whether a transform will help — and it's exactly 1 for noise."
tags: ["signal-processing", "compression", "information-theory"]
hero: /posts/compression-delete90.png
draft: true
---

*Draft — flesh out with a per-band energy figure before publishing.*

Last time I showed that wavelets compress by hiding the error where you can't see it. But here's a sharper question: can you tell, *before* running any compression, whether a signal will compress at all? Yes — with one number.

## Bits scale with the log of variance

To describe a signal of variance $\sigma^2$ down to an allowed error $D$ costs

$$R = \tfrac{1}{2}\log_2\frac{\sigma^2}{D}\quad\text{bits per sample.}$$

Something that wiggles more needs more bits — logarithmically. That log is the whole reason a geometric mean is about to show up.

## Coding gain

Split a signal into $M$ subbands with variances $\sigma_1^2,\dots,\sigma_M^2$. Spend a fixed bit budget the naive way (on the raw samples) versus the transform way (optimally across bands), at the same quality, and subtract. The costs collapse to a ratio:

$$G = \frac{\frac{1}{M}\sum_i \sigma_i^2}{\left(\prod_i \sigma_i^2\right)^{1/M}} = \frac{\text{arithmetic mean of band energies}}{\text{geometric mean of band energies}}.$$

You save $\tfrac{1}{2}\log_2 G$ bits per sample. By the AM–GM inequality, $G \ge 1$ always — the transform never hurts — and **$G = 1$ exactly when every band has equal energy**, which is white noise. Nothing to compact, no gain.

## The falsifier

Compression gain *is* energy imbalance across bands, and $G$ measures it. On my baby photo, $G = 26.8$ — huge, because a portrait is mostly smooth skin (one enormous low-frequency band, tiny detail bands). On white noise, $G = 1$, and no transform on earth will help you. That's the checkable claim: **a transform helps if and only if the signal is non-white, and $G$ says by how much.**

*The assumptions, stated so nobody has to catch me: Gaussian source, high-rate quantization, optimal bit allocation, orthonormal transform. Real images satisfy none exactly, so measured gain differs from predicted — G is the idealized number, not a guarantee.*
