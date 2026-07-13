---
title: "The 1/r hydrodynamic sum diverges — so why does colloid theory still work?"
date: 2025-03-25
tags: ["hydrodynamics", "colloids", "many-body", "stokes-flow"]
status: growing
domain: physics
draft: false
attribution: "spark: your physical objection · resolution sharpened with ChatGPT"
sources:
  - kind: chatgpt
    date: 2025-03-25
    speaker: you
    role: spark
    quote: "No, Im talking about the fact that when we have large populations of particles, the hydrodynamic interactions go with 1/r, meaning that the sum over lots of particles diverges, suggesting unbounded interaction"
  - kind: chatgpt
    date: 2025-03-25
    speaker: chatgpt
    role: crystallization
    quote: "The integral in your slide for the stability ratio \\( W \\) is based on **pairwise interactions** — it uses a **two-body model**."
---

My professor claims hydrodynamic interactions are already baked into the stability ratio W, but I don't buy that we've truly accounted for them. My worry is the many-body one: in Stokes flow a moving particle's disturbance decays only as 1/r, so summing over a large suspension gives a divergent (log R) interaction — seemingly unbounded coupling. The resolution I've landed on is that W is a strictly pairwise, dilute-limit model, and the apparent divergence gets tamed in real systems by finite size, force-neutrality (Stokeslets cancel on average), Brownian randomization, and renormalized/volume-averaged treatments like Batchelor's. So my professor and I are both right: hydrodynamics are 'included' in W, but only in the two-body sense — the full many-body problem is still open.
