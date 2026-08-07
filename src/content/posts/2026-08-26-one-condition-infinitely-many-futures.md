---
title: "One initial condition, infinitely many futures — the ODE your solver quietly lies about"
date: 2026-08-26
blurb: "dy/dx = 3y^(2/3), y(0)=0 has infinitely many solutions — stay at zero forever, or take off at any moment. A numerical solver hides all but one, and a 10^-15 change in the start (below roundoff) flips the future from 0 to 124. Uniqueness isn't a technicality."
tags: ["math", "differential-equations", "numerics", "chaos"]
hero: /posts/uniqueness.png
code: /posts/uniqueness.py
draft: false
---

Here's an equation that should make you nervous about every ODE you've ever trusted:

$$\frac{dy}{dx} = 3\,y^{2/3}, \qquad y(0)=0.$$

It has infinitely many solutions. Not approximately — genuinely, exactly, infinitely many. And a numerical solver will hand you *one* of them with total confidence and never mention the rest.

## Infinitely many futures from one start

Check them: $y \equiv 0$ solves it (both sides zero). So does $y = x^3$ ($y' = 3x^2$, and $3y^{2/3} = 3(x^3)^{2/3} = 3x^2$ ✓). And so does *staying at zero until any moment $a$ and then taking off* — $y = (x-a)^3$ for $x>a$, zero before. Every $a \ge 0$ gives a different, perfectly valid solution (left panel). One initial condition, a continuous infinity of futures.

![Left: the family of exact solutions — stay at zero, or take off at any time. Right: a solver started at 0 vs 10^-15 — one stays flat, one explodes; the Lipschitz equation ignores the difference.](/posts/uniqueness.png)

The reason is a single missing hypothesis. **Picard's theorem** guarantees a *unique* solution when the right-hand side is Lipschitz in $y$ — roughly, when its slope in $y$ is bounded. Here the slope of $3y^{2/3}$ is $2y^{-1/3}$, which blows up as $y\to 0$. Exactly at the initial condition, the Lipschitz condition fails, and uniqueness dies with it.

## Where the solver lies

Feed the exact problem to a numerical integrator. Starting from $y(0)=0$ it computes $3\cdot 0^{2/3}=0$ forever and returns the flat line — one answer, presented as *the* answer. Now nudge the start by $10^{-15}$, a value smaller than the roundoff already in your floating-point numbers. It **takes off and reaches 124** by $x=5$ (right panel, red vs grey). Same equation, same initial condition to fifteen digits, opposite futures — and which one you get is decided by numerical noise, not by the mathematics.

Compare a well-behaved (Lipschitz) equation, $y' = 1-y$: starting from $0$ and from $10^{-15}$ gives answers identical to fifteen digits (blue). The perturbation stays a perturbation. That's what uniqueness *buys* you — a future that's actually determined by the present.

## Why it's not a technicality

This equation is a textbook model of a **dormant-then-explosive** system — a population that can sit at zero or blow up, a threshold that may or may not trip. A researcher who solves it once and trusts the output could predict "nothing happens" when the real system detonates, or vice versa. The math didn't fail quietly in the background; it failed *at the answer*.

Uniqueness, which sounds like the driest possible corner of analysis, is the thing that makes "solve the equation" mean anything. When it holds, the present determines the future. When it doesn't, your solver is choosing one future out of infinitely many — and not telling you.

## The falsifier

If the solution were unique and stable, a $10^{-15}$ change in the start would produce a $10^{-15}$-scale change in the answer (that's what Lipschitz + Grönwall guarantee, and it's exactly what the blue curves show). Instead it produces a change of 124. The failure of uniqueness isn't argued — it's measured.

## From scratch

numpy — the exact solution family, an RK4 integrator, the roundoff-scale perturbation, and the Lipschitz control. [The script](/posts/uniqueness.py) reproduces both panels.
