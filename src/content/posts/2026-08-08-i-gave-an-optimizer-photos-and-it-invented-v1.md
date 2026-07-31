---
title: "I gave an optimizer photos and one rule. It invented the visual cortex."
date: 2026-08-08
blurb: "No edges, no orientations, no faces were put in — only natural image patches and a penalty for using too many units at once. What emerged is what an electrode finds in V1."
tags: ["neuromorphic", "sparse-coding", "signal-processing", "vision", "information-theory"]
hero: /posts/receptive-fields.png
code: /posts/sparse_coding.py
draft: false
---

In an [earlier post](/posts/2026-07-31-where-does-the-error-go/) I deleted 90% of a photo with a wavelet transform and the surviving detail landed on the face, not the background. The obvious question — *how did it know to focus on the face?* — has a blunt answer: **it didn't.** The wavelet is signal-blind; it runs the same filters everywhere. The face is simply where the local variation was, and a "keep the largest coefficients" rule surfaced it. No detection, no attention, no knower.

But that only pushes the mystery back one step. The wavelet works because its basis functions — localized, oriented, multi-scale — happen to match how natural images are built. **Who chose that basis?** For JPEG2000, humans did, over decades. For your brain, nobody did. So I ran the experiment.

![144 basis functions learned from natural image patches under a sparsity penalty — localized oriented edge detectors at many scales and orientations.](/posts/receptive-fields.png)

## The experiment

Every tile above is a basis function an optimizer **invented**. I gave it exactly two things:

1. Random 16×16 patches cut from natural photos.
2. A penalty for explaining each patch with too many active units.

That's the whole objective — for each patch $x$, find coefficients $a$ that

$$\min_a \;\underbrace{\lVert x - \Phi a\rVert^2}_{\text{reconstruction error} \;=\; \text{distortion } D} \;+\; \lambda \underbrace{\lVert a \rVert_1}_{\text{how many units fire} \;=\; \text{rate } R}$$

then nudge the dictionary $\Phi$ toward the residual and repeat. I never put in edges, orientations, scales, or the concept of a face. What came out is **localized, oriented, multi-scale edge detectors** — and that is precisely what an electrode finds when you record from simple cells in the primary visual cortex (V1). Hubel and Wiesel got a Nobel Prize for measuring these in a cat; here they fall out of one line of optimization. This reproduces Olshausen & Field (*Nature*, 1996).

## Three systems, one basis

A codec, this optimizer, and your visual cortex all converge on the same wavelet-like basis, because they are all solving one problem: **represent natural signals with the fewest active elements.**

- JPEG2000 does it to save **bits**.
- The optimizer does it because I charged it for active units.
- Your brain does it to save **spikes** — and a spike is not free. Firing one neuron costs on the order of $10^4$–$10^5$ ATP molecules ([Attwell & Laughlin, 2001](https://doi.org/10.1097/00004647-200110000-00001) put a number on the entire cortical energy budget). A brain that represents the world with fewer active neurons is a cheaper brain, so evolution selects for sparse codes — and the sparse code for natural scenes *is* the wavelet-like code.

That objective above is not a neural-network trick. It is **rate–distortion** — the same $D$ and $R$ from the compression posts — with the bit budget replaced by a spike budget. The receptive field isn't designed. It's what minimizing active units *forces* on any system that has to represent the natural world.

## The epistemology

Here's the part that took me a while to accept. The question "how does the system know what's important?" assumes there is a knower doing the deciding. There isn't. There is a basis, a threshold, and a world with structure. **Importance is never computed — it's just where the energy already was, and a sparsity constraint surfaces it.** The "attention to the face" in the wavelet, and the fact that your V1 neurons fire on edges and not on blank walls, are the *same* emergence: a sparse code meeting the statistics of the natural world, with no homunculus anywhere in the loop.

## Honest notes

This is a mid-resolution result, not a polished one, and I'd rather say so. The code settled at ~17% active where a cleaner run wants ~10–15%; a handful of tiles are dead atoms (unused, normal for an over-complete dictionary); more training and larger patches would sharpen the bars further. Two bugs got fixed to get here: the whitening step was amplifying high-frequency noise (fixed by keeping only the top principal components), and there was no learning-rate decay so the dictionary diverged (fixed by annealing). The result is the real phenomenon, caught partway to convergence — every one of the 144 tiles is shown, fixed random seed, nothing curated.

```python
# The entire learning rule — alternate sparse inference (ISTA) with a
# dictionary nudge. No autograd, no framework.
for it in range(ITERS):
    xb = X[batch].T
    a = np.zeros((NATOMS, BATCH))
    for _ in range(INFER):                       # infer a sparse code
        a = soft(a + step*(Phi.T @ (xb - Phi @ a)), step*LAM)
    Phi += (eta/BATCH) * (xb - Phi @ a) @ a.T     # move dictionary toward residual
    Phi /= np.linalg.norm(Phi, axis=0)            # keep receptive fields unit-norm
```

[Full script (numpy + PIL, ~70 lines)](/posts/sparse_coding.py) — point it at your own photos and watch V1 emerge.

*This is the thesis the rest of my work hangs from: the computing elements of the brain are sparse signal coders, and their receptive fields are the basis a metabolic budget forces on anything representing the natural world.*
