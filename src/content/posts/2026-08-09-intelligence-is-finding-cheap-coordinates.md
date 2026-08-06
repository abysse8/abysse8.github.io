---
title: "Intelligence is finding the coordinates where the world gets cheap"
date: 2026-08-09
blurb: "A good representation isn't magic — it's a coordinate system in which the data is sparse. Same data, four coordinate systems, and the loss you pay for a fixed budget spans 9×. On noise, the advantage vanishes — which is how you know it's a law, not a metaphor."
tags: ["signal-processing", "compression", "information-theory", "learning"]
hero: /posts/coordinates.png
code: /posts/coordinates.py
draft: false
---

For years I had a hunch I couldn't pin down: that wavelets, compression, and learning are secretly the same move — **finding a coordinate system in which the world becomes sparse.** It felt true and stayed an analogy. The honest question I kept writing next to it was: *is this a real formalization, or a suggestive metaphor?* So I finally turned it into a number.

## The setup

Take 4,000 little 8×8 patches from a photo. Pick a **coordinate system** — an orthonormal basis. Write each patch in those coordinates, keep only the $K$ largest coefficients, throw the rest away, rebuild the patch, and measure the **loss** (mean squared error). Sweep $K$ from 1 to 64. The lower the loss at a given budget, the better those coordinates fit the data.

Four strategies, from no-knowledge to learned-from-the-data:

- **Pixels** — the raw coordinates. No thought at all.
- **Random basis** — a coordinate system chosen with *zero* knowledge of the data.
- **DCT** — a fixed basis *designed* for natural images (the one inside JPEG).
- **PCA** — coordinates *learned* from the data's own covariance.

![Reconstruction loss vs. budget for four coordinate systems, on real image patches (left) and on white noise (right).](/posts/coordinates.png)

## The result

Keep 8 coefficients out of 64. On real image patches, the loss is:

| coordinates | loss @ K=8 |
|---|---|
| Pixels (raw) | 105.4 |
| Random basis | 94.4 |
| DCT (designed) | 10.7 |
| **PCA (learned)** | **10.5** |

Same data, same budget of 8 numbers. Choosing *where to look* buys a **9× reduction in loss** over a random basis. The learned coordinates (PCA) and the designed ones (DCT) plunge; the ignorant ones (pixels, random) lag by an order of magnitude. That's the left panel — the good coordinates fall off a cliff, the bad ones crawl.

## The falsifier — why this is a law, not a vibe

Here's the move that decides whether the whole idea is real. If "intelligence is finding coordinates where the data is sparse," then the advantage of good coordinates should **vanish when there's no structure to find.** That's a prediction that could fail.

Run the identical experiment on **white noise** (right panel). Every curve lands on top of every other: random 2731, PCA 2688 — indistinguishable. Learning the coordinates buys *nothing*, because noise has no cheap coordinate system; it's equally incompressible in all of them.

So the analogy graduates into a statement with teeth: **the payoff from good coordinates is exactly the amount of structure in the data, and it is zero on noise.** The metaphor made a numerical prediction, and the number came back on its side.

## The bridge to learning

The part I actually care about: the coefficients you *keep* are your **model** of the patch; the ones you *drop* are the **residual — the prediction error.** So "find good coordinates" and "find the representation that leaves the least unexplained" are the same sentence. A wavelet's detail coefficients, PCA's components, the features a neural network learns — all the same move: rotate the world until most of it is predictable from little, and call what's left the error you couldn't help.

That's why a good representation feels like understanding. It *is* understanding, operationalized: the coordinate system in which the world costs the fewest bits to describe.

## From scratch

No libraries beyond numpy — the four bases, the top-$K$ truncation, the loss sweep. [The script](/posts/coordinates.py) runs the whole experiment, noise control included, in about 40 lines. Point it at any image.
