---
title: "Learning doesn't need the true gradient — 5% of it will do"
date: 2026-08-12
blurb: "Backprop computes the exact gradient — but a learning rule only needs to point roughly downhill. Positive correlation with the true gradient is enough: 5% of it still learns, and below zero it explodes. That cliff is why brains can learn without backprop's exact wiring."
tags: ["learning", "backprop", "feedback-alignment", "neuromorphic"]
hero: /posts/gradient-alignment.png
code: /posts/gradient-alignment.py
draft: false
---

Backpropagation computes the exact gradient of the loss and steps against it. It's precise — and biologically implausible: a neuron would have to know the exact transpose of every downstream weight to do it. So here's the question that's bugged me for years: how *wrong* can the update direction be and still learn?

There's a one-line answer I wanted to test rather than take on faith: **any update whose expected inner product with the true gradient is positive will reduce the loss.** Not equal to the gradient — just positively correlated with it. Let me put a number on "how positive is enough."

## The experiment

Train a little two-layer network (student–teacher regression, MSE loss), all from scratch. Each step, compute the true gradient $g$, then **replace** it with a surrogate $g_\rho$ built to have a fixed cosine similarity $\rho$ with $g$ — same length, controlled angle:

$$g_\rho = \rho\,\hat g + \sqrt{1-\rho^2}\,\hat r,\qquad \hat r \perp g.$$

Step along $g_\rho$ instead of $g$, and sweep $\rho$ from $+1$ (ordinary backprop) down through zero into the negatives.

![Left: loss curves by ρ. Middle: final loss vs ρ — a cliff at zero. Right: random feedback makes ρ emerge on its own.](/posts/gradient-alignment.png)

## The result — a cliff at zero

- **ρ = 1.0** (the true gradient): converges, loss 0.06.
- **ρ = 0.2**: converges, 0.09.
- **ρ = 0.05** — a five-percent shadow of the real gradient: **still learns**, 0.16.
- **ρ = 0.0**: stalls. The update is orthogonal to the gradient — a random walk on the loss surface.
- **ρ = −0.2**: **explodes**, loss to $10^{25}$.

The middle panel is the law made visible: a sharp cliff at $\rho = 0$. Above it you learn, below it you diverge. It isn't "closer is better" in some fuzzy sense — it's a **sign condition**. The single bit $\langle \text{update}, g\rangle > 0$ decides whether learning happens at all.

That's the falsifier, and it's exact. If the claim were only the mushy "you need a decent gradient estimate," then ρ = 0.05 should fail. It doesn't. The prediction is specifically that the boundary sits at zero — and the cliff lands there.

## Why this isn't a toy — feedback alignment

Here's why I care. This is the crack through which brain-plausible learning gets in. In **feedback alignment**, you replace the transpose of the forward weights (which a neuron can't access) with a *fixed random matrix* $B$ in the backward pass. It sounds like it must fail — and it doesn't. The right panel shows why: I tracked the cosine between the random-feedback pseudo-gradient and the true gradient over training. It starts near zero and **climbs to ~0.45 on its own.** The forward weights rotate until they align with whatever random $B$ you handed them. The network *manufactures* the positive correlation it needs.

So backprop's exact, symmetric weights aren't sacred. Learning needs a direction that points vaguely downhill — and a system can bootstrap that out of randomness. That's a very different picture of what learning *requires*, and it's a lot friendlier to hardware and to neurons than "compute the exact transpose."

## From scratch

numpy, no autograd — the network, the controlled-ρ surrogate, and the feedback-alignment run. [The script](/posts/gradient-alignment.py) reproduces all three panels.
