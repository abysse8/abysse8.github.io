---
title: "Gradient descent is just optimization at zero temperature"
date: 2026-08-16
blurb: "Add noise to gradient descent and it stops minimizing — it starts sampling the Gibbs distribution e^(−L/T) (verified to 96%). Deterministic descent is the T→0 corner of that machine: greedy, and stuck at −1.65 while a little temperature reaches the global −2.87."
tags: ["optimization", "thermodynamics", "bayesian", "learning"]
hero: /posts/thermodynamics.png
code: /posts/thermodynamics.py
draft: false
---

Here's a reframing I couldn't shake: machine learning, Bayesian inference, and thermodynamics might be one machine seen through three accents — and ordinary gradient descent is its degenerate, zero-temperature corner. The way to check that isn't to admire the analogy; it's to add a thermometer and watch what happens.

## The free-energy view

Minimize a loss $L(\theta)$ and you get a point — the minimizer. But minimize a **free energy** — expected loss minus temperature times entropy,

$$F = \langle L\rangle - T\,S,$$

and you get a *distribution*: the one that balances low loss against spread is the Gibbs distribution

$$q(\theta) \propto e^{-L(\theta)/T}.$$

At high $T$ the entropy term dominates and $q$ spreads out to explore; at $T\to 0$ the $-TS$ term vanishes, you minimize pure energy, and $q$ collapses to a single point at the global minimizer. Deterministic optimization is the cold limit of a probabilistic one.

## The experiment

Take a double-well loss (a global minimum at $L=-2.87$, a shallower local one at $L=-1.65$). Run **Langevin dynamics** — gradient descent with a dose of noise scaled by temperature:

$$\theta \leftarrow \theta - \eta\,\nabla L + \sqrt{2\eta T}\,\xi.$$

![Left: with noise, the sampled histogram matches e^(−L/T), and the mass concentrates on the global minimum as T falls. Right: expected loss vs temperature — a little heat beats greedy descent.](/posts/thermodynamics.png)

## What the thermometer shows

**Gradient descent plus noise doesn't minimize — it samples.** The left panel overlays the histogram of a long Langevin run (at $T=1$) on the analytic $e^{-L/T}$: they match to a total-variation distance of **0.04 — 96% agreement.** Turn the temperature down and the distribution sharpens; at $T=0.08$ it's a spike on the global minimum. The zero-temperature limit is a delta at the minimizer — zero spread. That *is* gradient descent.

And here's the payoff (right panel). Pure greedy descent — $T=0$, no noise — started near the shallow well and **got stuck there, at $L=-1.65$.** The Gibbs distribution at a whisper of temperature sits at the global minimum, $L\approx-2.87$. A little heat finds a strictly better optimum than determinism can, because temperature is what lets the walker climb out of a basin it should never have entered.

## Why the reframing earns its keep

If this were just a metaphor, the histogram wouldn't have matched $e^{-L/T}$ — but it did, to 96%. That's the load-bearing check: **gradient descent isn't fundamental.** It's the $T\to0$ face of a thermodynamic machine whose general object is a *probability distribution*, not a point. Inference, learning, and statistical mechanics really are running the same computation — free-energy descent — and the deterministic version we usually teach is the one corner where the temperature happens to be zero.

## From scratch

numpy — the double well, Langevin sampling, the Gibbs comparison, the expected-loss sweep. [The script](/posts/thermodynamics.py) reproduces both panels.
