---
title: "The slow tail you can't fake — why 2D fluids have no viscosity and gravity has no thermodynamics"
date: 2026-08-20
blurb: "A power-law tail like 1/t can't be built from decaying exponential modes — it needs a continuum of them down to zero rate. That's not a math curiosity: it's why a fluid's transport coefficient diverges in 2D, and why gravity's 1/r refuses screening and thermodynamics."
tags: ["physics", "hydrodynamics", "gravity", "information-theory"]
hero: /posts/powerlaw.png
code: /posts/powerlaw.py
draft: false
---

Start with something that looks like a math triviality: you can't build the slow tail $1/t$ out of faster-decaying pieces. Every physicist's default toolkit — normal modes, relaxation, screening — is made of *fast* pieces: things that decay exponentially, $e^{-\lambda t}$, or as steep powers. The claim is that a genuinely slow tail is irreducible to them. It turns out this is the crack that gravity and hydrodynamics both fall through.

## Why a power law isn't a sum of modes

Take $1/t$ and try to fit it with a sum of decaying exponentials — one mode, three, ten. On a limited window they track it fine. Then look further out (left panel): every fit **peels off and dies.** A finite sum of exponentials is eventually ruled by its slowest mode, so past that timescale it drops exponentially while $1/t$ keeps crawling.

![Left: sums of exponentials track 1/t briefly, then collapse. Right: the transport integral converges in 3D but diverges in 2D.](/posts/powerlaw.png)

The exact reason is a one-line identity:

$$\frac{1}{t} = \int_0^\infty e^{-\lambda t}\,d\lambda.$$

A power law *is* a sum of exponentials — but a **continuum** of them, with weight all the way down to rate $\lambda = 0$. Ordinary relaxation has a discrete set of modes with a gap (a slowest rate). To make a power law you need modes arbitrarily close to *never decaying.* That's the irreducibility, stated precisely: no gapped, finite, or discrete spectrum can produce it.

## Hydrodynamics: no viscosity in 2D

Here's where it bites. When you tag a particle in a fluid and watch its velocity autocorrelation $C(t)$, it does **not** relax exponentially. It has a power-law **long-time tail**, $C(t)\sim t^{-d/2}$ (Alder & Wainwright, 1970) — the particle's own past nudges the fluid, which nudges it back, forever, slower and slower.

Transport coefficients are the time-integral of that correlation (Green–Kubo): viscosity, diffusion $\sim \int_0^\infty C(t)\,dt$. So the tail's exponent decides whether the coefficient even *exists* (right panel):

- **3D:** $\int t^{-3/2}\,dt$ converges → a finite diffusion constant (with non-analytic corrections).
- **2D:** $\int t^{-1}\,dt$ **diverges — logarithmically, forever.** A two-dimensional fluid has *no finite viscosity.* The integral I ran to $T=10^4$ was still climbing with no plateau.

That's not a numerical artifact; it's the irreducible tail. If $C(t)$ decayed exponentially, every integral would converge and 2D fluids would be unremarkable. The slow tail is why they aren't.

## Gravity: 1/r is the same thing in space

Swap time for space and the identical irreducibility becomes gravity. The potential goes as $1/r$ — too slow to screen (you can't cancel it with a cloud of opposite charge, because there's no negative mass) and too slow to sum: $\int (1/r)\,r^2\,dr$ over a large system grows with system size. Energy stops being extensive, there's no clean thermodynamic limit, and self-gravitating systems get pathological (negative specific heat). The reason gravity won't behave like the screened, short-range forces is the reason $1/r$ can't be built from them.

## The one idea

Slow tails — $1/r$ in space, $t^{-d/2}$ in time — are irreducible to the fast, local, gapped modes our standard tools are made of. And *that* irreducibility is precisely where the tools break: no finite viscosity in 2D, no thermodynamic limit for gravity. That $\ln$ has to be a new function — that $1/t$ isn't a combination of the powers you already had — is the innocent-looking shadow of it.

## From scratch

numpy — the exponential fits, the exact continuum identity, the Green–Kubo integral in 2D vs 3D. [The script](/posts/powerlaw.py) reproduces both panels.
