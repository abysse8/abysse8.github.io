---
title: "When skipping uniqueness makes your model lie: non-Lipschitz ODEs"
date: 2023-11-11
tags: ["differential-equations", "uniqueness", "mathematical-modeling", "teaching"]
status: growing
draft: false
attribution: "spark: your teaching goal · worked example and phrasing by ChatGPT"
sources:
  - kind: chatgpt
    date: 2023-11-11
    speaker: you
    role: spark
    quote: "suppose that you're studying this system and solve the equation without verifying existence and uniqueness, then your experiment might go completely astray or disaster might happen"
  - kind: chatgpt
    date: 2023-11-11
    speaker: chatgpt
    role: crystallization
    quote: "if a researcher solves this differential equation without ensuring uniqueness, they might incorrectly predict that the population will remain at zero (if they consider the trivial solution) or grow continuously (if they consider the non-trivial \\( x^3 \\) solution)"
---

I wanted a teaching example showing that if you solve an ODE without checking existence and uniqueness, your predictions can go completely astray. The equation $\frac{dy}{dx}=3y^{2/3}$ with $y(0)=0$ violates the Lipschitz condition at $y=0$, so it admits multiple genuinely different solutions: the trivial $y=0$, the growth curve $y=x^3$, and piecewise combinations of the two. Physically this models a system that stays dormant until a threshold is crossed — like a population that can either remain at zero or explode. The punchline is that a researcher trusting a single solution might badly under- or over-estimate what the real system does. It's a clean case where a math technicality has disaster-level consequences.
