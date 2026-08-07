---
title: "Break the symmetry, lose the law — energy and momentum, one at a time"
date: 2026-08-28
blurb: "Momentum is conserved because space looks the same everywhere; energy because time does. I broke each symmetry in a simulation and watched exactly its own quantity drift — momentum when I added a trap, energy when the forces turned time-dependent. Noether, surgically."
tags: ["physics", "mechanics", "symmetry", "noether"]
hero: /posts/noether.png
code: /posts/noether.py
draft: false
---

There's an asymmetry Dirac pointed at that bugged me: momentum conservation is visible *within a single instant* — you sum it over space at one moment — but energy conservation isn't, because it's a statement about comparing *different* moments. Why should momentum and energy, which sit side by side in relativity, behave so differently?

The answer is Noether's theorem: **every conservation law is a symmetry.** Momentum is conserved because space looks the same everywhere (translation symmetry); energy because time looks the same at every moment (time-translation symmetry). The cleanest way to feel that is to break each symmetry on purpose and watch which quantity dies.

## The experiment

Two particles on a line, coupled by a spring, integrated with a symplectic (energy-honest) scheme so any drift is physics, not the solver. Three worlds:

- **Both symmetries.** The spring force depends only on the separation $q_1-q_2$ (space-translation invariant) and nothing depends on time. → total momentum conserved to $10^{-14}$, energy conserved.
- **Break translation.** Add a fixed external trap $\tfrac12\Omega^2(q_1^2+q_2^2)$ — now *where* you are matters. → momentum drifts ($\Delta P = 0.72$), energy still holds.
- **Break time-translation.** Make the spring stiffness wobble in time, $k(t)=k_0(1+\tfrac12\sin\omega t)$ — now *when* you are matters. → energy drifts ($\Delta E = 7.3$, pumped in by the wobble), momentum still holds.

![Left: momentum stays flat under space symmetry, drifts when a fixed trap breaks it. Right: energy stays flat under time symmetry, drifts when the forces depend on time.](/posts/noether.png)

Each broken symmetry kills **exactly one** law, surgically. The external trap (a space asymmetry) touches momentum and leaves energy untouched. The time-dependent spring (a time asymmetry) touches energy and leaves momentum untouched. Green lines flat, red lines wandering — and never the wrong one.

## Why energy is the odd one out

Here's the asymmetry Dirac was pointing at, and why it's real. In the Hamiltonian picture, the spatial coordinates $q_i$ are *dynamical variables*. So a spatial symmetry shows up as a **missing coordinate** — if $H$ doesn't depend on some $q$, its momentum is conserved, and you can read that off at a single instant. But **time is not a coordinate in $H$ — it's the parameter you evolve along.** So time-translation symmetry can't appear as a "missing variable." It appears as $H$ having no *explicit* time dependence, which is a statement across moments, not within one. That's exactly why energy conservation "isn't visible in a single time-slice": its symmetry is the one direction the Hamiltonian singled out to march along.

The Lagrangian/relativistic view heals the split — it treats space and time on equal footing and packs both conservation laws into one equation, $\partial_\mu T^{\mu\nu}=0$, energy for $\nu=0$ and momentum for $\nu=i$. Same content, no favouritism. The Hamiltonian's asymmetry was a feature of the *bookkeeping*, not the physics.

## The falsifier

If conservation weren't tied one-to-one to symmetry, breaking translation would also disturb energy, and breaking time would also disturb momentum. Neither happens: each break moves its own quantity and nothing else, to the digit. That one-to-one is Noether's theorem, and it's on the screen.

## From scratch

numpy — two particles, a velocity-Verlet integrator, and the three symmetry worlds. [The script](/posts/noether.py) reproduces both panels.
