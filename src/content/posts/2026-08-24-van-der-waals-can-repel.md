---
title: "Van der Waals forces can push things apart — if the medium's dielectric sits between"
date: 2026-08-24
blurb: "Van der Waals is supposed to be always attractive. It isn't. Sandwich a medium whose dielectric constant falls between the two materials' and the force flips sign — the Hamaker constant goes negative, exactly where (ε₁−εₘ)(ε₂−εₘ) < 0. Not high dielectric. The ordering."
tags: ["physics", "electromagnetism", "surfaces", "casimir"]
hero: /posts/vanderwaals.png
code: /posts/vanderwaals.py
draft: false
---

Van der Waals forces have a reputation for being *always attractive* — it's why gecko feet stick and why fine powders clump. So a repulsive one sounds impossible. It isn't, and the puzzle that bothered me was this: a separating medium can have a perfectly high dielectric constant and nothing special happens. So what actually causes the repulsion?

The answer isn't the *strength* of the medium's response. It's the **ordering**.

## The sign law

Between two materials (dielectric constants $\varepsilon_1$, $\varepsilon_2$) across a medium ($\varepsilon_m$), Lifshitz theory gives a Hamaker constant whose leading term carries the sign

$$A \;\propto\; (\varepsilon_1-\varepsilon_m)(\varepsilon_2-\varepsilon_m).$$

Attraction is $A>0$, repulsion is $A<0$. And that product is negative for exactly one reason: **one factor positive, one negative** — i.e. $\varepsilon_m$ sits *between* $\varepsilon_1$ and $\varepsilon_2$.

![Left: the Hamaker constant vs the medium's dielectric — negative (repulsive) only between ε₁ and ε₂. Right: the sign map — repulsive exactly in the two 'sandwich' quadrants.](/posts/vanderwaals.png)

Sweep the medium's dielectric (left panel) with the two materials fixed at $\varepsilon_1=2$, $\varepsilon_2=12$: the force is attractive when $\varepsilon_m$ is below both or above both, and **repulsive only in the window between them.** It crosses zero precisely at $\varepsilon_m=\varepsilon_1$ and $\varepsilon_m=\varepsilon_2$. The right panel is the sign in the $(\varepsilon_1,\varepsilon_2)$ plane: repulsion lives in the two off-diagonal quadrants — one material above the medium, one below. Nowhere else.

## Why "between" is the magic word

One interface term $(\varepsilon_1-\varepsilon_m)$ says how material 1 stands out from the medium; the other says the same for material 2. If the medium is denser (optically) than one material and thinner than the other, those two terms have opposite signs — the medium couples more strongly to one wall than the other and wedges itself in, prying them apart. When the medium is more or less extreme than *both* walls, the terms agree in sign, the product is positive, and you're back to ordinary attraction.

This is why "high dielectric" alone does nothing: push $\varepsilon_m$ above *both* materials and the force is attractive again (right side of the left panel). It was never about magnitude — it was about being in the middle.

## The honest caveat

Real materials have **frequency-dependent** permittivity $\varepsilon(i\xi)$, and the full theory integrates over frequency. So the sign law above is the leading (static) picture; for a genuinely repulsive net force, the ordering $\varepsilon_1 < \varepsilon_m < \varepsilon_2$ has to hold across the frequency range that dominates the integral. When it does, the effect is real and measured: Munday, Capasso & Parsegian (2009) pulled it off with gold and silica across bromobenzene — a sandwich engineered to keep the ordering.

## The falsifier

If repulsion came from a strong medium, then $\varepsilon_m$ larger than both materials would repel. It attracts. The sign flips at $\varepsilon_m=\varepsilon_1$ and $\varepsilon_m=\varepsilon_2$ and nowhere else — which is exactly the prediction, and exactly what the sweep shows.

## From scratch

numpy — the Hamaker sign law, the sweep, the two-material sign map. [The script](/posts/vanderwaals.py) reproduces both panels.
