---
title: "Why energy conservation isn't manifest in the Hamiltonian but momentum is"
date: 2025-04-10
tags: ["physics", "field-theory", "noether", "stress-energy-tensor"]
status: growing
draft: false
attribution: "your question, ChatGPT's synthesis"
revisits: [2025-07-06, 2025-07-06]
sources:
  - kind: chatgpt
    date: 2025-04-10
    speaker: you
    role: spark
    quote: "yes please clarify while referring to Lagrange and the Hamiltonian. What's the stress-energy tensor?"
  - kind: chatgpt
    date: 2025-04-10
    speaker: chatgpt
    role: crystallization
    quote: "Momentum conservation is “visible” at a fixed time: you can define total momentum over space, and it doesn’t change.
- But energy conservation needs you to **compare energies at different times** — and you can’t do that if you’re stuck at one time slice."
---

I'm trying to understand Dirac's point that momentum conservation is visible within a single time slice while energy conservation isn't. My hunch, sharpened here, is that this comes down to the asymmetry the Hamiltonian introduces: by picking out time as special (via $\dot\phi$), it freezes a single moment, so total momentum can be defined over space at that instant, but energy conservation requires comparing across two different times. The Lagrangian formalism keeps space and time symmetric and packages everything into the stress-energy tensor $T^{\mu\nu}$, whose single equation $\partial_\mu T^{\mu\nu}=0$ encodes both energy ($\nu=0$) and momentum ($\nu=i$) conservation together. What's unresolved for me is exactly how the Noether derivation makes 'change across time' the essential ingredient.
