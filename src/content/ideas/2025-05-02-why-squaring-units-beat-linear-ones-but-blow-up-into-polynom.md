---
title: "Why squaring units beat linear ones but blow up into polynomial chaos"
date: 2025-05-02
tags: ["neural-networks", "nonlinearity", "activation-functions", "expressivity"]
status: growing
draft: false
attribution: "your question · ChatGPT's mathematical expansion"
sources:
  - kind: chatgpt
    date: 2025-05-02
    speaker: you
    role: spark
    quote: "Explain exactly what happens in your example of f(x)=Wx+b when we have stacked units that are f(x)=Wx^2+b. Really get into the math of what goes wrong or what goes better"
  - kind: chatgpt
    date: 2025-05-02
    speaker: chatgpt
    role: crystallization
    quote: "Unlike linear stacking (which collapses), squaring expands into a **polynomial explosion**."
---

I wanted to understand what actually happens if you build a neural net from squaring units $f(x)=Wx^2+b$ instead of linear ones. The key insight is that linear layers collapse — stacking $Wx+b$ just gives another linear map — but squaring layers don't collapse: each layer doubles the polynomial degree, so $n$ layers reach degree $2^n$. That buys real expressivity (you can fit curved boundaries), but at a cost: numerical instability, brutal non-convex loss landscapes, vanishing gradients wherever intermediate values hit zero, and loss of sign information that makes things like XOR hard. So it sits between useless (linear) and balanced (ReLU/tanh) — powerful but wild.
