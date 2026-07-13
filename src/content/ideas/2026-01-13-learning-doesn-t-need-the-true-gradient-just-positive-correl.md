---
title: "Learning doesn't need the true gradient — just positive correlation with it"
date: 2026-01-13
tags: ["feedback-alignment", "backprop", "learning-dynamics", "gradient-descent"]
status: mature
domain: ai
draft: false
attribution: "your prompt to formalise · ChatGPT's derivation and punchline"
revisits: [2025-05-02, 2025-07-13, 2026-04-11]
sources:
  - kind: chatgpt
    date: 2026-01-13
    speaker: you
    role: spark
    quote: "Let’s formalise alignment"
  - kind: chatgpt
    date: 2026-01-13
    speaker: chatgpt
    role: crystallization
    quote: "Any learning rule that produces updates with positive expected inner product with the true gradient will reduce loss."
---

I wanted to formalise why feedback alignment works instead of taking it on folklore. The core is that a fixed random feedback matrix $B$ replaces the transpose $V^T$ in the backward pass, and loss still decreases as long as $\langle V^T\delta_y, B\delta_y\rangle > 0$ — i.e. the pseudo-gradient just needs positive cosine similarity with the true gradient, not equality. What's striking is that alignment emerges dynamically: $V$ adapts to the subspace defined by $B$, so $V^T\delta_y$ rotates toward $B\delta_y$ over training. The linear case is provable ($\mathbb{E}[\cos\theta]\uparrow 1$); the nonlinear case only holds empirically and degrades with saturation and depth.
